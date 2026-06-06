#!/usr/bin/env python3
"""
Generator + static test set for Striver problem "Bottom view of BT" (slug: bottom-view-of-bt).

Constraints:
  - 1 <= Number of Nodes <= 10^4
  - -10^3 <= Node.val <= 10^3

Input format (root): level-order, space-separated, "null" for a missing child,
LeetCode-style (null nodes get no children). Field name in judge struct is `data`.

Output format (vector<int>): "[a, b, c]" like the example outputs.

Expected outputs are computed by an external C++ oracle (compiled from /tmp/bvbt/oracle.cpp,
same logic as the judge reference) to stay self-consistent with the live judge.
"""
import os
import random
import subprocess
import json
import collections

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/bottom-view-of-bt.jsonl"
ORACLE_SRC = "/tmp/bvbt/oracle.cpp"
ORACLE_BIN = "/tmp/bvbt/oracle"

VAL_MIN, VAL_MAX = -1000, 1000
N_CASES = 2000

def ensure_oracle():
    if not os.path.exists(ORACLE_BIN) or os.path.getmtime(ORACLE_SRC) > os.path.getmtime(ORACLE_BIN):
        subprocess.run(["clang++", "-std=c++17", "-O2", "-w", ORACLE_SRC, "-o", ORACLE_BIN], check=True)

def rv():
    return random.randint(VAL_MIN, VAL_MAX)

def build_random_tree(n):
    """Build a random binary tree with exactly n nodes, return level-order token list
    with 'null' for missing children (LeetCode trimmed style)."""
    if n <= 0:
        return ["null"]
    # Node objects with random structure: grow tree by attaching children to a pool of open slots.
    # Each node has value; children assigned probabilistically while we still have nodes to place.
    # We'll construct via a list of (parent_index, side) open slots.
    values = [rv() for _ in range(n)]
    # left/right child index arrays, -1 means none
    left = [-1] * n
    right = [-1] * n
    # open slots: list of (node_index, 'L'/'R')
    # root = node 0
    open_slots = [(0, 'L'), (0, 'R')]
    next_node = 1
    while next_node < n and open_slots:
        # pick a random open slot
        idx = random.randrange(len(open_slots))
        node_i, side = open_slots.pop(idx)
        # assign next_node to this slot
        child = next_node
        next_node += 1
        if side == 'L':
            left[node_i] = child
        else:
            right[node_i] = child
        # add this child's open slots
        open_slots.append((child, 'L'))
        open_slots.append((child, 'R'))
    # Now serialize in LeetCode level-order with trimmed trailing nulls
    return serialize_levelorder(values, left, right, n)

def serialize_levelorder(values, left, right, n):
    toks = []
    q = collections.deque([0])
    while q:
        node = q.popleft()
        if node == -1:
            toks.append("null")
            continue
        toks.append(str(values[node]))
        # push children (LeetCode style: only push children of non-null nodes)
        q.append(left[node])
        q.append(right[node])
    # trim trailing nulls
    while toks and toks[-1] == "null":
        toks.pop()
    return toks

def run_oracle(token_line):
    p = subprocess.run([ORACLE_BIN], input=token_line + "\n",
                       capture_output=True, text=True, check=True)
    return p.stdout.strip()

def single_node_tree():
    return [str(rv())]

def left_chain(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n-1):
        left[i] = i+1
    return serialize_levelorder(values, left, right, n)

def right_chain(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n-1):
        right[i] = i+1
    return serialize_levelorder(values, left, right, n)

def complete_tree(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n):
        l = 2*i+1; r = 2*i+2
        if l < n: left[i] = l
        if r < n: right[i] = r
    return serialize_levelorder(values, left, right, n)

def main():
    random.seed(115)  # deterministic
    ensure_oracle()
    cases = []

    # Edge cases
    cases.append(["20", "8", "22", "5", "3", "null", "25", "null", "null", "10", "14"])
    cases.append(["20", "8", "22", "5", "3", "4", "25", "null", "null", "10", "14"])
    cases.append(single_node_tree())                 # single node
    cases.append([str(VAL_MIN)])                       # single node, min val
    cases.append([str(VAL_MAX)])                       # single node, max val
    cases.append(left_chain(50))                       # pure left chain
    cases.append(right_chain(50))                      # pure right chain
    cases.append(left_chain(10000))                    # max size left chain
    cases.append(right_chain(10000))                   # max size right chain
    cases.append(complete_tree(10000))                 # max size complete tree
    cases.append(complete_tree(15))                    # small complete

    # Random trees of varying sizes
    target = N_CASES
    while len(cases) < target:
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 50)
        elif r < 0.8:
            n = random.randint(50, 500)
        elif r < 0.95:
            n = random.randint(500, 3000)
        else:
            n = random.randint(3000, 10000)
        toks = build_random_tree(n)
        cases.append(toks)

    cases = cases[:N_CASES]

    written = 0
    with open(OUT_PATH, "w") as f:
        for toks in cases:
            line = " ".join(toks)
            expected = run_oracle(line)
            obj = {"inputs": {"root": line}, "expected": expected}
            f.write(json.dumps(obj) + "\n")
            written += 1
    print(f"Wrote {written} cases to {OUT_PATH}")

if __name__ == "__main__":
    main()
