#!/usr/bin/env python3
"""Generator for 'find-the-length-of-the-linked-list'.

Problem: count nodes in a singly linked list.
  signature: int getLength(ListNode* head)
Constraints:
  0 <= number of nodes <= 1e5
  0 <= ListNode.val <= 1e4

Input format (judge): ListNode* as value-list array, e.g. "[1, 2, 3]".
Expected: integer length as string.

Reference oracle: length == number of nodes == len(list).
(Trivial; matches the C++ getLength that walks next pointers.)
"""
import json
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-the-length-of-the-linked-list.jsonl"
N_CASES = 2000
MAX_NODES = 10**5
MAX_VAL = 10**4

def fmt_list(vals):
    return "[" + ", ".join(str(v) for v in vals) + "]"

def make_case(n):
    vals = [random.randint(0, MAX_VAL) for _ in range(n)]
    return {"inputs": {"head": fmt_list(vals)}, "expected": str(n)}

def main():
    random.seed(12345)
    cases = []

    # Edge cases: empty list, single node (min/max val), small sizes.
    edge_sizes = [0, 0, 1, 1, 1, 2, 2, 3, 4, 5, 10, 100, 1000, 9999, 10000,
                  50000, 99999, 100000]
    for n in edge_sizes:
        if n == 1:
            # explicit min/max single-node values
            for v in (0, MAX_VAL, random.randint(0, MAX_VAL)):
                cases.append({"inputs": {"head": fmt_list([v])}, "expected": "1"})
        else:
            cases.append(make_case(n))

    # Random cases up to N_CASES total. Keep sizes mostly modest so file stays
    # reasonable, with a sprinkling of larger lists.
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.80:
            n = random.randint(0, 50)
        elif r < 0.95:
            n = random.randint(0, 500)
        else:
            n = random.randint(0, 5000)
        cases.append(make_case(n))

    cases = cases[:N_CASES]
    random.shuffle(cases)

    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")

if __name__ == "__main__":
    main()
