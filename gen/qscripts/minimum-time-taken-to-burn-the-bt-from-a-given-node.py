#!/usr/bin/env python3
"""
Generator for "Minimum time taken to burn the BT from a given Node"
(slug: minimum-time-taken-to-burn-the-bt-from-a-given-node).

starterCpp signature:  int timeToBurnTree(TreeNode* root, int start)
  -> params (in order):  root (TreeNode*),  start (int, the target node value)
  -> output: int (minimum time/seconds to burn the whole tree from `start`).

Input keys written to the jsonl are EXACTLY the starterCpp param names in order:
  "root"  (TreeNode*, level-order space-separated, "null" for missing child),
  "start" (int, value of the target node — always present in the tree).

TreeNode serialization (judge format): level-order, space-separated, "null" for
missing child, LeetCode-style (null nodes get no children), trailing nulls trimmed.
The judge's struct field is `data` (built via rdTree).

Constraints:
  1 <= Number of Nodes <= 10^4
  -10^5 <= Node.val <= 10^5
  All Node.val values are UNIQUE.
  target (start) is always present in the tree.

Reference algorithm (matches strivers-a2z-ref): BFS outward from the target node,
treating each node's neighbours as {left child, right child, parent}. The answer is
(number of BFS levels) - 1, i.e. the max graph distance from the target to any node.

Output one JSON object per line:
  {"inputs": {"root": "<level-order>", "start": "<int>"}, "expected": "<int>"}
"""
import json
import random
import sys
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-time-taken-to-burn-the-bt-from-a-given-node.jsonl"
N_CASES = 2000
MAX_NODES = 10000
VAL_LO, VAL_HI = -100000, 100000


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def unique_values(n):
    """Return n distinct ints within [VAL_LO, VAL_HI]."""
    # range size is 200001 which comfortably exceeds MAX_NODES (10^4)
    return random.sample(range(VAL_LO, VAL_HI + 1), n)


def attach(parent, side, node):
    if side == "left":
        parent.left = node
    else:
        parent.right = node


def random_tree(n):
    """Random-shaped binary tree of exactly n nodes (n>=1), unique values."""
    vals = unique_values(n)
    root = Node(vals[0])
    slots = [(root, "left"), (root, "right")]
    for k in range(1, n):
        idx = random.randrange(len(slots))
        parent, side = slots.pop(idx)
        node = Node(vals[k])
        attach(parent, side, node)
        slots.append((node, "left"))
        slots.append((node, "right"))
    return root


def skewed_tree(n, side):
    vals = unique_values(n)
    root = Node(vals[0])
    cur = root
    for k in range(1, n):
        nd = Node(vals[k])
        attach(cur, side, nd)
        cur = nd
    return root


def zigzag_tree(n):
    """Alternating left/right skew — long path, useful burn shape."""
    vals = unique_values(n)
    root = Node(vals[0])
    cur = root
    for k in range(1, n):
        nd = Node(vals[k])
        attach(cur, "left" if k % 2 else "right", nd)
        cur = nd
    return root


def perfect_tree(depth):
    """Perfect binary tree of given depth (depth=0 -> single node), unique values."""
    n = (1 << (depth + 1)) - 1
    vals = unique_values(n)
    it = iter(vals)
    nodes = [Node(v) for v in vals]
    # fill as complete tree
    for i in range(n):
        li, ri = 2 * i + 1, 2 * i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]
    return nodes[0]


def all_nodes(root):
    out = []
    q = deque([root])
    while q:
        x = q.popleft()
        if x is None:
            continue
        out.append(x)
        if x.left:
            q.append(x.left)
        if x.right:
            q.append(x.right)
    return out


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


def time_to_burn(root, start_val):
    """Reference oracle: max BFS distance (in the parent+children graph) from the
    node whose value == start_val to any node. Equals (#BFS levels) - 1."""
    # build parent map and locate the start node
    parent = {}
    start_node = None
    q = deque([root])
    while q:
        n = q.popleft()
        if n.val == start_val:
            start_node = n
        if n.left:
            parent[id(n.left)] = n
            q.append(n.left)
        if n.right:
            parent[id(n.right)] = n
            q.append(n.right)
    assert start_node is not None, "target must be present in the tree"

    visited = set()
    q = deque([start_node])
    visited.add(id(start_node))
    time = 0
    while q:
        sz = len(q)
        burned_new = False
        for _ in range(sz):
            cur = q.popleft()
            for nb in (cur.left, cur.right, parent.get(id(cur))):
                if nb is not None and id(nb) not in visited:
                    visited.add(id(nb))
                    q.append(nb)
                    burned_new = True
        if burned_new:
            time += 1
    return time


def build_from_levelorder(s):
    """Parse a level-order string back into a tree (for self-test)."""
    toks = s.split()
    if not toks or toks[0] == "null":
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


def self_test():
    # Example 1: root = [1,2,3,4,null,5,6,null,7], target=1 -> 3
    r1 = build_from_levelorder("1 2 3 4 null 5 6 null 7")
    assert time_to_burn(r1, 1) == 3, time_to_burn(r1, 1)
    # Example 2: root = [1,2,3,null,5,null,4], target=4 -> 4
    r2 = build_from_levelorder("1 2 3 null 5 null 4")
    assert time_to_burn(r2, 4) == 4, time_to_burn(r2, 4)
    # Article example: big tree, target 8 -> 7
    #         1 / 2 3 / 4 5 _ 6 / (5->)7 8 (6->)9 / (9->)10
    big = build_from_levelorder("1 2 3 4 5 null 6 null null 7 8 null 9 null null null null null 10")
    assert time_to_burn(big, 8) == 7, time_to_burn(big, 8)
    # round-trip the serialization matches what we parsed
    assert serialize_levelorder(big) == "1 2 3 4 5 null 6 null null 7 8 null 9 null null null null null 10"
    # single node -> 0
    assert time_to_burn(build_from_levelorder("5"), 5) == 0
    # nowYourTurn: root=[1,2,3,6,5,8,4], target=4. The dataset quiz key marks "3"
    # but the TRUE answer is 4 (4->3->1->2->{6,5}: 4 levels). The verified examples
    # above (1->3, 2->4) confirm this oracle; the quiz key is unreliable.
    rn = build_from_levelorder("1 2 3 6 5 8 4")
    assert time_to_burn(rn, 4) == 4, time_to_burn(rn, 4)
    # target deep in a skewed line: 1-2-3-4-5 (all left), burn from 5 -> 4
    sk = build_from_levelorder("1 2 null 3 null 4 null 5")
    assert time_to_burn(sk, 5) == 4
    # burn from the root of that skew -> 4 as well (line of 5 nodes)
    assert time_to_burn(sk, 1) == 4
    # burn from the middle node 3 -> max(dist to 1=2, dist to 5=2) = 2
    assert time_to_burn(sk, 3) == 2
    print("self-test passed", file=sys.stderr)


def gen_tree(case_idx):
    if case_idx == 0:
        return random_tree(1)                                   # single node
    if case_idx == 1:
        return skewed_tree(2, "left")
    if case_idx == 2:
        return skewed_tree(2, "right")
    if case_idx == 3:
        return build_from_levelorder("1 2 3 4 null 5 6 null 7")  # example 1
    if case_idx == 4:
        return build_from_levelorder("1 2 3 null 5 null 4")      # example 2
    if case_idx == 5:
        return skewed_tree(MAX_NODES, "left")                   # max-size skewed
    if case_idx == 6:
        return skewed_tree(MAX_NODES, "right")
    if case_idx == 7:
        return zigzag_tree(MAX_NODES)
    if case_idx == 8:
        return random_tree(MAX_NODES)                           # max-size random
    if case_idx == 9:
        return perfect_tree(13)                                 # 16383 nodes -> trimmed below

    r = random.random()
    if r < 0.25:
        n = random.randint(1, 12)
    elif r < 0.45:
        n = random.randint(13, 200)
    elif r < 0.70:
        n = random.randint(200, 2000)
    elif r < 0.85:
        n = random.randint(2000, MAX_NODES)
    else:
        choice = random.random()
        if choice < 0.4:
            return skewed_tree(random.randint(1, MAX_NODES),
                               random.choice(["left", "right"]))
        elif choice < 0.7:
            return zigzag_tree(random.randint(1, MAX_NODES))
        else:
            return perfect_tree(random.randint(1, 12))
    return random_tree(n)


def main():
    self_test()
    random.seed(20260606)
    lines = []
    for i in range(N_CASES):
        root = gen_tree(i)
        nodes = all_nodes(root)
        # enforce node-count constraint (perfect_tree(13) overshoots)
        if len(nodes) > MAX_NODES:
            root = random_tree(MAX_NODES)
            nodes = all_nodes(root)
        nc = len(nodes)
        assert 1 <= nc <= MAX_NODES, nc
        # uniqueness sanity
        vals = [nd.val for nd in nodes]
        assert len(set(vals)) == nc, "values must be unique"
        # value-range sanity
        assert all(VAL_LO <= v <= VAL_HI for v in vals)
        # pick a target that is present in the tree (always satisfiable)
        target = random.choice(vals)
        s = serialize_levelorder(root)
        assert s != "", "root must be non-empty (>=1 node)"
        ans = time_to_burn(root, target)
        lines.append(json.dumps({
            "inputs": {"root": s, "start": str(target)},
            "expected": str(ans),
        }))
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases to {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
