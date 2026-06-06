#!/usr/bin/env python3
# Generator for "Sort an array of 0's 1's and 2's"
# Signature: void sortZeroOneTwo(vector<int>& nums)
#   -> single param "nums", output is the sorted array (in non-decreasing order).
# Constraints: 1 <= nums.length <= 1e5 ; nums consists of 0,1,2 only.
#
# Reference oracle: sorting an array of {0,1,2} == counting sort (Dutch flag).
# We use Python's sorted() which is the ground truth for non-decreasing order.

import random
import os

OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "generated-tests",
    "sort-an-array-of-0's-1's-and-2's.jsonl",
)

random.seed(20260606)

MAXN = 10**5


def reference(nums):
    # Ground truth: non-decreasing sort of values in {0,1,2}.
    return sorted(nums)


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def make_case(n, mode="rand"):
    if mode == "rand":
        return [random.randint(0, 2) for _ in range(n)]
    if mode == "all0":
        return [0] * n
    if mode == "all1":
        return [1] * n
    if mode == "all2":
        return [2] * n
    if mode == "sorted":
        # already sorted mix
        z = random.randint(0, n)
        o = random.randint(0, n - z)
        t = n - z - o
        return [0] * z + [1] * o + [2] * t
    if mode == "revsorted":
        z = random.randint(0, n)
        o = random.randint(0, n - z)
        t = n - z - o
        return [2] * t + [1] * o + [0] * z
    if mode == "two_vals":
        vals = random.sample([0, 1, 2], 2)
        return [random.choice(vals) for _ in range(n)]
    return [random.randint(0, 2) for _ in range(n)]


def main():
    cases = []

    # ---- Edge cases (min size, extremes, single-value, etc.) ----
    edge = []
    # n = 1, each single value
    edge.append([0])
    edge.append([1])
    edge.append([2])
    # small explicit
    edge.append([1, 0, 2, 1, 0])      # example 1
    edge.append([0, 0, 1, 1, 1])      # example 2
    edge.append([1, 1, 2, 2, 1])      # nowYourTurn
    edge.append([2, 1, 0])
    edge.append([0, 1, 2])
    edge.append([2, 2, 2, 1, 1, 1, 0, 0, 0])
    edge.append([2, 0])
    edge.append([0, 2])
    edge.append([1, 1])
    # all-same large
    edge.append([0] * MAXN)
    edge.append([2] * MAXN)
    edge.append([1] * MAXN)
    # reverse sorted large
    edge.append([2] * 50000 + [1] * 30000 + [0] * 20000)
    # max size random
    edge.append([random.randint(0, 2) for _ in range(MAXN)])

    cases.extend(edge)

    # ---- Random cases across sizes ----
    modes = ["rand", "sorted", "revsorted", "two_vals", "all0", "all1", "all2"]
    target = 2000
    while len(cases) < target:
        r = random.random()
        if r < 0.45:
            n = random.randint(1, 50)
        elif r < 0.75:
            n = random.randint(1, 1000)
        elif r < 0.92:
            n = random.randint(1, 20000)
        else:
            n = random.randint(1, MAXN)
        mode = random.choice(modes)
        cases.append(make_case(n, mode))

    cases = cases[:target]

    with open(OUT, "w") as f:
        for nums in cases:
            assert 1 <= len(nums) <= MAXN, "size out of bounds"
            assert all(v in (0, 1, 2) for v in nums), "value out of bounds"
            exp = reference(nums)
            obj_in = fmt_arr(nums)
            obj_out = fmt_arr(exp)
            # Manual JSON to avoid huge memory overhead; values are simple.
            line = (
                '{"inputs": {"nums": '
                + _jstr(obj_in)
                + '}, "expected": '
                + _jstr(obj_out)
                + "}"
            )
            f.write(line + "\n")

    print(f"Wrote {len(cases)} cases to {OUT}")


def _jstr(s):
    # JSON-encode a string (these never contain quotes/backslashes, but be safe).
    out = ['"']
    for ch in s:
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


if __name__ == "__main__":
    main()
