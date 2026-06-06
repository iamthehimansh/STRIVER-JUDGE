#!/usr/bin/env python3
"""
Generator for Striver problem: Rearrange array elements by sign.

Signature: vector<int> rearrangeArray(vector<int>& nums)

Constraints:
  - 2 <= nums.length <= 10^5
  - 1 <= |nums[i]| <= 10^4
  - nums.length is even
  - number of positive and negative numbers are equal

Reference logic (matches strivers / ref2 optimal solution):
  positives go to even indices (0,2,4,...) preserving relative order,
  negatives go to odd indices (1,3,5,...) preserving relative order.
"""
import random
import json
import os

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/rearrange-array-elements-by-sign.jsonl"

# Max length kept modest so 2000 cases stay reasonable; still exercises constraint range.
MAX_N = 10**5
MAX_ABS = 10**4


def reference(nums):
    n = len(nums)
    ans = [0] * n
    pos = 0
    neg = 1
    for x in nums:
        if x > 0:
            ans[pos] = x
            pos += 2
        else:
            ans[neg] = x
            neg += 2
    return ans


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def make_nums(half):
    """Build an array with `half` positives and `half` negatives, shuffled.
    Values have absolute value in [1, MAX_ABS]; positives in [1,MAX_ABS],
    negatives in [-MAX_ABS, -1]."""
    n = 2 * half
    vals = []
    for _ in range(half):
        vals.append(random.randint(1, MAX_ABS))            # positive
    for _ in range(half):
        vals.append(-random.randint(1, MAX_ABS))           # negative
    random.shuffle(vals)
    return vals


def gen_cases(count):
    cases = []

    # Fixed edge cases first.
    edge = []
    # minimal size 2
    edge.append([1, -1])
    edge.append([-1, 1])
    edge.append([MAX_ABS, -MAX_ABS])
    edge.append([-MAX_ABS, MAX_ABS])
    # all max magnitude
    edge.append([MAX_ABS, MAX_ABS, -MAX_ABS, -MAX_ABS])
    # dataset examples
    edge.append([2, 4, 5, -1, -3, -4])
    edge.append([1, -1, -3, -4, 2, 3])
    edge.append([-4, 4, -4, 4, -4, 4])
    # already alternating starting positive
    edge.append([1, -2, 3, -4, 5, -6])
    # positives clustered then negatives
    edge.append([3, 1, 2, -3, -1, -2])
    # negatives clustered then positives
    edge.append([-3, -1, -2, 3, 1, 2])
    for e in edge:
        cases.append(e)

    while len(cases) < count:
        r = random.random()
        if r < 0.25:
            half = random.randint(1, 5)          # tiny
        elif r < 0.6:
            half = random.randint(1, 50)         # small
        elif r < 0.9:
            half = random.randint(1, 2000)       # medium
        else:
            half = random.randint(1, MAX_N // 2) # large (up to 10^5 total)
        cases.append(make_nums(half))

    return cases[:count]


def main():
    random.seed(20260606)
    count = 2000
    cases = gen_cases(count)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for nums in cases:
            ans = reference(nums)
            obj = {
                "inputs": {"nums": fmt_arr(nums)},
                "expected": fmt_arr(ans),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {count} cases to {OUT}")


if __name__ == "__main__":
    main()
