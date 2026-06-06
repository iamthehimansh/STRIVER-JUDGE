#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Divisors of a Number" (slug: divisors-of-a-number-1)

starterCpp signature:  vector<int> divisors(int n)
Constraints:           1 <= n <= 1000

Reference algorithm (oracle): all i in [1..n] that divide n, in sorted order.
This matches the reference at:
  strivers-a2z-ref/06.Bit Manipulation/3. Advanced Maths/02. All divisors of number.cpp

Output: one JSON object per line to generated-tests/divisors-of-a-number-1.jsonl
  {"inputs": {"n": "<int>"}, "expected": "[d1, d2, ...]"}
"""
import json
import random
import os

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/divisors-of-a-number-1.jsonl"
N_CASES = 2000
N_MIN, N_MAX = 1, 1000  # from constraints: 1 <= n <= 1000


def divisors(n):
    """Reference oracle: all divisors of n in ascending order."""
    res = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            res.append(i)
            if n // i != i:
                res.append(n // i)
        i += 1
    res.sort()
    return res


def fmt_int_array(arr):
    # Match example output formatting: "[1, 2, 4, 8]"
    return "[" + ", ".join(str(x) for x in arr) + "]"


def gen_inputs():
    """Yield n values: include edge cases, then random within constraints, dedup-free (random)."""
    cases = []
    # Edge cases first
    forced = [N_MIN, N_MAX, 2, 3, 4, 6, 7, 8,
              999, 998, 997,           # near upper bound (997 is prime)
              512, 256, 720, 840,      # highly composite within range
              900, 1000, 36, 100, 144]
    for v in forced:
        if N_MIN <= v <= N_MAX:
            cases.append(v)
    # Fill the rest with random values strictly within constraints
    while len(cases) < N_CASES:
        cases.append(random.randint(N_MIN, N_MAX))
    return cases[:N_CASES]


def main():
    random.seed(20240606)
    cases = gen_inputs()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for n in cases:
            assert N_MIN <= n <= N_MAX, f"out of constraints: {n}"
            d = divisors(n)
            obj = {"inputs": {"n": str(n)}, "expected": fmt_int_array(d)}
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
