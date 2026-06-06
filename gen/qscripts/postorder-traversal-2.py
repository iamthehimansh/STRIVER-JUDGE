#!/usr/bin/env python3
"""
Generator for Striver problem: postorder-traversal-2
"Post-order Traversal of Binary Tree using 1 stack"

Signature:  vector<int> postorder(TreeNode* root)
Input key:  root  (level-order, space-separated, "null" for missing child,
            LeetCode-style: null nodes get no children).
Output:     postorder traversal as "[a, b, c]"

Constraints:
  1 <= Number of Nodes <= 100
  -100 <= Node.val <= 100

Self-consistent reference: we build the TreeNode tree exactly the way the judge
does (level-order BFS, LeetCode-style where null gets no children), compute the
iterative postorder, and serialize the input string the same level-order way.
"""
import os
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postorder-traversal-2.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = -100, 100
MAX_NODES = 100


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def build_tree_from_level(tokens):
    """Build a tree from a LeetCode-style level-order token list (same as judge).
    tokens: list of strings, "null" for missing. Root is tokens[0].
    Null nodes get no children. Returns root Node (or None if empty)."""
    if not tokens or tokens[0] == "null":
        return None
    root = Node(int(tokens[0]))
    from collections import deque
    q = deque([root])
    i = 1
    n = len(tokens)
    while q and i < n:
        cur = q.popleft()
        # left
        if i < n:
            t = tokens[i]
            i += 1
            if t != "null":
                cur.left = Node(int(t))
                q.append(cur.left)
        # right
        if i < n:
            t = tokens[i]
            i += 1
            if t != "null":
                cur.right = Node(int(t))
                q.append(cur.right)
    return root


def serialize_level_order(root):
    """Serialize a tree back to LeetCode-style level-order tokens (trim trailing
    nulls). Used to produce the canonical input string."""
    if root is None:
        return []
    from collections import deque
    out = []
    q = deque([root])
    while q:
        cur = q.popleft()
        if cur is None:
            out.append("null")
            continue
        out.append(str(cur.val))
        q.append(cur.left)
        q.append(cur.right)
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return out


def postorder(root):
    """Iterative postorder (reference oracle)."""
    res = []
    if root is None:
        return res
    stack = []
    cur = root
    last = None
    while stack or cur is not None:
        if cur is not None:
            stack.append(cur)
            cur = cur.left
        else:
            peek = stack[-1]
            if peek.right is not None and last is not peek.right:
                cur = peek.right
            else:
                res.append(peek.val)
                last = stack.pop()
    return res


def random_tree(n):
    """Build a random binary tree with exactly n nodes (1..n), returns root.
    Each new node is attached to a randomly chosen free slot (left/right) of an
    existing node -> arbitrary shapes including skewed/full/balanced."""
    root = Node(random.randint(VAL_MIN, VAL_MAX))
    # list of (node, slot) free slots
    free = [(root, "left"), (root, "right")]
    for _ in range(n - 1):
        idx = random.randrange(len(free))
        parent, slot = free.pop(idx)
        node = Node(random.randint(VAL_MIN, VAL_MAX))
        setattr(parent, slot, node)
        free.append((node, "left"))
        free.append((node, "right"))
    return root


# The live batched judge caps a single run's captured stdout at 256 KB
# (scripts/judge_exec.py OUT_CAP). 2000 cases of up-to-100-node trees would
# overflow that and silently truncate the tail, so we keep the bulk of the
# random trees small (the algorithm is size-independent) while still covering
# the full 1..100 node range via dedicated edge cases. We verify the total
# output stays under the cap in main().
OUT_CAP = 256 * 1024
SMALL_MAX = 24  # node-count cap for the bulk of random cases


def gen_inputs():
    cases = []
    # ---- fixed edge cases ----
    # single node, extremes
    cases.append(["0"])
    cases.append(["100"])
    cases.append(["-100"])
    cases.append(["-100"])
    cases.append(["100"])
    # dataset examples
    cases.append(["1", "4", "null", "4", "2"])
    cases.append(["1", "null", "2", "3"])
    # nowYourTurn example
    cases.append(["5", "1", "2", "8", "null", "4", "5", "null", "6"])
    # left-skewed (chain via left only)
    cases.append(["1", "2", "null", "3", "null", "4"])
    # right-skewed
    cases.append(["1", "null", "2", "null", "3", "null", "4"])
    # full small tree
    cases.append(["1", "2", "3", "4", "5", "6", "7"])

    # ---- a handful of MAX-size (100 node) edge cases of varied shapes ----
    # left-skewed chain of 100 nodes: node null node null ... (last node no null)
    chain_l = []
    for k in range(MAX_NODES):
        chain_l.append(str(random.randint(VAL_MIN, VAL_MAX)))
        if k < MAX_NODES - 1:
            chain_l.append("null")
    cases.append(chain_l)
    # right-skewed chain of 100 nodes: node null node ... -> always right
    chain_r = [str(random.randint(VAL_MIN, VAL_MAX))]
    for k in range(MAX_NODES - 1):
        chain_r.append("null")
        chain_r.append(str(random.randint(VAL_MIN, VAL_MAX)))
    cases.append(chain_r)
    # complete tree of 100 nodes (no internal nulls)
    comp = [str(random.randint(VAL_MIN, VAL_MAX)) for _ in range(MAX_NODES)]
    cases.append(comp)
    # a few random 100-node trees
    for _ in range(8):
        cases.append(serialize_level_order(random_tree(MAX_NODES)))

    # ---- random cases to fill up (kept small to respect the 256KB cap) ----
    while len(cases) < N_CASES:
        n = random.randint(1, SMALL_MAX)
        root = random_tree(n)
        toks = serialize_level_order(root)
        cases.append(toks)
    return cases[:N_CASES]


def fmt_arr(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def main():
    random.seed(20260606)
    cases = gen_inputs()
    lines = []
    for toks in cases:
        root = build_tree_from_level(toks)
        expected = postorder(root)
        # canonical input string (level-order, space separated)
        root_str = " ".join(serialize_level_order(root))
        obj = {"inputs": {"root": root_str}, "expected": fmt_arr(expected)}
        lines.append(json.dumps(obj))
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    # Estimate the batched-judge stdout size: one space-separated postorder line
    # (without brackets/commas) per case + a newline. Must stay < 256KB so the
    # live judge does not truncate the tail of the batch.
    out_bytes = 0
    for ln in lines:
        rec = json.loads(ln)
        vals = rec["expected"].strip()[1:-1]
        flat = vals.replace(", ", " ")
        out_bytes += len(flat) + 1
    print(f"wrote {len(lines)} cases to {OUT_PATH}")
    print(f"estimated batched judge stdout: {out_bytes} bytes (cap {OUT_CAP})")
    if out_bytes >= OUT_CAP:
        print("WARNING: estimated output exceeds 256KB cap; reduce SMALL_MAX or case count")


if __name__ == "__main__":
    main()
