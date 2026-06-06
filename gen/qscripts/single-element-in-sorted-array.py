#!/usr/bin/env python3
"""
Generator for Striver problem: Single element in a Sorted Array
slug: single-element-in-sorted-array

Signature (starterCpp):  int singleNonDuplicate(vector<int> &nums)
  -> single input param "nums" (sorted, non-decreasing, every element appears
     exactly twice except ONE which appears once).

Constraints:
  n == nums.length,  1 <= n <= 1e4,  -1e4 <= nums[i] <= 1e4
  Therefore n is ALWAYS odd (k pairs + 1 single => 2k+1).

Output line format (per case):
  {"inputs": {"nums": "[...]"}, "expected": "<int>"}

Expected is computed by a Python port of the reference binary search
(strivers-a2z-ref/.../12.Find_single_element_in_sorted_array.cpp). We also
cross-check it against the unambiguous structural answer (the single element).
"""

import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/single-element-in-sorted-array.jsonl"
N_CASES = 2000
LO, HI = -10000, 10000   # value bounds
MAX_N = 10000            # max length

random.seed(20260606)


def reference(nums):
    """Port of the C++ reference binary search (ground-truth oracle)."""
    low, high = 0, len(nums) - 1
    while low < high:
        mid = low + (high - low) // 2
        if mid % 2 == 0:
            if nums[mid] == nums[mid + 1]:
                low = mid + 1
            else:
                high = mid
        else:
            if nums[mid] != nums[mid + 1]:
                low = mid + 1
            else:
                high = mid
    return nums[low]


def build_array(num_pairs, single_value, pair_values):
    """Construct a valid sorted array: each pair_value appears twice, single once.
    All values placed then sorted to guarantee non-decreasing order.
    """
    vals = []
    for v in pair_values:
        vals.append(v)
        vals.append(v)
    vals.append(single_value)
    vals.sort()
    return vals


def random_case():
    """Generate a random valid array.

    Strategy: choose how many distinct *positions* the array has. The array
    has 2k+1 elements. We pick k pair-values and 1 single-value. To keep it a
    clean 'every value twice except one' we make all chosen values distinct.
    n distinct values needed = k + 1 <= 20001 available integer values, and
    k <= (MAX_N-1)/2 = 4999. Both fit.
    """
    # n is odd: choose k pairs, k in [0 .. 4999]
    k = random.randint(0, (MAX_N - 1) // 2)
    total_distinct = k + 1  # k pair values + 1 single value, all distinct
    # available integers in [LO, HI] = 20001, always enough for k<=4999
    chosen = random.sample(range(LO, HI + 1), total_distinct)
    single_value = chosen[0]
    pair_values = chosen[1:]
    return build_array(k, single_value, pair_values)


def edge_cases():
    cases = []
    # n == 1 (minimum size), single element only
    cases.append([0])
    cases.append([-10000])
    cases.append([10000])
    # single at the very start
    cases.append([5, 7, 7, 9, 9])      # single = 5
    # single at the very end
    cases.append([1, 1, 3, 3, 8])      # single = 8
    # single in middle
    cases.append([1, 1, 3, 5, 5])      # single = 3 (example 2)
    # dataset example 1
    cases.append([1, 1, 2, 2, 3, 3, 4, 5, 5, 6, 6])  # single = 4
    # dataset example 3 (nowYourTurn)
    cases.append([1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7])  # single = 7
    # extreme negative pairs with single positive
    cases.append([-10000, -10000, -1, -1, 0, 0, 10000])
    # all values at min/around, single distinct
    cases.append([-10000, -9999, -9999])  # single = -10000
    # n == 3 single at start/mid/end variations
    cases.append([2, 4, 4])  # single 2
    cases.append([2, 2, 4])  # single 4
    # larger structured: pairs 0..4998 then single 9999  (length 9999)
    big = []
    for v in range(0, 4999):
        big.append(v); big.append(v)
    big.append(9999)
    big.sort()
    cases.append(big)
    # max length n == 9999 (largest odd <= 1e4): pairs of even-spaced negatives
    big2 = []
    vals = random.sample(range(LO, HI + 1), 4999 + 1)
    s = vals[0]
    for v in vals[1:]:
        big2.append(v); big2.append(v)
    big2.append(s)
    big2.sort()
    cases.append(big2)
    return cases


def fmt_array(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def validate(arr):
    n = len(arr)
    assert 1 <= n <= MAX_N, f"n out of range: {n}"
    assert n % 2 == 1, f"n must be odd, got {n}"
    # non-decreasing
    for i in range(1, n):
        assert arr[i - 1] <= arr[i], "not sorted"
    # value bounds
    for x in arr:
        assert LO <= x <= HI, f"value out of range: {x}"
    # exactly one element appears odd number of times; here structure => one single
    from collections import Counter
    c = Counter(arr)
    singles = [v for v, cnt in c.items() if cnt % 2 == 1]
    assert len(singles) == 1, f"expected exactly one single, got {singles}"
    # cross-check: reference must return the structural single
    assert reference(arr) == singles[0], "reference mismatch with structural single"
    return singles[0]


def main():
    cases = []
    ec = edge_cases()
    cases.extend(ec)
    while len(cases) < N_CASES:
        cases.append(random_case())
    cases = cases[:N_CASES]

    with open(OUT_PATH, "w") as f:
        for arr in cases:
            single = validate(arr)            # asserts validity + oracle agreement
            expected = reference(arr)
            assert expected == single
            line = {"inputs": {"nums": fmt_array(arr)}, "expected": str(expected)}
            f.write(json.dumps(line) + "\n")

    print(f"wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
