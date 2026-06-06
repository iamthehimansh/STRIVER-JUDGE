#!/usr/bin/env python3
"""Generator for Striver problem: search-in-linked-list.

Signature: bool searchKey(ListNode* head, int key)
- head: singly linked list, serialized as value array e.g. "[1, 2, 3]"
- key: int
Output: "true" / "false"

Constraints:
  1 <= n <= 1e5   (number of nodes; list is non-empty)
  1 <= Node.val <= 1e5
  1 <= key <= 1e5

Reference is a trivial linear search; computed directly in Python.
"""
import json
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/search-in-linked-list.jsonl"
VMIN, VMAX = 1, 100000
N_CASES = 2000

random.seed(20260606)


def reference(values, key):
    """Ground-truth oracle: is key present in the list values?"""
    return key in values


def fmt_list(values):
    return "[" + ", ".join(str(v) for v in values) + "]"


def make_case():
    # Choose list size. Bias toward small lists but include large ones.
    r = random.random()
    if r < 0.30:
        n = random.randint(1, 5)
    elif r < 0.70:
        n = random.randint(1, 50)
    elif r < 0.95:
        n = random.randint(1, 1000)
    else:
        n = random.randint(1, 100000)

    values = [random.randint(VMIN, VMAX) for _ in range(n)]

    # Decide whether key should be present (~50%) to balance true/false.
    if random.random() < 0.5 and values:
        key = random.choice(values)
    else:
        key = random.randint(VMIN, VMAX)

    return values, key


def edge_cases():
    cases = []
    # Single node, key present
    cases.append(([42], 42))
    # Single node, key absent
    cases.append(([42], 7))
    # min value / max value boundaries
    cases.append(([1], 1))
    cases.append(([100000], 100000))
    cases.append(([1], 100000))
    cases.append(([100000], 1))
    # key at head
    cases.append(([5, 6, 7], 5))
    # key at tail
    cases.append(([5, 6, 7], 7))
    # key in middle
    cases.append(([5, 6, 7], 6))
    # duplicates, present
    cases.append(([3, 3, 3, 3], 3))
    # duplicates, absent
    cases.append(([3, 3, 3, 3], 4))
    # all min, search max -> false
    cases.append(([1] * 100, 100000))
    # large list, key present at end
    big = [random.randint(VMIN, VMAX) for _ in range(100000)]
    big[-1] = 99999
    cases.append((big, 99999))
    # large list, key absent (fill with value, search different boundary-ish)
    big2 = [50000] * 100000
    cases.append((big2, 1))
    big3 = [50000] * 100000
    cases.append((big3, 50000))
    # example cases from dataset
    cases.append(([1, 2, 3, 4], 3))
    cases.append(([7, 8, 9, 10, 11], 5))
    cases.append(([100000, 99999, 12345, 678], 12345))
    return cases


def main():
    seen = set()
    out_lines = []

    def add(values, key):
        b = reference(values, key)
        obj = {
            "inputs": {"head": fmt_list(values), "key": str(key)},
            "expected": "true" if b else "false",
        }
        out_lines.append(json.dumps(obj))

    # Edge cases first.
    ec = edge_cases()
    for values, key in ec:
        add(values, key)

    # Random cases to fill up to N_CASES.
    while len(out_lines) < N_CASES:
        values, key = make_case()
        # de-dup small cases by signature to add variety (skip dedup for big lists)
        if len(values) <= 50:
            sig = (tuple(values), key)
            if sig in seen:
                continue
            seen.add(sig)
        add(values, key)

    out_lines = out_lines[:N_CASES]
    with open(OUT, "w") as f:
        f.write("\n".join(out_lines) + "\n")

    # quick self-report
    n_true = sum(1 for l in out_lines if json.loads(l)["expected"] == "true")
    print(f"wrote {len(out_lines)} cases to {OUT}")
    print(f"true={n_true} false={len(out_lines) - n_true}")


if __name__ == "__main__":
    main()
