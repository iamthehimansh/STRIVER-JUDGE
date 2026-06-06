#!/usr/bin/env python3
"""
Generator for Striver problem: morris-inorder-traversal-
  signature: vector<int> getInorder(TreeNode* root)

Generates random binary trees within constraints:
  1 <= number of nodes <= 100
  -100 <= Node.val <= 100

Tree serialization (LeetCode-style level-order, judge-compatible):
  space-separated values, "null" for a missing child; null nodes get no children.
  e.g. "1 4 null 4 2"  (judge struct: TreeNode{int data;TreeNode*left,*right;})

Output (vector<int>): "[v1, v2, ...]"

Writes ONE json object per line to the generated-tests jsonl.
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/morris-inorder-traversal-.jsonl"
N_CASES = 2000
MINV, MAXV = -100, 100
MAX_NODES = 100

random.seed(20260606)


class Node:
    __slots__ = ("val", "left", "right")
    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def random_tree(num_nodes):
    """Build a random binary tree with exactly num_nodes nodes (>=1)."""
    root = Node(random.randint(MINV, MAXV))
    nodes = [root]
    count = 1
    while count < num_nodes:
        parent = random.choice(nodes)
        if parent.left is not None and parent.right is not None:
            nodes = [n for n in nodes if n.left is None or n.right is None]
            if not nodes:
                break
            parent = random.choice(nodes)
        child = Node(random.randint(MINV, MAXV))
        if parent.left is None and parent.right is None:
            if random.random() < 0.5:
                parent.left = child
            else:
                parent.right = child
        elif parent.left is None:
            parent.left = child
        else:
            parent.right = child
        nodes.append(child)
        count += 1
    return root


def serialize_levelorder(root):
    """LeetCode-style level-order: null for missing child, null nodes get no children.
    Trim trailing nulls."""
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


def inorder(root):
    """Standard iterative inorder (oracle; equivalent result to Morris inorder)."""
    res = []
    stack = []
    cur = root
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        res.append(cur.val)
        cur = cur.right
    return res


def fmt_int_array(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def make_tree_from_levelorder(tokens):
    if not tokens or tokens[0] == "null":
        return None
    it = iter(tokens)
    root = Node(int(next(it)))
    q = deque([root])
    while q:
        node = q.popleft()
        try:
            lt = next(it)
        except StopIteration:
            break
        if lt != "null":
            node.left = Node(int(lt))
            q.append(node.left)
        try:
            rt = next(it)
        except StopIteration:
            break
        if rt != "null":
            node.right = Node(int(rt))
            q.append(node.right)
    return root


def main():
    # ---- Hand-crafted edge cases ----
    edge_token_strs = [
        "0",                       # single node, val 0
        "100",                     # single node, max val
        "-100",                    # single node, min val
        "1 null 2 3",              # example 2
        "1 4 null 4 2",            # example 1
        "5 1 2 8 null 4 5 null 6", # nowYourTurn case
    ]
    edge_trees = []
    for s in edge_token_strs:
        edge_trees.append(make_tree_from_levelorder(s.split()))

    # left-skewed 100 nodes
    lroot = Node(random.randint(MINV, MAXV))
    c = lroot
    for _ in range(99):
        c.left = Node(random.randint(MINV, MAXV))
        c = c.left
    edge_trees.append(lroot)

    # right-skewed 100 nodes
    rroot = Node(random.randint(MINV, MAXV))
    c = rroot
    for _ in range(99):
        c.right = Node(random.randint(MINV, MAXV))
        c = c.right
    edge_trees.append(rroot)

    # complete tree 100 nodes
    comp_nodes = [Node(random.randint(MINV, MAXV)) for _ in range(100)]
    for i in range(100):
        li, ri = 2 * i + 1, 2 * i + 2
        if li < 100:
            comp_nodes[i].left = comp_nodes[li]
        if ri < 100:
            comp_nodes[i].right = comp_nodes[ri]
    edge_trees.append(comp_nodes[0])

    # all-same-value tree
    same_nodes = [Node(7) for _ in range(50)]
    for i in range(50):
        li, ri = 2 * i + 1, 2 * i + 2
        if li < 50:
            same_nodes[i].left = same_nodes[li]
        if ri < 50:
            same_nodes[i].right = same_nodes[ri]
    edge_trees.append(same_nodes[0])

    lines = []
    seen_edge = 0
    for root in edge_trees:
        ser = serialize_levelorder(root)
        exp = fmt_int_array(inorder(root))
        lines.append(json.dumps({"inputs": {"root": ser}, "expected": exp}))
        seen_edge += 1

    # ---- Random cases ----
    while len(lines) < N_CASES:
        r = random.random()
        if r < 0.15:
            n = random.randint(1, 5)
        elif r < 0.5:
            n = random.randint(1, 20)
        else:
            n = random.randint(1, 100)
        root = random_tree(n)
        ser = serialize_levelorder(root)
        exp = fmt_int_array(inorder(root))
        lines.append(json.dumps({"inputs": {"root": ser}, "expected": exp}))

    lines = lines[:N_CASES]
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} cases to {OUT}")
    print(f"(edge cases: {seen_edge})")


if __name__ == "__main__":
    main()
