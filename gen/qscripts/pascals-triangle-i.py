#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Pascal's Triangle I (slug: pascals-triangle-i)

Signature: int pascalTriangleI(int r, int c)
Value at the r-th row and c-th column (1-indexed) of Pascal's Triangle
  = binomial coefficient C(r-1, c-1).

Constraints:
  1 <= r, c <= 30
  c <= r
  All values fit in a 32-bit integer.

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/pascals-triangle-i.jsonl
One JSON object per line: {"inputs": {"r": "<r>", "c": "<c>"}, "expected": "<value>"}
Keys are EXACTLY the starterCpp parameter names in signature order: r, c.
"""

import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/pascals-triangle-i.jsonl"
N_CASES = 2000
MAXV = 30  # constraint upper bound for r and c

random.seed(813)


def pascal_value(r, c):
    """Value at (r, c) 1-indexed = C(r-1, c-1) using the multiplicative
    binomial formula (same logic as the reference oracle)."""
    n = r - 1   # 0-indexed row
    k = c - 1   # 0-indexed column
    # C(n, k) via multiplicative formula; exact integer arithmetic
    coefficient = 1
    for col in range(1, k + 1):
        coefficient = coefficient * (n - col + 1) // col
    return coefficient


def gen_cases():
    seen = set()
    cases = []

    def add(r, c):
        if 1 <= r <= MAXV and 1 <= c <= MAXV and c <= r:
            key = (r, c)
            if key not in seen:
                seen.add(key)
                cases.append(key)

    # --- Edge cases / extremes ---
    add(1, 1)            # min size
    add(MAXV, 1)         # first column of max row -> 1
    add(MAXV, MAXV)      # last column of max row -> 1
    add(MAXV, 15)        # near middle of max row (largest values)
    add(MAXV, 16)
    add(2, 1)
    add(2, 2)
    # dataset examples
    add(4, 2)            # expected 3
    add(5, 3)            # expected 6
    # all diagonal (c == r) -> always 1
    for r in range(1, MAXV + 1):
        add(r, r)
        add(r, 1)        # first column -> always 1

    # --- Exhaustive enumeration of all valid (r, c) pairs ---
    # Total valid pairs = sum_{r=1..30} r = 30*31/2 = 465, all included.
    for r in range(1, MAXV + 1):
        for c in range(1, r + 1):
            add(r, c)

    # --- Random fill until N_CASES (with repeats allowed beyond the
    #     distinct pairs so the file has exactly N_CASES lines) ---
    all_pairs = [(r, c) for r in range(1, MAXV + 1) for c in range(1, r + 1)]
    while len(cases) < N_CASES:
        cases.append(random.choice(all_pairs))

    return cases[:N_CASES]


def main():
    cases = gen_cases()
    with open(OUT_PATH, "w") as f:
        for r, c in cases:
            expected = pascal_value(r, c)
            obj = {"inputs": {"r": str(r), "c": str(c)}, "expected": str(expected)}
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
