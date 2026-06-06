#!/usr/bin/env python3
"""
Generator for "Diameter of Binary Tree" (slug: diameter-of-binary-tree).

starterCpp signature:  int diameterOfBinaryTree(TreeNode* root)
  -> single input param "root" (TreeNode*), output int (number of edges in longest path).

TreeNode serialization (judge format): level-order, space-separated, "null" for
missing child, LeetCode-style (null nodes get no children). Trailing nulls trimmed.

Constraints:
  1 <= Number of Nodes <= 10^4
  -100 <= Node.val <= 100

Output one JSON object per line:
  {"inputs": {"root": "<level-order string>"}, "expected": "<int>"}
"""
import json
import random
import sys
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/diameter-of-binary-tree.jsonl"
N_CASES = 2000
MAX_NODES = 10000
VAL_LO, VAL_HI = -100, 100


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def random_tree(n):
    """Build a random binary tree with exactly n nodes (n>=1).

    Strategy: maintain a list of available 'slots' (parent, side). Start with
    the root; each new node attaches to a randomly chosen open slot, producing a
    variety of shapes (skewed, balanced, random)."""
    root = Node(random.randint(VAL_LO, VAL_HI))
    # open slots: list of (parent_node, 'left'/'right')
    slots = [(root, "left"), (root, "right")]
    for _ in range(n - 1):
        idx = random.randrange(len(slots))
        parent, side = slots.pop(idx)
        node = Node(random.randint(VAL_LO, VAL_HI))
        if side == "left":
            parent.left = node
        else:
            parent.right = node
        slots.append((node, "left"))
        slots.append((node, "right"))
    return root


def skewed_tree(n, side):
    """Fully left- or right-skewed tree of n nodes (diameter = n-1)."""
    root = Node(random.randint(VAL_LO, VAL_HI))
    cur = root
    for _ in range(n - 1):
        nd = Node(random.randint(VAL_LO, VAL_HI))
        if side == "left":
            cur.left = nd
        else:
            cur.right = nd
        cur = nd
    return root


def perfect_tree(depth):
    """Perfect binary tree of given depth (depth=0 -> single node)."""
    if depth < 0:
        return None
    root = Node(random.randint(VAL_LO, VAL_HI))
    if depth == 0:
        return root
    root.left = perfect_tree(depth - 1)
    root.right = perfect_tree(depth - 1)
    return root


def serialize_levelorder(root):
    """LeetCode-style level-order serialization with trailing nulls trimmed."""
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


def diameter(root):
    """Number of edges in the longest path between any two nodes.
    Matches the reference: at each node, diam = max(diam, left_h + right_h);
    return 1 + max(left_h, right_h)."""
    best = 0

    # iterative post-order to avoid recursion limits for skewed trees of 10^4
    # height map
    height = {}
    stack = [(root, False)]
    while stack:
        node, processed = stack.pop()
        if node is None:
            continue
        if processed:
            lh = height.get(id(node.left), 0) if node.left else 0
            rh = height.get(id(node.right), 0) if node.right else 0
            nonlocal_best = lh + rh
            if nonlocal_best > best:
                best = nonlocal_best
            height[id(node)] = 1 + max(lh, rh)
        else:
            stack.append((node, True))
            if node.left:
                stack.append((node.left, False))
            if node.right:
                stack.append((node.right, False))
    return best


def build_from_levelorder(s):
    """Parse a level-order string back into a tree (used for verifying examples)."""
    toks = s.split()
    if not toks:
        return None
    it = iter(toks)
    root = Node(int(next(it)))
    q = deque([root])
    tokens = list(it)
    i = 0
    while q and i < len(tokens):
        node = q.popleft()
        if i < len(tokens):
            t = tokens[i]; i += 1
            if t != "null":
                node.left = Node(int(t)); q.append(node.left)
        if i < len(tokens):
            t = tokens[i]; i += 1
            if t != "null":
                node.right = Node(int(t)); q.append(node.right)
    return root


def self_test():
    # Example 1: root = [1,2,3,4,5] -> 3
    r1 = build_from_levelorder("1 2 3 4 5")
    assert diameter(r1) == 3, diameter(r1)
    # Example 2: root = [1,2,3,null,4,null,5] -> 4
    r2 = build_from_levelorder("1 2 3 null 4 null 5")
    assert diameter(r2) == 4, diameter(r2)
    # single node -> 0
    assert diameter(build_from_levelorder("5")) == 0
    # [5,1,2,8,3,null,5,null,4] -> longest path 4-8-1-5-2-5 = 5 edges
    # (dataset's nowYourTurn quiz key marks "4" but the true diameter is 5)
    rn = build_from_levelorder("5 1 2 8 3 null 5 null 4")
    assert diameter(rn) == 5, diameter(rn)
    print("self-test passed", file=sys.stderr)


def gen_one(case_idx):
    """Return a Node root for one test case, mixing edge cases and random shapes."""
    # Edge cases first
    if case_idx == 0:
        return Node(random.randint(VAL_LO, VAL_HI))           # single node
    if case_idx == 1:
        return skewed_tree(2, "left")                          # 2 nodes left
    if case_idx == 2:
        return skewed_tree(2, "right")                         # 2 nodes right
    if case_idx == 3:
        return build_from_levelorder("1 2 3 4 5")             # example 1
    if case_idx == 4:
        return build_from_levelorder("1 2 3 null 4 null 5")   # example 2
    if case_idx == 5:
        return skewed_tree(MAX_NODES, "left")                 # max-size skewed
    if case_idx == 6:
        return skewed_tree(MAX_NODES, "right")
    if case_idx == 7:
        return perfect_tree(13)                               # 2^14-1 = 16383 > 10^4? trim
    if case_idx == 8:
        return random_tree(MAX_NODES)                         # max-size random

    r = random.random()
    if r < 0.20:
        n = random.randint(1, 10)            # small trees
    elif r < 0.40:
        n = random.randint(11, 200)
    elif r < 0.70:
        n = random.randint(200, 2000)
    elif r < 0.85:
        n = random.randint(2000, MAX_NODES)
    else:
        # skewed / perfect-ish shapes
        choice = random.random()
        if choice < 0.5:
            return skewed_tree(random.randint(1, MAX_NODES),
                               random.choice(["left", "right"]))
        else:
            d = random.randint(1, 12)        # perfect tree depth (<=8191 nodes)
            return perfect_tree(d)
    return random_tree(n)


def count_nodes(root):
    c = 0
    q = deque([root])
    while q:
        x = q.popleft()
        if x is None:
            continue
        c += 1
        if x.left:
            q.append(x.left)
        if x.right:
            q.append(x.right)
    return c


def main():
    self_test()
    random.seed(20240606)
    lines = []
    for i in range(N_CASES):
        root = gen_one(i)
        # Safety: enforce node-count constraint (perfect_tree(13) = 16383 > 10^4)
        nc = count_nodes(root)
        if nc > MAX_NODES:
            root = random_tree(MAX_NODES)
            nc = MAX_NODES
        assert 1 <= nc <= MAX_NODES, nc
        s = serialize_levelorder(root)
        assert s != "", "root must be non-empty (>=1 node)"
        d = diameter(root)
        lines.append(json.dumps({"inputs": {"root": s}, "expected": str(d)}))
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
