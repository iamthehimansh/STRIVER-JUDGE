#!/usr/bin/env python3
"""
Generator + reference oracle for Striver problem:
  "Generate Binary Strings Without Consecutive 1s"

starterCpp signature:
    vector<string> generateBinaryStrings(int n)

Constraints: 1 <= n <= 20

The reference generates all binary strings of length n that contain no two
consecutive '1's, in lexicographically increasing order. Building each string
by choosing '0' before '1' at every position yields lexicographic order
naturally.

Output is formatted like the dataset examples:  ["000", "001", ...]
The judge compares leniently (ignores brackets/commas/whitespace/quotes), but
we match the example shape exactly to be safe.
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/generate-binary-strings-without-consecutive-1s.jsonl"

N_CASES = 2000


def generate_binary_strings(n):
    """Reference oracle. Returns list of strings in lexicographic order."""
    res = []
    cur = []

    def rec(idx, last):
        # idx = current length so far, last = previous char ('' or '0'/'1')
        if idx == n:
            res.append("".join(cur))
            return
        # Choose '0' first (smaller -> lexicographic order)
        cur.append('0')
        rec(idx + 1, '0')
        cur.pop()
        # Then '1', only if previous char was not '1'
        if last != '1':
            cur.append('1')
            rec(idx + 1, '1')
            cur.pop()

    rec(0, '')
    return res


def format_output(strings):
    # Match example format: ["000", "001", ...]
    return "[" + ", ".join('"' + s + '"' for s in strings) + "]"


def main():
    random.seed(1234567)

    cases = []  # list of n values

    # Edge cases / all small n covered explicitly (1..20)
    for n in range(1, 21):
        cases.append(n)

    # Fill the rest with random n in [1, 20] until we hit N_CASES
    while len(cases) < N_CASES:
        cases.append(random.randint(1, 20))

    cases = cases[:N_CASES]

    lines = []
    for n in cases:
        out = generate_binary_strings(n)
        rec = {
            "inputs": {"n": str(n)},
            "expected": format_output(out),
        }
        lines.append(json.dumps(rec))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
