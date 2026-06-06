#!/usr/bin/env python3
"""Test-case generator for Striver problem: insertion-at-the-head-of-ll.

Problem: given the head of a singly linked list and an integer X, insert a node
with value X at the head and return the new head.

starterCpp signature: ListNode* insertAtHead(ListNode* &head, int X)
  -> params in order: head (ListNode*), X (int)

jsonl keys (matching the dataset examples; the judge binds "X" by name and the
list positionally to `head`):
  inputs.linkedList : list values as "[1, 2, 3]"
  inputs.X          : the integer to insert, e.g. "7"
  expected          : the new list values as "[7, 1, 2, 3]"

Reference oracle: inserting X at the head simply prepends X to the value list.
This is verified against the dataset examples below and against the live judge.

Constraints:
  0 <= number of nodes in the Linked List <= 1000
  0 <= ListNode.val <= 100
  0 <= X <= 100
"""

import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/insertion-at-the-head-of-ll.jsonl"
N_CASES = 2000

MAX_NODES = 1000
VAL_MIN, VAL_MAX = 0, 100
X_MIN, X_MAX = 0, 100

random.seed(20260606)


def fmt_list(vals):
    return "[" + ", ".join(str(v) for v in vals) + "]"


def reference(vals, x):
    """Insert x at head -> prepend."""
    return [x] + list(vals)


def make_case(vals, x):
    expected = reference(vals, x)
    return {
        "inputs": {"linkedList": fmt_list(vals), "X": str(x)},
        "expected": fmt_list(expected),
    }


# The judge runs all 2000 cases in ONE batched process and caps the captured
# stdout at OUT_CAP = 256 KB (scripts/judge_exec.py). The serialized output of a
# case is the new list's values space-separated, so the TOTAL output across all
# 2000 cases must stay well under 256 KB or later cases get truncated (and fail).
# We therefore keep most lists small and include only a couple of large
# (constraint-max, 1000-node) edge cases, then verify the budget before writing.
OUT_BUDGET = 200 * 1024  # stay comfortably under the judge's 256 KB cap


def out_bytes(case):
    """Estimate the batched stdout bytes the judge will produce for this case:
    the expected list values printed space-separated, plus a trailing newline."""
    toks = case["expected"].strip("[]").replace(",", " ").split()
    return sum(len(t) for t in toks) + max(0, len(toks) - 1) + 1


def gen_cases():
    cases = []

    # ---- Hand-crafted edge cases -------------------------------------------
    # empty list, various X
    for x in (0, 1, 50, 100):
        cases.append(make_case([], x))
    # single node, X at extremes
    cases.append(make_case([0], 0))
    cases.append(make_case([100], 100))
    cases.append(make_case([50], 0))
    cases.append(make_case([0], 100))
    # the dataset examples themselves
    cases.append(make_case([1, 2, 3], 7))
    cases.append(make_case([], 7))
    # max-size list (1000 nodes) edge cases — tests the upper constraint bound.
    # Kept to just two so the 256 KB batched-output budget is respected.
    cases.append(make_case([0] * MAX_NODES, 0))
    cases.append(make_case([random.randint(VAL_MIN, VAL_MAX) for _ in range(MAX_NODES)],
                           random.randint(X_MIN, X_MAX)))
    # a few moderately large lists
    cases.append(make_case([random.randint(VAL_MIN, VAL_MAX) for _ in range(500)],
                           random.randint(X_MIN, X_MAX)))
    cases.append(make_case([random.randint(VAL_MIN, VAL_MAX) for _ in range(300)],
                           random.randint(X_MIN, X_MAX)))
    # all same value list
    cases.append(make_case([42] * 10, 42))

    # ---- Random cases to fill up to N_CASES --------------------------------
    # Keep the bulk small so the cumulative batched output stays within budget.
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.12:
            n = 0
        elif r < 0.25:
            n = 1
        elif r < 0.92:
            n = random.randint(2, 20)
        else:
            n = random.randint(21, 60)
        vals = [random.randint(VAL_MIN, VAL_MAX) for _ in range(n)]
        x = random.randint(X_MIN, X_MAX)
        cases.append(make_case(vals, x))

    cases = cases[:N_CASES]

    total = sum(out_bytes(c) for c in cases)
    if total >= OUT_BUDGET:
        raise SystemExit(
            f"generated output {total} bytes exceeds budget {OUT_BUDGET}; "
            "reduce list sizes")
    print(f"estimated batched output: {total} bytes "
          f"({total / 1024:.1f} KB) < {OUT_BUDGET / 1024:.0f} KB cap budget")
    return cases


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cases = gen_cases()
    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
