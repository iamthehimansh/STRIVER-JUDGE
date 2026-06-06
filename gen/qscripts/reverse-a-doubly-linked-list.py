#!/usr/bin/env python3
"""
Test-case generator for Striver problem: reverse-a-doubly-linked-list

The judge builds a ListNode list from the input value array (struct ListNode
{ int val; ListNode* next; }), calls Solution::reverseDLL(head), and prints
the resulting list as space-separated values. Reversing a list (using next
pointers) just reverses the value sequence, so the expected output is the
reversed input array.

Constraints (from problem json):
  1 <= number of nodes <= 10^6
  0 <= node.val <= 10^4

We keep node counts modest. The judge runs ALL submit cases in ONE batched
process and scripts/judge_exec.py caps the captured stdout at 256 KiB
(OUT_CAP), so the TOTAL serialized output (space-separated values, no
brackets) across all 2000 cases must stay well under 256 KiB or later cases
get truncated and fail. We therefore keep lists small (mostly <= 30 nodes, a
handful up to ~120) so the whole batch output is ~150-180 KiB. Constraints
still allow up to 10^6 nodes; the standalone generator can be tuned for bigger
sizes, but the interactive 256 KiB-capped judge cannot serialize that much.

Output: ONE json object per line:
  {"inputs": {"head": "[..]"}, "expected": "[..reversed..]"}
"""

import json
import random
import os

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/reverse-a-doubly-linked-list.jsonl"
N_CASES = 2000
VAL_MIN = 0
VAL_MAX = 10_000  # 10^4

random.seed(20260606)


def fmt_arr(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def reverse_reference(arr):
    """Mirror of the judge: building a singly-linked list from arr, reversing
    via next pointers, and printing values yields the reversed value array."""
    return list(reversed(arr))


def gen_list():
    """Pick a node count within constraints with a bias toward small/edge sizes."""
    r = random.random()
    if r < 0.15:
        n = 1                                   # min size
    elif r < 0.70:
        n = random.randint(1, 10)               # small
    elif r < 0.95:
        n = random.randint(11, 30)              # medium
    else:
        n = random.randint(31, 120)             # larger (output stays bounded)

    style = random.random()
    if style < 0.15:
        v = random.randint(VAL_MIN, VAL_MAX)    # all equal
        return [v] * n
    if style < 0.25:
        return [VAL_MIN] * n                     # all zeros (extreme low)
    if style < 0.35:
        return [VAL_MAX] * n                     # all max (extreme high)
    if style < 0.50:
        # sorted ascending values
        return sorted(random.randint(VAL_MIN, VAL_MAX) for _ in range(n))
    # general random values across the full allowed range
    return [random.randint(VAL_MIN, VAL_MAX) for _ in range(n)]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = []

    # explicit edge cases first
    edge = [
        [0],
        [10000],
        [5],
        [10, 20, 30],
        [1, 3, 5, 7, 9],
        [0, 10000],
        [10000, 0],
        [0, 0, 0, 0],
        [10000] * 5,
        list(range(0, 40)),             # values 0..39 (all distinct, within range)
        [10000 - i for i in range(30)], # descending
    ]
    for arr in edge:
        lines.append({"inputs": {"head": fmt_arr(arr)},
                      "expected": fmt_arr(reverse_reference(arr))})

    while len(lines) < N_CASES:
        arr = gen_list()
        lines.append({"inputs": {"head": fmt_arr(arr)},
                      "expected": fmt_arr(reverse_reference(arr))})

    with open(OUT, "w") as f:
        for obj in lines[:N_CASES]:
            f.write(json.dumps(obj) + "\n")

    print(f"wrote {min(len(lines), N_CASES)} cases to {OUT}")


if __name__ == "__main__":
    main()
