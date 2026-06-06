#!/usr/bin/env python3
"""
Generator for the Striver problem "Preorder Traversal".

Signature: vector<int> preorder(TreeNode* root)
Input key : "s"  -> level-order, space-separated tree string, LeetCode style
            ("null" for missing child; null nodes get no children).
Output    : preorder traversal as "[a, b, c]".

Constraints:
  1 <= Number of Nodes <= 100
  -100 <= Node.val <= 100

We build the tree EXACTLY the way the judge does (BFS level-order, null nodes
have no children), then compute the preorder traversal as the ground truth.
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/preorder-traversal.jsonl"
N_CASES = 2000
VMIN, VMAX = -100, 100
MAX_NODES = 100


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_from_level(tokens):
    """Build a tree from a LeetCode-style level-order token list.
    tokens[0] is the root (never 'null' here). Returns root Node.
    This mirrors the judge's deserialization."""
    if not tokens or tokens[0] == "null":
        return None
    root = Node(int(tokens[0]))
    q = deque([root])
    i = 1
    n = len(tokens)
    while q and i < n:
        node = q.popleft()
        # left child
        if i < n:
            t = tokens[i]
            i += 1
            if t != "null":
                node.left = Node(int(t))
                q.append(node.left)
        # right child
        if i < n:
            t = tokens[i]
            i += 1
            if t != "null":
                node.right = Node(int(t))
                q.append(node.right)
    return root


def preorder(root):
    out = []
    stack = [root]
    # iterative preorder
    st = []
    cur = root
    while cur or st:
        while cur:
            out.append(cur.val)
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        cur = cur.right
    return out


def random_tree(n):
    """Build a random binary tree with exactly n nodes, return root.
    We grow by attaching each new node to a random available (free) slot."""
    root = Node(random.randint(VMIN, VMAX))
    # list of (node, side) free attachment points
    free = [(root, "L"), (root, "R")]
    for _ in range(n - 1):
        idx = random.randrange(len(free))
        parent, side = free.pop(idx)
        child = Node(random.randint(VMIN, VMAX))
        if side == "L":
            parent.left = child
        else:
            parent.right = child
        free.append((child, "L"))
        free.append((child, "R"))
    return root


def serialize_level_order(root):
    """Serialize tree to LeetCode-style level-order tokens, trimming trailing
    nulls. Matches the judge's input format ('s')."""
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


def make_case(n):
    root = random_tree(n)
    s = serialize_level_order(root)
    # Re-build from the serialized string the SAME way the judge does, to
    # guarantee self-consistency, then compute preorder.
    rebuilt = build_from_level(s.split())
    pre = preorder(rebuilt)
    expected = "[" + ", ".join(str(x) for x in pre) + "]"
    return {"inputs": {"s": s}, "expected": expected}


def main():
    random.seed(1337)
    cases = []
    # Edge cases first
    # single node, extremes
    cases.append({"inputs": {"s": "1"}, "expected": "[1]"})
    cases.append({"inputs": {"s": "0"}, "expected": "[0]"})
    cases.append({"inputs": {"s": "-100"}, "expected": "[-100]"})
    cases.append({"inputs": {"s": "100"}, "expected": "[100]"})
    cases.append({"inputs": {"s": "1 4 null 4 2"}, "expected": "[1, 4, 4, 2]"})
    # left-skewed chain of 100 nodes
    chain_vals = [random.randint(VMIN, VMAX) for _ in range(MAX_NODES)]
    # build left chain manually
    root = Node(chain_vals[0])
    cur = root
    for v in chain_vals[1:]:
        cur.left = Node(v)
        cur = cur.left
    cases.append({"inputs": {"s": serialize_level_order(root)},
                  "expected": "[" + ", ".join(str(x) for x in preorder(root)) + "]"})
    # right-skewed chain of 100 nodes
    root = Node(chain_vals[0])
    cur = root
    for v in chain_vals[1:]:
        cur.right = Node(v)
        cur = cur.right
    cases.append({"inputs": {"s": serialize_level_order(root)},
                  "expected": "[" + ", ".join(str(x) for x in preorder(root)) + "]"})
    # full tree of 100 nodes (random shape)
    cases.append(make_case(MAX_NODES))

    # Fill the rest with random sizes. The live judge caps captured stdout at
    # 256 KB total across ALL batched cases, so we bias toward SMALL trees
    # (keeping total preorder output comfortably under the cap) while still
    # mixing in occasional larger trees for coverage. A handful of explicit
    # large edge cases (above) guarantee the big-tree path is exercised.
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.80:
            n = random.randint(1, 20)      # mostly small
        elif r < 0.95:
            n = random.randint(21, 45)     # medium
        else:
            n = random.randint(46, MAX_NODES)  # occasional large
        cases.append(make_case(n))

    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("wrote", len(cases), "cases to", OUT)


if __name__ == "__main__":
    main()
