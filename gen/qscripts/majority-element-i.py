#!/usr/bin/env python3
"""
Test-case generator for Striver problem: majority-element-i

Problem: Given an integer array nums of size n, return the majority element
(the element that appears more than n/2 times). Array guaranteed to have one.

Signature: int majorityElement(vector<int>& nums)
  -> input key: "nums"  (int array, formatted "[a, b, c]")
  -> expected: the majority element as a plain int string

Constraints:
  1 <= n <= 1e5
  -1e4 <= nums[i] <= 1e4
  One value appears more than n/2 times (guaranteed).

We GENERATE inputs that always satisfy the "majority exists" constraint by
construction: pick a majority value, fill > n/2 slots with it, fill the rest
with arbitrary in-range values, then shuffle. We then compute the expected
output with the Boyer-Moore reference oracle and additionally cross-check it
against a direct frequency count, asserting agreement.
"""

import json
import random
from collections import Counter

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/majority-element-i.jsonl"
N_CASES = 2000

LO, HI = -10**4, 10**4          # value range
N_MAX = 10**5                   # max array length

random.seed(20260606)


def boyer_moore(nums):
    """Ground-truth oracle (mirrors the C++ reference)."""
    cnt = 0
    el = None
    n = len(nums)
    for x in nums:
        if cnt == 0:
            el = x
            cnt = 1
        elif x == el:
            cnt += 1
        else:
            cnt -= 1
    # verify the candidate truly is the majority. Our generated inputs ALWAYS
    # have a strict majority, so this must hold. (Note: -1 is a legitimate
    # answer when -1 is the majority value, so we never use -1 as a sentinel.)
    c = sum(1 for x in nums if x == el)
    if c > n // 2:
        return el
    raise ValueError("input has no strict majority (generator bug)")


def make_majority_array(n):
    """Build an array of length n with a guaranteed strict majority element."""
    # majority must appear MORE than n//2 times.
    maj = random.randint(LO, HI)
    min_maj_count = n // 2 + 1          # strictly more than half
    maj_count = random.randint(min_maj_count, n)
    rest = n - maj_count

    arr = [maj] * maj_count
    # fill remaining with values != maj when possible (still in range)
    for _ in range(rest):
        v = random.randint(LO, HI)
        if v == maj:
            # nudge to keep them non-majority noise; staying in range
            v = maj + 1 if maj < HI else maj - 1
        arr.append(v)
    random.shuffle(arr)
    return arr


def fmt_arr(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def gen_case(idx):
    if idx == 0:
        arr = [0]                                  # min size n=1
    elif idx == 1:
        arr = [LO]                                 # n=1, extreme low
    elif idx == 2:
        arr = [HI]                                 # n=1, extreme high
    elif idx == 3:
        arr = [5, 5]                               # n=2 (count 2 > 1)
    elif idx == 4:
        arr = make_majority_array(3)               # tiny odd
    elif idx == 5:
        arr = [HI] * 50000 + [LO] * 49999          # near max, tight margin
        random.shuffle(arr)
    elif idx == 6:
        arr = [LO] * (N_MAX // 2 + 1) + [random.randint(LO, HI) for _ in range(N_MAX // 2 - 1)]
        random.shuffle(arr)                        # full size n=1e5
    elif idx == 7:
        arr = [-1, -1, -1, -1]                     # dataset "now your turn" case
    else:
        # vary size: bias toward small, but include large occasionally
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 30)
        elif r < 0.85:
            n = random.randint(31, 1000)
        else:
            n = random.randint(1001, N_MAX)
        arr = make_majority_array(n)
    return arr


def main():
    lines = []
    for i in range(N_CASES):
        arr = gen_case(i)

        # sanity: bounds
        assert 1 <= len(arr) <= N_MAX, f"bad length {len(arr)}"
        assert all(LO <= x <= HI for x in arr), "value out of range"
        # sanity: a strict majority must exist
        c = Counter(arr)
        top_val, top_cnt = c.most_common(1)[0]
        assert top_cnt > len(arr) // 2, f"no strict majority in case {i}"

        exp = boyer_moore(arr)
        # cross-check oracle against direct frequency
        assert exp == top_val, f"oracle mismatch case {i}: {exp} vs {top_val}"

        lines.append(json.dumps({"inputs": {"nums": fmt_arr(arr)},
                                 "expected": str(exp)}))

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
