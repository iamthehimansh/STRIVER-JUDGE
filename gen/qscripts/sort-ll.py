#!/usr/bin/env python3
"""Test-case generator for Striver problem "Sort LL" (slug: sort-ll).

Problem: given the head of a singly linked list, sort the values in
non-decreasing order and return the head.

starterCpp signature:  ListNode* sortList(ListNode* head)

Constraints:
  - 0 <= number of nodes <= 1000
  - -10^4 <= ListNode.val <= 10^4

I/O serialization (must match the judge exactly):
  - ListNode INPUT  : the list values as an array, e.g. "[1, 2, 3]"
  - ListNode OUTPUT : the list values space-separated, e.g. "1 2 3"
    (the judge's pr(ListNode*) prints node->val space-separated)

The reference "oracle" is simply Python's stable sort of the values, which
is exactly what a correct sortList must produce (non-decreasing order).
We additionally verify a real C++ class Solution against this data via the
live judge before trusting the output.

Output: generated-tests/sort-ll.jsonl  -- one JSON object per line:
  {"inputs": {"head": "[5, 6, 1, 2, 1]"}, "expected": "1 1 2 5 6"}
"""
import json
import os
import random

VAL_MIN = -10_000
VAL_MAX = 10_000
MAX_NODES = 1000
N_CASES = 2000

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/sort-ll.jsonl"


def fmt_input(vals):
    """int array like the examples: '[3, 1, 2]'  (empty list -> '[]')."""
    return "[" + ", ".join(str(v) for v in vals) + "]"


def fmt_expected(vals):
    """ListNode* output: values space-separated, sorted non-decreasing.
    Empty list -> empty string (judge prints nothing for a null head)."""
    return " ".join(str(v) for v in sorted(vals))


def gen_case(rng, force_size=None):
    if force_size is not None:
        n = force_size
    else:
        # bias toward small/medium sizes but allow up to MAX_NODES
        r = rng.random()
        if r < 0.05:
            n = rng.randint(0, 2)
        elif r < 0.5:
            n = rng.randint(0, 30)
        elif r < 0.85:
            n = rng.randint(0, 200)
        else:
            n = rng.randint(0, MAX_NODES)
    return [rng.randint(VAL_MIN, VAL_MAX) for _ in range(n)]


def main():
    rng = random.Random(20240606)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    cases = []

    # ---- deterministic edge cases ----
    edge_lists = [
        [],                       # empty list (0 nodes) -> empty output
        [0],                      # single node
        [VAL_MIN],                # single extreme low
        [VAL_MAX],                # single extreme high
        [5, 6, 1, 2, 1],          # dataset example 1
        [6, 5, -1, -2, -3],       # dataset example 2
        [-1, -2, -3, -1],         # dataset "now your turn"
        [VAL_MAX, VAL_MIN],       # extremes
        [VAL_MIN, VAL_MAX],
        [1, 1, 1, 1, 1],          # all equal
        [VAL_MAX] * 10,           # all equal extreme
        [VAL_MIN] * 10,
        list(range(1, 21)),       # already sorted ascending
        list(range(20, 0, -1)),   # sorted descending
        [3, 1, 2],                # tiny
        [2, 1],
        [1, 2],
        [0, 0],
        [-10000, 10000, 0, -1, 1],
        list(range(-5, 6)),
    ]
    # a couple of full-size extremes
    edge_lists.append([VAL_MAX] * MAX_NODES)          # 1000 equal max
    edge_lists.append([VAL_MIN] * MAX_NODES)          # 1000 equal min
    edge_lists.append(list(range(MAX_NODES, 0, -1)))  # 1000 reverse sorted
    edge_lists.append([(-1) ** i * (i % 10001) for i in range(MAX_NODES)])  # 1000 mixed

    for vals in edge_lists:
        # clamp just in case (range(MAX_NODES,0,-1) max is 1000, within bounds)
        cases.append(vals)

    # ---- random cases to fill up to N_CASES ----
    while len(cases) < N_CASES:
        cases.append(gen_case(rng))

    cases = cases[:N_CASES]

    # sanity: every value within bounds, every size within bounds
    for vals in cases:
        assert 0 <= len(vals) <= MAX_NODES, f"bad size {len(vals)}"
        for v in vals:
            assert VAL_MIN <= v <= VAL_MAX, f"bad val {v}"

    with open(OUT_PATH, "w") as f:
        for vals in cases:
            rec = {
                "inputs": {"head": fmt_input(vals)},
                "expected": fmt_expected(vals),
            }
            f.write(json.dumps(rec) + "\n")

    print(f"wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
