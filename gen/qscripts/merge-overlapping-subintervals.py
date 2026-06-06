#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Merge Overlapping Subintervals
(slug: merge-overlapping-subintervals)

starterCpp signature:
    vector<vector<int>> mergeOverlap(vector<vector<int>>& arr)

Param name (signature order): arr   -> 2D int array
Output: array of non-overlapping merged intervals, flattened to space-separated
        numbers (judge compares leniently, ignoring brackets/commas/whitespace).

Constraints:
    1 <= intervals.length <= 10^5
    0 <= start_i <= end_i <= 10^5

Reference algorithm (matches /Users/iamthehimansh/Downloads/ref2/Merge Intervals.cpp
and strivers-a2z-ref): sort by start, then linear merge.

Writes 2000 cases to:
    /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/merge-overlapping-subintervals.jsonl
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/merge-overlapping-subintervals.jsonl"
N_CASES = 2000
VAL_MAX = 10 ** 5          # 0 <= start <= end <= 10^5
LEN_MAX = 10 ** 5          # 1 <= length <= 10^5

random.seed(20260606)


def merge_reference(intervals):
    """Ground-truth oracle. intervals: list of [start, end]."""
    arr = sorted(intervals)  # sort by start (then end) — same as C++ default sort
    ans = []
    for s, e in arr:
        if ans and s <= ans[-1][1]:
            if e > ans[-1][1]:
                ans[-1][1] = e
        else:
            ans.append([s, e])
    return ans


def fmt_2d(intervals):
    # e.g. [[1,2],[3,4]]
    return "[" + ",".join("[" + str(s) + "," + str(e) + "]" for s, e in intervals) + "]"


def fmt_expected(intervals):
    # flatten matrix to space-separated numbers on one line
    flat = []
    for s, e in intervals:
        flat.append(str(s))
        flat.append(str(e))
    return " ".join(flat)


def rand_interval(vmax=VAL_MAX):
    s = random.randint(0, vmax)
    e = random.randint(s, vmax)
    return [s, e]


def gen_case(idx):
    """Return a list of intervals respecting all constraints."""
    # A handful of deterministic edge cases first.
    if idx == 0:
        return [[0, 0]]                                   # min size, min values
    if idx == 1:
        return [[VAL_MAX, VAL_MAX]]                       # min size, max values
    if idx == 2:
        return [[0, VAL_MAX]]                             # single full-range interval
    if idx == 3:
        return [[1, 5], [3, 6], [8, 10], [15, 18]]       # example 1
    if idx == 4:
        return [[5, 7], [1, 3], [4, 6], [8, 10]]         # example 2
    if idx == 5:
        return [[2, 3], [4, 5], [6, 7], [8, 9]]          # all disjoint (Case 3)
    if idx == 6:
        return [[1, 4], [4, 5]]                          # touching endpoints (merge)
    if idx == 7:
        return [[0, 0], [0, 0], [0, 0]]                  # all identical zero-width
    if idx == 8:
        return [[VAL_MAX, VAL_MAX]] * 5                   # identical max zero-width
    if idx == 9:
        return [[0, VAL_MAX]] * 4                         # identical full-range
    if idx == 10:
        return [[i, i] for i in range(0, 50)]            # many tiny disjoint points
    if idx == 11:
        # nested intervals -> one big merge
        return [[0, VAL_MAX], [10, 20], [5, 9], [30, 40]]
    if idx == 12:
        # reverse-sorted input, all overlapping in chain
        return [[10, 12], [8, 11], [6, 9], [4, 7], [2, 5], [0, 3]]
    if idx == 13:
        # large case at near-max length, fully overlapping -> single output
        return [[0, VAL_MAX] for _ in range(LEN_MAX)]
    if idx == 14:
        # large case, all disjoint points -> length-preserving output
        return [[i, i] for i in range(0, LEN_MAX)]

    # Random cases with varied profiles.
    bucket = idx % 5
    if bucket == 0:
        n = random.randint(1, 5)                         # tiny
        vmax = random.choice([5, 20, 100, VAL_MAX])
    elif bucket == 1:
        n = random.randint(5, 50)                        # small
        vmax = random.choice([20, 100, 1000, VAL_MAX])
    elif bucket == 2:
        n = random.randint(50, 500)                      # medium
        vmax = random.choice([100, 1000, 50000, VAL_MAX])
    elif bucket == 3:
        n = random.randint(500, 5000)                    # large
        vmax = VAL_MAX
    else:
        n = random.randint(1, 30)                        # tight value range -> heavy overlap
        vmax = random.choice([2, 5, 10])

    intervals = [rand_interval(vmax) for _ in range(n)]
    random.shuffle(intervals)
    return intervals


def main():
    lines = []
    for idx in range(N_CASES):
        intervals = gen_case(idx)
        # safety: enforce constraints
        assert 1 <= len(intervals) <= LEN_MAX
        for s, e in intervals:
            assert 0 <= s <= e <= VAL_MAX
        expected = fmt_expected(merge_reference(intervals))
        obj = {"inputs": {"arr": fmt_2d(intervals)}, "expected": expected}
        lines.append(json.dumps(obj, separators=(",", ":")))

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", len(lines), "cases to", OUT_PATH)


if __name__ == "__main__":
    main()
