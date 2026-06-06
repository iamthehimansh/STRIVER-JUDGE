#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Reverse a LL" (slug: reverse-a-ll-1).

Problem: given the head of a singly linked list, reverse it and return the head.

starterCpp signature:  ListNode* reverseList(ListNode* head)
  -> single param named `head`, type ListNode*.

The judge (lib/judge/harness.ts):
  * builds ListNode* from the array form "[1, 2, 3]" via rdList (uses .val).
  * binds the input key to the param `head` (name-match for key "head",
    otherwise positional -- so any single key works; we use "head").
  * prints a ListNode* OUTPUT as space-separated values (pr(ListNode*)),
    e.g. reversed [1,2,3,4,5] -> "5 4 3 2 1".
  * comparator (lib/judge/compare.ts) is lenient: it strips brackets/commas/
    quotes and compares token-by-token, so we may write expected as "[5, 4, ...]".

Constraints:
  * 0 <= number of nodes <= 10^5
  * 0 <= ListNode.val <= 10^4

The reference (reversing a list) is trivially correct, so we compute the
expected output directly in Python (reverse the values list). This matches
exactly what the judge's pr(ListNode*) will print for a correct solution.

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/reverse-a-ll-1.jsonl
  one JSON object per line: {"inputs": {"head": "[...]"}, "expected": "[...]"}
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/reverse-a-ll-1.jsonl"
N_CASES = 2000
# Problem constraint allows up to 10^5 nodes, but the judge's BATCH submit path
# (lib/judge/runner.ts) caps the total captured stdout of the single batched
# process at 1 MB. With 2000 cases each printing one line of space-separated
# values, we must keep the TOTAL output volume well under that cap or trailing
# cases get truncated and mis-graded. We therefore bound per-case list sizes so
# the aggregate output stays comfortably under ~700 KB, while still covering
# small/medium/large lists and edge cases.
MAX_NODES = 10**5          # hard problem constraint (used only for assertions)
GEN_MAX_NODES = 4000       # largest list we actually emit (keeps batch output small)
MAX_VAL = 10**4
SEED = 20260606

random.seed(SEED)


def reference_reverse(vals):
    """Ground-truth: reverse the list of node values."""
    return list(reversed(vals))


def fmt_list(vals):
    """Format a list of ints the way the dataset examples show arrays."""
    return "[" + ", ".join(str(v) for v in vals) + "]"


def rand_vals(n):
    return [random.randint(0, MAX_VAL) for _ in range(n)]


def build_cases():
    cases = []  # list of value-lists

    # ---- Edge cases ----
    cases.append([])              # empty list (0 nodes, min size)
    cases.append([0])             # single node, min value
    cases.append([MAX_VAL])       # single node, max value
    cases.append([0, 0])          # two equal (min)
    cases.append([MAX_VAL, MAX_VAL])
    cases.append([6, 8])          # dataset example 2
    cases.append([1, 2, 3, 4, 5]) # dataset example 1
    cases.append([0, MAX_VAL, 0, MAX_VAL])
    cases.append(list(range(0, 100)))             # increasing
    cases.append(list(range(99, -1, -1)))         # decreasing
    cases.append([7] * 50)                        # all same value
    # a few of the largest lists we emit (well within batch-output budget)
    cases.append(rand_vals(GEN_MAX_NODES))        # largest emitted size
    cases.append(rand_vals(GEN_MAX_NODES - 1))
    cases.append([MAX_VAL] * GEN_MAX_NODES)       # large + max-width values

    # ---- Random small cases (exercise serialization / many short lists) ----
    while len(cases) < 1400:
        n = random.randint(0, 12)
        cases.append(rand_vals(n))

    # ---- Random medium cases ----
    while len(cases) < 1900:
        n = random.randint(13, 60)
        cases.append(rand_vals(n))

    # ---- A modest number of larger cases (kept small so total batch output
    #      stays under the judge's 1 MB cap) ----
    while len(cases) < N_CASES:
        n = random.randint(61, 200)
        cases.append(rand_vals(n))

    # trim/pad to exactly N_CASES
    cases = cases[:N_CASES]
    return cases


def main():
    cases = build_cases()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for vals in cases:
            # validate constraints
            assert 0 <= len(vals) <= MAX_NODES, f"node count out of range: {len(vals)}"
            for v in vals:
                assert 0 <= v <= MAX_VAL, f"val out of range: {v}"
            expected = reference_reverse(vals)
            obj = {
                "inputs": {"head": fmt_list(vals)},
                "expected": fmt_list(expected),
            }
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
