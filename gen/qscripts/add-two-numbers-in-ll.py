#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Add two numbers in Linked List"
(slug: add-two-numbers-in-ll).

Two non-empty linked lists represent two non-negative integers with digits
stored in REVERSE order (one digit per node). Return the sum as a linked list,
also in reverse order.

Constraints:
  - 1 <= number of nodes in each LL <= 100
  - 0 <= value of each node <= 9
  - numbers have no leading zeros (except the number 0 itself, a single node 0)

ListNode is serialized by the judge as the array of node values, e.g. "[1, 2, 3]".

Reference logic (digit-by-digit add with carry) is equivalent to the C++
reference at ref2/"Add 2 numbers in linked list.cpp".
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/add-two-numbers-in-ll.jsonl"
N_CASES = 2000


def add_ll(a, b):
    """a, b are lists of digits (reverse order). Return sum list (reverse order)."""
    res = []
    carry = 0
    i = 0
    while i < len(a) or i < len(b) or carry:
        s = carry
        if i < len(a):
            s += a[i]
        if i < len(b):
            s += b[i]
        res.append(s % 10)
        carry = s // 10
        i += 1
    return res


def fmt_list(lst):
    return "[" + ", ".join(str(x) for x in lst) + "]"


def gen_number(max_nodes):
    """Generate a valid reverse-order digit list with no leading zeros.

    In reverse order, "no leading zeros" means the MOST significant digit
    (the LAST node) is non-zero -- unless the number is just a single 0.
    """
    n = random.randint(1, max_nodes)
    if n == 1:
        # single digit 0..9 (0 allowed -> represents the number 0)
        return [random.randint(0, 9)]
    digits = [random.randint(0, 9) for _ in range(n)]
    # last digit (most significant) must be non-zero
    digits[-1] = random.randint(1, 9)
    return digits


def make_case():
    return gen_number(100), gen_number(100)


def main():
    random.seed(20240606)
    cases = []

    # ---- Edge cases ----
    # minimal single nodes
    cases.append(([0], [0]))
    cases.append(([0], [9]))
    cases.append(([9], [0]))
    cases.append(([9], [9]))            # 9+9=18 -> [8,1]
    cases.append(([5], [5]))            # 5+5=10 -> [0,1]
    # example cases from dataset
    cases.append(([5, 4], [4]))         # 45+4=49 -> [9,4]
    cases.append(([4, 5, 6], [1, 2, 3]))  # 654+321=975 -> [5,7,9]
    # max length both (100 nines each) -> carry growth
    cases.append(([9] * 100, [9] * 100))
    cases.append(([9] * 100, [1]))      # carry propagation full length
    cases.append(([1], [9] * 100))
    # one long one short
    cases.append(([9] * 100, [9]))
    cases.append(([0], [9] * 100))
    # 99 nines + leading-nonzero already satisfied
    cases.append(([9] * 99 + [9], [1]))

    # ---- biased size buckets ----
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.15:
            a = gen_number(3)
            b = gen_number(3)
        elif r < 0.25:
            a = gen_number(1)
            b = gen_number(1)
        elif r < 0.35:
            a = gen_number(100)
            b = gen_number(1)
        elif r < 0.45:
            a = gen_number(1)
            b = gen_number(100)
        else:
            a = gen_number(100)
            b = gen_number(100)
        cases.append((a, b))

    cases = cases[:N_CASES]

    with open(OUT_PATH, "w") as f:
        for a, b in cases:
            # validate constraints
            assert 1 <= len(a) <= 100 and 1 <= len(b) <= 100
            assert all(0 <= d <= 9 for d in a) and all(0 <= d <= 9 for d in b)
            if len(a) > 1:
                assert a[-1] != 0
            if len(b) > 1:
                assert b[-1] != 0
            res = add_ll(a, b)
            obj = {
                "inputs": {
                    "linkedList1": fmt_list(a),
                    "linkedList2": fmt_list(b),
                },
                "expected": fmt_list(res),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
