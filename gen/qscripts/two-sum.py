#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Two Sum".

Signature (starterCpp):
    vector<int> twoSum(vector<int>& nums, int target)

Output line format (one JSON object per line):
    {"inputs": {"nums": "[..]", "target": "T"}, "expected": "[i, j]"}

CONSTRAINTS enforced on every generated input:
    2 <= nums.length <= 1e5
    -1e4 <= nums[i] <= 1e4
    -1e5 <= target <= 1e5
    EXACTLY ONE valid answer exists (problem guarantee). The judge runs the
    user's solution and compares leniently against our expected output. If more
    than one pair summed to target, the user's (correct) answer could legally
    differ from ours and the case would be unfairly judged. So we construct
    every array to contain EXACTLY ONE unordered pair (i<j) with
    nums[i]+nums[j] == target, and we compute the expected indices ourselves
    (this IS the reference oracle -- it is trivial and exact).

Strategy to guarantee a unique pair:
    1. Choose target T in [-1e5, 1e5] but reduced so a valid in-range pair
       exists: we choose two pair values a,b with a+b == T, each in [-1e4,1e4].
    2. Fill the remaining n-2 slots with "filler" values drawn so that:
         - no two fillers sum to T
         - no filler f pairs with a (i.e. f + a != T  => f != b) and
           no filler pairs with b (f != a)
       We achieve this by picking all fillers from a half-range that makes any
       pair-sum strictly avoid T, and excluding the two pair values.
    3. Place a and b at two random distinct indices; shuffle the rest.
    4. Expected = sorted [i, j] (any order accepted, we output ascending).

The "no two fillers sum to T" guarantee:
    We pick filler values v such that v < T/2 strictly AND v != needed
    complements. If every filler v satisfies 2*v < T (i.e. v <= floor((T-1)/2)),
    then for any two fillers u,v: u+v < T (since each < T/2 ... careful with
    integers). To be fully safe and simple we instead pick fillers from a set
    where the complement (T - v) is OUTSIDE the allowed filler range, so two
    fillers can never sum to T. Concretely: choose a threshold and keep all
    fillers strictly on one side such that T - v lands outside [lo, hi] of the
    filler pool. We just reject any filler whose complement is also a possible
    filler value, by restricting the pool to one side of T/2 with a margin and
    excluding {a, b}.
"""

import json
import random

random.seed(20260606)

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/two-sum.jsonl"

VMIN, VMAX = -10000, 10000          # nums[i] range
TMIN, TMAX = -100000, 100000        # target range
NMIN, NMAX = 2, 100000              # nums.length range

N_CASES = 2000


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def build_case(n):
    """Return (nums_list, target, expected_indices) with EXACTLY ONE valid pair."""
    while True:
        # Pick pair values a, b in [VMIN, VMAX] with a != b ideally, but they
        # CAN be equal (different indices) as long as it's the only pair.
        a = random.randint(VMIN, VMAX)
        b = random.randint(VMIN, VMAX)
        T = a + b
        if not (TMIN <= T <= TMAX):
            continue
        # We want a unique pair. Build a filler pool that cannot create a second
        # pair summing to T, and cannot pair with a or b.
        #
        # For any filler v: need v + a != T (=> v != b) and v + b != T (=> v != a).
        # For any two fillers u,v: need u + v != T.
        #
        # Pick fillers all strictly less than ceil(T/2) by a margin so that two
        # fillers can't reach T, OR all strictly greater than floor(T/2). We pick
        # the side that has room within [VMIN, VMAX].
        #
        # half = T/2. If u,v < half then u+v < T. If u,v > half then u+v > T.
        # Use strict integer side.
        import math
        half_low = math.floor((T - 1) / 2)   # largest int v with 2v < T  => v <= half_low => u+v <= 2*half_low < T
        half_high = math.ceil((T + 1) / 2)   # smallest int v with 2v > T

        # Candidate pools (must intersect [VMIN, VMAX] and exclude {a,b})
        pools = []
        lo1, hi1 = VMIN, min(VMAX, half_low)
        if hi1 >= lo1 and (hi1 - lo1 + 1) > 0:
            pools.append((lo1, hi1))
        lo2, hi2 = max(VMIN, half_high), VMAX
        if hi2 >= lo2 and (hi2 - lo2 + 1) > 0:
            pools.append((lo2, hi2))

        # Need a pool large enough to supply n-2 distinct-ish fillers.
        # Fillers may repeat among themselves as long as they don't sum to T;
        # within one side they never sum to T, and repeats are fine.
        # Exclude values a and b from the pool to avoid pairing with b or a.
        chosen = None
        for (lo, hi) in pools:
            size = hi - lo + 1
            # account for excluding a, b if they fall in range (at most 2)
            excl = 0
            if lo <= a <= hi:
                excl += 1
            if lo <= b <= hi and b != a:
                excl += 1
            if size - excl >= 1:   # need at least one distinct filler value to draw from
                chosen = (lo, hi)
                break
        if chosen is None:
            continue

        lo, hi = chosen
        fillers = []
        need = n - 2
        # Draw fillers from [lo,hi] excluding {a,b}. Repeats allowed (same side
        # => never sum to T). Reject draws equal to a or b.
        # To be efficient for large n, build value set excluding a,b then sample.
        tries = 0
        while len(fillers) < need:
            v = random.randint(lo, hi)
            if v == a or v == b:
                continue
            fillers.append(v)
            tries += 1
            if tries > need * 5 + 100:
                break
        if len(fillers) < need:
            continue

        nums = fillers + [a, b]
        random.shuffle(nums)

        # Locate the unique pair indices.
        # a + b == T. Find index of a and index of b (they are distinct objects;
        # if a == b there are exactly two copies among nums by construction since
        # fillers exclude a,b). Find two indices i<j with nums[i]+nums[j]==T.
        idx_pair = find_pair(nums, T)
        if idx_pair is None:
            continue
        # Verify uniqueness (defensive): count pairs summing to T.
        if count_pairs(nums, T) != 1:
            continue
        i, j = idx_pair
        return nums, T, [i, j]


def find_pair(nums, T):
    seen = {}
    for idx, v in enumerate(nums):
        comp = T - v
        if comp in seen:
            return (seen[comp], idx)
        if v not in seen:
            seen[v] = idx
    return None


def count_pairs(nums, T):
    """Count unordered index pairs (i<j) with nums[i]+nums[j]==T.
    Stops early once >1 found."""
    from collections import Counter
    cnt = Counter(nums)
    total = 0
    seen_keys = set()
    for v in cnt:
        comp = T - v
        if comp not in cnt:
            continue
        if v == comp:
            c = cnt[v]
            total += c * (c - 1) // 2
        else:
            key = frozenset((v, comp))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            total += cnt[v] * cnt[comp]
        if total > 1:
            return total
    return total


def main():
    lines = []

    # ---- Deterministic edge / example cases first ----
    # Dataset examples (must reproduce exactly with our index oracle).
    ex1 = ([1, 6, 2, 10, 3], 7)
    ex2 = ([1, 3, 5, -7, 6, -3], 0)
    for nums, T in (ex1, ex2):
        ij = find_pair(nums, T)
        i, j = sorted(ij)
        lines.append({"inputs": {"nums": fmt_arr(nums), "target": str(T)},
                      "expected": fmt_arr([i, j])})

    # Edge: minimum size n=2.
    for _ in range(20):
        nums, T, ij = build_case(2)
        lines.append({"inputs": {"nums": fmt_arr(nums), "target": str(T)},
                      "expected": fmt_arr(ij)})

    # Edge: extreme values / targets.
    # target at +max via 10000+90000? no, value max is 10000 so max pair sum = 20000.
    # min pair sum = -20000. So target effectively in [-20000, 20000].
    edge_targets = [
        ([10000, 10000, -3, 5, 7], 20000),     # max pair, but ensure unique
        ([-10000, -10000, 3, 5, 7], -20000),   # min pair
    ]
    for nums, T in edge_targets:
        # only add if exactly one pair
        if count_pairs(nums, T) == 1:
            ij = sorted(find_pair(nums, T))
            lines.append({"inputs": {"nums": fmt_arr(nums), "target": str(T)},
                          "expected": fmt_arr(ij)})

    # ---- Random cases ----
    remaining = N_CASES - len(lines)
    # size distribution: many small, some medium, a few large.
    for k in range(remaining):
        r = random.random()
        if r < 0.55:
            n = random.randint(2, 30)
        elif r < 0.85:
            n = random.randint(31, 1000)
        elif r < 0.97:
            n = random.randint(1001, 20000)
        else:
            n = random.randint(20001, 100000)
        nums, T, ij = build_case(n)
        lines.append({"inputs": {"nums": fmt_arr(nums), "target": str(T)},
                      "expected": fmt_arr(ij)})

    # Trim to exactly N_CASES (we may have a couple extra edge cases).
    lines = lines[:N_CASES]

    with open(OUT, "w") as f:
        for obj in lines:
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(lines)} cases to {OUT}")


if __name__ == "__main__":
    main()
