#!/usr/bin/env python3
"""
Test-case generator for Striver problem: lca-in-bt (LCA in Binary Tree).

Method signature (starterCpp):
    TreeNode* lowestCommonAncestor(TreeNode* root, TreeNode* p, TreeNode* q)

Constraints:
    2 <= Number of Nodes <= 10^5
    -10^6 <= node.val <= 10^6
    All values in the tree are UNIQUE.
    p and q are two given nodes -> their values are always PRESENT in the tree.

Output format (judge serialization of the returned TreeNode*):
    The method returns a TreeNode* (the LCA node). The judge serializes that
    return value with pr(TreeNode*): the SUBTREE rooted at the LCA, level-order,
    "null" for a missing child, trailing nulls trimmed (LeetCode-style).
    => `expected` is the FULL subtree serialization, NOT just the LCA value.
    (The dataset's own example outputs show only the bare LCA value, which would
     fail the real judge on token count; we emit what the live judge actually
     produces, verified end-to-end against http://localhost:3000.)

p and q params are TreeNode* too: the judge reads a bare integer like "5" via
rdTree into a single-node tree, and the reference compares ->data. So a p value
of "5" yields p->data == 5. We emit p/q as bare integers.

jsonl line: {"inputs": {"root": "..", "p": "..", "q": ".."}, "expected": ".."}
Input keys are bound by NAME by the harness, so order is robust; we use
root, p, q.

expected values are produced by /tmp/lca_gen/oracle, a C++ program that reuses
the judge's EXACT rdTree / pr(TreeNode*) plus the reference class Solution, so a
correct submission reproduces them token-for-token.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_PATH = os.path.join(PROJECT, "generated-tests", "lca-in-bt.jsonl")
ORACLE = "/tmp/lca_gen/oracle"

MIN_NODES = 2
MAX_NODES = 10**5
VAL_LO = -10**6
VAL_HI = 10**6
N_CASES = 2000

# IMPORTANT — output-size budget (HARD constraint of the judge).
# This method RETURNS a TreeNode*; the judge serializes the WHOLE subtree rooted
# at the LCA (often near the root -> close to the full tree). The judge batches
# all 2000 cases into ONE process and the LOCAL backend (scripts/judge_exec.py)
# caps the captured batched stdout at OUT_CAP = 256 KB (262144 bytes). Beyond
# that the stdout string is truncated mid-line, so every case past the cutoff
# fails -> wrong_answer. We therefore bound node counts so the SUM of all 2000
# expected outputs stays well under 256 KB, while still covering the constraint
# space (distinct values across the full [-1e6,1e6] range, skewed shapes, p==q,
# extremes, ancestor-of relationships). MAX_OUT_BYTES guards it.
MAX_OUT_BYTES = 220_000   # safety margin below the judge's 262144-byte stdout cap
# Random binary trees serialize to ~12.4 bytes/node (many null markers). To keep
# the SUM of all 2000 expected outputs under MAX_OUT_BYTES we bound total nodes
# to ~16k; hence trees are small (avg ~8 nodes) with only a few larger ones.
MAX_CASE_NODES = 120  # largest tree we emit (keeps any single line small)

random.seed(20260606)


def distinct_values(n):
    """Return n distinct integer values in [VAL_LO, VAL_HI]."""
    span = VAL_HI - VAL_LO + 1  # 2_000_001, plenty for n <= 10^5
    return random.sample(range(VAL_LO, VAL_HI + 1), n)


def build_random_tree(values):
    """Build a random-shaped binary tree over `values` (values[0] is the root).
    Returns level-order serialization string and the list of node values.

    Strategy: incremental insertion. Maintain a list of "open slots" (node,
    side). For each new value, attach it to a randomly chosen open slot, then add
    its own two open slots. This yields arbitrary (non-degenerate-biased) shapes;
    we also support explicitly skewed shapes via the caller choosing the slot
    policy.
    """
    if not values:
        return "", []
    n = len(values)
    left = {}
    right = {}
    root = values[0]
    # open slots as (parent_value, side)
    slots = [(root, "L"), (root, "R")]
    for v in values[1:]:
        idx = random.randrange(len(slots))
        # swap-remove for O(1)
        parent, side = slots[idx]
        slots[idx] = slots[-1]
        slots.pop()
        if side == "L":
            left[parent] = v
        else:
            right[parent] = v
        slots.append((v, "L"))
        slots.append((v, "R"))
    return serialize_levelorder(root, left, right), values


def build_skewed_tree(values, direction):
    """Degenerate chain. direction in {'L','R','zigzag'}."""
    if not values:
        return "", []
    left = {}
    right = {}
    root = values[0]
    prev = root
    for i, v in enumerate(values[1:]):
        if direction == "L":
            left[prev] = v
        elif direction == "R":
            right[prev] = v
        else:  # zigzag
            if i % 2 == 0:
                left[prev] = v
            else:
                right[prev] = v
        prev = v
    return serialize_levelorder(root, left, right), values


def serialize_levelorder(root, left, right):
    """LeetCode-style level-order (null for missing child, trailing nulls
    trimmed). Matches the judge's pr(TreeNode*)."""
    out = []
    q = [root]
    while q:
        nxt = []
        for node in q:
            if node is None:
                out.append("null")
            else:
                out.append(str(node))
                # use sentinel objects: children may be missing
                lc = left.get(node, None)
                rc = right.get(node, None)
                nxt.append(lc)
                nxt.append(rc)
        q = nxt
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def pick_pq(values):
    """Pick p and q from present node values. ~10% chance p == q (a node is a
    descendant of itself per the LCA definition)."""
    if random.random() < 0.10:
        v = random.choice(values)
        return v, v
    p = random.choice(values)
    q = random.choice(values)
    return p, q


def gen_random_case():
    # Size distribution is bounded to respect the judge's 1 MB batched-stdout cap
    # (see MAX_OUT_BYTES note above): mostly tiny trees, a few up to MAX_CASE_NODES.
    r = random.random()
    if r < 0.06:
        n = MIN_NODES                          # minimum size (2)
    elif r < 0.92:
        n = random.randint(2, 12)              # tiny (bulk of cases)
    elif r < 0.99:
        n = random.randint(13, 40)             # small-medium
    else:
        n = random.randint(41, MAX_CASE_NODES)  # larger (few)
    vals = distinct_values(n)
    shape = random.random()
    if shape < 0.12:
        ser, vals = build_skewed_tree(vals, random.choice(["L", "R", "zigzag"]))
    else:
        ser, vals = build_random_tree(vals)
    p, q = pick_pq(vals)
    return ser, p, q


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    cases = []  # (root_ser, p, q)

    # ---- explicit edge cases ----
    # dataset examples (values match; serialization is judge-style full subtree)
    cases.append(("3 5 1 6 2 0 8 null null 7 4", 5, 1))
    cases.append(("3 5 1 6 2 0 8 null null 7 4", 5, 4))
    cases.append(("3 5 1 6 2 0 8 null null 7 4", 7, 4))   # LCA = 2
    cases.append(("3 5 1 6 2 0 8 null null 7 4", 6, 4))   # LCA = 5
    cases.append(("3 5 1 6 2 0 8 null null 7 4", 0, 8))   # LCA = 1
    cases.append(("1 2 3 null 4 null 5", 4, 5))           # LCA = root 1
    cases.append(("7 1 2 8 10 4 5 null 6", 6, 10))        # nowYourTurn: LCA = 1
    # minimum size (2 nodes), both orientations
    cases.append(("1 2", 1, 2))         # LCA = 1 (root)
    cases.append(("1 null 2", 1, 2))    # LCA = 1 (root)
    cases.append(("1 2", 2, 2))         # p == q == leaf -> node 2
    cases.append(("1 2", 1, 1))         # p == q == root  -> root subtree
    # extreme values present
    cases.append((f"{VAL_LO} {VAL_HI}", VAL_LO, VAL_HI))
    cases.append((f"{VAL_HI} {VAL_LO} 0", VAL_LO, 0))
    cases.append((f"0 {VAL_LO} {VAL_HI}", VAL_LO, VAL_HI))
    # one of p/q is an ancestor of the other (LCA is the ancestor itself)
    cases.append(("10 20 30 40 50", 20, 40))   # 20 is ancestor of 40 -> LCA 20
    cases.append(("10 20 30 40 50", 10, 50))   # root ancestor -> LCA 10

    # a few skewed (degenerate) trees
    for d in ("L", "R", "zigzag"):
        vals = distinct_values(40)
        ser, vals = build_skewed_tree(vals, d)
        p, q = pick_pq(vals)
        cases.append((ser, p, q))

    # a couple of larger trees to exercise size handling (bounded to keep the
    # batched output under the judge's 256 KB stdout cap)
    for _ in range(2):
        vals = distinct_values(random.randint(80, MAX_CASE_NODES))
        ser, vals = build_random_tree(vals)
        p = random.choice(vals)
        q = random.choice(vals)
        cases.append((ser, p, q))

    # ---- fill with random cases ----
    while len(cases) < N_CASES:
        cases.append(gen_random_case())

    cases = cases[:N_CASES]

    # ---- compute expected via the C++ oracle (judge-identical serialization) ----
    if not os.path.exists(ORACLE):
        print(f"ERROR: oracle not found at {ORACLE}; compile it first "
              f"(clang++ -std=c++17 -O2 -w -I/tmp/lca_gen "
              f"/tmp/lca_gen/oracle.cpp -o {ORACLE}).", file=sys.stderr)
        sys.exit(1)

    stdin_lines = [f"{ser}\t{p}\t{q}" for (ser, p, q) in cases]
    proc = subprocess.run([ORACLE], input="\n".join(stdin_lines) + "\n",
                          capture_output=True, text=True)
    if proc.returncode != 0:
        print("ORACLE FAILED:", proc.stderr, file=sys.stderr)
        sys.exit(1)

    expected = proc.stdout.split("\n")
    expected = expected[:len(cases)]
    if len(expected) != len(cases):
        print(f"ERROR: oracle returned {len(expected)} lines for "
              f"{len(cases)} cases", file=sys.stderr)
        sys.exit(1)

    # Guard: total batched output must stay under the judge's 1 MB stdout cap so
    # no case line is truncated during a live submit.
    total_bytes = sum(len(e) + 1 for e in expected)
    print(f"total expected output bytes: {total_bytes} (cap target {MAX_OUT_BYTES})")
    if total_bytes > MAX_OUT_BYTES:
        print("ERROR: total expected output exceeds the safe budget; reduce "
              "MAX_CASE_NODES / tree sizes.", file=sys.stderr)
        sys.exit(1)

    with open(OUT_PATH, "w") as f:
        for (ser, p, q), exp in zip(cases, expected):
            obj = {
                "inputs": {"root": ser, "p": str(p), "q": str(q)},
                "expected": exp,
            }
            f.write(json.dumps(obj) + "\n")

    # sanity: every expected non-empty (LCA always exists since p,q present)
    empties = sum(1 for e in expected if not e.strip())
    print(f"Wrote {len(cases)} cases to {OUT_PATH}  (empty expected: {empties})")


if __name__ == "__main__":
    main()
