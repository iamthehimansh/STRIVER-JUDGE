#!/usr/bin/env python3
"""
Generator for Striver problem: largest-bst-in-binary-tree (Largest BST in Binary Tree).

Given the root of a Binary Tree (arbitrary, NOT necessarily a BST), return the
size (number of nodes) of the largest subtree which is itself a valid BST.

starterCpp signature:
    int largestBST(TreeNode* root);
The judge's struct is `struct TreeNode { int data; TreeNode *left,*right; }`.

Input key (exactly, in signature order):
  - root : space-separated level-order serialization (LeetCode style) with "null"
           for absent children, e.g. "2 1 3" or "10 null 20 null 30 ...".

Output (expected): a bare integer string, e.g. "3".

Constraints enforced:
  - 1 <= Number of Nodes <= 10^4
  - 1 <= Node.val <= 10^5
We build arbitrary binary trees (random shapes), and many trees that ARE or
CONTAIN large BSTs, to exercise the algorithm.

Reference oracle: bottom-up post-order. For each node we return
(is_bst, size, min, max). A node forms a BST iff both children are BSTs and
left.max < node.data < right.min. We track the global max BST size.
This matches strivers-a2z-ref/.../12. Largest BST in Binary Tree.cpp.
Implemented iteratively to handle skewed trees of up to 10^4 nodes.
"""

import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/largest-bst-in-binary-tree.jsonl"
N_CASES = 2000
VAL_LO = 1            # 1 <= Node.val
VAL_HI = 10 ** 5      # Node.val <= 10^5
MAX_NODES = 10 ** 4   # 1 <= nodes <= 10^4


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


# ---------------------------------------------------------------------------
# Tree builders
# ---------------------------------------------------------------------------
def random_general_tree(n):
    """Random binary tree of exactly n nodes with arbitrary values in range.
    Build by attaching each new node to a random existing node with a free slot."""
    if n <= 0:
        return None
    root = Node(random.randint(VAL_LO, VAL_HI))
    nodes_with_free_slots = [root]
    count = 1
    while count < n:
        parent = random.choice(nodes_with_free_slots)
        nd = Node(random.randint(VAL_LO, VAL_HI))
        # which slots are free on parent?
        free = []
        if parent.left is None:
            free.append("L")
        if parent.right is None:
            free.append("R")
        slot = random.choice(free)
        if slot == "L":
            parent.left = nd
        else:
            parent.right = nd
        count += 1
        # update free-slot list
        if parent.left is not None and parent.right is not None:
            nodes_with_free_slots.remove(parent)
        nodes_with_free_slots.append(nd)
    return root


def build_bst(values):
    """Build a genuine BST by inserting values (duplicates go right)."""
    root = None
    for v in values:
        if root is None:
            root = Node(v)
            continue
        cur = root
        while True:
            if v < cur.val:
                if cur.left is None:
                    cur.left = Node(v)
                    break
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = Node(v)
                    break
                cur = cur.right
    return root


def skewed_tree(n, side):
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
    if depth < 0:
        return None
    root = Node(random.randint(VAL_LO, VAL_HI))
    if depth == 0:
        return root
    root.left = perfect_tree(depth - 1)
    root.right = perfect_tree(depth - 1)
    return root


def tree_with_bst_subtree():
    """A general tree where one subtree is a sizeable genuine BST, glued under a
    non-BST arrangement, to test that the largest BST subtree is found."""
    # genuine BST subtree
    k = random.randint(3, 200)
    vals = random.sample(range(VAL_LO, VAL_HI + 1), min(k, VAL_HI))
    bst = build_bst(vals)
    # wrap it: root with a messy left side and the BST on the right (or vice-versa)
    root = Node(random.randint(VAL_LO, VAL_HI))
    junk = random_general_tree(random.randint(0, 50))
    if random.random() < 0.5:
        root.left = junk
        root.right = bst
    else:
        root.left = bst
        root.right = junk
    return root


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------
def serialize_levelorder(root):
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
    toks = s.split()
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
                node.left = Node(int(t)); q.append(node.left)
        if i < len(toks):
            t = toks[i]; i += 1
            if t != "null":
                node.right = Node(int(t)); q.append(node.right)
    return root


# ---------------------------------------------------------------------------
# Oracle: size of largest BST subtree (iterative post-order)
# ---------------------------------------------------------------------------
NEG_INF = float("-inf")
POS_INF = float("inf")


def largest_bst(root):
    if root is None:
        return 0
    best = 0
    # info[id(node)] = (is_bst, size, min, max)
    info = {}
    stack = [(root, False)]
    while stack:
        node, processed = stack.pop()
        if node is None:
            continue
        if not processed:
            stack.append((node, True))
            if node.left is not None:
                stack.append((node.left, False))
            if node.right is not None:
                stack.append((node.right, False))
        else:
            if node.left is None:
                lis, lsz, lmin, lmax = True, 0, POS_INF, NEG_INF
            else:
                lis, lsz, lmin, lmax = info[id(node.left)]
            if node.right is None:
                ris, rsz, rmin, rmax = True, 0, POS_INF, NEG_INF
            else:
                ris, rsz, rmin, rmax = info[id(node.right)]

            if lis and ris and lmax < node.val < rmin:
                sz = lsz + rsz + 1
                cur_min = min(lmin, node.val)
                cur_max = max(rmax, node.val)
                info[id(node)] = (True, sz, cur_min, cur_max)
                if sz > best:
                    best = sz
            else:
                info[id(node)] = (False, 0, 0, 0)
            # free children info to keep memory bounded
            if node.left is not None:
                info.pop(id(node.left), None)
            if node.right is not None:
                info.pop(id(node.right), None)
    return best


# ---------------------------------------------------------------------------
# Case generation
# ---------------------------------------------------------------------------
def make_tree(i):
    r = random.random()
    if i == 0:
        return Node(random.randint(VAL_LO, VAL_HI))          # single node
    if i == 1:
        return Node(VAL_LO)                                   # min value, single
    if i == 2:
        n = Node(VAL_HI); n.left = Node(1); n.right = Node(VAL_HI)  # tiny
        return n
    if i == 3:
        return build_bst(random.sample(range(VAL_LO, VAL_HI + 1), 50))  # pure BST
    if r < 0.30:
        return random_general_tree(random.randint(1, 60))
    if r < 0.50:
        # genuine BST of random size (answer == node count)
        k = random.randint(1, 300)
        vals = random.sample(range(VAL_LO, VAL_HI + 1), min(k, VAL_HI))
        return build_bst(vals)
    if r < 0.68:
        return tree_with_bst_subtree()
    if r < 0.78:
        return skewed_tree(random.randint(1, 200), random.choice(["left", "right"]))
    if r < 0.86:
        return perfect_tree(random.randint(0, 6))
    if r < 0.93:
        # larger random general tree
        return random_general_tree(random.randint(60, 800))
    # occasional big tree near upper bound for stress
    return random_general_tree(random.randint(800, 3000))


def self_test():
    # Example 1: root = [2,1,3] -> 3
    t1 = build_from_levelorder("2 1 3")
    assert largest_bst(t1) == 3, largest_bst(t1)
    # Example 2: root = [10,null,20,null,30,null,40,null,50] -> 5
    t2 = build_from_levelorder("10 null 20 null 30 null 40 null 50")
    assert largest_bst(t2) == 5, largest_bst(t2)
    # root = [3,1,4,null,null,2]: tree 3(L=1, R=4(L=2)); root 3 not BST since
    # right.min=2 < 3 fails 3<2; largest BST is subtree {4,2} -> size 2.
    t3 = build_from_levelorder("3 1 4 null null 2")
    assert largest_bst(t3) == 2, largest_bst(t3)
    # round-trip serialize check
    assert serialize_levelorder(t1) == "2 1 3"
    print("self_test OK")


def main():
    random.seed(98)
    self_test()
    seen = set()
    lines = []
    i = 0
    attempts = 0
    while len(lines) < N_CASES and attempts < N_CASES * 6:
        attempts += 1
        root = make_tree(i)
        i += 1
        ser = serialize_levelorder(root)
        if not ser:
            continue
        # cap node count safely within constraints (<= 10^4)
        ncount = len([t for t in ser.split() if t != "null"])
        if ncount > MAX_NODES:
            continue
        if ser in seen:
            continue
        seen.add(ser)
        ans = largest_bst(root)
        lines.append(json.dumps({"inputs": {"root": ser}, "expected": str(ans)}))

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
