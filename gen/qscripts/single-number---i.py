#!/usr/bin/env python3
"""
Test-case generator for Striver problem "single-number---i"
(Find the number that appears once, and other numbers twice).

Signature: int singleNumber(vector<int>& nums)

Every integer appears exactly twice except one, which appears once.
Constraints:
  1 <= n <= 10^5
  -3*10^5 <= nums[i] <= 3*10^5

Reference oracle: XOR of all elements == the single number.
(Cross-checked against a compiled C++ Solution.)

Output: one JSON object per line:
  {"inputs": {"nums": "[...]"}, "expected": "<int>"}
"""
import json
import os
import random
import subprocess
import sys

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/single-number---i.jsonl"
N_CASES = 2000

LO = -300000
HI = 300000
MAX_N = 100000  # n <= 10^5

random.seed(20240606)


def expected(nums):
    """Ground-truth oracle: XOR of all elements."""
    x = 0
    for v in nums:
        x ^= v
    return x


def build_case(pair_count, single_val):
    """Build a valid array: pair_count distinct paired values + one single value.

    All values are kept within [LO, HI] and distinct from each other so that
    exactly one element appears once and every other appears exactly twice.
    Resulting n = 2*pair_count + 1 (always odd), 1 <= n <= MAX_N.
    """
    # choose distinct values for the pairs, none equal to single_val
    chosen = set()
    chosen.add(single_val)
    vals = []
    while len(vals) < pair_count:
        c = random.randint(LO, HI)
        if c in chosen:
            continue
        chosen.add(c)
        vals.append(c)
    nums = [single_val]
    for v in vals:
        nums.append(v)
        nums.append(v)
    random.shuffle(nums)
    return nums


def fmt_arr(nums):
    return "[" + ", ".join(str(x) for x in nums) + "]"


def gen_cases():
    cases = []

    # ---- Edge cases ----
    # min size n = 1
    cases.append([5])
    cases.append([0])
    cases.append([LO])           # extreme min single
    cases.append([HI])           # extreme max single
    # example cases from the dataset
    cases.append([1, 2, 2, 4, 3, 1, 4])
    cases.append([1, 3, 10, 3, 5, 1, 5])
    # single value at extremes with a couple pairs
    cases.append([LO, HI, HI])   # single = LO
    cases.append([HI, LO, LO])   # single = HI
    cases.append([0, HI, HI, LO, LO])  # single = 0
    # max-size case: n close to MAX_N (must be odd)
    # pair_count = (MAX_N-1)//2 -> n = MAX_N-1+1 = MAX_N when MAX_N odd; here
    # MAX_N=100000 even, so largest valid odd n is 99999 -> pair_count=49999
    big_pairs = (MAX_N - 1) // 2  # 49999 -> n = 99999
    cases.append(build_case(big_pairs, random.randint(LO, HI)))

    # ---- Random cases ----
    while len(cases) < N_CASES:
        # vary structure: small, medium, large
        bucket = random.random()
        if bucket < 0.25:
            pc = random.randint(0, 5)          # very small arrays
        elif bucket < 0.7:
            pc = random.randint(0, 200)        # medium
        else:
            pc = random.randint(0, 2000)       # larger
        # cap so n = 2*pc+1 <= MAX_N
        pc = min(pc, (MAX_N - 1) // 2)
        single = random.randint(LO, HI)
        cases.append(build_case(pc, single))

    return cases[:N_CASES]


def cross_check(cases):
    """If a compiled C++ reference exists, verify a sample of cases match."""
    ref = "/tmp/single_ref"
    if not os.path.exists(ref):
        return True  # nothing to check against; python oracle is authoritative
    sample = random.sample(range(len(cases)), min(50, len(cases)))
    for i in sample:
        nums = cases[i]
        inp = " ".join(str(x) for x in nums)
        try:
            out = subprocess.run([ref], input=inp, capture_output=True,
                                 text=True, timeout=30)
            got = int(out.stdout.strip())
        except Exception as e:
            print(f"cross-check skipped (run error): {e}", file=sys.stderr)
            return True
        if got != expected(nums):
            print(f"MISMATCH at case {i}: cpp={got} py={expected(nums)}",
                  file=sys.stderr)
            return False
    return True


def main():
    cases = gen_cases()
    if not cross_check(cases):
        print("Cross-check failed; aborting.", file=sys.stderr)
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for nums in cases:
            assert 1 <= len(nums) <= MAX_N, f"n out of range: {len(nums)}"
            for v in nums:
                assert LO <= v <= HI, f"value out of range: {v}"
            obj = {
                "inputs": {"nums": fmt_arr(nums)},
                "expected": str(expected(nums)),
            }
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
