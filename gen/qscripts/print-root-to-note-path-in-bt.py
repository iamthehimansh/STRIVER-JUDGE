#!/usr/bin/env python3
"""
Generator for Striver problem: "Print root to leaf path in BT"
slug: print-root-to-note-path-in-bt

Method signature (starterCpp):
    vector<vector<int>> allRootToLeaf(TreeNode* root)

Input: root -> TreeNode* serialized level-order, space separated, LeetCode-style
       ("null" for a missing child; null nodes get no children).
       Struct field is `data`.
Output: all root-to-leaf paths (left-to-right DFS order).
        Flattened to space-separated numbers on one line (judge compares leniently,
        ignoring brackets/commas/whitespace).

Constraints:
   1 <= Number of Nodes <= 3*10^3
   -10^3 <= Node.val <= 10^3
"""
import json
import random
import os
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/print-root-to-note-path-in-bt.jsonl"

VAL_MIN, VAL_MAX = -1000, 1000
MAX_NODES = 3000


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_random_tree(n):
    """Build a random binary tree with exactly n nodes (n>=1).
    Returns root Node. Each new node attached to a random open slot."""
    root = Node(random.randint(VAL_MIN, VAL_MAX))
    # open slots: list of (parent_node, side) where side in ('L','R')
    open_slots = [(root, 'L'), (root, 'R')]
    count = 1
    while count < n:
        idx = random.randrange(len(open_slots))
        parent, side = open_slots.pop(idx)
        node = Node(random.randint(VAL_MIN, VAL_MAX))
        if side == 'L':
            parent.left = node
        else:
            parent.right = node
        open_slots.append((node, 'L'))
        open_slots.append((node, 'R'))
        count += 1
    return root


def build_skewed_tree(n, side="L"):
    """Build a pure left- (or right-) skewed chain of n nodes.
    Has exactly one leaf -> a single path of length n. Lets us test the
    max node-count (constraint upper bound) with tiny output."""
    root = Node(random.randint(VAL_MIN, VAL_MAX))
    cur = root
    for _ in range(n - 1):
        nxt = Node(random.randint(VAL_MIN, VAL_MAX))
        if side == "L":
            cur.left = nxt
        else:
            cur.right = nxt
        cur = nxt
    return root


def build_caterpillar_tree(n):
    """A 'spine' (left chain) where every spine node also has a right leaf.
    n nodes total, ~n/2 leaves but each path is short -> moderate output;
    used to exercise larger node counts with bounded output."""
    root = Node(random.randint(VAL_MIN, VAL_MAX))
    cur = root
    count = 1
    while count < n:
        # add a right leaf to current spine node
        cur.right = Node(random.randint(VAL_MIN, VAL_MAX))
        count += 1
        if count >= n:
            break
        nxt = Node(random.randint(VAL_MIN, VAL_MAX))
        cur.left = nxt
        cur = nxt
        count += 1
    return root


def serialize_level_order(root):
    """LeetCode-style level order: null for missing child, null nodes get no
    children. Trim trailing nulls."""
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


def deserialize_level_order(s):
    """Build tree from LeetCode-style level order string (null = missing)."""
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


def case_from_string(s):
    """Build a case dict from a level-order root string using the reference."""
    root = deserialize_level_order(s)
    return {"inputs": {"root": s}, "expected": flatten_expected(all_root_to_leaf(root))}


def all_root_to_leaf(root):
    """Return list of paths (each a list of ints), left-to-right DFS order.
    Iterative (explicit stack) so deep skewed trees (up to 3000) don't blow
    Python's recursion limit. Mirrors the recursive reference's preorder /
    left-before-right path ordering exactly."""
    res = []
    if root is None:
        return res
    # stack of (node, path_so_far). Use a tuple-path to keep ordering simple.
    # To preserve left-to-right DFS order, push right child first then left.
    stack = [(root, (root.val,))]
    while stack:
        node, path = stack.pop()
        if node.left is None and node.right is None:
            res.append(list(path))
            continue
        # push right first so left is processed first (LIFO)
        if node.right is not None:
            stack.append((node.right, path + (node.right.val,)))
        if node.left is not None:
            stack.append((node.left, path + (node.left.val,)))
    return res


def flatten_expected(paths):
    """Flatten 2D output to space-separated numbers on one line."""
    flat = []
    for p in paths:
        flat.extend(str(x) for x in p)
    return " ".join(flat)


def case_from_root(root):
    root_str = serialize_level_order(root)
    expected = flatten_expected(all_root_to_leaf(root))
    return {"inputs": {"root": root_str}, "expected": expected}


def make_case(n):
    return case_from_root(build_random_tree(n))


# The live judge batches ALL 2000 cases into ONE process and the local runner
# (scripts/judge_exec.py) caps that process's TOTAL stdout at OUT_CAP = 256 KiB
# (= 256*1024). The runner.ts cap (1 MiB) is looser; the 256 KiB one binds.
# If cumulative output exceeds 256 KiB, later cases are truncated and fail.
# So we BUDGET total expected bytes well under 256 KiB while still covering the
# constraint space (the 3000-node upper bound is hit via skewed trees whose
# single-path output stays tiny).
OUTPUT_BUDGET = 210_000  # bytes of "expected" content across all 2000 cases (< 256 KiB)


def main():
    random.seed(12345)
    cases = []

    # ---- Edge / fixed cases (expected computed via reference) ----
    fixed_strings = [
        "0",                       # single node (min size)
        "1000",                    # max val
        "-1000",                   # min val
        "1 2 3 null 5 null 4",     # dataset example 1
        "1 2 3 4 5",               # dataset example 2
        "1 2 null 3 null 4",       # left-skewed chain
        "1 null 2 null 3 null 4",  # right-skewed chain
        "1 2 null 3 4 5 null null 6",  # dataset case 3 structure
    ]
    for s in fixed_strings:
        cases.append(case_from_string(s))

    # explicit small structured trees built by code (so paths verified)
    for n in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
        cases.append(make_case(n))

    # ---- Constraint upper-bound (3000 nodes) cases with SMALL output ----
    # Skewed chains: 3000 nodes, single path -> tiny output but stresses the
    # max node count and recursion depth.
    # one full-bound skewed tree each direction (single path => ~13 KB each).
    cases.append(case_from_root(build_skewed_tree(MAX_NODES, "L")))
    cases.append(case_from_root(build_skewed_tree(MAX_NODES, "R")))
    # a couple of smaller deep chains to keep the byte budget modest.
    cases.append(case_from_root(build_skewed_tree(500, "L")))
    cases.append(case_from_root(build_skewed_tree(300, "R")))
    # Small caterpillars: spine with right leaves. Output grows ~O(n^2) so keep
    # these SMALL (a big caterpillar would blow the judge's 256 KiB stdout cap).
    cases.append(case_from_root(build_caterpillar_tree(30)))
    cases.append(case_from_root(build_caterpillar_tree(50)))

    used = sum(len(c["expected"]) + 1 for c in cases)

    # ---- Random cases up to 2000 total, within the output budget ----
    # Keep most trees small so cumulative stdout stays under the judge cap.
    attempts = 0
    while len(cases) < 2000 and attempts < 200000:
        attempts += 1
        remaining_slots = 2000 - len(cases)
        budget_left = OUTPUT_BUDGET - used
        # average bytes we can still afford per remaining case
        avg_left = budget_left / max(1, remaining_slots)

        r = random.random()
        if r < 0.70:
            n = random.randint(1, 20)
        elif r < 0.92:
            n = random.randint(20, 60)
        elif avg_left > 300:
            n = random.randint(60, 150)
        else:
            n = random.randint(1, 15)

        c = make_case(n)
        size = len(c["expected"]) + 1
        # hard per-case output cap so no single case dominates the small budget
        if len(c["expected"]) > 1500:
            continue
        # don't blow the overall budget; if a case is too big, skip and retry small
        if used + size > OUTPUT_BUDGET and len(c["expected"]) > 60:
            continue
        cases.append(c)
        used += size

    # fill any leftover slots with guaranteed-tiny cases
    while len(cases) < 2000:
        cases.append(make_case(random.randint(1, 5)))

    cases = cases[:2000]

    total_bytes = sum(len(c["expected"]) + 1 for c in cases)
    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c, separators=(",", ":")) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")
    print(f"total expected bytes (with newline): {total_bytes} "
          f"(~{total_bytes/1024:.0f} KiB, budget {OUTPUT_BUDGET})")


if __name__ == "__main__":
    main()
