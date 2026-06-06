#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Pre, Post, Inorder in one traversal"
slug: pre,-post,-inorder-in-one-traversal

Method signature (starterCpp):
    vector<vector<int>> treeTraversal(TreeNode* root)

Return: [ inorder, preorder, postorder ]  (3 vectors, in that order)

Constraints:
    1 <= Number of Nodes <= 1e5
    0 <= Node.val <= 1e5

Input serialization (matches judge rdTree):
    level-order, space-separated, "null" for a missing child (LeetCode-style;
    null nodes get no children). Trailing nulls trimmed.

Output serialization (matches judge pr(vector<vector<int>>) flattened to one
line by the batch driver):
    inorder values, then preorder values, then postorder values, all
    space-separated on one line.

Writes ONE json object per line to the generated-tests path.
"""

import json
import random
import sys
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/pre,-post,-inorder-in-one-traversal.jsonl"

MAX_VAL = 10 ** 5  # 0 <= Node.val <= 1e5


# ---------------------------------------------------------------------------
# Tree representation: a node is (val, left, right); None = absent.
# ---------------------------------------------------------------------------
class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def rand_val(hi=MAX_VAL):
    return random.randint(0, hi)


# Current value cap used by builders (lets us shrink output bytes by using
# smaller values for the bulk of cases; edge cases still use the full range).
_VAL_HI = MAX_VAL


def rv():
    return random.randint(0, _VAL_HI)


def build_random_tree(n):
    """Build a random binary tree with exactly n nodes (n >= 1)."""
    root = Node(rv())
    # frontier holds nodes that still have at least one free child slot,
    # tracked as (node, which_slots_free).
    # We attach the remaining n-1 nodes to random available slots.
    # available_slots: list of (parent_node, side) where side in (0=left,1=right)
    available = [(root, 0), (root, 1)]
    count = 1
    while count < n:
        # pick a random free slot
        idx = random.randrange(len(available))
        parent, side = available[idx]
        # remove that slot (swap-pop for O(1))
        available[idx] = available[-1]
        available.pop()
        child = Node(rv())
        if side == 0:
            parent.left = child
        else:
            parent.right = child
        available.append((child, 0))
        available.append((child, 1))
        count += 1
    return root


def build_skewed_tree(n, left=True):
    """Fully left- or right-skewed tree of n nodes."""
    root = Node(rv())
    cur = root
    for _ in range(n - 1):
        nxt = Node(rv())
        if left:
            cur.left = nxt
        else:
            cur.right = nxt
        cur = nxt
    return root


def build_complete_tree(n):
    """Complete binary tree of n nodes (level order fill)."""
    nodes = [Node(rv()) for _ in range(n)]
    for i in range(n):
        li = 2 * i + 1
        ri = 2 * i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]
    return nodes[0]


# ---------------------------------------------------------------------------
# Serialization of input: LeetCode-style level order, trailing nulls trimmed.
# ---------------------------------------------------------------------------
def serialize_tree(root):
    if root is None:
        return ""  # not used (n >= 1), but be safe
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
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


# ---------------------------------------------------------------------------
# Reference: iterative single-pass traversal (Striver's approach) producing
# inorder, preorder, postorder. We use an explicit iterative method to avoid
# Python recursion-limit issues on large/skewed trees (n up to 1e5).
# ---------------------------------------------------------------------------
def traversals(root):
    inorder = []
    preorder = []
    postorder = []
    if root is None:
        return inorder, preorder, postorder
    # stack of (node, state): 1->pre, 2->in, 3->post
    stack = [(root, 1)]
    while stack:
        node, state = stack.pop()
        if state == 1:
            preorder.append(node.val)
            stack.append((node, 2))
            if node.left is not None:
                stack.append((node.left, 1))
        elif state == 2:
            inorder.append(node.val)
            stack.append((node, 3))
            if node.right is not None:
                stack.append((node.right, 1))
        else:  # state == 3
            postorder.append(node.val)
    return inorder, preorder, postorder


def expected_string(root):
    ino, pre, post = traversals(root)
    flat = ino + pre + post
    return " ".join(str(x) for x in flat)


# ---------------------------------------------------------------------------
# Case generation
# ---------------------------------------------------------------------------
def make_case(root):
    return {
        "inputs": {"root": serialize_tree(root)},
        "expected": expected_string(root),
    }


# The live judge runs ALL cases in ONE batched process and caps that process's
# TOTAL stdout at 256 KB (scripts/judge_exec.py: OUT_CAP = 256*1024). Each case
# emits one output line = the 3 traversals = 3*nodes integers. If cumulative
# output exceeds 256 KB, later cases are truncated and (wrongly) fail. So we
# enforce a hard total-output-byte budget here and keep trees small.
OUT_BUDGET = 210 * 1024  # stay safely under the 256 KB judge cap


def set_val_hi(hi):
    global _VAL_HI
    _VAL_HI = hi


def gen_cases(n_cases):
    global _VAL_HI
    cases = []
    budget = OUT_BUDGET

    def add(root):
        # account for one output line + newline against the byte budget
        c = make_case(root)
        nonlocal budget
        budget -= len(c["expected"]) + 1
        cases.append(c)
        return c

    # --- Required edge / known cases first (full value range) ---
    set_val_hi(MAX_VAL)
    add(deserialize("1 3 4 5 2 7 6"))          # dataset example 1
    add(deserialize("1 2 3 null null null 6"))  # dataset example 2
    add(deserialize("5 1 2 8 null 4 5 null 6")) # nowYourTurn
    add(Node(0))                                 # single node, min value
    add(Node(MAX_VAL))                           # single node, max value
    add(Node(rv()))                              # single node, random

    # small skewed trees (left / right), sizes 2..8 — exercise depth/order
    for sz in range(2, 9):
        add(build_skewed_tree(sz, left=True))
        add(build_skewed_tree(sz, left=False))

    # small complete trees, sizes 2..20
    for sz in range(2, 21):
        add(build_complete_tree(sz))

    # a few moderately larger structural edge cases — use SMALL node values so
    # they stay cheap in output bytes while still exercising structure/depth.
    set_val_hi(99)
    add(build_complete_tree(120))
    add(build_skewed_tree(120, left=True))
    add(build_skewed_tree(120, left=False))
    add(build_random_tree(150))
    set_val_hi(MAX_VAL)

    # --- Random fill up to n_cases, respecting the byte budget ---
    # Average ~6 nodes/case keeps 2000 cases well under 210 KB. We bias to small
    # trees but include variety; values mostly small to conserve bytes, with a
    # fraction using the full 0..1e5 range to exercise large values.
    while len(cases) < n_cases:
        remaining = n_cases - len(cases)
        # estimate affordable bytes/case for the rest; if tight, force tiny trees
        per = budget / max(1, remaining)
        # choose value magnitude: 30% full range, else small (fewer bytes)
        set_val_hi(MAX_VAL if random.random() < 0.30 else random.randint(9, 999))

        if per < 40:
            n = random.randint(1, 3)
            root = build_random_tree(n)
        else:
            roll = random.random()
            if roll < 0.55:
                n = random.randint(1, 12)
                root = build_random_tree(n)
            elif roll < 0.78:
                n = random.randint(1, 8)
                root = build_complete_tree(n)
            elif roll < 0.93:
                n = random.randint(1, 10)
                root = build_skewed_tree(n, left=random.random() < 0.5)
            else:
                n = random.randint(12, 25)
                root = build_random_tree(n)
        add(root)

    set_val_hi(MAX_VAL)
    return cases[:n_cases]


# ---------------------------------------------------------------------------
# deserialize (same as judge rdTree) — used only for the fixed example cases
# so we feed exactly the dataset's structure.
# ---------------------------------------------------------------------------
def deserialize(s):
    toks = s.replace(",", " ").split()
    if not toks or toks[0] in ("null", "N"):
        return None
    root = Node(int(toks[0]))
    q = deque([root])
    i = 1
    while q and i < len(toks):
        node = q.popleft()
        if i < len(toks):
            t = toks[i]
            i += 1
            if t not in ("null", "N"):
                node.left = Node(int(t))
                q.append(node.left)
        if i < len(toks):
            t = toks[i]
            i += 1
            if t not in ("null", "N"):
                node.right = Node(int(t))
                q.append(node.right)
    return root


def main():
    n_cases = 2000
    if len(sys.argv) > 1:
        n_cases = int(sys.argv[1])
    random.seed(20260606)
    cases = gen_cases(n_cases)
    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
