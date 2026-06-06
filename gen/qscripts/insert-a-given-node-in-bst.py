#!/usr/bin/env python3
"""
Test-case generator for Striver problem: insert-a-given-node-in-bst

Signature: TreeNode* insertIntoBST(TreeNode* root, int val)
Keys (signature order): root, val

Constraints:
  1 <= number of nodes <= 1e4
  -1e8 <= Node.val <= 1e8
  all values unique
  -1e8 <= val <= 1e8
  val does NOT exist in the original BST

Serialization (must match judge EXACTLY):
  TreeNode input/output: level-order, space/comma separated, "null" for missing child,
  LeetCode-style (null nodes get no children); trailing nulls trimmed on output.
  The judge struct uses field `data`.

Output file: one JSON obj per line:
  {"inputs": {"root": "<level-order tokens>", "val": "<int>"}, "expected": "[level-order]"}
"""
import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/insert-a-given-node-in-bst.jsonl"
N_CASES = 2000
VLO, VHI = -10**8, 10**8

random.seed(20260606)


class Node:
    __slots__ = ("data", "left", "right")
    def __init__(self, v):
        self.data = v
        self.left = None
        self.right = None


def bst_insert(root, val):
    """Reference: standard recursive BST insert (matches the C++ reference)."""
    if root is None:
        return Node(val)
    if root.data < val:
        root.right = bst_insert(root.right, val)
    else:
        root.left = bst_insert(root.left, val)
    return root


def build_from_tokens(tokens):
    """Build tree from level-order tokens (LeetCode style)."""
    if not tokens or tokens[0] == "null":
        return None
    root = Node(int(tokens[0]))
    q = deque([root])
    i = 1
    while q and i < len(tokens):
        cur = q.popleft()
        if i < len(tokens):
            if tokens[i] != "null":
                cur.left = Node(int(tokens[i]))
                q.append(cur.left)
            i += 1
        if i < len(tokens):
            if tokens[i] != "null":
                cur.right = Node(int(tokens[i]))
                q.append(cur.right)
            i += 1
    return root


def serialize_input(root):
    """Level-order with 'null', LeetCode style (no children for null), trim trailing nulls.
    Returns a space-separated token string for the INPUT root field."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        cur = q.popleft()
        if cur is None:
            out.append("null")
            continue
        out.append(str(cur.data))
        q.append(cur.left)
        q.append(cur.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def serialize_output(root):
    """Level-order bracketed, trim trailing nulls -> matches example output format."""
    if root is None:
        return "[]"
    out = []
    q = deque([root])
    while q:
        cur = q.popleft()
        if cur is None:
            out.append("null")
            continue
        out.append(str(cur.data))
        q.append(cur.left)
        q.append(cur.right)
    while out and out[-1] == "null":
        out.pop()
    return "[" + ", ".join(out) + "]"


def random_distinct_values(n, lo, hi):
    """Return n distinct ints in [lo, hi]."""
    span = hi - lo + 1
    if span <= 4 * n:
        # dense range: sample without replacement from full range
        return random.sample(range(lo, hi + 1), n)
    # sparse: sample with dedup via set
    s = set()
    while len(s) < n:
        s.add(random.randint(lo, hi))
    return list(s)


def make_random_bst(n, lo, hi):
    """Build a random valid BST by inserting n distinct random values via bst_insert.
    Returns (root, set_of_values)."""
    vals = random_distinct_values(n, lo, hi)
    random.shuffle(vals)
    root = None
    for v in vals:
        root = bst_insert(root, v)
    return root, set(vals)


def pick_insert_val(used, lo, hi):
    """Pick a value in [lo,hi] NOT in used."""
    for _ in range(10000):
        v = random.randint(lo, hi)
        if v not in used:
            return v
    # fallback: linear scan
    v = lo
    while v in used:
        v += 1
    return v


def make_case(n, lo=VLO, hi=VHI):
    root, used = make_random_bst(n, lo, hi)
    val = pick_insert_val(used, VLO, VHI)
    root_in = serialize_input(root)
    # compute expected by running reference on a FRESH copy is unnecessary:
    # bst_insert mutates root in place and returns it; rebuild root from tokens to be safe
    root2 = build_from_tokens(root_in.split())
    res = bst_insert(root2, val)
    expected = serialize_output(res)
    return {"inputs": {"root": root_in, "val": str(val)}, "expected": expected}


def make_skewed_case(n, direction):
    """Skewed tree built by inserting sorted/reverse-sorted values."""
    base = random.randint(-1000, 1000)
    vals = [base + i for i in range(n)]
    if direction == "desc":
        vals = vals[::-1]
    root = None
    for v in vals:
        root = bst_insert(root, v)
    ti = serialize_input(root)
    v = pick_insert_val(set(vals), VLO, VHI)
    r2 = build_from_tokens(ti.split())
    res = bst_insert(r2, v)
    return {"inputs": {"root": ti, "val": str(v)}, "expected": serialize_output(res)}


def harness_line_len(expected):
    """Bytes the live harness emits for one case: space-separated level-order
    tokens (value or 'null'), NO brackets/commas. We mirror that to budget the
    256 KiB stdout cap (scripts/judge_exec.py: OUT_CAP = 256*1024)."""
    toks = [t for t in expected.replace("[", " ").replace("]", " ")
            .replace(",", " ").split() if t]
    return len(" ".join(toks)) + 1  # + newline


def main():
    # NOTE on size budget (CRITICAL):
    # The live judge runs all 2000 cases in ONE batched process and caps the
    # TOTAL captured stdout at 256 KiB (scripts/judge_exec.py: OUT_CAP=256*1024).
    # Each case emits a single space-separated level-order line ("null" for a
    # missing child). If cumulative stdout exceeds 256 KiB, later cases are
    # truncated/dropped and fail. So we keep trees SMALL and budget by the
    # HARNESS output format. This is fully within the constraint (1..1e4 nodes).
    OUTPUT_BUDGET = 200_000  # bytes of harness stdout; safely under 256 KiB

    cases = []

    # --- explicit edge / structural cases ---
    # min size = 1 node
    for _ in range(20):
        cases.append(make_case(1))
    # single node at extremes
    for rootv in (VLO, VHI, 0):
        r = Node(rootv)
        ti = serialize_input(r)
        v = pick_insert_val({rootv}, VLO, VHI)
        r2 = build_from_tokens(ti.split())
        res = bst_insert(r2, v)
        cases.append({"inputs": {"root": ti, "val": str(v)}, "expected": serialize_output(res)})

    # dataset examples (sanity)
    for toks, val in (("4 2 7 1 3", 5), ("40 20 60 10 30 50 70", 25)):
        r = build_from_tokens(toks.split())
        res = bst_insert(r, val)
        cases.append({"inputs": {"root": toks, "val": str(val)},
                      "expected": serialize_output(res)})

    # skewed trees (all left / all right) — small sizes only
    for direction in ("asc", "desc"):
        for n in (2, 4, 6, 8, 12):
            cases.append(make_skewed_case(n, direction))

    # small dense trees (good coverage of small shapes)
    for n in range(1, 13):
        for _ in range(8):
            cases.append(make_case(n, -50, 50))

    # mostly tiny trees, full value range (bulk of the set)
    while len(cases) < 1500:
        n = random.randint(1, 8)
        cases.append(make_case(n))

    # a smaller slice of slightly larger trees for variety
    while len(cases) < 1900:
        n = random.randint(6, 14)
        cases.append(make_case(n))

    # a handful of the largest we allow under the tight budget
    for _ in range(25):
        n = random.randint(14, 22)
        cases.append(make_case(n))

    # fill remaining with tiny random trees
    while len(cases) < N_CASES:
        n = random.randint(1, 8)
        cases.append(make_case(n))

    cases = cases[:N_CASES]

    # enforce the total HARNESS-output budget (judge caps stdout at 256 KiB).
    total_harness = sum(harness_line_len(c["expected"]) for c in cases)
    total_expected = sum(len(c["expected"]) + 1 for c in cases)
    if total_harness > OUTPUT_BUDGET:
        raise SystemExit(
            f"harness output budget exceeded: {total_harness} > {OUTPUT_BUDGET}; "
            "reduce tree sizes")

    with open(OUT_PATH, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    print(f"wrote {len(cases)} cases to {OUT_PATH}; "
          f"harness-output bytes ~= {total_harness} (cap 262144); "
          f"expected-string bytes ~= {total_expected}")


if __name__ == "__main__":
    main()
