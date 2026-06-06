#!/usr/bin/env python3
"""
Test-case generator for Striver problem: floor-and-ceil-in-a-bst-1
"Floor in a Binary Search Tree" (here: floor AND ceil).

Signature: vector<int> floorCeilOfBST(TreeNode* root, int key)
Output: [floor, ceil] where
  floor = greatest node value <= key  (-1 if none)
  ceil  = smallest node value >= key  (-1 if none)

Constraints:
  1 <= Number of Nodes <= 5000
  1 <= Node.val <= 1e7
  1 <= key <= 1e7

The judge builds the tree level-order from a space-separated string using the
TreeNode{.data} struct, LeetCode-style (null = missing child). So we build a
VALID BST in memory, then serialize it level-order (trailing nulls trimmed)
exactly the way the judge's pr(TreeNode*) would, so a correct submission
reproduces our "expected".

Output line format:
  {"inputs": {"root": "<level-order>", "key": "<int>"}, "expected": "[floor, ceil]"}

Key order = signature order = root, key.
"""
import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/floor-and-ceil-in-a-bst-1.jsonl"
N_CASES = 2000
MAXV = 10_000_000  # 1e7
MAX_NODES = 5000


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def bst_insert(root, val):
    """Insert into BST; ignore duplicates (keep distinct values)."""
    if root is None:
        return Node(val), True
    cur = root
    while True:
        if val == cur.val:
            return root, False  # duplicate, skip
        if val < cur.val:
            if cur.left is None:
                cur.left = Node(val)
                return root, True
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = Node(val)
                return root, True
            cur = cur.right


def build_bst(values):
    root = None
    for v in values:
        root, _ = bst_insert(root, v)
    return root


def serialize_levelorder(root):
    """LeetCode-style level-order, 'null' for missing children, trailing nulls trimmed.
    Matches judge's pr(TreeNode*) exactly (space separated)."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is not None:
            out.append(str(n.val))
            q.append(n.left)
            q.append(n.right)
        else:
            out.append("null")
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def floor_ceil(root, key):
    """Iterative BST floor/ceil. floor = greatest <= key, ceil = smallest >= key."""
    floor = -1
    ceil = -1
    cur = root
    while cur:
        if cur.val == key:
            return [key, key]
        if cur.val < key:
            floor = cur.val
            cur = cur.right
        else:  # cur.val > key
            ceil = cur.val
            cur = cur.left
    return [floor, ceil]


def gen_values(n, lo=1, hi=MAXV):
    """n distinct values in [lo, hi]."""
    if hi - lo + 1 <= n:
        # full range small -> sample without replacement from whole range
        return random.sample(range(lo, hi + 1), n)
    s = set()
    while len(s) < n:
        s.add(random.randint(lo, hi))
    return list(s)


def make_case():
    """Return (root_str, key_int)."""
    mode = random.random()
    # node count distribution: lots of small + some large
    r = random.random()
    if r < 0.15:
        n = random.randint(1, 3)
    elif r < 0.6:
        n = random.randint(1, 30)
    elif r < 0.9:
        n = random.randint(1, 300)
    else:
        n = random.randint(1, MAX_NODES)

    if mode < 0.2:
        # small value range to force many duplicate keys / boundaries
        hi = max(2, min(MAXV, n * 3 + random.randint(0, 20)))
        vals = gen_values(n, 1, hi)
    elif mode < 0.35:
        # values clustered in a band
        base = random.randint(1, MAXV - 1)
        span = random.randint(1, MAXV - base)
        hi = min(MAXV, base + span)
        lo = base
        # ensure enough distinct slots
        if hi - lo + 1 < n:
            lo = 1
            hi = MAXV
        vals = gen_values(n, lo, hi)
    else:
        vals = gen_values(n, 1, MAXV)

    random.shuffle(vals)  # random insertion order -> varied tree shapes
    root = build_bst(vals)
    root_str = serialize_levelorder(root)

    # key selection: bias toward existing values & boundaries
    kr = random.random()
    if kr < 0.3 and vals:
        key = random.choice(vals)  # exact hit
    elif kr < 0.45:
        key = 1  # min boundary
    elif kr < 0.6:
        key = MAXV  # max boundary
    elif kr < 0.75 and vals:
        # just below or above an existing value
        v = random.choice(vals)
        key = max(1, min(MAXV, v + random.choice([-1, 1])))
    else:
        key = random.randint(1, MAXV)
    return root, root_str, key


def main():
    random.seed(20260606)
    lines = []
    seen = set()

    # --- explicit edge cases first ---
    edge = []
    # dataset examples
    edge.append(([8, 4, 12, 2, 6, 10, 14], 11))
    edge.append(([8, 4, 12, 2, 6, 10, 14], 15))
    # single node
    edge.append(([5], 5))
    edge.append(([5], 3))
    edge.append(([5], 7))
    edge.append(([1], 1))
    edge.append(([MAXV], MAXV))
    edge.append(([1], MAXV))
    edge.append(([MAXV], 1))
    # two nodes
    edge.append(([2, 1], 1))
    edge.append(([2, 1], 2))
    edge.append(([1, None, 2] if False else [1], 1))  # placeholder, replaced below
    # left-skewed and right-skewed via insertion order
    edge.append((list(range(1, 11)), 5))          # right skew 1..10
    edge.append((list(range(10, 0, -1)), 5))       # left skew 10..1
    # key below all / above all
    edge.append(([100, 50, 150], 1))
    edge.append(([100, 50, 150], MAXV))
    edge.append(([100, 50, 150], 100))

    for vals, key in edge:
        vals = [v for v in vals if v is not None]
        root = build_bst(vals)
        rs = serialize_levelorder(root)
        exp = floor_ceil(root, key)
        sig = (rs, key)
        if sig in seen:
            continue
        seen.add(sig)
        lines.append({"inputs": {"root": rs, "key": str(key)},
                      "expected": "[{}, {}]".format(exp[0], exp[1])})

    attempts = 0
    while len(lines) < N_CASES and attempts < N_CASES * 50:
        attempts += 1
        root, rs, key = make_case()
        sig = (rs, key)
        if sig in seen:
            continue
        seen.add(sig)
        exp = floor_ceil(root, key)
        lines.append({"inputs": {"root": rs, "key": str(key)},
                      "expected": "[{}, {}]".format(exp[0], exp[1])})

    with open(OUT_PATH, "w") as f:
        for obj in lines[:N_CASES]:
            f.write(json.dumps(obj) + "\n")
    print("wrote", min(len(lines), N_CASES), "cases to", OUT_PATH)


if __name__ == "__main__":
    main()
