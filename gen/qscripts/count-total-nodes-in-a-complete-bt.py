#!/usr/bin/env python3
"""
Generator for Striver problem: count-total-nodes-in-a-complete-bt

Problem: Given the root of a COMPLETE binary tree, return the number of nodes.

Constraints:
  - 1 <= Number of Nodes <= 5*10^4
  - -10^5 <= Node.val <= 10^5
  - The tree is guaranteed to be COMPLETE.

A complete binary tree with N nodes is filled level-by-level, left to right,
with no gaps. Therefore its level-order serialization is exactly the N node
values in order, with NO "null" placeholders. The answer is simply N.

The judge builds a TreeNode* from a space-separated, level-order string
("null" for missing children, LeetCode style) using struct field `data`.
For a complete tree there are never any nulls, so the input is just the
values separated by spaces.

We compute "expected" by a real reference (the standard O(log^2 n) algorithm)
to be 100% self-consistent with what the judge runs, rather than just trusting
that the answer == N.

Output: one JSON object per line:
  {"inputs": {"root": "1 2 3 4 5 6"}, "expected": "6"}
"""

import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-total-nodes-in-a-complete-bt.jsonl"

VAL_MIN = -100000
VAL_MAX = 100000
N_MIN = 1
N_MAX = 50000  # 5 * 10^4

random.seed(20260606)


# ----- Reference (mirrors the C++ reference / what the judge will run) -----
class TreeNode:
    __slots__ = ("data", "left", "right")

    def __init__(self, val):
        self.data = val
        self.left = None
        self.right = None


def build_complete_tree(values):
    """Build a complete binary tree from level-order values (no nulls)."""
    if not values:
        return None
    nodes = [TreeNode(v) for v in values]
    n = len(nodes)
    for i in range(n):
        li = 2 * i + 1
        ri = 2 * i + 2
        if li < n:
            nodes[i].left = nodes[li]
        if ri < n:
            nodes[i].right = nodes[ri]
    return nodes[0]


def left_height(root):
    h = 1
    while root:
        h += 1
        root = root.left
    return h


def right_height(root):
    h = 1
    while root:
        h += 1
        root = root.right
    return h


def count_nodes(root):
    if not root:
        return 0
    lh = left_height(root.left)
    rh = right_height(root.right)
    if lh == rh:
        return (1 << lh) - 1
    return 1 + count_nodes(root.left) + count_nodes(root.right)


def gen_values(n):
    return [random.randint(VAL_MIN, VAL_MAX) for _ in range(n)]


def make_case(n):
    values = gen_values(n)
    root = build_complete_tree(values)
    expected = count_nodes(root)
    # sanity: a complete tree's count must equal n
    assert expected == n, (n, expected)
    root_str = " ".join(str(v) for v in values)
    return {"inputs": {"root": root_str}, "expected": str(expected)}


def main():
    cases = []
    seen_sizes = set()

    # Edge / structural cases first.
    edge_sizes = [
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,  # small + perfect/full boundaries
        31, 32, 33, 63, 64, 65, 127, 128, 255, 256, 511, 512, 1023, 1024,
        49998, 49999, 50000,  # near max
        2, 1,
    ]
    for n in edge_sizes:
        if N_MIN <= n <= N_MAX:
            cases.append(make_case(n))

    # Some cases with extreme value content (all min, all max, mixed)
    for n in [1, 2, 7, 15, 100, 1000, 50000]:
        values = [VAL_MIN] * n
        cases.append({"inputs": {"root": " ".join(map(str, values))},
                      "expected": str(count_nodes(build_complete_tree(values)))})
        values = [VAL_MAX] * n
        cases.append({"inputs": {"root": " ".join(map(str, values))},
                      "expected": str(count_nodes(build_complete_tree(values)))})

    # Fill up to 2000 with random sizes (bias toward small/medium, some large).
    target = 2000
    while len(cases) < target:
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 200)
        elif r < 0.80:
            n = random.randint(1, 5000)
        elif r < 0.95:
            n = random.randint(1, 50000)
        else:
            n = random.choice([N_MAX, N_MAX - 1, N_MAX - 2])
        cases.append(make_case(n))

    cases = cases[:target]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
