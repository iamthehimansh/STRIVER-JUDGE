#!/usr/bin/env python3
"""
Generator + static test set for Striver problem:
  "Check if a tree is a BST or not"  (slug: check-if-a-tree-is-a-bst-or-not)

starterCpp signature:  bool isBST(TreeNode* root)
  -> single param "root" (a TreeNode*)

Input serialization (must match judge EXACTLY):
  TreeNode* : level-order, space-separated, "null" for missing child,
              LeetCode-style (null nodes get no children).
              e.g. "5 3 6 2 4 null 7"

Output: "true" / "false".

Constraints:
  1 <= number of nodes <= 1e4
  -2^31 <= Node.val <= 2^31 - 1
We keep node counts modest (so the .jsonl stays small) but include edge cases:
  single node, full int extremes, skewed trees, perfect BSTs, near-BSTs that
  break by 1, duplicate values (must be FALSE since strict inequality), etc.
"""

import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-if-a-tree-is-a-bst-or-not.jsonl"

INT_MIN = -(2**31)        # -2147483648
INT_MAX = (2**31) - 1     #  2147483647

random.seed(1234567)


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


# ------------------------------------------------------------------
# Reference oracle: is this binary tree a valid BST?
# strict less on left subtree, strict greater on right subtree.
# Use Python's unbounded ints as bounds (mirrors LLONG_MIN/MAX in C++).
# ------------------------------------------------------------------
def is_bst(node, low, high):
    if node is None:
        return True
    if node.val <= low or node.val >= high:
        return False
    return is_bst(node.left, low, node.val) and is_bst(node.right, node.val, high)


def is_valid_bst(root):
    # iterative bounds check to avoid recursion limits on skewed trees
    stack = [(root, float("-inf"), float("inf"))]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        if node.val <= low or node.val >= high:
            return False
        stack.append((node.left, low, node.val))
        stack.append((node.right, node.val, high))
    return True


# ------------------------------------------------------------------
# Serialize a tree to LeetCode-style level-order with "null" markers,
# trimming trailing nulls. This is exactly how the example input looks
# and how the judge deserializes.
# ------------------------------------------------------------------
def serialize(root):
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
            continue
        out.append(str(node.val))
        q.append(node.left)
        q.append(node.right)
    # trim trailing "null"
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


# ------------------------------------------------------------------
# Tree builders
# ------------------------------------------------------------------
def build_random_shape(n, value_fn):
    """Build a random binary tree of exactly n nodes; values from value_fn()."""
    if n <= 0:
        return None
    root = Node(value_fn())
    leaves = [root]   # nodes with a free child slot
    created = 1
    while created < n:
        # pick a random node that still has a free slot
        idx = random.randrange(len(leaves))
        parent = leaves[idx]
        # choose left or right (only among free slots)
        free = []
        if parent.left is None:
            free.append("L")
        if parent.right is None:
            free.append("R")
        side = random.choice(free)
        child = Node(value_fn())
        if side == "L":
            parent.left = child
        else:
            parent.right = child
        created += 1
        leaves.append(child)
        # remove parent if now full
        if parent.left is not None and parent.right is not None:
            # swap-remove
            leaves[idx] = leaves[-1]
            leaves.pop()
    return root


def build_bst_from_sorted(vals):
    """Build a balanced BST from a sorted distinct list -> guaranteed valid BST."""
    if not vals:
        return None
    mid = len(vals) // 2
    node = Node(vals[mid])
    node.left = build_bst_from_sorted(vals[:mid])
    node.right = build_bst_from_sorted(vals[mid + 1:])
    return node


def insert_bst(root, val):
    """Standard BST insert (skips duplicates -> keeps it a valid BST)."""
    if root is None:
        return Node(val)
    cur = root
    while True:
        if val < cur.val:
            if cur.left is None:
                cur.left = Node(val)
                return root
            cur = cur.left
        elif val > cur.val:
            if cur.right is None:
                cur.right = Node(val)
                return root
            cur = cur.right
        else:
            return root  # duplicate, skip
    return root


def random_value():
    return random.randint(INT_MIN, INT_MAX)


def small_value():
    return random.randint(-50, 50)


def distinct_sample(k, lo, hi):
    """k distinct ints in [lo, hi]."""
    if hi - lo + 1 >= k:
        return random.sample(range(lo, hi + 1), k)
    # fall back: allow set growth
    s = set()
    while len(s) < k:
        s.add(random.randint(lo, hi))
    return list(s)


def perturb_one_node(root):
    """Pick a random node and change its value to a random value (may or may not break BST)."""
    nodes = []
    q = deque([root])
    while q:
        nd = q.popleft()
        nodes.append(nd)
        if nd.left:
            q.append(nd.left)
        if nd.right:
            q.append(nd.right)
    target = random.choice(nodes)
    target.val = random.randint(INT_MIN, INT_MAX)
    return root


def make_case(kind):
    """Return a root node according to a generation strategy."""
    if kind == "single":
        return Node(random.choice([INT_MIN, INT_MAX, 0, random_value()]))

    if kind == "bst_balanced":
        n = random.randint(1, 60)
        vals = sorted(distinct_sample(n, -10000, 10000))
        return build_bst_from_sorted(vals)

    if kind == "bst_insert":
        n = random.randint(1, 60)
        root = None
        for _ in range(n):
            root = insert_bst(root, random.randint(-10000, 10000))
        return root

    if kind == "bst_extremes":
        # BST spanning the full int range
        vals = sorted(set([INT_MIN, INT_MAX, 0,
                           random.randint(INT_MIN, 0),
                           random.randint(0, INT_MAX)]
                          + distinct_sample(random.randint(1, 20), -10**9, 10**9)))
        return build_bst_from_sorted(vals)

    if kind == "bst_then_break":
        # build a valid BST, then perturb one node -> often false, sometimes still true
        n = random.randint(2, 60)
        vals = sorted(distinct_sample(n, -10000, 10000))
        root = build_bst_from_sorted(vals)
        return perturb_one_node(root)

    if kind == "bst_with_dup":
        # valid-shaped BST but introduce a duplicate equal to an ancestor -> must be FALSE
        n = random.randint(2, 40)
        vals = sorted(distinct_sample(n, -1000, 1000))
        root = build_bst_from_sorted(vals)
        # set a random node's value equal to root value (often breaks strictness)
        nodes = []
        q = deque([root])
        while q:
            nd = q.popleft()
            nodes.append(nd)
            if nd.left:
                q.append(nd.left)
            if nd.right:
                q.append(nd.right)
        if len(nodes) >= 2:
            a, b = random.sample(nodes, 2)
            b.val = a.val
        return root

    if kind == "random_small":
        n = random.randint(1, 30)
        return build_random_shape(n, small_value)

    if kind == "random_big":
        n = random.randint(1, 80)
        return build_random_shape(n, random_value)

    if kind == "skewed_left":
        n = random.randint(1, 50)
        # decreasing values down left spine -> valid BST
        vals = sorted(distinct_sample(n, -10000, 10000), reverse=True)
        root = Node(vals[0])
        cur = root
        for v in vals[1:]:
            cur.left = Node(v)
            cur = cur.left
        return root

    if kind == "skewed_right":
        n = random.randint(1, 50)
        vals = sorted(distinct_sample(n, -10000, 10000))
        root = Node(vals[0])
        cur = root
        for v in vals[1:]:
            cur.right = Node(v)
            cur = cur.right
        return root

    # default
    n = random.randint(1, 40)
    return build_random_shape(n, small_value)


def main():
    cases = []

    # Hand-crafted edge cases first (deterministic) -------------------
    fixed = [
        "5 3 6 2 4 null 7",      # true  (example 1)
        "5 3 6 4 2 null 7",      # false (example 2)
        "2 1 3",                 # true  (now-your-turn)
        str(INT_MIN),            # single min
        str(INT_MAX),            # single max
        "0",                     # single zero
        "1 1",                   # left dup -> false (1 not < 1)
        "1 null 1",              # right dup -> false (1 not > 1)
        "2 1 2",                 # right equal -> false
        "2 2 3",                 # left equal -> false
        "10 5 15 null null 6 20",# 6 in right subtree of 10 but < 10 -> false
        "3 1 5 0 2 4 6",         # full small BST -> true
        f"{INT_MAX} {INT_MIN} null",  # min on left of max -> true
        "1 null 2 null 3 null 4",     # right skew increasing -> true
        "4 3 2 1",                    # left skew decreasing -> true
    ]
    seen = set()
    for s in fixed:
        if s in seen:
            continue
        seen.add(s)
        cases.append(s)

    kinds = [
        "single", "bst_balanced", "bst_insert", "bst_extremes",
        "bst_then_break", "bst_with_dup", "random_small", "random_big",
        "skewed_left", "skewed_right",
    ]

    target = 2000
    attempts = 0
    while len(cases) < target and attempts < target * 50:
        attempts += 1
        kind = random.choice(kinds)
        root = make_case(kind)
        if root is None:
            continue
        s = serialize(root)
        if s == "" or s in seen:
            continue
        seen.add(s)
        cases.append(s)

    # Trim to exactly target
    cases = cases[:target]

    # Build, evaluate, write -----------------------------------------
    def parse(serial):
        toks = serial.split()
        if not toks:
            return None
        it = iter(toks)
        root = Node(int(next(it)))
        q = deque([root])
        toks = list(it)
        i = 0
        while q and i < len(toks):
            node = q.popleft()
            # left
            if i < len(toks):
                t = toks[i]; i += 1
                if t != "null":
                    node.left = Node(int(t))
                    q.append(node.left)
            # right
            if i < len(toks):
                t = toks[i]; i += 1
                if t != "null":
                    node.right = Node(int(t))
                    q.append(node.right)
        return root

    with open(OUT, "w") as f:
        for s in cases:
            root = parse(s)
            res = is_valid_bst(root)
            obj = {"inputs": {"root": s}, "expected": "true" if res else "false"}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
