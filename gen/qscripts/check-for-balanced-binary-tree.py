#!/usr/bin/env python3
"""
Test-case generator for Striver problem: check-for-balanced-binary-tree

starterCpp signature:  bool isBalanced(TreeNode *root)
  -> single param "root" of type TreeNode*

Input serialization (judge format): level-order, space-separated, "null" for
missing child, LeetCode-style (null nodes get no children).
Output: "Yes" if balanced else "No" (matches dataset examples).

Constraints:
  0 <= Number of Nodes <= 10^5
  1 <= Node.val <= 10^5

Reference (ground truth):
  strivers-a2z-ref/11. Binary Trees/2. Medium Problems/02. Balanced Binary Tree.cpp
  A tree is height-balanced iff for every node |h(left)-h(right)| <= 1 and both
  subtrees are balanced.
"""
import json
import random
import sys
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-for-balanced-binary-tree.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = 1, 100000
MAX_NODES = 100000  # 10^5

random.seed(20260606)


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


# ---------- reference oracle ----------
def is_balanced(root):
    """Iterative post-order to avoid recursion limits on skewed trees.
    Returns True/False. Height computed bottom-up; -1 sentinel = unbalanced."""
    # iterative post-order computing height, short-circuit on unbalanced
    stack = []
    last = None
    height = {}  # id(node)-> height; None handled as 0
    node = root
    # Standard iterative postorder
    cur = root
    unbalanced = [False]

    def h(n):
        return 0 if n is None else height.get(id(n), 0)

    while stack or cur is not None:
        if cur is not None:
            stack.append(cur)
            cur = cur.left
        else:
            peek = stack[-1]
            if peek.right is not None and last is not peek.right:
                cur = peek.right
            else:
                # process peek
                lh = h(peek.left)
                rh = h(peek.right)
                if abs(lh - rh) > 1:
                    return False
                height[id(peek)] = max(lh, rh) + 1
                last = stack.pop()
    return True


# ---------- tree builders ----------
def build_random_tree(n, force_balanced=None):
    """Build a random binary tree with exactly n nodes.
    If force_balanced is True -> complete-ish balanced; if False -> skewed-ish.
    Otherwise fully random shape."""
    if n == 0:
        return None
    root = Node(rand_val())
    if n == 1:
        return root
    # nodes that can still accept children
    open_slots = deque([root])
    placed = 1
    while placed < n and open_slots:
        # pick from front (BFS-ish) sometimes randomly to vary shape
        if force_balanced is True:
            parent = open_slots.popleft()
            # attach left then right
            parent.left = Node(rand_val())
            open_slots.append(parent.left)
            placed += 1
            if placed < n:
                parent.right = Node(rand_val())
                open_slots.append(parent.right)
                placed += 1
        elif force_balanced is False:
            # build a path (skewed) -> heavily unbalanced
            parent = open_slots.pop()  # always extend last
            if random.random() < 0.5:
                parent.left = Node(rand_val())
                open_slots.append(parent.left)
            else:
                parent.right = Node(rand_val())
                open_slots.append(parent.right)
            placed += 1
        else:
            # random shape
            idx = random.randrange(len(open_slots))
            # rotate to access random index efficiently for deque -> use list
            open_slots.rotate(-idx)
            parent = open_slots[0]
            open_slots.rotate(idx)
            attached = False
            if parent.left is None and (parent.right is not None or random.random() < 0.5):
                parent.left = Node(rand_val())
                open_slots.append(parent.left)
                placed += 1
                attached = True
            elif parent.right is None:
                parent.right = Node(rand_val())
                open_slots.append(parent.right)
                placed += 1
                attached = True
            else:
                attached = False
            # remove parent if both children filled
            if parent.left is not None and parent.right is not None:
                try:
                    open_slots.remove(parent)
                except ValueError:
                    pass
            if not attached:
                # avoid infinite loop: drop a node
                try:
                    open_slots.remove(parent)
                except ValueError:
                    pass
    return root


def build_skewed(n, direction):
    if n == 0:
        return None
    root = Node(rand_val())
    cur = root
    for _ in range(n - 1):
        nn = Node(rand_val())
        if direction == "left":
            cur.left = nn
        elif direction == "right":
            cur.right = nn
        else:
            if random.random() < 0.5:
                cur.left = nn
            else:
                cur.right = nn
        cur = nn
    return root


def build_perfect(depth):
    """Perfect binary tree of given depth (depth=0 -> single node)."""
    if depth < 0:
        return None
    root = Node(rand_val())
    if depth == 0:
        return root
    root.left = build_perfect(depth - 1)
    root.right = build_perfect(depth - 1)
    return root


# ---------- serialization (LeetCode level-order, trim trailing nulls) ----------
def serialize(root):
    # Empty tree -> "null" (NOT "") so the judge's batch driver (which skips
    # empty lines via `if (line.empty()) continue;`) does not drop the case and
    # shift all subsequent outputs. rdTree("null") deserializes to nullptr.
    if root is None:
        return "null"
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
        else:
            out.append(str(node.val))
            q.append(node.left)
            q.append(node.right)
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def make_case():
    r = random.random()
    if r < 0.05:
        # empty tree
        root = None
    elif r < 0.10:
        root = Node(rand_val())  # single node
    elif r < 0.30:
        # perfect / balanced
        depth = random.randint(1, 9)
        root = build_perfect(depth)
    elif r < 0.45:
        # left or right skewed (unbalanced for n>=3)
        n = random.randint(2, 60)
        root = build_skewed(n, random.choice(["left", "right", "mixed"]))
    elif r < 0.70:
        n = random.randint(1, 120)
        root = build_random_tree(n)
    elif r < 0.85:
        n = random.randint(1, 30)
        root = build_random_tree(n, force_balanced=True)
    else:
        n = random.randint(2, 40)
        root = build_random_tree(n, force_balanced=False)
    return root


def main():
    cases = []
    # deterministic edge cases first
    edge = []
    edge.append(None)                       # empty -> balanced -> Yes
    edge.append(Node(rand_val()))           # single -> Yes
    edge.append(build_perfect(0))           # single
    edge.append(build_perfect(1))           # 3 nodes balanced
    edge.append(build_skewed(3, "left"))    # unbalanced -> No
    edge.append(build_skewed(2, "left"))    # 2 nodes -> balanced (diff 1) -> Yes
    # example trees from dataset
    def from_level(tokens):
        toks = tokens.split()
        if not toks or toks[0] == "null":
            return None
        it = iter(toks)
        root = Node(int(next(it)))
        q = deque([root])
        toks_list = toks[1:]
        i = 0
        while q and i < len(toks_list):
            node = q.popleft()
            # left
            if i < len(toks_list):
                t = toks_list[i]; i += 1
                if t != "null":
                    node.left = Node(int(t)); q.append(node.left)
            if i < len(toks_list):
                t = toks_list[i]; i += 1
                if t != "null":
                    node.right = Node(int(t)); q.append(node.right)
        return root
    edge.append(from_level("3 9 20 null null 15 7"))  # Yes
    edge.append(from_level("1 2 null null 3"))         # No

    for root in edge:
        cases.append(root)
    while len(cases) < N_CASES:
        cases.append(make_case())

    lines = []
    for root in cases[:N_CASES]:
        inp = serialize(root)
        bal = is_balanced(root)
        expected = "Yes" if bal else "No"
        lines.append(json.dumps({"inputs": {"root": inp}, "expected": expected}))

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
