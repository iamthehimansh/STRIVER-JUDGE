#!/usr/bin/env python3
"""
Generator for Striver problem: bst-iterator (BST Iterator).

Design problem. The judge drives a sequence of operations against a `BSTIterator`
built over a BST `root`:
  - "BSTIterator" : constructor (produces NO output entry)
  - "next"        : returns the next in-order element (int)
  - "hasNext"     : returns whether another element exists (true/false)

Input keys (exactly as in the dataset testcases, in this order):
  - nums : JSON array of operation-name strings, e.g. ["BSTIterator", "next", "hasNext"]
  - root : space-separated level-order serialization (LeetCode style) with "null"
           for absent children, e.g. "7 3 15 null null 9 20"

Output (expected): a JSON-array-style list aggregating the output of every op
after the constructor, e.g. [3, 7, true, 9, true, 15, true, 20, false].
Ints are printed bare; booleans as lowercase true/false.

Reference oracle: standard in-order traversal of the BST. next() returns the
in-order elements one-by-one; hasNext() is true while elements remain.
This matches strivers-a2z-ref/.../09. BST Iterator.cpp (stack-based, same result).

Constraints enforced:
  - 1 <= number of nodes <= 10^4
  - at most 10^4 calls to next and hasNext (combined)
  - 0 <= Node.val <= 1054
We build genuine BSTs (BST property holds) by inserting distinct/repeatable
values via BST insertion, then serialize level-order.
"""

import json
import random
import sys

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/bst-iterator.jsonl"
N_CASES = 2000
VAL_MAX = 1054          # 0 <= Node.val <= 1054
MAX_NODES = 10**4       # 1 <= nodes <= 10^4
MAX_CALLS = 10**4       # at most 10^4 calls to next + hasNext


# ---------------------------------------------------------------------------
# BST construction + level-order serialization
# ---------------------------------------------------------------------------
class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def bst_insert(root, val):
    """Insert val into BST. Duplicates go to the right subtree (valid BST shape).
    Returns the (possibly new) root."""
    if root is None:
        return Node(val)
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = Node(val)
                return root
            cur = cur.left
        else:  # val >= cur.val
            if cur.right is None:
                cur.right = Node(val)
                return root
            cur = cur.right
    # unreachable


def build_bst(values):
    root = None
    for v in values:
        root = bst_insert(root, v)
    return root


def serialize_levelorder(root):
    """LeetCode-style level-order serialization with trailing-null trimming.
    Returns a space-separated string with 'null' for missing children."""
    if root is None:
        return ""
    out = []
    q = [root]
    i = 0
    while i < len(q):
        node = q[i]
        i += 1
        if node is None:
            out.append("null")
            continue
        out.append(str(node.val))
        q.append(node.left)
        q.append(node.right)
    # trim trailing 'null'
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def inorder(root):
    """Iterative in-order traversal -> list of values (the oracle order)."""
    res = []
    st = []
    cur = root
    while cur is not None or st:
        while cur is not None:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        res.append(cur.val)
        cur = cur.right
    return res


# ---------------------------------------------------------------------------
# Simulate the operation sequence -> expected output list
# ---------------------------------------------------------------------------
def simulate(ops, root):
    """Run the op sequence against an oracle iterator over in-order(root).
    Returns a list of output tokens (ints and python bools), one per op after
    the constructor."""
    order = inorder(root)
    idx = 0  # pointer: number of elements already returned by next()
    out = []
    for op in ops:
        if op == "BSTIterator":
            # constructor: no output
            continue
        elif op == "next":
            # next() calls are guaranteed valid by the problem statement
            out.append(order[idx])
            idx += 1
        elif op == "hasNext":
            out.append(idx < len(order))
        else:
            raise ValueError("unknown op: %r" % op)
    return out


def format_expected(tokens):
    parts = []
    for t in tokens:
        if isinstance(t, bool):
            parts.append("true" if t else "false")
        else:
            parts.append(str(t))
    return "[" + ", ".join(parts) + "]"


# ---------------------------------------------------------------------------
# Random op-sequence generation (always valid: never call next past the end)
# ---------------------------------------------------------------------------
def random_ops(n_nodes, rng):
    """Build a sequence: starts with 'BSTIterator', then a mix of 'next'/'hasNext'.
    Never emits more 'next' than there are nodes (next() must always be valid).
    Total next+hasNext calls <= MAX_CALLS."""
    ops = ["BSTIterator"]
    nexts_left = n_nodes
    # total operation budget (excluding constructor), bounded by MAX_CALLS
    budget = rng.randint(1, min(MAX_CALLS, 60))
    for _ in range(budget):
        # choose hasNext freely; choose next only if elements remain
        if nexts_left == 0:
            ops.append("hasNext")
        else:
            if rng.random() < 0.6:
                ops.append("next")
                nexts_left -= 1
            else:
                ops.append("hasNext")
    return ops


def make_values(n, rng):
    """n values in [0, VAL_MAX]; uses sampling without replacement when possible
    to get distinct values, else allows duplicates."""
    if n <= VAL_MAX + 1:
        return rng.sample(range(0, VAL_MAX + 1), n)
    return [rng.randint(0, VAL_MAX) for _ in range(n)]


def gen_case(rng, forced=None):
    if forced is not None:
        values, ops_spec = forced
        n = len(values)
    else:
        # bias toward small/medium trees; occasionally large
        r = rng.random()
        if r < 0.55:
            n = rng.randint(1, 30)
        elif r < 0.85:
            n = rng.randint(31, 300)
        elif r < 0.97:
            n = rng.randint(301, 2000)
        else:
            n = rng.randint(2001, MAX_NODES)
        values = make_values(n, rng)
        ops_spec = None

    root = build_bst(values)
    if ops_spec is not None:
        ops = ops_spec
    else:
        ops = random_ops(n, rng)

    root_str = serialize_levelorder(root)
    expected = format_expected(simulate(ops, root))
    return {
        "inputs": {
            "nums": json.dumps(ops),
            "root": root_str,
        },
        "expected": expected,
    }


def main():
    rng = random.Random(20260606)

    cases = []

    # ---- Edge / fixed cases first ----
    # The two dataset examples (exact reproduction check happens in verify()):
    # tree 7 3 15 null null 9 20 == build from [7,3,15,9,20] (BST insertion).
    example_values = [7, 3, 15, 9, 20]
    ex1_ops = ["BSTIterator", "next", "next", "hasNext", "next", "hasNext",
               "next", "hasNext", "next", "hasNext"]
    ex2_ops = ["BSTIterator", "next", "next", "next", "hasNext", "next", "hasNext"]
    cases.append(gen_case(rng, forced=(example_values, ex1_ops)))
    cases.append(gen_case(rng, forced=(example_values, ex2_ops)))

    # single node, value extremes
    cases.append(gen_case(rng, forced=([0], ["BSTIterator", "hasNext", "next", "hasNext"])))
    cases.append(gen_case(rng, forced=([1054], ["BSTIterator", "next", "hasNext"])))
    cases.append(gen_case(rng, forced=([0], ["BSTIterator", "next", "hasNext"])))
    # only hasNext calls (no next)
    cases.append(gen_case(rng, forced=([5, 3, 8], ["BSTIterator", "hasNext", "hasNext"])))
    # exhaust all then hasNext false
    cases.append(gen_case(rng, forced=([5, 3, 8, 1, 4, 7, 9],
                 ["BSTIterator"] + ["next"] * 7 + ["hasNext"])))
    # left-skewed (sorted descending insert -> all-left chain)
    cases.append(gen_case(rng, forced=(list(range(20, 0, -1)),
                 ["BSTIterator"] + ["next", "hasNext"] * 10)))
    # right-skewed (sorted ascending insert -> all-right chain)
    cases.append(gen_case(rng, forced=(list(range(1, 21)),
                 ["BSTIterator"] + ["next", "hasNext"] * 10)))
    # duplicates present
    cases.append(gen_case(rng, forced=([5, 5, 5, 3, 3, 8],
                 ["BSTIterator", "next", "next", "next", "next", "hasNext"])))

    # ---- Random cases to fill up to N_CASES ----
    while len(cases) < N_CASES:
        cases.append(gen_case(rng))

    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    print("wrote %d cases to %s" % (len(cases), OUT_PATH))


# ---------------------------------------------------------------------------
# Self-verification against the dataset examples
# ---------------------------------------------------------------------------
def verify():
    # Example 1
    vals = [7, 3, 15, 9, 20]
    root = build_bst(vals)
    assert serialize_levelorder(root) == "7 3 15 null null 9 20", \
        "serialize mismatch: " + serialize_levelorder(root)
    ops1 = ["BSTIterator", "next", "next", "hasNext", "next", "hasNext",
            "next", "hasNext", "next", "hasNext"]
    exp1 = format_expected(simulate(ops1, root))
    assert exp1 == "[3, 7, true, 9, true, 15, true, 20, false]", exp1
    ops2 = ["BSTIterator", "next", "next", "next", "hasNext", "next", "hasNext"]
    exp2 = format_expected(simulate(ops2, root))
    assert exp2 == "[3, 7, 9, true, 15, true]", exp2
    print("verify OK: examples reproduced")
    print("  ex1:", exp1)
    print("  ex2:", exp2)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify()
    else:
        verify()
        main()
