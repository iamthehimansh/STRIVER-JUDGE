#!/usr/bin/env python3
"""
Generator for "Maximum path sum" (slug: maximum-path-sum-).

starterCpp signature:  int maxPathSum(TreeNode* root)
  -> single input param "root" (TreeNode*), output int (largest path sum of any
     non-empty path; the path need not pass through the root).

TreeNode serialization (judge format): level-order, space-separated, "null" for
missing child, LeetCode-style (null nodes get no children). Trailing nulls trimmed.
The judge's struct field is `data` (not val), built via level-order.

Constraints:
  1 <= Number of Nodes <= 3*10^4
  -10^3 <= Node.val <= 10^3

Reference algorithm (from strivers-a2z-ref):
  solve(node): lh = max(0, solve(left)); rh = max(0, solve(right));
               best = max(best, node.val + lh + rh);
               return node.val + max(lh, rh)
  answer = best (initialized to -INF)

Output one JSON object per line:
  {"inputs": {"root": "<level-order string>"}, "expected": "<int>"}
"""
import json
import random
import sys
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/maximum-path-sum-.jsonl"
N_CASES = 2000
MAX_NODES = 30000          # 3*10^4
VAL_LO, VAL_HI = -1000, 1000   # -10^3 .. 10^3


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def random_tree(n, lo=VAL_LO, hi=VAL_HI):
    """Build a random binary tree with exactly n nodes (n>=1) via open-slot attach."""
    root = Node(random.randint(lo, hi))
    slots = [(root, "left"), (root, "right")]
    for _ in range(n - 1):
        idx = random.randrange(len(slots))
        parent, side = slots.pop(idx)
        node = Node(random.randint(lo, hi))
        if side == "left":
            parent.left = node
        else:
            parent.right = node
        slots.append((node, "left"))
        slots.append((node, "right"))
    return root


def skewed_tree(n, side, lo=VAL_LO, hi=VAL_HI):
    """Fully left- or right-skewed tree of n nodes."""
    root = Node(random.randint(lo, hi))
    cur = root
    for _ in range(n - 1):
        nd = Node(random.randint(lo, hi))
        if side == "left":
            cur.left = nd
        else:
            cur.right = nd
        cur = nd
    return root


def perfect_tree(depth, lo=VAL_LO, hi=VAL_HI):
    """Perfect binary tree of given depth (depth=0 -> single node)."""
    if depth < 0:
        return None
    root = Node(random.randint(lo, hi))
    if depth == 0:
        return root
    root.left = perfect_tree(depth - 1, lo, hi)
    root.right = perfect_tree(depth - 1, lo, hi)
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
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


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
    return node if False else root


def max_path_sum(root):
    """Iterative post-order computation mirroring the reference recursion.

    For each node:
      lh = max(0, gain(left)); rh = max(0, gain(right))
      best = max(best, val + lh + rh)
      gain(node) = val + max(lh, rh)
    """
    best = -10**18
    gain = {}          # id(node) -> downward gain (val + max(0,lh), max(0,rh))
    stack = [(root, False)]
    while stack:
        node, processed = stack.pop()
        if node is None:
            continue
        if processed:
            lh = max(0, gain.get(id(node.left), 0)) if node.left else 0
            rh = max(0, gain.get(id(node.right), 0)) if node.right else 0
            cur = node.val + lh + rh
            if cur > best:
                best = cur
            gain[id(node)] = node.val + max(lh, rh)
        else:
            stack.append((node, True))
            if node.left:
                stack.append((node.left, False))
            if node.right:
                stack.append((node.right, False))
    return best


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


def self_test():
    # Example 1: [20,9,-10,null,null,15,7] -> 34 (15 -> -10 -> 20 -> 9)
    assert max_path_sum(build_from_levelorder("20 9 -10 null null 15 7")) == 34
    # Example 2: [-10,9,20,null,null,15,7] -> 42 (15 -> 20 -> 7)
    assert max_path_sum(build_from_levelorder("-10 9 20 null null 15 7")) == 42
    # single node, negative
    assert max_path_sum(build_from_levelorder("-3")) == -3
    # single node, positive
    assert max_path_sum(build_from_levelorder("7")) == 7
    # all negative: best single node
    assert max_path_sum(build_from_levelorder("-2 -1 -3")) == -1
    # dataset Case 3: [1,2,-3,-4,null,5,8]
    #   node5=5, node8=8, node-3: -3 + max(0,5)+max(0,8)=10; node2: 2 + max(0,-4)+0 = 2
    #   node1: 1 + max(0,2gain) + max(0,-3gain) ; 2gain=2, -3gain = -3+8=5
    #     root path = 1 + 2 + 5 = 8 ; but node-3 split = 10 is larger
    assert max_path_sum(build_from_levelorder("1 2 -3 -4 null 5 8")) == 10, \
        max_path_sum(build_from_levelorder("1 2 -3 -4 null 5 8"))
    print("self-test passed", file=sys.stderr)


def gen_one(case_idx):
    """Return a Node root for one test case, mixing edge cases and random shapes."""
    if case_idx == 0:
        return Node(random.randint(VAL_LO, VAL_HI))                 # single node
    if case_idx == 1:
        return Node(VAL_LO)                                          # single min
    if case_idx == 2:
        return Node(VAL_HI)                                          # single max
    if case_idx == 3:
        return build_from_levelorder("20 9 -10 null null 15 7")     # example 1
    if case_idx == 4:
        return build_from_levelorder("-10 9 20 null null 15 7")     # example 2
    if case_idx == 5:
        return skewed_tree(MAX_NODES, "left", VAL_HI, VAL_HI)       # max-size, all max
    if case_idx == 6:
        return skewed_tree(MAX_NODES, "right", VAL_LO, VAL_LO)      # max-size, all min
    if case_idx == 7:
        return random_tree(MAX_NODES)                               # max-size random
    if case_idx == 8:
        return random_tree(MAX_NODES, VAL_LO, -1)                   # all negative big
    if case_idx == 9:
        return perfect_tree(14)                                     # 2^15-1=32767>30000 -> trimmed below

    r = random.random()
    if r < 0.25:
        n = random.randint(1, 10)
    elif r < 0.45:
        n = random.randint(11, 200)
    elif r < 0.70:
        n = random.randint(200, 3000)
    elif r < 0.85:
        n = random.randint(3000, MAX_NODES)
    else:
        choice = random.random()
        if choice < 0.5:
            return skewed_tree(random.randint(1, MAX_NODES),
                               random.choice(["left", "right"]))
        else:
            d = random.randint(1, 14)        # perfect tree depth (2^15-1 capped below)
            return perfect_tree(d)
    # occasionally bias value ranges to all-negative or all-positive
    rr = random.random()
    if rr < 0.15:
        return random_tree(n, VAL_LO, -1)
    if rr < 0.30:
        return random_tree(n, 1, VAL_HI)
    return random_tree(n)


def main():
    self_test()
    random.seed(20240606)
    lines = []
    for i in range(N_CASES):
        root = gen_one(i)
        nc = count_nodes(root)
        if nc > MAX_NODES:
            root = random_tree(MAX_NODES)
            nc = MAX_NODES
        assert 1 <= nc <= MAX_NODES, nc
        s = serialize_levelorder(root)
        assert s != "", "root must be non-empty (>=1 node)"
        ans = max_path_sum(root)
        lines.append(json.dumps({"inputs": {"root": s}, "expected": str(ans)}))
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
