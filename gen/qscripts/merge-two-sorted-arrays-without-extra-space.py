#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
  "Merge two sorted arrays without extra space"
  signature: void merge(vector<int>& nums1, int m, vector<int>& nums2, int n)

The automated judge's BATCH harness binds every method parameter to an input
column, so the jsonl MUST provide all four params by name:
    nums1, m, nums2, n
nums1 is given at its FULL length m+n: the first m sorted elements followed by
n placeholder 0s (exactly as the LeetCode signature requires, since the merge
reads/writes indices up to m+n-1).

Because merge() returns void and BOTH nums1 and nums2 are non-const references,
the harness prints  pr(nums1) + " " + pr(nums2)  after the call. The reference
used here is the canonical back-to-front fill that writes only into nums1 and
leaves nums2 unchanged (the standard accepted LeetCode solution), so the
expected output is:  merged_nums1 (m+n ints)  followed by  nums2 (n ints).

Constraints enforced:
  0 <= n, m <= 1000 ; -1e4 <= values <= 1e4 ; both arrays sorted non-decreasing.

Outputs:
  /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/merge-two-sorted-arrays-without-extra-space.jsonl
"""
import json
import os
import random

random.seed(20250606)

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/merge-two-sorted-arrays-without-extra-space.jsonl"
LO, HI = -10000, 10000
MAXLEN = 1000  # max for each of m and n
N_CASES = 2000

def sorted_arr(k):
    """k sorted (non-decreasing) ints in [LO, HI]."""
    if k == 0:
        return []
    return sorted(random.randint(LO, HI) for _ in range(k))

def reference_merge(nums1_full, m, nums2, n):
    """Canonical in-place merge (does NOT modify nums2). Returns (nums1_merged)."""
    a = list(nums1_full)
    i, j, k = m - 1, n - 1, m + n - 1
    while j >= 0:
        if i >= 0 and a[i] > nums2[j]:
            a[k] = a[i]; i -= 1
        else:
            a[k] = nums2[j]; j -= 1
        k -= 1
    return a

def fmt_list(xs):
    return "[" + ", ".join(str(x) for x in xs) + "]"

def make_case(m, n):
    first = sorted_arr(m)
    nums1_full = first + [0] * n           # full length m+n
    nums2 = sorted_arr(n)
    merged = reference_merge(nums1_full, m, nums2, n)
    # harness prints merged nums1 then nums2 (unchanged)
    expected_tokens = list(merged) + list(nums2)
    expected = " ".join(str(x) for x in expected_tokens)
    return {
        "inputs": {
            "nums1": fmt_list(nums1_full),
            "m": str(m),
            "nums2": fmt_list(nums2),
            "n": str(n),
        },
        "expected": expected,
    }

def edge_cases():
    cases = []
    # both empty -> empty output
    cases.append((0, 0))
    # one side empty
    cases.append((0, 1))
    cases.append((1, 0))
    cases.append((0, 1000))
    cases.append((1000, 0))
    # min sizes
    cases.append((1, 1))
    # max sizes
    cases.append((1000, 1000))
    cases.append((1000, 1))
    cases.append((1, 1000))
    return cases

def build_extreme(m, n, kind):
    """Some structurally special (but valid) cases via explicit construction."""
    if kind == "all_min":
        first = [LO] * m; nums2 = [LO] * n
    elif kind == "all_max":
        first = [HI] * m; nums2 = [HI] * n
    elif kind == "all_same":
        v = random.randint(LO, HI); first = [v]*m; nums2=[v]*n
    elif kind == "disjoint_low_high":
        # nums1 entirely below nums2
        first = sorted(random.randint(LO, 0) for _ in range(m))
        nums2 = sorted(random.randint(1, HI) for _ in range(n))
    elif kind == "disjoint_high_low":
        first = sorted(random.randint(1, HI) for _ in range(m))
        nums2 = sorted(random.randint(LO, 0) for _ in range(n))
    elif kind == "interleave":
        first = sorted(random.randint(LO, HI) for _ in range(m))
        nums2 = sorted(random.randint(LO, HI) for _ in range(n))
    else:
        first = sorted_arr(m); nums2 = sorted_arr(n)
    nums1_full = first + [0]*n
    merged = reference_merge(nums1_full, m, nums2, n)
    expected = " ".join(str(x) for x in (list(merged)+list(nums2)))
    return {
        "inputs": {
            "nums1": fmt_list(nums1_full),
            "m": str(m), "nums2": fmt_list(nums2), "n": str(n),
        },
        "expected": expected,
    }

def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cases = []

    # 1) explicit edge cases
    for (m, n) in edge_cases():
        cases.append(make_case(m, n))

    # 2) extreme/structural cases
    kinds = ["all_min","all_max","all_same","disjoint_low_high",
             "disjoint_high_low","interleave"]
    for kind in kinds:
        for (m, n) in [(1,1),(5,5),(50,30),(1000,1000),(1000,500),(0,500),(500,0)]:
            cases.append(build_extreme(m, n, kind))

    # 3) small-size cases (exhaustive-ish coverage of tiny shapes)
    while len(cases) < 250:
        m = random.randint(0, 8)
        n = random.randint(0, 8)
        cases.append(make_case(m, n))

    # 4) bulk random cases until we hit N_CASES
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.5:
            m = random.randint(0, 50); n = random.randint(0, 50)
        elif r < 0.8:
            m = random.randint(0, 300); n = random.randint(0, 300)
        else:
            m = random.randint(0, MAXLEN); n = random.randint(0, MAXLEN)
        cases.append(make_case(m, n))

    cases = cases[:N_CASES]

    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c, separators=(",", ":")) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")

if __name__ == "__main__":
    main()
