#!/usr/bin/env python3
"""Generator for Striver problem 'Subsets I' (subsets-i).

Problem: Given array nums of n integers, return the array of sums of all subsets.
starterCpp signature: vector<int> subsetSums(vector<int>& nums)
  -> single param "nums" (int array). No size param to drop.

Constraints:
  1 <= n <= 15
  0 <= nums[i] <= 10^4

Reference oracle (implemented inline in Python, matches Striver C++ reference):
  enumerate all 2^n subsets, sum each, sort ascending.
  (The dataset examples show sorted output; judge is lenient anyway.)

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/subsets-i.jsonl
  one JSON object per line: {"inputs": {"nums": "[...]"}, "expected": "[...]"}
"""
import json
import random
from itertools import combinations

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/subsets-i.jsonl"
N_CASES = 2000
MAX_VAL = 10**4
MAX_N = 15
MIN_N = 1


def subset_sums(nums):
    """Reference oracle: sums of all subsets, sorted ascending."""
    n = len(nums)
    sums = []
    for mask in range(1 << n):
        s = 0
        m = mask
        i = 0
        while m:
            if m & 1:
                s += nums[i]
            m >>= 1
            i += 1
        sums.append(s)
    sums.sort()
    return sums


def fmt_int_array(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def make_case(rng):
    n = rng.randint(MIN_N, MAX_N)
    nums = [rng.randint(0, MAX_VAL) for _ in range(n)]
    return nums


def main():
    rng = random.Random(20240606)
    seen = set()
    cases = []

    # ---- deterministic edge cases ----
    edge = []
    edge.append([0])                      # min size, zero
    edge.append([10000])                  # min size, max value
    edge.append([1])                      # nowYourTurn example -> [0,1]
    edge.append([2, 3])                   # example 1
    edge.append([5, 2, 1])                # example 2
    edge.append([9, 23, 76, 19, 1])       # dataset case 3 (expected null)
    edge.append([0] * 15)                 # all zeros, max n
    edge.append([10000] * 15)             # all max, max n
    edge.append(list(range(15)))          # 0..14
    edge.append([10000] * 14 + [0])       # near-max n with zero
    edge.append([0, 0, 1])                # duplicates incl zero
    edge.append([7, 7, 7, 7])             # all equal
    edge.append([10000, 0])               # max and min
    for n in range(1, 16):                # one all-max array per size
        edge.append([MAX_VAL] * n)

    for c in edge:
        key = tuple(c)
        if key not in seen:
            seen.add(key)
            cases.append(c)

    # ---- random cases ----
    attempts = 0
    while len(cases) < N_CASES and attempts < N_CASES * 50:
        attempts += 1
        c = make_case(rng)
        key = tuple(c)
        if key in seen:
            continue
        seen.add(key)
        cases.append(c)

    cases = cases[:N_CASES]

    with open(OUT, "w") as f:
        for nums in cases:
            assert MIN_N <= len(nums) <= MAX_N
            assert all(0 <= x <= MAX_VAL for x in nums)
            expected = subset_sums(nums)
            obj = {
                "inputs": {"nums": fmt_int_array(nums)},
                "expected": fmt_int_array(expected),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
