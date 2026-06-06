#!/usr/bin/env python3
"""
Test-case generator for Striver problem: merge-sorting (slug: merge-sorting)

Problem: Given an array of integers `nums`, sort it in non-decreasing order
using merge sort. Return the sorted array.

Signature (starterCpp):  vector<int> mergeSort(vector<int>& nums)
  -> single param: nums  (int array)
  -> output: the sorted int array

Constraints:
  1 <= nums.length <= 10^6
  -10^4 <= nums[i] <= 10^4   (duplicates allowed)

Oracle: a full sort in non-decreasing order is exactly what merge sort produces;
Python's sorted() is used as the ground-truth reference (identical result to a
correct merge sort for a complete ascending sort).

Output file format (one JSON object per line):
  {"inputs": {"nums": "[3, 1, 2]"}, "expected": "[1, 2, 3]"}
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/merge-sorting.jsonl"
N_CASES = 2000

LO, HI = -10**4, 10**4          # value range
MIN_LEN = 1                      # min array length per constraints
# We keep generated array lengths modest so the judge can run user code per
# case quickly. The constraint upper bound is 10^6, but small/medium arrays
# fully exercise the sort. A few large cases are included as stress tests.

def merge_sort_reference(a):
    """Ground-truth merge sort (faithful to the problem's algorithm)."""
    n = len(a)
    if n <= 1:
        return list(a)
    mid = n // 2
    left = merge_sort_reference(a[:mid])
    right = merge_sort_reference(a[mid:])
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:])
    res.extend(right[j:])
    return res

def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"

def gen_array(rng):
    """Pick a length and value distribution within constraints."""
    r = rng.random()
    if r < 0.10:
        n = 1                                   # min size edge case
    elif r < 0.55:
        n = rng.randint(2, 30)                  # small
    elif r < 0.85:
        n = rng.randint(30, 300)                # medium
    elif r < 0.97:
        n = rng.randint(300, 2000)              # large
    else:
        n = rng.randint(2000, 20000)            # stress (well under 10^6)

    mode = rng.random()
    if mode < 0.55:
        # fully random
        return [rng.randint(LO, HI) for _ in range(n)]
    elif mode < 0.70:
        # many duplicates (narrow value window)
        lo = rng.randint(LO, HI - 5)
        hi = min(HI, lo + rng.randint(1, 5))
        return [rng.randint(lo, hi) for _ in range(n)]
    elif mode < 0.80:
        # already sorted ascending
        arr = sorted(rng.randint(LO, HI) for _ in range(n))
        return arr
    elif mode < 0.90:
        # reverse sorted
        arr = sorted((rng.randint(LO, HI) for _ in range(n)), reverse=True)
        return arr
    elif mode < 0.95:
        # all equal
        v = rng.randint(LO, HI)
        return [v] * n
    else:
        # extreme values only
        return [rng.choice([LO, HI, 0]) for _ in range(n)]

def main():
    rng = random.Random(20260606)
    seen = set()
    lines = []

    # Explicit edge cases first.
    edge = [
        [7, 4, 1, 5, 3],          # dataset example 1
        [5, 4, 4, 1, 1],          # dataset example 2
        [3, 2, 3, 4, 5],          # dataset "now your turn"
        [0],                       # single zero
        [LO],                      # single min
        [HI],                      # single max
        [LO, HI],                  # two extremes
        [HI, LO],                  # two extremes reversed
        [0, 0, 0, 0],              # all zeros
        [LO, LO, LO],              # all min
        [HI, HI, HI],              # all max
        [1, -1, 1, -1, 1, -1],     # alternating
        [2, 1],                    # tiny unsorted
        [1, 2],                    # tiny sorted
    ]
    for a in edge:
        key = tuple(a)
        if key in seen:
            continue
        seen.add(key)
        lines.append({"inputs": {"nums": fmt_arr(a)},
                      "expected": fmt_arr(merge_sort_reference(a))})

    while len(lines) < N_CASES:
        a = gen_array(rng)
        # dedupe only on small arrays (large ones are effectively unique)
        if len(a) <= 30:
            key = tuple(a)
            if key in seen:
                continue
            seen.add(key)
        expected = merge_sort_reference(a)
        # sanity: reference must equal Python's sorted()
        assert expected == sorted(a)
        lines.append({"inputs": {"nums": fmt_arr(a)},
                      "expected": fmt_arr(expected)})

    lines = lines[:N_CASES]
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for obj in lines:
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(lines)} cases to {OUT_PATH}")

if __name__ == "__main__":
    main()
