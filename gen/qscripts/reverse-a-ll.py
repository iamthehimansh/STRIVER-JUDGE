#!/usr/bin/env python3
"""
Test-case generator for Striver problem "reverse-a-ll"
(Reverse a LinkedList [Iterative]).

Problem: Given the head of a singly linked list, reverse it and return the new head.

Constraints:
  - 0 <= number of nodes <= 10^5
  - 0 <= ListNode.val <= 10^4

Judge I/O contract (verified live against http://localhost:3000/api/run):
  - starterCpp signature: ListNode* reverseList(ListNode* head)
  - The judge feeds the linked list under input key "nums" as a values array,
    e.g. "[1, 2, 3]"  (an empty list is "[]").
  - The judge serializes a ListNode* OUTPUT as space-separated values,
    e.g. "3 2 1"  (an empty list prints "").
  - Comparison is lenient (ignores brackets/commas/whitespace), but the
    "expected" we emit here matches the judge's raw stdout exactly.

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/reverse-a-ll.jsonl
  One JSON object per line: {"inputs": {"nums": "<array>"}, "expected": "<space-sep values>"}
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/reverse-a-ll.jsonl"
N_CASES = 2000

VAL_MIN = 0
VAL_MAX = 10_000          # 10^4
CONSTRAINT_MAX_NODES = 100_000   # 10^5 (the problem's stated upper bound)

# IMPORTANT — judge output cap.
# The live judge runs ALL cases in ONE batched process (one C++ binary reading
# every case from stdin and printing one output line per case). That single
# process's combined stdout is truncated by the judge at 256 KB
# (scripts/judge_exec.py: OUT_CAP = 256*1024, applied as out[:OUT_CAP]).
# Anything past 256 KB is dropped, so the tail cases lose their output and fail.
# The ListNode output is space-separated values (~6 bytes per value: up to 5
# digits + 1 space). Therefore the SUM of all expected outputs across the 2000
# cases must stay comfortably under 256 KB.
#
# We enforce a total-output budget and cap individual list sizes:
#   - TOTAL_OUTPUT_BUDGET: hard ceiling on summed expected-output bytes.
#   - MAX_NODES: ceiling on any single list's size.
# All inputs still satisfy the problem constraint (0 <= nodes <= 10^5).
TOTAL_OUTPUT_BUDGET = 200_000   # bytes, safely under the 256 KB judge cap
MAX_NODES = 3_000               # ~18 KB output for the largest single case

random.seed(20260606)

# Cumulative expected-output byte counter (shared across the generator).
_out_bytes = [0]


def reference_reverse(values):
    """Ground-truth oracle: reversing a singly linked list == reversing the value list."""
    return list(reversed(values))


def fmt_input(values):
    # Match the example/dataset format: int array -> "[3, 1, 2]"
    return "[" + ", ".join(str(v) for v in values) + "]"


def fmt_expected(values):
    # Judge prints ListNode output as space-separated values; empty list -> ""
    return " ".join(str(v) for v in values)


def make_case(values):
    return {
        "inputs": {"nums": fmt_input(values)},
        "expected": fmt_expected(reference_reverse(values)),
    }


def _expected_bytes(values):
    # bytes of the serialized reversed output (same as fmt_expected length)
    return len(fmt_expected(values))


def gen_cases(n):
    cases = []
    seen = set()

    def add(values, force=False):
        # de-dup on the input representation so the file isn't full of repeats
        key = tuple(values)
        if key in seen:
            return False
        # Enforce the cumulative output budget so the batched judge stdout
        # (capped at 1 MB) never truncates. `force` lets the must-have edge
        # cases through (they are small) regardless of the running total.
        eb = _expected_bytes(values) + 1  # +1 for the newline the batch emits
        if not force and _out_bytes[0] + eb > TOTAL_OUTPUT_BUDGET:
            return False
        seen.add(key)
        _out_bytes[0] += eb
        cases.append(make_case(values))
        return True

    # ---- Deterministic edge cases (always included; all small) ----
    edge = [
        [],                         # min size: empty list
        [0],                        # single node, min value
        [VAL_MAX],                  # single node, max value
        [0, 0],                     # duplicates, min value
        [VAL_MAX, VAL_MAX],         # duplicates, max value
        [6, 8],                     # dataset example 2
        [1, 2, 3, 4, 5],            # dataset example 1
        [0, VAL_MAX],               # extremes mixed
        [VAL_MAX, 0],
        list(range(0, 100)),                          # ascending small
        list(range(99, -1, -1)),                      # descending small
        [VAL_MAX] * 200,                              # all-max moderate
        [0] * 200,                                    # all-min moderate
        list(range(0, 1000)),                         # medium ascending
    ]
    for e in edge:
        add(e, force=True)

    # A couple of LARGE lists (capped at MAX_NODES) to exercise big inputs while
    # respecting the output budget. Forced through; each is ~36 KB.
    add([random.randint(VAL_MIN, VAL_MAX) for _ in range(MAX_NODES)], force=True)
    add([5000] * MAX_NODES, force=True)

    # ---- Random cases ----
    # We bias heavily toward small lists so 2000 cases fit inside the output
    # budget; sizes shrink automatically as the budget fills (add() rejects any
    # case that would overflow, and we retry with a smaller size).
    attempts = 0
    while len(cases) < n and attempts < n * 200:
        attempts += 1
        remaining_budget = TOTAL_OUTPUT_BUDGET - _out_bytes[0]
        if remaining_budget <= 2:
            break
        # average remaining bytes-per-case we can afford
        cases_left = n - len(cases)
        afford_avg = max(1, remaining_budget // max(1, cases_left))
        # a value is ~6 output bytes; keep most lists small, allow occasional
        # mid-size lists, but never exceed what the budget can afford.
        r = random.random()
        if r < 0.65:
            size = random.randint(1, 30)
        elif r < 0.90:
            size = random.randint(1, 150)
        else:
            size = random.randint(1, 800)
        # cap by what we can afford (~6 bytes/value) so we don't waste attempts
        size = max(1, min(size, MAX_NODES, max(1, afford_avg // 6)))
        values = [random.randint(VAL_MIN, VAL_MAX) for _ in range(size)]
        add(values)

    return cases[:n]


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    cases = gen_cases(N_CASES)
    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
