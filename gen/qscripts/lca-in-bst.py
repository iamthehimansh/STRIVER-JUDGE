#!/usr/bin/env python3
"""
Test-case generator for Striver problem: lca-in-bst (LCA in BST).

Method signature (starterCpp):
    TreeNode* lca(TreeNode* root, int p, int q)

Constraints:
    1 <= Number of Nodes <= 10^4
    1 <= Node.val <= 10^5
    All values in BST are unique.
    p and q are always present in the given BST.

Output format (judge serialization of returned TreeNode*):
    The subtree rooted at the LCA node, level-order, "null" for missing
    children, trailing nulls trimmed (LeetCode-style). NOTE: this is the
    WHOLE subtree, not just the LCA value — confirmed against the live judge.

jsonl line: {"inputs": {"p": "..","q":"..","root":".."}, "expected": ".."}
Input key order matches the dataset's testcases (p, q, root).

expected values are produced by an external C++ oracle that reuses the judge's
EXACT TreeNode (de)serialization (rdTree / pr(TreeNode*)) so a correct
submission reproduces them token-for-token.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_PATH = os.path.join(PROJECT, "generated-tests", "lca-in-bst.jsonl")
ORACLE = "/tmp/lcagen/oracle"

MAX_NODES = 10**4
MAX_VAL = 10**5
N_CASES = 2000

random.seed(20260606)


def build_bst(values):
    """Insert distinct values into a BST in the given order; return root index
    structure. We represent the tree as a dict of node -> (left, right) using a
    standard BST insertion. Returns the root value and child maps."""
    if not values:
        return None, {}, {}
    left = {}
    right = {}
    root = values[0]
    for v in values[1:]:
        cur = root
        while True:
            if v < cur:
                if cur in left:
                    cur = left[cur]
                else:
                    left[cur] = v
                    break
            else:  # v > cur (all distinct)
                if cur in right:
                    cur = right[cur]
                else:
                    right[cur] = v
                    break
    return root, left, right


def serialize_levelorder(root, left, right):
    """LeetCode-style level-order serialization (null for missing child,
    trailing nulls trimmed)."""
    if root is None:
        return ""
    out = []
    q = [root]
    while q:
        nxt = []
        for node in q:
            if node is None:
                out.append("null")
            else:
                out.append(str(node))
                nxt.append(left.get(node))
                nxt.append(right.get(node))
        q = nxt
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def make_random_bst(n):
    """Pick n distinct values in [1, MAX_VAL], insert in random order to make a
    (random-shape) BST. Returns (serialization, sorted_list_of_values)."""
    if n >= MAX_VAL:
        vals = list(range(1, MAX_VAL + 1))
    else:
        vals = random.sample(range(1, MAX_VAL + 1), n)
    insert_order = vals[:]
    random.shuffle(insert_order)
    root, left, right = build_bst(insert_order)
    ser = serialize_levelorder(root, left, right)
    return ser, vals


def make_skewed_bst(n, increasing=True):
    """Skewed BST = inserting already-sorted values -> a chain. Stays within
    MAX_VAL and gives a degenerate (height n) tree edge case."""
    n = min(n, MAX_VAL)
    vals = sorted(random.sample(range(1, MAX_VAL + 1), n))
    insert_order = vals if increasing else list(reversed(vals))
    root, left, right = build_bst(insert_order)
    ser = serialize_levelorder(root, left, right)
    return ser, vals


def gen_case(kind=None):
    """Generate one (root_serialization, p, q) honoring all constraints."""
    if kind is None:
        kind = random.random()

    if kind == "single" or (isinstance(kind, float) and kind < 0.06):
        # n = 1 (minimum size): p and q must both be that single node value.
        ser, vals = make_random_bst(1)
        v = vals[0]
        return ser, v, v
    if kind == "skewed" or (isinstance(kind, float) and kind < 0.16):
        ser, vals = make_skewed_bst(random.randint(2, 30),
                                    increasing=random.random() < 0.5)
    elif kind == "small" or (isinstance(kind, float) and kind < 0.80):
        ser, vals = make_random_bst(random.randint(2, 20))
    else:
        ser, vals = make_random_bst(random.randint(21, 60))

    # The serialized OUTPUT is the LCA subtree; the judge batches ~2000 lines
    # into a single process whose stdout is capped at 256 KB, so keep each
    # output line short. Biasing p,q to ADJACENT sorted values makes the LCA
    # deep and its subtree tiny, but we also cap tree size above to be safe.
    if random.random() < 0.5 and len(vals) > 4:
        svals = sorted(vals)
        lo = random.randint(0, len(svals) - 2)
        hi = min(len(svals) - 1, lo + random.randint(1, 4))
        a, b = svals[lo], svals[hi]
        if random.random() < 0.10:
            return ser, a, a
        return ser, a, b

    # p and q: choose from existing node values (guaranteed present). Allow
    # p == q occasionally (node is descendant of itself per LCA definition).
    if random.random() < 0.08:
        p = q = random.choice(vals)
    else:
        p = random.choice(vals)
        q = random.choice(vals)
    return ser, p, q


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    cases = []  # list of (root_ser, p, q)

    # --- explicit edge cases ---
    # dataset examples (self-check)
    cases.append(("5 3 6 2 4 null 7", 2, 4))
    cases.append(("5 3 6 2 4 null 7", 2, 7))
    cases.append(("10 5 14 1 9 11 19", 1, 11))
    # single-node trees
    cases.append(("1", 1, 1))
    cases.append((str(MAX_VAL), MAX_VAL, MAX_VAL))
    # two nodes
    cases.append(("2 1", 1, 2))
    cases.append(("1 null 2", 1, 2))
    cases.append(("2 1", 1, 1))
    # extreme values present
    cases.append((f"50000 1 {MAX_VAL}", 1, MAX_VAL))
    cases.append((f"50000 1 {MAX_VAL}", 1, 50000))
    # p == q on a deeper tree
    s, vals = make_random_bst(50)
    v = random.choice(vals)
    cases.append((s, v, v))
    # one of p/q is the root
    s, vals = make_random_bst(40)
    root_val = int(s.split()[0])
    cases.append((s, root_val, random.choice(vals)))

    # A few larger trees to exercise scale. Use p == q at a leaf value so the
    # returned LCA subtree is a SINGLE node (tiny output) regardless of tree
    # size — the judge batches ~2000 lines into one 256 KB-capped stdout, so
    # large subtree outputs would otherwise overflow it.
    for _ in range(6):
        s, vals = make_random_bst(random.randint(800, 4000))
        v = max(vals)  # the largest value is always a leaf in a BST
        cases.append((s, v, v))
    # One near-cap tree (node count == 10^4) with p == q at a leaf value, so
    # its LCA subtree is a single small node (tiny output), exercising the
    # node-count boundary without bloating cumulative stdout.
    s, vals = make_random_bst(MAX_NODES)
    v = max(vals)
    cases.append((s, v, v))

    # --- random cases to fill up to N_CASES ---
    while len(cases) < N_CASES:
        cases.append(gen_case(random.random()))

    cases = cases[:N_CASES]

    # --- compute expected via the oracle (one tab-sep line per case) ---
    if not os.path.exists(ORACLE):
        print(f"ERROR: oracle not found at {ORACLE}; compile it first.",
              file=sys.stderr)
        sys.exit(1)

    stdin_lines = []
    for ser, p, q in cases:
        stdin_lines.append(f"{ser}\t{p}\t{q}")
    proc = subprocess.run([ORACLE], input="\n".join(stdin_lines) + "\n",
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print("ORACLE FAILED:", proc.stderr, file=sys.stderr)
        sys.exit(1)
    expected = proc.stdout.split("\n")
    # last element may be empty due to trailing newline
    expected = [e for e in expected]
    # align: there should be exactly len(cases) output lines
    expected = expected[:len(cases)]
    if len(expected) != len(cases):
        print(f"ERROR: oracle returned {len(expected)} lines for "
              f"{len(cases)} cases", file=sys.stderr)
        sys.exit(1)

    with open(OUT_PATH, "w") as f:
        for (ser, p, q), exp in zip(cases, expected):
            obj = {
                "inputs": {"p": str(p), "q": str(q), "root": ser},
                "expected": exp,
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
