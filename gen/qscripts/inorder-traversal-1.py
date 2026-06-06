#!/usr/bin/env python3
"""
Generator for Striver problem: inorder-traversal-1
"Iterative Inorder Traversal of Binary Tree"

Method signature (starterCpp):  vector<int> inorder(TreeNode* root)
  - single param: root  (TreeNode*)
  - input serialized level-order, space-separated, "null" for missing child,
    LeetCode-style (null nodes get no children). e.g. "1 4 null 4 2"
  - output: vector<int> -> "[4, 4, 2, 1]"

Constraints:
  - 1 <= Number of Nodes <= 100
  - -100 <= Node.val <= 100

Reference oracle: standard inorder traversal (result is identical whether
recursive or iterative). Verified against dataset examples below.

Writes: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/inorder-traversal-1.jsonl
One JSON object per line: {"inputs": {"root": "<level-order str>"}, "expected": "[..]"}
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/inorder-traversal-1.jsonl"
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


def inorder(root):
    """Iterative inorder traversal -> list[int]."""
    res = []
    st = []
    cur = root
    while cur is not None or st:
        while cur is not None:
            st.append(cur)
            cur = cur.left
        cur = st.pop()
        res.append(cur.data)
        cur = cur.right
    return res


def random_tree_tokens(n):
    """Generate a valid level-order token list for a random tree with exactly
    n nodes (1 <= n <= MAX_NODES). LeetCode-style: only real nodes can spawn
    children; nulls are emitted to fill missing children of real nodes.

    Strategy: build the tree structurally first by deciding, for each real node
    in BFS order, whether it has a left/right child (drawn from a remaining pool
    of nodes), then serialize with LeetCode trailing-null trimming semantics.
    """
    vals = [random.randint(MINV, MAXV) for _ in range(n)]
    root = TreeNode(vals[0])
    q = deque([root])
    created = 1
    # Randomly attach the remaining nodes as children of existing real nodes.
    while q and created < n:
        node = q.popleft()
        for side in ("left", "right"):
            if created >= n:
                break
            # probability of attaching a child here; biased so trees aren't
            # always perfectly balanced nor always degenerate.
            remaining = n - created
            # ensure we can still place all remaining nodes given queue capacity
            # capacity if we skip: (len(q) + open slots later). To guarantee all
            # nodes placed, attach when remaining is large relative to capacity.
            slots_after = len(q) * 2 + (1 if side == "left" else 0)
            force = remaining > slots_after  # must attach to fit all nodes
            if force or random.random() < 0.7:
                child = TreeNode(vals[created])
                created += 1
                setattr(node, side, child)
                q.append(child)
    # If we couldn't place all (shouldn't happen due to force logic), top up by
    # appending to leftmost open slots via another BFS pass.
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
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def fmt_list(lst):
    return "[" + ", ".join(str(x) for x in lst) + "]"


def make_case(tokens_str):
    root = build_tree(tokens_str.split())
    res = inorder(root)
    return {"inputs": {"root": tokens_str}, "expected": fmt_list(res)}


def verify_examples():
    examples = [
        ("1 4 null 4 2", "[4, 4, 2, 1]"),
        ("1 null 2 3", "[1, 3, 2]"),
    ]
    for inp, exp in examples:
        got = make_case(inp)["expected"]
        assert got == exp, f"MISMATCH for {inp!r}: got {got} expected {exp}"
    print("example verification OK")


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
        "1 2 3",        # full small
        "1 null 2 3",   # right-skewed-ish (example 2)
        "1 4 null 4 2", # example 1
        "1 2 null",     # left only
        "1 null 2",     # right only
        "0 -100 100",   # extremes
        "5 3 8 1 4 7 9",# balanced
    ]
    # left-skewed chain of 100 nodes
    left_chain = []
    for i in range(100):
        left_chain.append(str(random.randint(MINV, MAXV)))
        if i < 99:
            left_chain.append("__L__")  # placeholder, fix below
    # build proper left chain: each node has left child only
    lc = []
    for i in range(100):
        lc.append(str(random.randint(MINV, MAXV)))
        if i < 99:
            lc.append("__")  # left, then no right
    # construct manually: level order for pure left chain is v0 v1 null v2 null ...
    def left_chain_tokens(n):
        # root v0; v0.left=v1, v0.right=null; v1.left=v2 ...
        vs = [random.randint(MINV, MAXV) for _ in range(n)]
        toks = []
        for i, v in enumerate(vs):
            toks.append(str(v))
            if i < n - 1:
                toks.append("null")  # right child of current is null
        # this is the BFS order: v0, (v1, null), (v2, null), ...
        # but BFS expands v0 -> v1,null ; then v1 -> v2,null ; ok
        return " ".join(toks)
    def right_chain_tokens(n):
        vs = [random.randint(MINV, MAXV) for _ in range(n)]
        toks = []
        for i, v in enumerate(vs):
            toks.append(str(v))
            if i < n - 1:
                toks.append("null")  # left child null first... wait
        # For pure right chain: v0.left=null, v0.right=v1.
        # BFS: v0 -> null, v1 ; v1 -> null, v2 ; ...
        toks = []
        for i, v in enumerate(vs):
            toks.append(str(v))
            if i < n - 1:
                # current node: left=null, right=next
                toks.append("null")
        return " ".join(toks)

    # Use structural builders to be safe instead of hand BFS:
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

    edge_token_strs.append(chain(100, "left"))
    edge_token_strs.append(chain(100, "right"))
    edge_token_strs.append(chain(2, "left"))
    edge_token_strs.append(chain(2, "right"))
    # full balanced 100-ish via random builder
    edge_token_strs.append(random_tree_tokens(100))
    edge_token_strs.append(random_tree_tokens(1))

    # The live judge caps captured stdout at 256 KB (scripts/judge_exec.py
    # OUT_CAP). With 2000 cases the SUM of all "expected" outputs (one inorder
    # line per case) must stay comfortably under that, or trailing cases are
    # dropped during batched judging. Each output value is up to 4 chars + a
    # separator; a 100-node tree emits ~400 bytes. We therefore bias most random
    # trees small and budget the total output to ~200 KB (safe margin under 256).
    OUTPUT_BUDGET = 200 * 1024  # bytes of combined "expected" output

    def out_bytes(case):
        # expected is "[a, b, c]" -> the judge prints "a b c"; budget by the
        # printed form length (values + single-space separators).
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
    # Skewed size distribution: mostly tiny/small trees, occasional larger ones,
    # so we hit 2000 cases while keeping total output well under the 256 KB cap.
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
        # If we're getting close to the budget, force tiny trees so we can still
        # reach 2000 cases without overflowing the cap.
        remaining_cases = N_CASES - len(cases)
        remaining_budget = OUTPUT_BUDGET - total_out
        if remaining_budget < remaining_cases * 12:
            n = 1  # smallest possible output
        elif remaining_budget < remaining_cases * 40:
            n = random.randint(1, 6)
        ts = random_tree_tokens(n)
        if not ts:
            continue
        if ts in seen:
            if attempts > N_CASES * 50:
                # allow exact dups if we somehow run out of unique tiny trees
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

    print(f"estimated total output bytes: {total_out} (cap 256KB, budget {OUTPUT_BUDGET})")

    cases = cases[:N_CASES]
    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")
    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
