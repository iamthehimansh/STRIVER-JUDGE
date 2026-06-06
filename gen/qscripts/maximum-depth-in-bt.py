#!/usr/bin/env python3
"""
Generator for "Maximum Depth in BT".

Builds random valid binary trees within constraints:
  1 <= Number of Nodes <= 10^4
  0 <= Node.val <= 10^4

Serializes the tree as the judge expects: LeetCode-style level-order,
space-separated, "null" for missing children, null nodes get NO children
(trailing nulls trimmed). Then computes maxDepth as the reference does:
  depth(root) = 0 if null else max(depth(left), depth(right)) + 1

Output: one JSON object per line:
  {"inputs": {"root": "1 2 3 null null null 6"}, "expected": "3"}
"""
import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/maximum-depth-in-bt.jsonl"
N_CASES = 2000
MAX_NODES_CAP = 10000   # constraint upper bound
VAL_MIN, VAL_MAX = 0, 10000


class Node:
    __slots__ = ("val", "left", "right")
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def rand_val(rng):
    return rng.randint(VAL_MIN, VAL_MAX)


def build_random_tree(rng, n):
    """Build a random binary tree with exactly n nodes (n >= 1)."""
    root = Node(rand_val(rng))
    nodes = [root]
    # candidate (node, side) open slots
    # We grow by repeatedly picking a random existing node that has a free slot.
    open_slots = [(root, "left"), (root, "right")]
    while len(nodes) < n:
        idx = rng.randrange(len(open_slots))
        parent, side = open_slots.pop(idx)
        child = Node(rand_val(rng))
        setattr(parent, side, child)
        nodes.append(child)
        open_slots.append((child, "left"))
        open_slots.append((child, "right"))
    return root


def build_skewed(rng, n, left=True):
    """Build a fully skewed tree of n nodes."""
    root = Node(rand_val(rng))
    cur = root
    for _ in range(n - 1):
        nxt = Node(rand_val(rng))
        if left:
            cur.left = nxt
        else:
            cur.right = nxt
        cur = nxt
    return root


def serialize_level_order(root):
    """LeetCode-style level-order serialization with 'null', null nodes get
    no children, trailing 'null's trimmed. Returns space-separated string."""
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
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def max_depth(root):
    # Iterative (BFS level count) to avoid Python recursion limit on deep
    # skewed trees. Equivalent to the reference recurrence:
    #   depth(null)=0; depth(n)=max(depth(l),depth(r))+1
    if root is None:
        return 0
    depth = 0
    q = deque([root])
    while q:
        depth += 1
        for _ in range(len(q)):
            node = q.popleft()
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return depth


def make_tree_for_case(rng, i):
    """Mix of edge cases and random trees."""
    if i == 0:
        # min size: single node
        return Node(rand_val(rng))
    if i == 1:
        # two nodes, left
        r = Node(rand_val(rng)); r.left = Node(rand_val(rng)); return r
    if i == 2:
        # two nodes, right
        r = Node(rand_val(rng)); r.right = Node(rand_val(rng)); return r
    if i == 3:
        # left-skewed deep
        return build_skewed(rng, rng.randint(50, 300), left=True)
    if i == 4:
        # right-skewed deep
        return build_skewed(rng, rng.randint(50, 300), left=False)
    if i == 5:
        # value extremes
        r = Node(VAL_MIN); r.left = Node(VAL_MAX); r.right = Node(VAL_MIN)
        r.left.left = Node(VAL_MAX); return r
    if i == 6:
        # near-max sized skewed (deep) but keep modest to bound string size
        return build_skewed(rng, 1000, left=rng.random() < 0.5)
    if i == 7:
        # large balanced-ish random
        return build_random_tree(rng, 2000)

    r = rng.random()
    if r < 0.15:
        n = 1
    elif r < 0.55:
        n = rng.randint(2, 50)
    elif r < 0.85:
        n = rng.randint(50, 500)
    else:
        n = rng.randint(500, 3000)
    if rng.random() < 0.08:
        return build_skewed(rng, n, left=rng.random() < 0.5)
    return build_random_tree(rng, n)


def main():
    rng = random.Random(20240606)
    lines = []
    for i in range(N_CASES):
        root = make_tree_for_case(rng, i)
        s = serialize_level_order(root)
        depth = max_depth(root)
        # sanity: node count within bound
        n_nodes = s.replace("null", " ").split()
        assert 1 <= len(n_nodes) <= MAX_NODES_CAP, f"node count out of bound: {len(n_nodes)}"
        obj = {"inputs": {"root": s}, "expected": str(depth)}
        lines.append(json.dumps(obj))
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
