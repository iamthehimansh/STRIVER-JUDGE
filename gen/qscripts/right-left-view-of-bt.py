#!/usr/bin/env python3
"""
Generator for Striver problem: Right/Left View of Binary Tree (slug: right-left-view-of-bt)

Method signature (starterCpp):
    vector<int> rightSideView(TreeNode* root)

Input param: root (TreeNode*) -> serialized as level-order, space-separated, "null" for
missing children, LeetCode-style (null nodes get no children). e.g. "1 2 3 null 5 null 4".
The judge struct field is `data`.

Output: vector<int> -> formatted like the example output "[1, 3, 4]".

Constraints:
    1 <= Number of Nodes <= 10^4
    -10^3 <= Node.val <= 10^3
"""

import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/right-left-view-of-bt.jsonl"

VAL_MIN, VAL_MAX = -1000, 1000


class TreeNode:
    __slots__ = ("data", "left", "right")

    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


def build_random_tree(n, max_height=None):
    """Build a random binary tree with exactly n nodes (n >= 1).

    We grow the tree by repeatedly attaching a new node to a random available
    (left or right) slot of an existing node. This produces arbitrary shapes
    (skewed, balanced, sparse, etc.).

    `max_height` (if given) bounds the depth of any leaf, so the right-side-view
    output (which has one element per level == tree height) stays short. This is
    required because the judge caps total batch stdout at 1 MB; deep skewed trees
    would otherwise blow that budget. The tree shape is still fully valid and
    arbitrary within the height bound.
    """
    root = TreeNode(rand_val())
    # open_slots: list of (parent_node, side, depth) where side in {"L","R"}
    open_slots = [(root, "L", 1), (root, "R", 1)]
    created = 1
    while created < n and open_slots:
        idx = random.randrange(len(open_slots))
        parent, side, depth = open_slots.pop(idx)
        if max_height is not None and depth >= max_height:
            # cannot extend below this slot; skip it
            continue
        node = TreeNode(rand_val())
        if side == "L":
            parent.left = node
        else:
            parent.right = node
        open_slots.append((node, "L", depth + 1))
        open_slots.append((node, "R", depth + 1))
        created += 1
    return root


def build_complete_tree(n):
    """Build a complete-ish tree (array form, parent i -> children 2i+1, 2i+2)."""
    nodes = [TreeNode(rand_val()) for _ in range(n)]
    for i in range(n):
        li, ri = 2 * i + 1, 2 * i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]
    return nodes[0]


def build_left_skewed(n):
    root = TreeNode(rand_val())
    cur = root
    for _ in range(n - 1):
        cur.left = TreeNode(rand_val())
        cur = cur.left
    return root


def build_right_skewed(n):
    root = TreeNode(rand_val())
    cur = root
    for _ in range(n - 1):
        cur.right = TreeNode(rand_val())
        cur = cur.right
    return root


def serialize_tree(root):
    """LeetCode-style level-order serialization with trailing nulls trimmed.
    null nodes get no children (standard LeetCode encoding)."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
            continue
        out.append(str(node.data))
        q.append(node.left)
        q.append(node.right)
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def right_side_view(root):
    """Reference oracle: BFS, take last node of each level."""
    if root is None:
        return []
    ans = []
    q = deque([root])
    while q:
        sz = len(q)
        last = None
        for _ in range(sz):
            node = q.popleft()
            last = node.data
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        ans.append(last)
    return ans


def fmt_int_array(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def make_case(n, shape, max_height=None):
    if shape == "random":
        root = build_random_tree(n, max_height=max_height)
    elif shape == "complete":
        root = build_complete_tree(n)
    elif shape == "left":
        root = build_left_skewed(n)
    elif shape == "right":
        root = build_right_skewed(n)
    else:
        root = build_random_tree(n, max_height=max_height)
    inp = serialize_tree(root)
    out = right_side_view(root)
    return {"inputs": {"root": inp}, "expected": fmt_int_array(out)}


def main():
    random.seed(20260606)
    cases = []

    # ---- Edge / specific cases ----
    # single node (min size)
    cases.append(make_case(1, "complete"))
    # tiny skewed trees
    cases.append(make_case(2, "left"))
    cases.append(make_case(2, "right"))
    cases.append(make_case(3, "complete"))
    # extreme value single node
    sn = TreeNode(VAL_MIN)
    cases.append({"inputs": {"root": serialize_tree(sn)}, "expected": fmt_int_array([VAL_MIN])})
    sn2 = TreeNode(VAL_MAX)
    cases.append({"inputs": {"root": serialize_tree(sn2)}, "expected": fmt_int_array([VAL_MAX])})
    # dataset examples reproduced
    # root = [1, 2, 3, null, 5, null, 4] -> [1, 3, 4]
    # build from level-order array to verify serialization & oracle
    def build_from_levelorder(tokens):
        if not tokens or tokens[0] == "null":
            return None
        root = TreeNode(int(tokens[0]))
        q = deque([root])
        i = 1
        while q and i < len(tokens):
            node = q.popleft()
            if i < len(tokens):
                t = tokens[i]; i += 1
                if t != "null":
                    node.left = TreeNode(int(t)); q.append(node.left)
            if i < len(tokens):
                t = tokens[i]; i += 1
                if t != "null":
                    node.right = TreeNode(int(t)); q.append(node.right)
        return root

    for toks in (["1", "2", "3", "null", "5", "null", "4"],
                 ["1", "2", "3", "6", "5", "8", "4"]):
        r = build_from_levelorder(toks)
        cases.append({"inputs": {"root": serialize_tree(r)},
                      "expected": fmt_int_array(right_side_view(r))})

    # Largest skewed trees we allow (skewed height == node count, so the
    # right-side-view output has SKEW_CAP elements -- keep modest).
    SKEW_CAP = 120
    cases.append(make_case(SKEW_CAP, "left"))   # max allowed left skewed
    cases.append(make_case(SKEW_CAP, "right"))  # max allowed right skewed

    # Large structural extremes at the 10^4 node cap. These use LOW-HEIGHT
    # shapes (complete or height-bounded random) so the right-side-view output
    # stays short even though the tree is huge -- this exercises the max node
    # count constraint without exploding batch stdout.
    cases.append(make_case(10000, "complete"))               # max size, complete (height ~14)
    cases.append(make_case(10000, "random", max_height=40))  # max size, bushy random
    cases.append(make_case(5000, "complete"))
    cases.append(make_case(5000, "random", max_height=30))

    # ---- Bulk random cases ----
    # The judge caps TOTAL batch stdout at ~1 MB. The right-side-view output
    # length == tree height, so we keep heights bounded to stay well under it.
    OUTPUT_BUDGET = 800_000  # bytes of serialized output across all cases
    used = sum(len(c["expected"]) for c in cases)

    def add(case):
        nonlocal used
        cases.append(case)
        used += len(case["expected"])

    while len(cases) < 2000:
        remaining = 2000 - len(cases)
        # Reserve budget per remaining case so we never overrun.
        per_case_budget = max(50, (OUTPUT_BUDGET - used) // max(1, remaining))

        r = random.random()
        if r < 0.20:
            shape = random.choice(["left", "right"])
            # skewed: output length == node count; bound by per-case budget (~6 chars/val)
            cap = min(SKEW_CAP, max(1, per_case_budget // 6))
            n = random.randint(1, cap)
            add(make_case(n, shape))
        elif r < 0.40:
            # complete trees: height is log2(n); short output even when large
            n = random.randint(1, 10000)
            add(make_case(n, "complete"))
        else:
            # height-bounded random trees of varied sizes
            rr = random.random()
            if rr < 0.30:
                n = random.randint(1, 15)
                mh = None  # tiny trees: unbounded height is still short
            elif rr < 0.65:
                n = random.randint(1, 200)
                mh = random.randint(4, 25)
            elif rr < 0.90:
                n = random.randint(1, 2000)
                mh = random.randint(8, 30)
            else:
                n = random.randint(1, 10000)
                mh = random.randint(12, 35)
            add(make_case(n, "random", max_height=mh))

    cases = cases[:2000]

    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    total_out = sum(len(c["expected"]) for c in cases)
    maxline = max(len(c["expected"]) for c in cases)
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")
    print(f"total expected bytes ~{total_out}, max line ~{maxline}")


if __name__ == "__main__":
    main()
