#!/usr/bin/env python3
"""
Test-case generator for Striver problem
"Check if LL is palindrome or not" (slug: check-if-ll-is-palindrome-or-not).

Given the head of a singly linked list representing a positive integer (one
digit per node, most-significant digit first). Return true if the digit
sequence reads the same forwards and backwards, else false.

Constraints:
  - 1 <= number of nodes in the Linked List <= 1e5
  - 0 <= ListNode.val <= 9
  - The represented number has no leading zeroes.

"No leading zeroes" => the first node (head) value must be non-zero, EXCEPT a
single-node list may be 0 (the number 0). To keep generation simple and always
within constraints we enforce: head != 0 whenever n > 1; for n == 1 the single
digit may be 0..9.

Note: when n > 1 and head != 0, a palindrome's LAST digit equals the first, so
it is automatically non-zero — still valid.

ListNode is serialized by the judge as the array of node values, e.g.
"[3, 7, 5, 7, 3]". The bool return is printed as "true"/"false".

The judge binds the single input column to the single ListNode* param
positionally; we use the dataset's key name "nums".
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-if-ll-is-palindrome-or-not.jsonl"
N_CASES = 2000
MAX_NODES = 100000


def is_palindrome(digits):
    return digits == digits[::-1]


def fmt_list(lst):
    return "[" + ", ".join(str(x) for x in lst) + "]"


def gen_valid_number(n):
    """Random valid number of length n (no leading zero unless n == 1)."""
    if n == 1:
        return [random.randint(0, 9)]
    digits = [random.randint(0, 9) for _ in range(n)]
    digits[0] = random.randint(1, 9)  # no leading zero
    return digits


def gen_palindrome(n):
    """Random palindrome of length n with no leading zero (unless n == 1)."""
    if n == 1:
        return [random.randint(0, 9)]
    half = (n + 1) // 2
    left = [random.randint(0, 9) for _ in range(half)]
    left[0] = random.randint(1, 9)  # no leading zero
    # mirror
    if n % 2 == 0:
        digits = left + left[::-1]
    else:
        digits = left + left[-2::-1]
    return digits


def make_case(kind, n):
    if kind == "pal":
        return gen_palindrome(n)
    if kind == "nonpal":
        # generate until non-palindrome (for n>=2 with random digits this is
        # overwhelmingly likely; force a break for tiny n to guarantee progress)
        for _ in range(200):
            d = gen_valid_number(n)
            if not is_palindrome(d):
                return d
        # fall back: deterministically break the palindrome
        d = gen_palindrome(n)
        if n >= 2:
            # flip one digit near the end to differ from its mirror
            i = n - 1
            d[i] = (d[i] + 1) % 10
            # if that made the last digit 0 it's still fine (not the head)
            if is_palindrome(d):
                d[i] = (d[i] + 1) % 10
        return d
    return gen_valid_number(n)


def main():
    random.seed(2844)
    cases = []

    # --- deterministic edge cases ---
    edge = [
        [0],                 # single node 0 -> palindrome, number 0
        [5],                 # single node -> palindrome
        [1, 1],              # smallest even palindrome
        [1, 2],              # smallest non-palindrome
        [3, 7, 5, 7, 3],     # example 1 -> true
        [1, 1, 2, 1],        # example 2 -> false
        [9, 9, 9, 9],        # example 3 (nowYourTurn) -> true
        [1, 0, 1],           # palindrome with internal zero
        [1, 2, 1],           # odd palindrome
        [1, 2, 3],           # odd non-palindrome
        [1, 2, 2, 1],        # even palindrome
        [1, 2, 3, 1],        # even non-palindrome
    ]
    for d in edge:
        cases.append(d)

    # large palindrome (max-ish size, even and odd)
    cases.append(gen_palindrome(MAX_NODES))
    cases.append(gen_palindrome(MAX_NODES - 1))
    # large non-palindrome
    cases.append(make_case("nonpal", MAX_NODES))
    cases.append(make_case("nonpal", MAX_NODES - 1))

    remaining = N_CASES - len(cases)

    for _ in range(remaining):
        r = random.random()
        if r < 0.45:
            kind = "pal"
        elif r < 0.90:
            kind = "nonpal"
        else:
            kind = "rand"

        # size distribution: mostly small/medium, occasionally large
        s = random.random()
        if s < 0.55:
            n = random.randint(1, 12)
        elif s < 0.80:
            n = random.randint(13, 200)
        elif s < 0.95:
            n = random.randint(201, 5000)
        else:
            n = random.randint(5001, MAX_NODES)

        # n == 1 with kind nonpal is impossible -> coerce to rand/pal
        if n == 1 and kind == "nonpal":
            kind = "rand"

        cases.append(make_case(kind, n))

    # trim to exactly N_CASES (edges may have pushed us over by a tiny amount)
    cases = cases[:N_CASES]

    with open(OUT_PATH, "w") as f:
        for d in cases:
            obj = {
                "inputs": {"nums": fmt_list(d)},
                "expected": "true" if is_palindrome(d) else "false",
            }
            f.write(json.dumps(obj) + "\n")

    n_true = sum(1 for d in cases if is_palindrome(d))
    print(f"wrote {len(cases)} cases to {OUT_PATH}")
    print(f"  palindromes (true): {n_true}, non-palindromes (false): {len(cases) - n_true}")
    print(f"  max list length: {max(len(d) for d in cases)}")


if __name__ == "__main__":
    main()
