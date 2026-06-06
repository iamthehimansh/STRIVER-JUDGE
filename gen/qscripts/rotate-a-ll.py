#!/usr/bin/env python3
"""
Test-case generator for Striver problem "rotate-a-ll" (Rotate a Linked List).

Problem: Given the head of a singly linked list, shift the elements to the
RIGHT by k places and return the head of the modified list. Only links change,
not node values.

Constraints (from the problem JSON):
  - 0 <= number of nodes in the linked list <= 10^5
  - -10^4 <= ListNode.val <= 10^4
  - 0 <= k <= 5 * 10^5   (k may exceed the list length)

Judge I/O contract (verified live against http://localhost:3000/api/run):
  - starterCpp signature: ListNode* rotateRight(ListNode* head, int k)
  - Input keys are EXACTLY the parameter names in signature order, dropping the
    list itself which the judge feeds under "nums" as a values array:
        head  -> fed as "nums" : "[1, 2, 3, 4, 5]"   (empty list -> "[]")
        k     -> "2"
    (The dataset's own testcases use keys {"k", "nums"}.)
  - The judge serializes a ListNode* OUTPUT as space-separated values,
    e.g. "4 5 1 2 3"  (an empty list prints "").
  - Comparison is lenient (ignores brackets/commas/whitespace/quotes), but the
    "expected" we emit matches the judge's raw stdout shape.

Reference oracle: right-rotating a singly linked list by k places permutes the
SAME nodes; it is exactly equivalent to right-rotating the value list by
k % len. Verified live (passed 2000/2000) by submitting an equivalent C++
class Solution against this generated data.

GOTCHA for the live verification: the judge's signature parser calls the FIRST
method it finds inside `class Solution`. The reference must therefore expose
`rotateRight` as the FIRST/only public method (inline any helper) — otherwise a
helper declared above rotateRight gets called instead and everything fails.

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/rotate-a-ll.jsonl
  One JSON object per line:
    {"inputs": {"head": "<array>", "k": "<int>"}, "expected": "<space-sep values>"}
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/rotate-a-ll.jsonl"
N_CASES = 2000

VAL_MIN = -10_000        # -10^4
VAL_MAX = 10_000         #  10^4
K_MIN = 0
K_MAX = 500_000          # 5 * 10^5
CONSTRAINT_MAX_NODES = 100_000   # 10^5 (problem's stated upper bound on list size)

# IMPORTANT — TOTAL output budget for "submit":
# The judge runs all N_CASES in ONE batched process and captures its combined
# stdout, which scripts/judge_exec.py truncates at OUT_CAP = 256 KB. Every case
# emits one line of space-separated values; if the SUM of all output lines
# exceeds 256 KB, the tail is silently dropped and every case after the cut
# desyncs/fails. So we must keep the *total* output (all 2000 lines together)
# comfortably under 256 KB. We budget ~180 KB total (verified live: a correct
# class Solution must pass 100% of this set).
#
# A value is up to 6 chars ("-10000") + 1 space ~= 7 bytes/node. To respect the
# budget we cap individual list sizes at MAX_NODES and keep big lists rare. All
# inputs still satisfy the problem constraint (size <= 10^5); we simply don't
# emit the very largest legal lists because the judge can't capture their output
# in batch mode. The re-runnable script can raise these caps on demand.
MAX_NODES = 600          # serialization-safe ceiling for generated lists
TOTAL_OUT_BUDGET = 180_000   # bytes; stay well under judge's 256 KB stdout cap

random.seed(20260606)


def reference_rotate_right(values, k):
    """
    Ground-truth oracle.

    Right-rotating a singly linked list by k places is identical to right-
    rotating the list of node VALUES by k % n (nodes are only relinked, not
    copied or mutated). Mirrors the canonical Striver solution:
      if head==NULL or k==0: return head
      k %= len; if k==0: return head
      new head = element at index (len - k)
    """
    n = len(values)
    if n == 0 or k == 0:
        return list(values)
    k %= n
    if k == 0:
        return list(values)
    # right rotation by k: last k elements move to front
    return values[n - k:] + values[: n - k]


def fmt_list(values):
    # Match the example/dataset format: int array -> "[3, 1, 2]"; empty -> "[]"
    return "[" + ", ".join(str(v) for v in values) + "]"


def fmt_expected(values):
    # Judge prints ListNode output as space-separated values; empty list -> ""
    return " ".join(str(v) for v in values)


def make_case(values, k):
    return {
        # Keys EXACTLY the starterCpp param names in signature order:
        # rotateRight(ListNode* head, int k) -> head (as value array), then k.
        "inputs": {"head": fmt_list(values), "k": str(k)},
        "expected": fmt_expected(reference_rotate_right(values, k)),
    }


def rand_values(size):
    return [random.randint(VAL_MIN, VAL_MAX) for _ in range(size)]


def gen_cases(n):
    cases = []
    seen = set()

    def add(values, k):
        key = (tuple(values), k)
        if key in seen:
            return False
        seen.add(key)
        cases.append(make_case(values, k))
        return True

    # ---- Deterministic edge cases (always included) ----
    edge = [
        # (values, k)
        ([], 0),                      # empty list, k=0
        ([], 5),                      # empty list, k>0
        ([], K_MAX),                  # empty list, k at max
        ([0], 0),                     # single node, k=0
        ([0], 1),                     # single node, k=1
        ([7], K_MAX),                 # single node, huge k
        ([VAL_MIN], 3),               # single node, min value
        ([VAL_MAX], 3),               # single node, max value
        ([1, 2, 3, 4, 5], 0),         # no rotation
        ([1, 2, 3, 4, 5], 2),         # dataset example 1 -> 4 5 1 2 3
        ([1, 2, 3, 4, 5], 4),         # dataset example 2 -> 2 3 4 5 1
        ([1, 2, 3, 4, 5], 5),         # k == len -> unchanged
        ([1, 2, 3, 4, 5], 7),         # dataset "now your turn", k>len -> 4 5 1 2 3
        ([1, 2, 3, 4, 5], 10),        # k multiple of len -> unchanged
        ([1, 2, 3, 4, 5], K_MAX),     # k at max bound
        ([VAL_MIN, VAL_MAX], 1),      # extremes, two nodes
        ([VAL_MIN, VAL_MAX], 2),      # k == len
        ([0, 0, 0, 0], 2),            # duplicates
        ([VAL_MAX] * 10, 3),          # all-max moderate
        ([VAL_MIN] * 10, 3),          # all-min moderate
        (list(range(0, 100)), 37),    # ascending small
        (list(range(99, -1, -1)), 50),# descending small
        (list(range(-50, 50)), 1),    # spans negatives/positives
        (list(range(0, 300)), 299),   # medium, k = len-1
        (list(range(0, 300)), 300),   # medium, k = len
        (list(range(0, 300)), 301),   # medium, k = len+1
        (list(range(0, 300)), K_MAX), # medium, huge k
    ]
    # A few larger lists at the serialization-safe ceiling.
    edge.append((rand_values(MAX_NODES), random.randint(K_MIN, K_MAX)))
    edge.append(([5000] * MAX_NODES, 12345))
    edge.append((rand_values(MAX_NODES), MAX_NODES))      # k == len
    edge.append((rand_values(MAX_NODES), 0))              # k == 0, large list

    out_bytes = 0
    for values, k in edge:
        if add(values, k):
            out_bytes += len(cases[-1]["expected"]) + 1

    # ---- Random cases ----
    # Size distribution is kept small so the TOTAL output of all cases fits the
    # judge's 256 KB batched-stdout cap (see TOTAL_OUT_BUDGET above). Most lists
    # are tiny; a minority are medium; large lists are rare.
    while len(cases) < n:
        remaining_cases = n - len(cases)
        budget_left = TOTAL_OUT_BUDGET - out_bytes
        # average bytes we can still spend per remaining case
        avg_left = budget_left / max(1, remaining_cases)

        r = random.random()
        if r < 0.70:
            size = random.randint(1, 20)
        elif r < 0.92:
            size = random.randint(1, 60)
        elif r < 0.99:
            size = random.randint(1, 200)
        else:
            size = random.randint(1, MAX_NODES)
        # If we're running low on budget, force small lists so we never blow the cap.
        if avg_left < 60:
            size = random.randint(1, 12)
        values = rand_values(size)

        # k distribution: often within [0, size] (interesting boundaries),
        # sometimes well beyond size up to the full constraint bound.
        kr = random.random()
        if kr < 0.45:
            k = random.randint(0, size)                # 0..len incl. k==len
        elif kr < 0.65:
            k = random.choice([0, size, size - 1 if size > 0 else 0,
                                size + 1])             # boundary values
        elif kr < 0.85:
            k = random.randint(0, max(1, 3 * size))    # a few multiples of len
        else:
            k = random.randint(K_MIN, K_MAX)           # full range, k may >> len
        k = max(K_MIN, min(K_MAX, k))

        # Hard guard: never let a single case push us over the total budget.
        projected = len(fmt_expected(reference_rotate_right(values, k))) + 1
        if out_bytes + projected > TOTAL_OUT_BUDGET and size > 12:
            # shrink to a tiny list and retry
            values = rand_values(random.randint(1, 8))
            k = random.randint(0, max(1, 2 * len(values)))
            projected = len(fmt_expected(reference_rotate_right(values, k))) + 1

        if not add(values, k):
            continue
        out_bytes += projected

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
