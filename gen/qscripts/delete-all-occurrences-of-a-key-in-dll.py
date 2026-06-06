#!/usr/bin/env python3
"""
Test-case generator for Striver problem: delete-all-occurrences-of-a-key-in-dll

Signature: ListNode* deleteAllOccurrences(ListNode* head, int target)
  - head   : doubly linked list, but the judge's injected struct only exposes
             val + next (prev is commented out in the starter), so the reference
             treats it as a singly linked list of values.
  - target : int to delete.

Constraints:
  - 0 <= number of nodes <= 1e5
  - -1e4 <= ListNode.val <= 1e4
  - -1e4 <= target <= 1e4

Output: head of modified list, serialized by the judge as space-separated
        values (empty string for an empty list). The judge compares leniently
        (brackets/commas/whitespace ignored).

jsonl line: {"inputs": {"head": "[...]", "target": "k"}, "expected": "v1 v2 ..."}
"""
import json
import os
import random
import subprocess

REF_BIN = "/tmp/dllgen/ref"
OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/delete-all-occurrences-of-a-key-in-dll.jsonl"
N_CASES = 2000

VAL_MIN, VAL_MAX = -10000, 10000
MAX_NODES = 100000


def run_ref(values, target):
    """Run the compiled reference; return expected output string (space-separated)."""
    list_line = " ".join(str(v) for v in values)
    inp = f"{list_line}\n{target}\n"
    res = subprocess.run([REF_BIN], input=inp, capture_output=True, text=True)
    return res.stdout.rstrip("\n")


def make_case(rng):
    """Produce (values_list, target) within constraints.

    NOTE on sizes: the judge captures the batched program's stdout with a
    256 KB cap (scripts/judge_exec.py OUT_CAP). With 2000 cases, each output
    line must stay short or later cases get truncated and misjudged. We keep
    list lengths small (<= ~16) so total output stays well under the cap while
    still exercising all deletion patterns. The constraint allows up to 1e5
    nodes, but huge lists are unnecessary for correctness coverage here.
    """
    mode = rng.random()
    if mode < 0.05:
        # empty list edge case
        n = 0
    elif mode < 0.35:
        # tiny lists
        n = rng.randint(1, 5)
    else:
        n = rng.randint(1, 16)

    # choose a small value universe sometimes so target deletions actually hit
    universe_mode = rng.random()
    if universe_mode < 0.4:
        lo = rng.randint(VAL_MIN, VAL_MAX - 5)
        hi = min(VAL_MAX, lo + rng.choice([1, 2, 3, 5, 10]))
        values = [rng.randint(lo, hi) for _ in range(n)]
    elif universe_mode < 0.6:
        # include extremes
        pool = [VAL_MIN, VAL_MAX, 0, -1, 1] + [rng.randint(VAL_MIN, VAL_MAX) for _ in range(5)]
        values = [rng.choice(pool) for _ in range(n)]
    else:
        values = [rng.randint(VAL_MIN, VAL_MAX) for _ in range(n)]

    # choose target: often a value present in the list so deletions occur
    tmode = rng.random()
    if n > 0 and tmode < 0.6:
        target = rng.choice(values)
    elif n > 0 and tmode < 0.75:
        # all-same list deletion (delete everything)
        v = values[0]
        values = [v] * n
        target = v
    else:
        target = rng.randint(VAL_MIN, VAL_MAX)
    return values, target


def fixed_cases():
    """Deterministic edge cases."""
    cases = []
    # dataset examples
    cases.append(([1, 2, 3, 1, 4], 1))
    cases.append(([2, 3, -1, 4, 2], 2))
    cases.append(([7, 7, 7, 7], 7))
    # empty list
    cases.append(([], 5))
    cases.append(([], -10000))
    # single node, deleted / not deleted
    cases.append(([5], 5))
    cases.append(([5], 3))
    cases.append(([-10000], -10000))
    cases.append(([10000], 10000))
    # target not present
    cases.append(([1, 2, 3], 9))
    # delete head only
    cases.append(([4, 1, 2, 3], 4))
    # delete tail only
    cases.append(([1, 2, 3, 4], 4))
    # all same, delete all
    cases.append(([0] * 10, 0))
    # extremes mix
    cases.append(([10000, -10000, 10000, -10000], 10000))
    cases.append(([10000, -10000, 10000, -10000], -10000))
    # alternating
    cases.append(([1, 2, 1, 2, 1, 2], 2))
    cases.append(([1, 2, 1, 2, 1, 2], 1))
    return cases


def main():
    rng = random.Random(20260606)
    seen_lines = []
    written = 0
    with open(OUT, "w") as f:
        # fixed edge cases first
        for values, target in fixed_cases():
            expected = run_ref(values, target)
            line = {
                "inputs": {
                    "head": "[" + ", ".join(str(v) for v in values) + "]",
                    "target": str(target),
                },
                "expected": expected,
            }
            f.write(json.dumps(line) + "\n")
            written += 1

        while written < N_CASES:
            values, target = make_case(rng)
            expected = run_ref(values, target)
            line = {
                "inputs": {
                    "head": "[" + ", ".join(str(v) for v in values) + "]",
                    "target": str(target),
                },
                "expected": expected,
            }
            f.write(json.dumps(line) + "\n")
            written += 1

    print(f"wrote {written} cases to {OUT}")


if __name__ == "__main__":
    main()
