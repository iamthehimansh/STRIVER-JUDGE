#!/usr/bin/env python3
"""
Generator + static test set for Striver problem:
  "Kth Smallest and Largest element in BST"
  (slug: kth-smallest-and-largest-element-in-bst)

starterCpp signature:
    vector<int> kLargesSmall(TreeNode* root, int k)
  -> params in signature order: "root" (TreeNode*), "k" (int)

Input serialization (must match the judge EXACTLY):
  TreeNode* : level-order, space-separated, "null" for a missing child,
              LeetCode-style (null nodes get no children), trailing nulls
              trimmed.  e.g. "3 1 4 null 2"
  k         : an int, formatted as a bare string e.g. "3"

Output:
  vector<int> = [kth_smallest, kth_largest], formatted like the examples
  e.g. "[1, 4]".  (Judge compares leniently, ignoring brackets/commas/ws.)

Reference oracle:
  In-order traversal of a BST yields sorted values.  For n nodes,
    kth smallest = sorted[k-1]
    kth largest  = sorted[n-k]
  (1-indexed, 1 <= k <= n).

Constraints (from problem):
  number of nodes n:  1 <= k <= n <= 1e4
  Node.val:           0 <= Node.val <= 1e5
We build VALID BSTs (in-order sorted, distinct values so the structure is a
proper BST) with modest sizes to keep the .jsonl small, plus edge cases:
  single node, k=1, k=n, min/max values, skewed trees, balanced trees.
"""

import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/kth-smallest-and-largest-element-in-bst.jsonl"

VAL_MIN = 0
VAL_MAX = 10**5

random.seed(20260606)


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


# ------------------------------------------------------------------
# Serialize a tree to LeetCode-style level-order with "null" markers,
# trimming trailing nulls. Exactly how the example input looks and how
# the judge deserializes.
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
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def inorder_vals(root):
    """Iterative in-order traversal -> sorted list of values for a BST."""
    res = []
    stack = []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        res.append(cur.val)
        cur = cur.right
    return res


# ------------------------------------------------------------------
# BST builders (all produce valid BSTs from DISTINCT sorted values)
# ------------------------------------------------------------------
def build_balanced_bst(vals):
    """Balanced BST from a sorted distinct list."""
    if not vals:
        return None
    mid = len(vals) // 2
    node = Node(vals[mid])
    node.left = build_balanced_bst(vals[:mid])
    node.right = build_balanced_bst(vals[mid + 1:])
    return node


def insert_bst(root, val):
    """Standard iterative BST insert; skips duplicates."""
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
            return root  # duplicate -> skip
    return root


def build_insert_bst(vals_in_random_order):
    root = None
    for v in vals_in_random_order:
        root = insert_bst(root, v)
    return root


def build_skewed_right(sorted_vals):
    root = Node(sorted_vals[0])
    cur = root
    for v in sorted_vals[1:]:
        cur.right = Node(v)
        cur = cur.right
    return root


def build_skewed_left(sorted_vals):
    # decreasing down left spine -> valid BST
    root = Node(sorted_vals[-1])
    cur = root
    for v in reversed(sorted_vals[:-1]):
        cur.left = Node(v)
        cur = cur.left
    return root


def distinct_sample(n, lo, hi):
    """n distinct ints in [lo, hi]."""
    span = hi - lo + 1
    if span >= n:
        return random.sample(range(lo, hi + 1), n)
    s = set()
    while len(s) < n:
        s.add(random.randint(lo, hi))
    return list(s)


def make_tree(kind, n):
    """Return root of a valid BST with exactly n distinct nodes."""
    # choose value range; keep distinct so BST is proper
    if kind == "extremes":
        # include 0 and 1e5 explicitly
        base = distinct_sample(max(n - 2, 0), VAL_MIN, VAL_MAX)
        vals = sorted(set(base) | {VAL_MIN, VAL_MAX})
        # adjust to exactly n if possible
        while len(vals) < n:
            c = random.randint(VAL_MIN, VAL_MAX)
            if c not in vals:
                vals.append(c)
        vals = sorted(vals)[:n]
    else:
        vals = sorted(distinct_sample(n, VAL_MIN, VAL_MAX))

    if kind in ("balanced", "extremes"):
        return build_balanced_bst(vals)
    if kind == "insert":
        order = vals[:]
        random.shuffle(order)
        return build_insert_bst(order)
    if kind == "skewed_right":
        return build_skewed_right(vals)
    if kind == "skewed_left":
        return build_skewed_left(vals)
    # default balanced
    return build_balanced_bst(vals)


def compute_expected(root, k):
    vals = inorder_vals(root)  # sorted ascending
    n = len(vals)
    assert 1 <= k <= n, f"k={k} n={n}"
    kth_smallest = vals[k - 1]
    kth_largest = vals[n - k]
    return f"[{kth_smallest}, {kth_largest}]"


def main():
    cases = []  # list of (serial, k)
    seen = set()

    def add(serial, k):
        if not serial:
            return
        key = (serial, k)
        if key in seen:
            return
        seen.add(key)
        cases.append((serial, k))

    # ---- Hand-crafted deterministic edge cases ----
    # example 1
    add("3 1 4 null 2", 1)
    add("3 1 4 null 2", 2)
    add("3 1 4 null 2", 3)
    add("3 1 4 null 2", 4)
    # example 2
    add("5 3 6 2 null null null 1", 3)
    # single node, k=1
    add("0", 1)
    add(str(VAL_MAX), 1)
    add("500", 1)
    # two nodes
    add("1 0", 1)
    add("1 0", 2)
    add("1 null 2", 1)
    add("1 null 2", 2)
    # balanced 7-node, all k
    seven = build_balanced_bst([1, 2, 3, 4, 5, 6, 7])
    s7 = serialize(seven)
    for k in range(1, 8):
        add(s7, k)

    # ---- Randomized cases ----
    kinds = ["balanced", "insert", "skewed_right", "skewed_left", "extremes"]
    target = 2000
    attempts = 0
    while len(cases) < target and attempts < target * 80:
        attempts += 1
        kind = random.choice(kinds)
        # bias toward small/medium trees so file stays modest; occasionally bigger
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 40)
        elif r < 0.85:
            n = random.randint(1, 200)
        else:
            n = random.randint(1, 1500)
        root = make_tree(kind, n)
        actual_n = len(inorder_vals(root))  # distinct may reduce n in insert path
        if actual_n < 1:
            continue
        # pick k within [1, actual_n]; include the extreme ks often
        kr = random.random()
        if kr < 0.2:
            k = 1
        elif kr < 0.4:
            k = actual_n
        else:
            k = random.randint(1, actual_n)
        serial = serialize(root)
        add(serial, k)

    cases = cases[:target]

    # ---- Write file ----
    n_written = 0
    with open(OUT, "w") as f:
        for serial, k in cases:
            root = parse(serial)
            expected = compute_expected(root, k)
            obj = {"inputs": {"root": serial, "k": str(k)}, "expected": expected}
            f.write(json.dumps(obj) + "\n")
            n_written += 1

    print(f"Wrote {n_written} cases to {OUT}")


def parse(serial):
    """Deserialize level-order serialization back into a tree (oracle round-trip)."""
    toks = serial.split()
    if not toks:
        return None
    root = Node(int(toks[0]))
    q = deque([root])
    i = 1
    while q and i < len(toks):
        node = q.popleft()
        if i < len(toks):
            t = toks[i]; i += 1
            if t != "null":
                node.left = Node(int(t))
                q.append(node.left)
        if i < len(toks):
            t = toks[i]; i += 1
            if t != "null":
                node.right = Node(int(t))
                q.append(node.right)
    return root


if __name__ == "__main__":
    main()
