#!/usr/bin/env python3
"""
Generator for: check-if-two-trees-are-identical-or-not (LeetCode "Same Tree").

starterCpp signature: bool isSameTree(TreeNode* p, TreeNode* q)
Params (signature order): p, q  -> both TreeNode* serialized as level-order
LeetCode-style: "null" for missing child, null nodes get no children.

Constraints:
  - 0 <= Number of Nodes <= 100
  - -10^4 <= Node.val <= 10^4

Output JSONL lines: {"inputs": {"p": "...", "q": "..."}, "expected": "true"/"false"}
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-if-two-trees-are-identical-or-not.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = -10000, 10000
MAX_NODES = 100


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_random_tree(num_nodes):
    """Build a random binary tree with exactly num_nodes nodes."""
    if num_nodes == 0:
        return None
    root = Node(random.randint(VAL_MIN, VAL_MAX))
    # candidate slots where a new node can attach (parent, side)
    # we grow by repeatedly attaching to a random available slot
    slots = [(root, "left"), (root, "right")]
    for _ in range(num_nodes - 1):
        idx = random.randrange(len(slots))
        parent, side = slots.pop(idx)
        node = Node(random.randint(VAL_MIN, VAL_MAX))
        setattr(parent, side, node)
        slots.append((node, "left"))
        slots.append((node, "right"))
    return root


def serialize_level_order(root):
    """LeetCode-style level-order with 'null', trailing nulls trimmed."""
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


def clone(root):
    if root is None:
        return None
    n = Node(root.val)
    n.left = clone(root.left)
    n.right = clone(root.right)
    return n


def is_same_tree(p, q):
    """Reference oracle = the C++ reference logic."""
    if p is None and q is None:
        return True
    if p is None or q is None:
        return False
    return (p.val == q.val) and is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


def all_nodes(root):
    res = []
    if root is None:
        return res
    q = deque([root])
    while q:
        n = q.popleft()
        res.append(n)
        if n.left:
            q.append(n.left)
        if n.right:
            q.append(n.right)
    return res


def mutate_value(root):
    """Return a clone with one node's value changed (forces 'false')."""
    c = clone(root)
    nodes = all_nodes(c)
    if not nodes:
        return None  # empty tree can't be value-mutated
    target = random.choice(nodes)
    while True:
        nv = random.randint(VAL_MIN, VAL_MAX)
        if nv != target.val:
            target.val = nv
            break
    return c


def main():
    random.seed(12345)
    cases = []

    # ---- Deterministic edge cases ----
    # 1. both empty -> true
    cases.append(("", "", "true"))
    # 2. p empty, q one node -> false
    cases.append(("", "5", "false"))
    # 3. q empty, p one node -> false
    cases.append(("5", "", "false"))
    # 4. single same node -> true
    cases.append(("0", "0", "true"))
    # 5. single diff node -> false
    cases.append(("1", "-1", "false"))
    # 6. extreme values, identical
    cases.append(("10000 -10000", "10000 -10000", "true"))
    # 7. structurally different (example 2 style)
    cases.append(("1 2 1", "1 1 2", "false"))
    # 8. example 1
    cases.append(("1 2 3", "1 2 3", "true"))
    # 9. same values different structure
    cases.append(("1 2 3 4", "1 2 4 3", "false"))
    # 10. left-only skew identical
    skew = "1"
    node = Node(1)
    cur = node
    for v in range(2, 21):
        cur.left = Node(v)
        cur = cur.left
    s = serialize_level_order(node)
    cases.append((s, s, "true"))
    # 11. full 100-node tree identical (max size)
    big = build_random_tree(100)
    bs = serialize_level_order(big)
    cases.append((bs, bs, "true"))
    # 12. 100-node tree vs same-but-one-value-changed -> false
    bigm = mutate_value(big)
    cases.append((bs, serialize_level_order(bigm), "false"))

    # ---- Random cases ----
    while len(cases) < N_CASES:
        r = random.random()
        n1 = random.randint(0, MAX_NODES)
        t1 = build_random_tree(n1)
        s1 = serialize_level_order(t1)

        if r < 0.34:
            # identical clone -> true
            t2 = clone(t1)
        elif r < 0.60:
            # mutate one value (if possible) -> usually false
            t2 = mutate_value(t1)
            if t2 is None:
                # empty tree: pick another fully independent tree
                n2 = random.randint(0, MAX_NODES)
                t2 = build_random_tree(n2)
        else:
            # fully independent random tree (could be same by chance, oracle decides)
            n2 = random.randint(0, MAX_NODES)
            t2 = build_random_tree(n2)

        s2 = serialize_level_order(t2)
        exp = "true" if is_same_tree(t1, t2) else "false"
        cases.append((s1, s2, exp))

    with open(OUT, "w") as f:
        for p, q, exp in cases[:N_CASES]:
            f.write(json.dumps({"inputs": {"p": p, "q": q}, "expected": exp}) + "\n")

    print(f"Wrote {min(len(cases), N_CASES)} cases to {OUT}")
    # quick distribution sanity
    t = sum(1 for c in cases[:N_CASES] if c[2] == "true")
    print(f"true: {t}, false: {N_CASES - t}")


if __name__ == "__main__":
    main()
