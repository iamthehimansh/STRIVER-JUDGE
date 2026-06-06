#!/usr/bin/env python3
"""
Generator for: Remove Nth node from the back of the LL
Signature: ListNode* removeNthFromEnd(ListNode* head, int n)
  -> keys: "head" (ListNode* serialized as value array "[1, 2, 3]"), "n" (int)
Constraints:
  - 1 <= number of nodes <= 1e5
  - 0 <= ListNode.val <= 1e4
  - 1 <= n <= number of nodes

Reference oracle (matches ref2 / strivers-a2z): remove the nth node from the end.
Since n <= length is guaranteed, the result is always a valid list (possibly empty
when length == 1 and n == 1).
"""
import json
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/remove-nth-node-from-the-back-of-the-ll.jsonl"

MAXVAL = 10000  # 0 <= val <= 1e4


def remove_nth_from_end(vals, n):
    """Return list of vals after removing the nth node from the end (1-indexed)."""
    length = len(vals)
    # index from the front of the node to remove: length - n  (0-indexed)
    idx = length - n
    return vals[:idx] + vals[idx + 1:]


def fmt_list(vals):
    return "[" + ", ".join(str(v) for v in vals) + "]"


def make_case(length):
    vals = [random.randint(0, MAXVAL) for _ in range(length)]
    n = random.randint(1, length)
    return vals, n


def main():
    random.seed(20240606)
    cases = []
    seen = set()

    # ---- Edge cases ----
    edge = []
    # single node, n=1 -> empty result
    edge.append(([0], 1))
    edge.append(([10000], 1))
    edge.append(([5], 1))
    # two nodes, both n values
    edge.append(([1, 2], 1))
    edge.append(([1, 2], 2))
    edge.append(([0, 10000], 1))
    edge.append(([0, 10000], 2))
    # remove head (n == length)
    edge.append(([1, 2, 3, 4, 5], 5))
    # remove tail (n == 1)
    edge.append(([1, 2, 3, 4, 5], 1))
    # dataset examples
    edge.append(([1, 2, 3, 4, 5], 2))
    edge.append(([5, 4, 3, 2, 1], 5))
    edge.append(([9, 8, 7], 1))
    # extreme values
    edge.append(([0, 0, 0, 0], 2))
    edge.append(([10000, 10000, 10000], 1))
    edge.append(([10000, 10000, 10000], 3))
    # larger lists (kept modest so the full 2000-case harness stays within the
    # judge's global time budget; correctness is independent of length)
    edge.append((list(range(0, 100)), 50))
    edge.append(([i % (MAXVAL + 1) for i in range(200)], 1))
    edge.append(([i % (MAXVAL + 1) for i in range(200)], 200))
    edge.append(([i % (MAXVAL + 1) for i in range(200)], 100))

    for vals, n in edge:
        cases.append((vals, n))

    # ---- Random small/medium cases for variety ----
    target = 2000
    while len(cases) < target:
        # bias toward small lengths for diversity, occasionally large
        r = random.random()
        if r < 0.80:
            length = random.randint(1, 30)
        elif r < 0.97:
            length = random.randint(1, 100)
        else:
            length = random.randint(1, 250)
        vals, n = make_case(length)
        cases.append((vals, n))

    cases = cases[:target]

    with open(OUT, "w") as f:
        for vals, n in cases:
            expected = remove_nth_from_end(vals, n)
            obj = {
                "inputs": {
                    "head": fmt_list(vals),
                    "n": str(n),
                },
                "expected": fmt_list(expected),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
