#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Generate Parentheses (slug: generate-parentheses).

Problem: Given an integer n, generate all combinations of well-formed parentheses
of length 2*n.
Constraint: 1 <= n <= 8  (so there are only 8 distinct valid inputs).

starterCpp signature:  vector<string> generateParenthesis(int n)
  -> single input param "n" (int).

Output file: generated-tests/generate-parentheses.jsonl
  One JSON object per line: {"inputs": {"n": "<n>"}, "expected": "[ \"..\" , .. ]"}

The expected output is computed by an embedded, self-verified reference
implementation (open-first recursion) that reproduces the dataset's example
outputs exactly (ordering matters for n=3 / n=2 in the dataset, and this matches).
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/generate-parentheses.jsonl"
N_CASES = 2000
MIN_N = 1
MAX_N = 8


def generate(open_c, close_c, n, cur, ans):
    # Mirrors the reference C++ recursion order (open first, then close)
    # so the produced ordering matches the dataset examples.
    if open_c == n and close_c == n:
        ans.append(cur)
        return
    if open_c < n:
        generate(open_c + 1, close_c, n, cur + "(", ans)
    if open_c > close_c:
        generate(open_c, close_c + 1, n, cur + ")", ans)


def expected_for(n):
    ans = []
    generate(0, 0, n, "", ans)
    # Format like the example output: [ "((()))" , "(()())" , ... ]
    return "[ " + " , ".join('"' + s + '"' for s in ans) + " ]"


def main():
    random.seed(12345)

    # Build the list of n values: cover every valid n (edge cases: min=1, max=8)
    # first, then fill the rest by cycling so we always have all 8 represented.
    ns = []
    # Guarantee each valid n appears; deterministic coverage then random fill.
    for n in range(MIN_N, MAX_N + 1):
        ns.append(n)
    while len(ns) < N_CASES:
        ns.append(random.randint(MIN_N, MAX_N))
    ns = ns[:N_CASES]

    # Precompute expected per n (only 8 possibilities) for speed.
    cache = {n: expected_for(n) for n in range(MIN_N, MAX_N + 1)}

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for n in ns:
            obj = {"inputs": {"n": str(n)}, "expected": cache[n]}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(ns)} cases to {OUT_PATH}")
    # quick self-check on dataset examples
    assert cache[3] == '[ "((()))" , "(()())" , "(())()" , "()(())" , "()()()" ]', cache[3]
    assert cache[2] == '[ "(())" , "()()" ]', cache[2]
    assert cache[1] == '[ "()" ]', cache[1]
    print("Self-check passed: n=1,2,3 match dataset examples.")


if __name__ == "__main__":
    main()
