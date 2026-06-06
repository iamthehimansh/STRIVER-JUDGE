#!/usr/bin/env python3
"""
Generator for Striver problem: postorder-traversal-1
"Post-order Traversal of Binary Tree using 2 stack"

Method signature (starterCpp):  vector<int> postorder(TreeNode* root)
  - single param: root  (TreeNode*)
  - input serialized level-order, space-separated, "null" for missing child,
    LeetCode-style (null nodes get no children). e.g. "1 4 null 4 2"
  - output: vector<int> -> "[4, 2, 4, 1]"

Constraints:
  - 1 <= Number of Nodes <= 100
  - -100 <= Node.val <= 100

Reference oracle: standard postorder traversal (result is identical whether
recursive or iterative / 2-stack). Verified against dataset examples below
and against the live judge (passed == total).

Writes: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postorder-traversal-1.jsonl
One JSON object per line: {"inputs": {"root": "<level-order str>"}, "expected": "[..]"}
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postorder-traversal-1.jsonl"
N_CASES = 2000
MINV, MAXV = -100, 100
MAX_NODES = 100


class TreeNode:
    __slots__ = ("data", "left", "right")
    def __init__(self, v):
        self.data = v
        self.left = None
        self.right = None


def build_tree(tokens):
    """Build tree from level-order tokens (list of str). LeetCode-style:
    null nodes contribute no children. Returns root (or None)."""
    if not tokens or tokens[0] == "null":
        return None
    it = iter(tokens)
    root = TreeNode(int(next(it)))
    q = deque([root])
    while q:
        node = q.popleft()
        # left
        try:
            t = next(it)
        except StopIteration:
            break
        if t != "null":
            node.left = TreeNode(int(t))
            q.append(node.left)
        # right
        try:
            t = next(it)
        except StopIteration:
            break
        if t != "null":
            node.right = TreeNode(int(t))
            q.append(node.right)
    return root


def postorder(root):
    """Iterative postorder traversal (2-stack method) -> list[int].
    Identical result to recursive postorder."""
    res = []
    if root is None:
        return res
    st1 = [root]
    st2 = []
    while st1:
        node = st1.pop()
        st2.append(node)
        if node.left is not None:
            st1.append(node.left)
        if node.right is not None:
            st1.append(node.right)
    while st2:
        res.append(st2.pop().data)
    return res


def serialize_tree(root):
    """Serialize tree level-order, 'null' for missing children, LeetCode-style:
    null placeholders only appear for missing children of real nodes; trailing
    nulls trimmed (a null node produces no further entries)."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        node = q.popleft()
        if node is None:
            out.append("null")
            continue
        out.append(str(node.data))
        q.append(node.left)
        q.append(node.right)
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def random_tree_tokens(n):
    """Generate a valid level-order token list for a random tree with exactly
    n nodes (1 <= n <= MAX_NODES). LeetCode-style: only real nodes can spawn
    children; nulls are emitted to fill missing children of real nodes."""
    vals = [random.randint(MINV, MAXV) for _ in range(n)]
    root = TreeNode(vals[0])
    q = deque([root])
    created = 1
    while q and created < n:
        node = q.popleft()
        for side in ("left", "right"):
            if created >= n:
                break
            remaining = n - created
            slots_after = len(q) * 2 + (1 if side == "left" else 0)
            force = remaining > slots_after  # must attach to fit all nodes
            if force or random.random() < 0.7:
                child = TreeNode(vals[created])
                created += 1
                setattr(node, side, child)
                q.append(child)
    if created < n:
        q2 = deque([root])
        while q2 and created < n:
            node = q2.popleft()
            if node.left is None and created < n:
                node.left = TreeNode(vals[created]); created += 1
                q2.append(node.left)
            elif node.left is not None:
                q2.append(node.left)
            if node.right is None and created < n:
                node.right = TreeNode(vals[created]); created += 1
                q2.append(node.right)
            elif node.right is not None:
                q2.append(node.right)
    return serialize_tree(root)


def fmt_list(lst):
    return "[" + ", ".join(str(x) for x in lst) + "]"


def make_case(tokens_str):
    root = build_tree(tokens_str.split())
    res = postorder(root)
    return {"inputs": {"root": tokens_str}, "expected": fmt_list(res)}


def verify_examples():
    examples = [
        ("1 4 null 4 2", "[4, 2, 4, 1]"),
        ("1 null 2 3", "[3, 2, 1]"),
    ]
    for inp, exp in examples:
        got = make_case(inp)["expected"]
        assert got == exp, f"MISMATCH for {inp!r}: got {got} expected {exp}"
    print("example verification OK")


def chain(n, direction):
    root = TreeNode(random.randint(MINV, MAXV))
    cur = root
    for _ in range(n - 1):
        child = TreeNode(random.randint(MINV, MAXV))
        if direction == "left":
            cur.left = child
        else:
            cur.right = child
        cur = child
    return serialize_tree(root)


def main():
    random.seed(20260606)
    verify_examples()

    cases = []
    seen = set()

    # ---- edge cases ----
    edge_token_strs = [
        "1",            # single node, min size
        "-100",         # single node extreme low
        "100",          # single node extreme high
        "0",            # single node zero
        "1 2 3",        # full small
        "1 null 2 3",   # example 2
        "1 4 null 4 2", # example 1
        "1 2 null",     # left only
        "1 null 2",     # right only
        "0 -100 100",   # extremes
        "5 3 8 1 4 7 9",# balanced
        "-100 -100 -100",  # all same extreme low
        "100 100 100",     # all same extreme high
    ]
    edge_token_strs.append(chain(100, "left"))
    edge_token_strs.append(chain(100, "right"))
    edge_token_strs.append(chain(2, "left"))
    edge_token_strs.append(chain(2, "right"))
    edge_token_strs.append(random_tree_tokens(100))
    edge_token_strs.append(random_tree_tokens(1))

    # The live judge caps captured stdout. Keep total output well under it by
    # biasing trees small (postorder emits one value per node).
    OUTPUT_BUDGET = 200 * 1024  # bytes of combined "expected" output

    def out_bytes(case):
        vals = case["expected"].strip("[]")
        vals = [v for v in vals.split(",") if v.strip() != ""]
        return sum(len(v.strip()) for v in vals) + max(0, len(vals) - 1) + 1

    total_out = 0

    for ts in edge_token_strs:
        if not ts:
            continue
        if ts in seen:
            continue
        seen.add(ts)
        c = make_case(ts)
        cases.append(c)
        total_out += out_bytes(c)

    # ---- random cases ----
    def random_size():
        r = random.random()
        if r < 0.55:
            return random.randint(1, 15)     # tiny
        elif r < 0.85:
            return random.randint(16, 40)    # small/medium
        elif r < 0.97:
            return random.randint(41, 70)    # medium/large
        else:
            return random.randint(71, MAX_NODES)  # large (rare)

    attempts = 0
    while len(cases) < N_CASES:
        attempts += 1
        n = random_size()
        remaining_cases = N_CASES - len(cases)
        remaining_budget = OUTPUT_BUDGET - total_out
        if remaining_budget < remaining_cases * 12:
            n = 1
        elif remaining_budget < remaining_cases * 40:
            n = random.randint(1, 6)
        ts = random_tree_tokens(n)
        if not ts:
            continue
        if ts in seen:
            if attempts > N_CASES * 50:
                pass
            else:
                continue
        seen.add(ts)
        # sanity: node count within bounds, values within range
        toks = ts.split()
        nodecount = sum(1 for t in toks if t != "null")
        assert 1 <= nodecount <= MAX_NODES, f"bad node count {nodecount}"
        for t in toks:
            if t != "null":
                assert MINV <= int(t) <= MAXV, f"val out of range {t}"
        c = make_case(ts)
        cases.append(c)
        total_out += out_bytes(c)

    print(f"estimated total output bytes: {total_out} (budget {OUTPUT_BUDGET})")

    cases = cases[:N_CASES]
    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
