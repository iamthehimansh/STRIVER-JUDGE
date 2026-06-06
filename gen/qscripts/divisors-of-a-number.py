#!/usr/bin/env python3
"""Test-case generator for Striver problem 'divisors-of-a-number' (Print all Divisors).

Signature: vector<int> divisors(int n)   with constraint 1 <= n <= 1000.

Reference logic (verified against dataset example n=8 -> [1, 2, 4, 8]):
    divisors(n) = sorted list of all i in [1..n] with n % i == 0.

Output JSONL line shape:
    {"inputs": {"n": "<n>"}, "expected": "[d1, d2, ...]"}
"""
import json
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/divisors-of-a-number.jsonl"
N_CASES = 2000
LOW, HIGH = 1, 1000  # from constraints: 1 <= n <= 1000


def divisors(n):
    res = []
    i = 1
    while i * i <= n:
        if n % i == 0:
            res.append(i)
            if i != n // i:
                res.append(n // i)
        i += 1
    res.sort()
    return res


def fmt_list(lst):
    # match example output format: "[1, 2, 4, 8]"
    return "[" + ", ".join(str(x) for x in lst) + "]"


def main():
    random.seed(20240606)
    cases = []

    # Edge cases / full coverage of the small domain first.
    forced = list(range(LOW, HIGH + 1))  # 1..1000 (covers min, max, every value)
    for n in forced:
        cases.append(n)

    # Fill the rest with random values within constraints.
    while len(cases) < N_CASES:
        cases.append(random.randint(LOW, HIGH))

    # Trim to exactly N_CASES (forced already <= N_CASES).
    cases = cases[:N_CASES]

    with open(OUT, "w") as f:
        for n in cases:
            assert LOW <= n <= HIGH, f"input out of constraint: {n}"
            line = {"inputs": {"n": str(n)}, "expected": fmt_list(divisors(n))}
            f.write(json.dumps(line) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
