#!/usr/bin/env python3
"""Generator for 'Children Sum Property in Binary Tree'.

Problem: return true iff every node's value equals the sum of its left and
right children's values (a missing/null child counts as 0; leaves trivially OK).

Constraints: 1 <= n <= 10^4 ; -10^5 <= Node.val <= 10^5.

Tree serialization (matches the judge's rdTree): level-order, space-separated,
"null" for a missing child, LeetCode-style (null nodes get no children).
Output: bool -> "true" / "false".
"""
import json
import random
import os

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/children-sum-property-in-binary-tree.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = -10**5, 10**5
MAX_NODES = 10**4


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def random_shape(n):
    """Build a random binary tree shape with exactly n nodes (n>=1).
    Returns the root Node (values set to 0 placeholders)."""
    root = Node(0)
    nodes = [root]
    # available "slots" to attach children: list of (parent, side)
    slots = [(root, "left"), (root, "right")]
    created = 1
    while created < n and slots:
        idx = random.randrange(len(slots))
        parent, side = slots.pop(idx)
        child = Node(0)
        setattr(parent, side, child)
        nodes.append(child)
        created += 1
        slots.append((child, "left"))
        slots.append((child, "right"))
    return root, nodes


def assign_satisfying(root):
    """Assign values bottom-up so the children-sum property holds, while
    keeping every value within [VAL_MIN, VAL_MAX]. Returns True on success."""
    ok = True

    def dfs(node):
        nonlocal ok
        if node is None:
            return 0
        if node.left is None and node.right is None:
            # leaf: free choice
            node.val = random.randint(VAL_MIN, VAL_MAX)
            return node.val
        l = dfs(node.left) if node.left else 0
        r = dfs(node.right) if node.right else 0
        s = l + r
        node.val = s
        if not (VAL_MIN <= s <= VAL_MAX):
            ok = False
        return s

    dfs(root)
    return ok


def assign_satisfying_bounded(root):
    """Assign values so property holds AND all values stay in range, by picking
    leaf values small enough that internal sums won't overflow the bound.
    We bound leaf magnitude by VAL_MAX / (number of leaves) roughly. Retries
    by clamping: assign top-down target sums isn't trivial, so do bottom-up with
    small leaves."""
    # count leaves under each node
    leaves_under = {}

    def count(node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            leaves_under[id(node)] = 1
            return 1
        c = (count(node.left) if node.left else 0) + (count(node.right) if node.right else 0)
        leaves_under[id(node)] = c
        return c

    total_leaves = count(root)
    # any internal node value = sum of leaf values in its subtree. To keep every
    # such sum within [VAL_MIN, VAL_MAX], cap each leaf magnitude by
    # VAL_MAX // total_leaves (worst case all leaves under root).
    cap = max(1, VAL_MAX // max(1, total_leaves))

    def dfs(node):
        if node is None:
            return 0
        if node.left is None and node.right is None:
            node.val = random.randint(-cap, cap)
            return node.val
        l = dfs(node.left) if node.left else 0
        r = dfs(node.right) if node.right else 0
        node.val = l + r
        return node.val

    dfs(root)
    return True


def assign_random(root):
    """Assign fully random values in range (property usually false)."""
    def dfs(node):
        if node is None:
            return
        node.val = random.randint(VAL_MIN, VAL_MAX)
        dfs(node.left)
        dfs(node.right)
    dfs(root)


def perturb(root, nodes):
    """Take a satisfying tree and flip one node's value so property breaks."""
    n = random.choice(nodes)
    delta = random.choice([-1, 1]) * random.randint(1, 1000)
    nv = n.val + delta
    nv = max(VAL_MIN, min(VAL_MAX, nv))
    if nv == n.val:
        nv = n.val + 1 if n.val < VAL_MAX else n.val - 1
    n.val = nv


def check_children_sum(root):
    """Reference oracle: true iff every node's val == left.val(0) + right.val(0)."""
    ok = True

    def dfs(node):
        nonlocal ok
        if node is None:
            return
        if node.left is None and node.right is None:
            return
        l = node.left.val if node.left else 0
        r = node.right.val if node.right else 0
        if node.val != l + r:
            ok = False
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ok


def serialize(root):
    """Level-order with 'null' for missing children, LeetCode-style; trailing
    nulls trimmed. Space-separated (judge also accepts commas)."""
    if root is None:
        return ""
    from collections import deque
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


def gen_one(case_idx):
    # edge cases first
    if case_idx == 0:
        # single node (min size) -> leaf -> true
        root = Node(random.randint(VAL_MIN, VAL_MAX))
        nodes = [root]
    elif case_idx == 1:
        # single node extreme val
        root = Node(VAL_MAX)
        nodes = [root]
    elif case_idx == 2:
        root = Node(VAL_MIN)
        nodes = [root]
    elif case_idx == 3:
        # dataset example 1: false
        root, nodes = build_from_level([1, 4, 3, 5])
    elif case_idx == 4:
        # dataset example 2: true
        root, nodes = build_from_level([10, 4, 6, 1, 3, 2, 4])
    elif case_idx == 5:
        # two nodes: root + left child only -> needs root.val == left.val
        root, nodes = build_from_level([5, 5])
    elif case_idx == 6:
        root, nodes = build_from_level([5, 3])  # false
    else:
        n = random.randint(1, choose_size())
        root, nodes = random_shape(n)
        mode = random.random()
        if mode < 0.40:
            # satisfying & in-range
            assign_satisfying_bounded(root)
            # sometimes perturb to make false but still valid input
            if random.random() < 0.45 and len(nodes) > 1:
                perturb(root, nodes)
        elif mode < 0.70:
            # try unbounded satisfying; if out of range fall back to bounded
            if not assign_satisfying(root):
                assign_satisfying_bounded(root)
            if random.random() < 0.4 and len(nodes) > 1:
                perturb(root, nodes)
        else:
            assign_random(root)
    return root, nodes


def choose_size():
    """Distribution favoring small trees but occasionally large (up to 10^4)."""
    r = random.random()
    if r < 0.55:
        return random.randint(1, 20)
    if r < 0.85:
        return random.randint(1, 200)
    if r < 0.97:
        return random.randint(1, 2000)
    return random.randint(1, MAX_NODES)


def build_from_level(vals):
    """Build a tree from a list of ints (no nulls in these helpers)."""
    from collections import deque
    if not vals:
        return None, []
    root = Node(vals[0])
    nodes = [root]
    q = deque([root])
    i = 1
    while q and i < len(vals):
        node = q.popleft()
        if i < len(vals):
            c = Node(vals[i]); i += 1
            node.left = c; nodes.append(c); q.append(c)
        if i < len(vals):
            c = Node(vals[i]); i += 1
            node.right = c; nodes.append(c); q.append(c)
    return root, nodes


def main():
    random.seed(20260606)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = []
    true_cnt = 0
    for i in range(N_CASES):
        root, nodes = gen_one(i)
        s = serialize(root)
        # safety: validate every value within range
        bad = any(not (VAL_MIN <= nd.val <= VAL_MAX) for nd in nodes)
        if bad:
            # clamp into range (shouldn't happen with bounded gen)
            for nd in nodes:
                nd.val = max(VAL_MIN, min(VAL_MAX, nd.val))
            s = serialize(root)
        # also enforce node count <= MAX_NODES
        assert 1 <= len(nodes) <= MAX_NODES, f"bad node count {len(nodes)}"
        ans = check_children_sum(root)
        if ans:
            true_cnt += 1
        lines.append(json.dumps({
            "inputs": {"root": s},
            "expected": "true" if ans else "false",
        }))
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {len(lines)} cases to {OUT}")
    print(f"true={true_cnt} false={len(lines)-true_cnt}")


if __name__ == "__main__":
    main()
