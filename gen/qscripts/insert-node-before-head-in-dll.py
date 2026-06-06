#!/usr/bin/env python3
"""
Generator for Striver problem: insert-node-before-head-in-dll

Problem: Given the head of a (doubly) linked list and an integer X, insert a node
with value X before the head and return the head of the modified list.

The judge models the list with struct ListNode { int val; ListNode *next; } and
builds it from the input key "nums" (an array of values). The integer param key is "X".
Output is the list values, space-separated by the judge.

Constraints:
  1 <= n <= 100
  0 <= ListNode.val <= 100
  0 <= X <= 100

Reference (oracle): inserting X before head simply prepends X -> [X] + original values.

JSONL line format:
  {"inputs": {"nums": "[v0, v1, ...]", "X": "k"}, "expected": "[k, v0, v1, ...]"}
"""
import json
import random
import os

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/insert-node-before-head-in-dll.jsonl"
N_CASES = 2000
random.seed(20260606)

VAL_MIN, VAL_MAX = 0, 100   # 0 <= ListNode.val <= 100
N_MIN, N_MAX = 1, 100       # 1 <= n <= 100
X_MIN, X_MAX = 0, 100       # 0 <= X <= 100


def reference(values, X):
    """Insert X before head -> prepend."""
    return [X] + list(values)


def fmt_arr(arr):
    return "[" + ", ".join(str(v) for v in arr) + "]"


def gen_values(n):
    return [random.randint(VAL_MIN, VAL_MAX) for _ in range(n)]


# The judge captures batch stdout up to a hard byte cap (~256 KB) for the whole
# 2000-case run, then truncates — which would mark later cases as wrong. So we
# keep the TOTAL serialized output comfortably under that cap by biasing list
# sizes small while still covering the full constraint range (incl. n=100 edges).
OUTPUT_BYTE_CAP = 240_000  # safety margin under the observed ~262144 (256 KiB) cap


def out_bytes(values, X):
    expected = reference(values, X)
    return len(" ".join(str(v) for v in expected)) + 1  # +newline


def make_case(values, X):
    expected = reference(values, X)
    return {
        "inputs": {"nums": fmt_arr(values), "X": str(X)},
        "expected": fmt_arr(expected),
    }


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cases = []
    total_bytes = [0]

    def add(values, X):
        cases.append(make_case(values, X))
        total_bytes[0] += out_bytes(values, X)

    # ---- Edge cases (always included; these consume some byte budget) ----
    # min size n=1, extremes of X and val
    for v in (VAL_MIN, VAL_MAX):
        for x in (X_MIN, X_MAX):
            add([v], x)
    # max size n=100, all min / all max  (full-size edge coverage)
    add([VAL_MIN] * N_MAX, X_MIN)
    add([VAL_MAX] * N_MAX, X_MAX)
    add([VAL_MIN] * N_MAX, X_MAX)
    add([VAL_MAX] * N_MAX, X_MIN)
    # single element equal to X
    add([50], 50)
    # ascending / descending full range at max size
    add([i % 101 for i in range(N_MAX)], 0)
    add([(100 - (i % 101)) for i in range(N_MAX)], 100)
    # small lists
    for n in range(1, 6):
        add(list(range(n)), n)

    # ---- Random cases to fill up to N_CASES, keeping total output under cap ----
    # Bias list sizes small so all 2000 cases fit within the judge's stdout cap,
    # while still occasionally sampling larger lists across the full range.
    remaining = N_CASES - len(cases)
    # average byte budget left for the remaining random cases
    while len(cases) < N_CASES:
        left = N_CASES - len(cases)
        budget_left = OUTPUT_BYTE_CAP - total_bytes[0]
        avg_allowed = budget_left / max(1, left)
        # choose n so that the expected per-case bytes stays within budget;
        # ~3 bytes per value incl. separators, +1 for the prepended X.
        n_cap = max(1, min(N_MAX, int(avg_allowed / 3)))
        # mostly-small distribution, but allow up to n_cap
        if n_cap <= 1:
            n = 1
        else:
            # weighted toward smaller sizes
            r = random.random()
            if r < 0.6:
                n = random.randint(1, min(20, n_cap))
            elif r < 0.9:
                n = random.randint(1, min(50, n_cap))
            else:
                n = random.randint(1, n_cap)
        values = gen_values(n)
        X = random.randint(X_MIN, X_MAX)
        add(values, X)

    cases = cases[:N_CASES]

    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    # report total output bytes for the cap sanity check
    tot = sum(out_bytes(json.loads(c["inputs"]["nums"]), int(c["inputs"]["X"])) for c in cases)
    print(f"Wrote {len(cases)} cases to {OUT}")
    print(f"Total serialized output bytes = {tot} ({round(tot/1024,1)} KiB), cap target {OUTPUT_BYTE_CAP}")


if __name__ == "__main__":
    main()
