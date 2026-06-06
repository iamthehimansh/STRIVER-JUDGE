#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Boundary Traversal (slug: boundary-traversal).

Method signature (starterCpp):
    vector<int> boundary(TreeNode* root)

Input key: "root"  -> TreeNode* serialized LeetCode-style, level-order, space-separated,
                       "null" for a missing child (LeetCode rule: null nodes get no children).
Output:    vector<int> serialized space-separated (judge compares leniently).

Strategy:
  - Generate random binary trees within constraints:
        0 <= number of nodes <= 10^4 ,  -10^3 <= node.val <= 10^3
  - Serialize each tree exactly the way the judge's rdTree() expects (level-order,
    "null" for absent children, trailing nulls trimmed).
  - Compute the expected boundary traversal using a Python oracle that mirrors the
    accepted C++ reference EXACTLY (left boundary, then leaves L->R, then reversed
    right boundary; single-node tree -> just the root).
  - Write 2000 JSONL lines to generated-tests/boundary-traversal.jsonl.

The Python oracle is validated below against the dataset examples before generating.
"""
import json, os, random, sys
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/boundary-traversal.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = -1000, 1000
MAX_NODES = 10000

# ----------------------------------------------------------------------------
# Tree model: a node is a dict {"v": int, "l": node|None, "r": node|None}
# ----------------------------------------------------------------------------

def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)

def gen_tree(n):
    """Build a random binary tree with exactly n nodes (n>=0)."""
    if n == 0:
        return None
    root = {"v": rand_val(), "l": None, "r": None}
    # list of (node, slot) open child slots; slot in {"l","r"}
    open_slots = [(root, "l"), (root, "r")]
    created = 1
    while created < n and open_slots:
        idx = random.randrange(len(open_slots))
        node, slot = open_slots.pop(idx)
        child = {"v": rand_val(), "l": None, "r": None}
        node[slot] = child
        created += 1
        # add child's own slots
        open_slots.append((child, "l"))
        open_slots.append((child, "r"))
    return root

def gen_left_skewed(n):
    if n == 0:
        return None
    root = {"v": rand_val(), "l": None, "r": None}
    cur = root
    for _ in range(n - 1):
        cur["l"] = {"v": rand_val(), "l": None, "r": None}
        cur = cur["l"]
    return root

def gen_right_skewed(n):
    if n == 0:
        return None
    root = {"v": rand_val(), "l": None, "r": None}
    cur = root
    for _ in range(n - 1):
        cur["r"] = {"v": rand_val(), "l": None, "r": None}
        cur = cur["r"]
    return root

def gen_complete(n):
    """Complete binary tree with n nodes (array-style)."""
    if n == 0:
        return None
    nodes = [{"v": rand_val(), "l": None, "r": None} for _ in range(n)]
    for i in range(n):
        li, ri = 2 * i + 1, 2 * i + 2
        if li < n:
            nodes[i]["l"] = nodes[li]
        if ri < n:
            nodes[i]["r"] = nodes[ri]
    return nodes[0]

# ----------------------------------------------------------------------------
# Serialize tree to judge's level-order format (LeetCode-style, trim trailing nulls)
# ----------------------------------------------------------------------------

def serialize(root):
    # Empty tree: emit the literal token "null" (NOT an empty string). The judge's
    # batch driver skips wholly-empty stdin lines, which would shift the answer key
    # by one; "null" is non-empty and rdTree("null") correctly yields a nullptr root.
    if root is None:
        return "null"
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is None:
            out.append("null")
        else:
            out.append(str(n["v"]))
            q.append(n["l"])
            q.append(n["r"])
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)

# ----------------------------------------------------------------------------
# Oracle: mirror the accepted C++ reference exactly.
# ----------------------------------------------------------------------------

def _is_leaf(n):
    return n is not None and n["l"] is None and n["r"] is None

def boundary(root):
    """Iterative mirror of the accepted C++ reference (no recursion -> no stack
    overflow on deeply skewed trees of up to 10^4 nodes)."""
    if root is None:
        return []
    # single-node tree -> just the root
    if root["l"] is None and root["r"] is None:
        return [root["v"]]

    ans = [root["v"]]

    # left boundary (top-down): start at root.left, prefer left then right,
    # stop at (and exclude) leaves.
    node = root["l"]
    while node is not None and not _is_leaf(node):
        ans.append(node["v"])
        node = node["l"] if node["l"] is not None else node["r"]

    # leaves left-to-right over the WHOLE tree's left subtree then right subtree,
    # matching reference order: leaf(root.left) then leaf(root.right).
    def collect_leaves(start):
        if start is None:
            return
        # explicit pre-order using a stack, pushing right before left so that
        # left children are processed first (left-to-right leaf order).
        stack = [start]
        while stack:
            n = stack.pop()
            if n["l"] is None and n["r"] is None:
                ans.append(n["v"])
            else:
                if n["r"] is not None:
                    stack.append(n["r"])
                if n["l"] is not None:
                    stack.append(n["l"])
    collect_leaves(root["l"])
    collect_leaves(root["r"])

    # right boundary, collected top-down then appended in reverse.
    rstack = []
    node = root["r"]
    while node is not None and not _is_leaf(node):
        rstack.append(node["v"])
        node = node["r"] if node["r"] is not None else node["l"]
    ans.extend(reversed(rstack))
    return ans

def fmt_out(vals):
    return "[" + ", ".join(str(x) for x in vals) + "]"

# ----------------------------------------------------------------------------
# Self-test against dataset examples before generating.
# ----------------------------------------------------------------------------

def parse_level_order(s):
    """Inverse of judge rdTree: build tree dict from level-order tokens."""
    toks = [t for t in s.replace("[", " ").replace("]", " ").replace(",", " ").split()]
    if not toks or toks[0] == "null":
        return None
    root = {"v": int(toks[0]), "l": None, "r": None}
    q = deque([root])
    i = 1
    while q and i < len(toks):
        node = q.popleft()
        if i < len(toks):
            if toks[i] != "null":
                node["l"] = {"v": int(toks[i]), "l": None, "r": None}
                q.append(node["l"])
            i += 1
        if i < len(toks):
            if toks[i] != "null":
                node["r"] = {"v": int(toks[i]), "l": None, "r": None}
                q.append(node["r"])
            i += 1
    return root

def self_test():
    cases = [
        ("1 2 3 4 5 6 7 null null 8 9", [1, 2, 4, 8, 9, 6, 7, 3]),
        ("1 2 null 4 9 6 5 3 null null null null null 7 8", [1, 2, 4, 6, 5, 7, 8]),
    ]
    for s, exp in cases:
        got = boundary(parse_level_order(s))
        assert got == exp, f"SELF-TEST FAILED: {s!r} -> {got} != {exp}"
    print("self-test OK", file=sys.stderr)

# ----------------------------------------------------------------------------
# Generation
# ----------------------------------------------------------------------------

# NOTE on sizing: the judge runs all 2000 cases in ONE batched process and the
# local executor (scripts/judge_exec.py) caps captured stdout at 256 KiB
# (OUT_CAP = 256*1024). If the SUM of all per-case output lines exceeds that,
# later lines are dropped and the answer key shifts. So we keep node counts
# moderate and enforce a global output-byte budget well under 256 KiB. Node
# count always stays within the constraint (<= 10^4); we simply don't need to
# max it on every case.
OUTPUT_BUDGET_BYTES = 200_000   # safely under the 256 KiB (262,144) cap

def make_case(i):
    # deterministic-ish mix of shapes + sizes; include edge cases up front
    if i == 0:
        return None                       # empty tree (0 nodes)
    if i == 1:
        return gen_tree(1)                # single node
    if i == 2:
        return gen_left_skewed(2)
    if i == 3:
        return gen_right_skewed(2)
    if i == 4:
        return gen_left_skewed(120)       # long left boundary (output ~120 nums)
    if i == 5:
        return gen_right_skewed(120)      # long right boundary
    if i == 6:
        return gen_complete(31)
    if i == 7:
        return gen_complete(255)          # moderate complete tree
    if i == 8:
        return gen_tree(400)              # one larger random tree

    r = random.random()
    if r < 0.15:
        n = random.randint(0, 1)
    elif r < 0.55:
        n = random.randint(1, 12)
    elif r < 0.85:
        n = random.randint(1, 60)
    elif r < 0.97:
        n = random.randint(1, 200)
    else:
        n = random.randint(1, 500)
    shape = random.random()
    if shape < 0.6:
        return gen_tree(n)
    elif shape < 0.75:
        return gen_left_skewed(n)
    elif shape < 0.90:
        return gen_right_skewed(n)
    else:
        return gen_complete(n)

def main():
    random.seed(20240606)
    self_test()
    sys.setrecursionlimit(100000)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    written = 0
    total_out = 0
    with open(OUT, "w") as f:
        for i in range(N_CASES):
            root = make_case(i)
            exp_list = boundary(root)
            # Global output budget: if a case would push total output over the
            # judge's stdout cap, shrink it to a tiny tree instead (still valid).
            line_bytes = sum(len(str(x)) for x in exp_list) + max(0, len(exp_list) - 1) + 1
            if total_out + line_bytes > OUTPUT_BUDGET_BYTES:
                root = gen_tree(random.randint(1, 8))
                exp_list = boundary(root)
                line_bytes = sum(len(str(x)) for x in exp_list) + max(0, len(exp_list) - 1) + 1
            total_out += line_bytes
            ser = serialize(root)
            exp = fmt_out(exp_list)
            obj = {"inputs": {"root": ser}, "expected": exp}
            f.write(json.dumps(obj) + "\n")
            written += 1
    print(f"wrote {written} cases to {OUT} (approx total output {total_out} bytes)",
          file=sys.stderr)

if __name__ == "__main__":
    main()
