#!/usr/bin/env python3
"""
Test-case generator for Striver problem: two-sum-in-bst
"Two Sum In BST | Check if there exists a pair with Sum K"

Signature: bool twoSumBST(TreeNode* root, int k)
Output: "true" if there exist two distinct nodes in the BST whose values sum to k,
        else "false".

Constraints:
  1 <= Number of Nodes <= 10^4
  -10^4 <= Node.val <= 10^4
  -10^5 <= k <= 10^5

The judge builds the tree level-order from a space-separated string using the
TreeNode{.data} struct, LeetCode-style ("null" = missing child). We build a
VALID BST in memory, then serialize level-order (trailing nulls trimmed) the
same way the judge's pr(TreeNode*) would.

Output line format:
  {"inputs": {"root": "<level-order>", "k": "<int>"}, "expected": "true"|"false"}

Key order = signature order = root, k.
"""
import json
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/two-sum-in-bst.jsonl"
N_CASES = 2000
VAL_MIN = -10_000
VAL_MAX = 10_000
K_MIN = -100_000
K_MAX = 100_000
MAX_NODES = 10_000


class Node:
    __slots__ = ("val", "left", "right")

    def __init__(self, val):
        self.val = val
        self.left = None
        self.right = None


def bst_insert(root, val):
    """Insert into BST; ignore duplicates (keep distinct values)."""
    if root is None:
        return Node(val), True
    cur = root
    while True:
        if val == cur.val:
            return root, False  # duplicate, skip
        if val < cur.val:
            if cur.left is None:
                cur.left = Node(val)
                return root, True
            cur = cur.left
        else:
            if cur.right is None:
                cur.right = Node(val)
                return root, True
            cur = cur.right


def build_bst(values):
    root = None
    for v in values:
        root, _ = bst_insert(root, v)
    return root


def serialize_levelorder(root):
    """LeetCode-style level-order, 'null' for missing children, trailing nulls trimmed."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is not None:
            out.append(str(n.val))
            q.append(n.left)
            q.append(n.right)
        else:
            out.append("null")
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def inorder_vals(root):
    """Return sorted (ascending) list of values via inorder traversal."""
    out = []
    stack = []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        cur = cur.right
    return out


def two_sum_bst(root, k):
    """Two pointers on sorted inorder. Distinct nodes required (i != j)."""
    vals = inorder_vals(root)
    i, j = 0, len(vals) - 1
    while i < j:
        s = vals[i] + vals[j]
        if s == k:
            return True
        if s < k:
            i += 1
        else:
            j -= 1
    return False


def gen_distinct_values(n, lo=VAL_MIN, hi=VAL_MAX):
    """n distinct values in [lo, hi]."""
    total = hi - lo + 1
    if total <= n:
        return random.sample(range(lo, hi + 1), total)
    if n > total // 2:
        # sample without replacement is cheap; use random.sample directly
        return random.sample(range(lo, hi + 1), n)
    s = set()
    while len(s) < n:
        s.add(random.randint(lo, hi))
    return list(s)


def make_case():
    """Return (root, root_str, k)."""
    # node count distribution: lots of small + some large
    r = random.random()
    if r < 0.2:
        n = random.randint(1, 3)
    elif r < 0.65:
        n = random.randint(1, 30)
    elif r < 0.9:
        n = random.randint(1, 300)
    elif r < 0.98:
        n = random.randint(1, 2000)
    else:
        n = random.randint(1, MAX_NODES)

    # value range mode
    mode = random.random()
    if mode < 0.25:
        # small value range, forces collisions/dupes (we skip dupes -> fewer nodes)
        span = max(2, min(VAL_MAX - VAL_MIN + 1, n * 3 + random.randint(0, 20)))
        lo = random.randint(VAL_MIN, VAL_MAX - span + 1)
        hi = lo + span - 1
        vals = gen_distinct_values(n, lo, hi)
    elif mode < 0.4:
        # narrow band somewhere
        lo = random.randint(VAL_MIN, VAL_MAX - 1)
        hi = random.randint(lo + 1, VAL_MAX)
        if hi - lo + 1 < n:
            lo, hi = VAL_MIN, VAL_MAX
        vals = gen_distinct_values(n, lo, hi)
    else:
        vals = gen_distinct_values(n, VAL_MIN, VAL_MAX)

    random.shuffle(vals)  # random insertion order -> varied tree shapes
    root = build_bst(vals)
    root_str = serialize_levelorder(root)

    sorted_vals = sorted(vals)

    # k selection: bias toward existing pair-sums to get more "true" cases
    kr = random.random()
    if kr < 0.45 and len(sorted_vals) >= 2:
        # pick a real pair sum -> "true"
        a, b = random.sample(sorted_vals, 2)
        k = a + b
    elif kr < 0.55 and sorted_vals:
        # twice a node value (allowed only if there's another node equal — won't be since distinct)
        # this will typically be "false" unless coincidence; that's fine for diversity
        k = 2 * random.choice(sorted_vals)
    elif kr < 0.65:
        k = K_MIN  # extreme low
    elif kr < 0.75:
        k = K_MAX  # extreme high
    elif kr < 0.85:
        k = 0
    elif kr < 0.92 and sorted_vals:
        # near a real pair sum (off by 1)
        a, b = random.sample(sorted_vals, 2) if len(sorted_vals) >= 2 else (sorted_vals[0], sorted_vals[0])
        k = a + b + random.choice([-1, 1])
        k = max(K_MIN, min(K_MAX, k))
    else:
        k = random.randint(K_MIN, K_MAX)

    # ensure k within constraints (it always will be for picked pair sums since
    # 2 * VAL_MAX = 20_000 < K_MAX = 100_000, and 2 * VAL_MIN = -20_000 > K_MIN)
    if k < K_MIN: k = K_MIN
    if k > K_MAX: k = K_MAX
    return root, root_str, k


def main():
    random.seed(20260606)
    lines = []
    seen = set()

    # --- explicit edge cases first ---
    edge_cases = []
    # dataset examples
    edge_cases.append(([5, 3, 6, 2, 4, None, 7], 9))   # true
    edge_cases.append(([5, 3, 6, 2, 4, None, 7], 14))  # false
    edge_cases.append(([6, 5, 7, 4, None, None, 10], 12))  # 5+7=12 -> true
    # single node — can never have two nodes summing to k
    edge_cases.append(([1], 2))     # false (only one node)
    edge_cases.append(([1], 1))     # false
    edge_cases.append(([0], 0))     # false
    edge_cases.append(([VAL_MIN], 2 * VAL_MIN))  # false (single node)
    edge_cases.append(([VAL_MAX], 2 * VAL_MAX))  # false (single node)
    # two nodes
    edge_cases.append(([2, 1], 3))         # true
    edge_cases.append(([2, 1], 4))         # false
    edge_cases.append(([2, 1], 0))         # false
    edge_cases.append(([VAL_MAX, VAL_MIN], 0))  # true (-10000 + 10000 = 0)
    edge_cases.append(([VAL_MAX, VAL_MIN], 1))  # false
    # negative values
    edge_cases.append(([-1, -2, 0], -3))   # true: -1 + -2
    edge_cases.append(([-1, -2, 0], -2))   # true: -2 + 0
    edge_cases.append(([-1, -2, 0], 1))    # false
    # k boundary
    edge_cases.append(([VAL_MAX, VAL_MAX - 1], K_MAX))  # false (max pair sum = 19999 < 100000)
    edge_cases.append(([VAL_MIN, VAL_MIN + 1], K_MIN))  # false
    # right-skewed / left-skewed
    edge_cases.append((list(range(1, 11)), 19))   # 9+10=19 -> true
    edge_cases.append((list(range(1, 11)), 21))   # max pair 9+10=19 -> false
    edge_cases.append((list(range(10, 0, -1)), 3))  # 1+2=3 -> true
    edge_cases.append((list(range(10, 0, -1)), 1))  # false
    # zero pair
    edge_cases.append(([-5, -3, 5, -7, None, 3, 7], 0))  # -5+5=0 -> true
    edge_cases.append(([-5, -3, 5, -7, None, 3, 7], 100))  # false

    for vals, k in edge_cases:
        vals = [v for v in vals if v is not None]
        root = build_bst(vals)
        rs = serialize_levelorder(root)
        exp = two_sum_bst(root, k)
        sig = (rs, k)
        if sig in seen:
            continue
        seen.add(sig)
        lines.append({
            "inputs": {"root": rs, "k": str(k)},
            "expected": "true" if exp else "false",
        })

    attempts = 0
    while len(lines) < N_CASES and attempts < N_CASES * 50:
        attempts += 1
        root, rs, k = make_case()
        if not rs:
            continue  # skip empty tree (constraints say >=1 node, but be safe)
        sig = (rs, k)
        if sig in seen:
            continue
        seen.add(sig)
        exp = two_sum_bst(root, k)
        lines.append({
            "inputs": {"root": rs, "k": str(k)},
            "expected": "true" if exp else "false",
        })

    with open(OUT_PATH, "w") as f:
        for obj in lines[:N_CASES]:
            f.write(json.dumps(obj) + "\n")
    print("wrote", min(len(lines), N_CASES), "cases to", OUT_PATH)


if __name__ == "__main__":
    main()
