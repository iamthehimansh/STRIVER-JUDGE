#!/usr/bin/env python3
"""Test-case generator for Striver problem: Count all subsequences with sum K.

Signature (starterCpp):
    int countSubsequenceWithTargetSum(vector<int>& nums, int k)

Constraints:
    1 <= nums.length <= 20
    1 <= nums[i] <= 100
    1 <= k <= 2000

Output: number of NON-EMPTY subsequences whose element sum == k.

JSONL keys are in signature order: "nums", "k".
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-all-subsequences-with-sum-k.jsonl"
N_CASES = 2000


def count_subsequences_with_sum(nums, k):
    """Reference: count non-empty subsequences with sum exactly k.

    DP over counts. dp[s] = number of subsequences (including empty) with sum s.
    Empty subsequence contributes to dp[0]; we subtract it only if k == 0,
    but k >= 1 by constraints so empty never matches. We answer dp[k].
    """
    # dp[s] = number of subsequences (incl. empty) summing to s, for 0..k
    dp = [0] * (k + 1)
    dp[0] = 1  # empty subsequence
    for v in nums:
        if v > k:
            continue  # can't be part of any subsequence summing to <= k
        # iterate sums downward not needed here because each element used once;
        # but since we add a NEW element across all existing subsequences,
        # iterate s from k down to v to avoid reusing the same element twice.
        for s in range(k, v - 1, -1):
            dp[s] += dp[s - v]
    return dp[k]


def fmt_int_array(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def gen_case(rng):
    n = rng.randint(1, 20)
    nums = [rng.randint(1, 100) for _ in range(n)]
    # Choose k strategy to get a healthy mix of zero / non-zero answers.
    mode = rng.random()
    if mode < 0.45 and n >= 1:
        # k = sum of a random non-empty subset => guarantees >=1 match,
        # clamped to <= 2000.
        subset_size = rng.randint(1, n)
        idxs = rng.sample(range(n), subset_size)
        s = sum(nums[i] for i in idxs)
        if 1 <= s <= 2000:
            k = s
        else:
            k = rng.randint(1, 2000)
    elif mode < 0.7:
        # k within total-sum range (likely achievable for small sums)
        total = sum(nums)
        hi = min(total, 2000)
        k = rng.randint(1, max(1, hi))
    else:
        # uniform over full k range
        k = rng.randint(1, 2000)
    k = max(1, min(2000, k))
    return nums, k


def main():
    rng = random.Random(20240606)
    cases = []

    # --- Edge / extreme cases first ---
    # min size, single element matching
    cases.append(([1], 1))
    cases.append(([100], 100))
    cases.append(([1], 2000))      # no match
    cases.append(([100], 1))       # no match
    cases.append(([1], 2))         # no match (single element)
    # all ones, max length -> many subsequences
    cases.append(([1] * 20, 10))   # C(20,10)
    cases.append(([1] * 20, 20))   # 1 (the full set)
    cases.append(([1] * 20, 1))    # 20
    cases.append(([1] * 20, 21))   # 0 impossible
    # max values, max length, large k
    cases.append(([100] * 20, 2000))  # all 20 -> 1
    cases.append(([100] * 20, 100))   # 20
    cases.append(([100] * 20, 1))     # 0
    cases.append(([100] * 20, 500))   # C(20,5)
    # example cases from the problem statement
    cases.append(([4, 9, 2, 5, 1], 10))            # -> 2
    cases.append(([4, 2, 10, 5, 1, 3], 5))         # -> 3
    cases.append(([1, 10, 4, 5], 16))              # -> 1 ({1,10,5}); nowYourTurn case
    cases.append(([1, 2, 3, 4, 5, 6, 7], 7))       # testcase 3
    # mixed
    cases.append(([2, 2, 2, 2], 4))                # C(4,2) = 6
    cases.append(([5, 5, 5], 5))                   # 3
    cases.append(([1, 2, 3], 6))                   # 1

    # --- Random cases to fill up to N_CASES ---
    while len(cases) < N_CASES:
        cases.append(gen_case(rng))

    cases = cases[:N_CASES]

    with open(OUT_PATH, "w") as f:
        for nums, k in cases:
            expected = count_subsequences_with_sum(nums, k)
            obj = {
                "inputs": {
                    "nums": fmt_int_array(nums),
                    "k": str(k),
                },
                "expected": str(expected),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
