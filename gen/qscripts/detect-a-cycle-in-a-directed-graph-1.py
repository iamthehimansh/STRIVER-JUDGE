#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Detect a cycle in a directed graph"
slug: detect-a-cycle-in-a-directed-graph-1

Signature (starterCpp):  bool isCyclic(int N, vector<int> adj[])
The judge's batch harness does NOT support `vector<int> adj[]` (array params are
unsupported), so a runnable `class Solution` reference must use
`vector<vector<int>>& adj`. We therefore emit jsonl keys matching that adjacency
representation. Keys used: "V" (vertex count) and "adj" (adjacency list as 2D array),
matching the dataset's own example/testcase keys.

Constraints (must ALL hold for every generated input):
  1 <= V <= 10^4
  adj.size() == V
  0 <= adj[i][j] < V
  1 <= sum(adj[i].size()) <= 10^4   (total edges)

Output line format (one JSON object per line):
  {"inputs": {"V": "<int>", "adj": "[[...],[...]]"}, "expected": "True"|"False"}

Expected is computed with Kahn's algorithm (BFS topological sort): a directed graph
has a cycle iff a topological ordering cannot include all V vertices.
"""

import json
import os
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/detect-a-cycle-in-a-directed-graph-1.jsonl"
N_CASES = 2000
MAX_V = 10**4
MAX_EDGES = 10**4

random.seed(20260606)


def has_cycle(V, adj):
    """Kahn's algorithm. Returns True iff the directed graph contains a cycle."""
    indeg = [0] * V
    for u in range(V):
        for w in adj[u]:
            indeg[w] += 1
    q = deque(i for i in range(V) if indeg[i] == 0)
    cnt = 0
    while q:
        node = q.popleft()
        cnt += 1
        for w in adj[node]:
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    return cnt != V


def fmt_adj(adj):
    """Format adjacency list as a 2D-array string: [[1,2],[],[0]]"""
    return "[" + ",".join("[" + ",".join(str(x) for x in row) + "]" for row in adj) + "]"


def empty_adj(V):
    return [[] for _ in range(V)]


def add_edge(adj, u, v):
    adj[u].append(v)


# ---------------------------------------------------------------------------
# Random graph builders. Each returns (V, adj) with sum(len(adj[i])) within bounds.
# We deliberately mix acyclic (DAG) and cyclic graphs so both expected outcomes
# appear, including tricky near-DAG-with-one-back-edge cases.
# ---------------------------------------------------------------------------

def gen_random(force=None):
    """force in {None,'acyclic','cyclic'}; choose V and edge count within bounds."""
    # Vertex count: bias toward small/medium but include large.
    r = random.random()
    if r < 0.45:
        V = random.randint(1, 12)
    elif r < 0.75:
        V = random.randint(2, 120)
    elif r < 0.92:
        V = random.randint(2, 1500)
    else:
        V = random.randint(2, MAX_V)

    adj = empty_adj(V)
    # max edges we may add (respect global cap)
    cap = MAX_EDGES

    if force == 'acyclic' or (force is None and random.random() < 0.5):
        # Build a DAG: only edges from lower perm-rank to higher perm-rank.
        perm = list(range(V))
        random.shuffle(perm)
        pos = {node: i for i, node in enumerate(perm)}
        # target edge count
        max_possible = min(cap, V * 3)
        e_target = random.randint(0, max(0, max_possible))
        e_target = min(e_target, cap)
        edges = set()
        attempts = 0
        while len(edges) < e_target and attempts < e_target * 5 + 50:
            attempts += 1
            a = random.randrange(V)
            b = random.randrange(V)
            if pos[a] < pos[b]:  # a -> b only if a earlier in topo order
                if (a, b) not in edges:
                    edges.add((a, b))
        for (a, b) in edges:
            add_edge(adj, a, b)
        # Ensure at least 1 edge total (constraint sum >= 1) when possible.
        if sum(len(x) for x in adj) == 0 and V >= 2:
            # add a forward edge between two distinct perm-adjacent nodes
            a, b = perm[0], perm[1]
            add_edge(adj, a, b)
        elif sum(len(x) for x in adj) == 0 and V == 1:
            # V==1: only possible edge is self loop 0->0, which would be a cycle.
            # For an "acyclic" V==1 graph we still need >=1 edge -> impossible
            # without a cycle. So switch to cyclic self-loop.
            add_edge(adj, 0, 0)
        return V, adj

    # ---- cyclic branch ----
    # Start from a DAG then add at least one back edge to guarantee a cycle.
    perm = list(range(V))
    random.shuffle(perm)
    pos = {node: i for i, node in enumerate(perm)}
    max_possible = min(cap - 1, V * 3)
    e_target = random.randint(0, max(0, max_possible))
    edges = set()
    attempts = 0
    while len(edges) < e_target and attempts < e_target * 5 + 50:
        attempts += 1
        a = random.randrange(V)
        b = random.randrange(V)
        if pos[a] < pos[b]:
            edges.add((a, b))
    for (a, b) in edges:
        add_edge(adj, a, b)

    total = sum(len(x) for x in adj)
    # Add a guaranteed cycle. Pick cycle length k (>=1: self-loop allowed).
    remaining = cap - total
    if remaining <= 0:
        # remove one forward edge to make room
        for u in range(V):
            if adj[u]:
                adj[u].pop()
                total -= 1
                remaining = cap - total
                break
    if V == 1:
        # only cycle possible is self-loop
        add_edge(adj, 0, 0)
    else:
        kmax = min(V, max(2, remaining), 6)
        k = random.randint(2, kmax) if kmax >= 2 else 2
        if random.random() < 0.06:
            # self-loop cycle
            node = random.randrange(V)
            add_edge(adj, node, node)
        else:
            nodes = random.sample(range(V), k)
            for i in range(k):
                add_edge(adj, nodes[i], nodes[(i + 1) % k])
    return V, adj


def gen_edge_cases():
    """Deterministic edge cases covering bounds/structure extremes."""
    cases = []

    # V=1 with self loop -> cycle (True). (Only way to have >=1 edge on V=1.)
    cases.append((1, [[0]]))

    # V=2: single forward edge -> acyclic
    cases.append((2, [[1], []]))
    # V=2: mutual edges -> cycle
    cases.append((2, [[1], [0]]))
    # V=2: self loop on node 0
    cases.append((2, [[0], []]))

    # small chain (DAG)
    cases.append((5, [[1], [2], [3], [4], []]))
    # small cycle
    cases.append((5, [[1], [2], [3], [4], [0]]))

    # the two dataset examples (exact)
    cases.append((6, [[1], [2, 5], [3], [4], [1], []]))   # True
    cases.append((4, [[1, 2], [2], [], [0, 2]]))          # False
    cases.append((3, [[1, 2], [0, 2], [0]]))              # True (nowYourTurn)

    # disconnected: one acyclic component + one isolated node, single edge
    cases.append((4, [[1], [], [], []]))                  # False
    # disconnected with a cycle in one component
    cases.append((6, [[1], [2], [0], [4], [], []]))       # True (0-1-2 cycle)

    # multi-edges (duplicate edge same target) acyclic
    cases.append((3, [[1, 1, 2], [2], []]))               # False
    # multi-edges with back edge -> cycle
    cases.append((3, [[1, 1], [2], [0]]))                 # True

    # star DAG: 0 points to many
    cases.append((6, [[1, 2, 3, 4, 5], [], [], [], [], []]))  # False

    # long simple cycle
    n = 50
    cycle = [[(i + 1) % n] for i in range(n)]
    cases.append((n, cycle))                              # True
    # long chain (acyclic) of same size
    chain = [[i + 1] for i in range(n - 1)] + [[]]
    cases.append((n, chain))                              # False

    # Max-ish V with a single edge (sparse, acyclic): V=10000, edge 0->1
    big = empty_adj(MAX_V)
    big[0] = [1]
    cases.append((MAX_V, big))                            # False

    # Max-ish V with a self-loop somewhere (cycle)
    big2 = empty_adj(MAX_V)
    big2[5000] = [5000]
    cases.append((MAX_V, big2))                           # True

    # Dense up to edge cap: one node with ~10000 out-edges (acyclic, V=10001? no, keep < V)
    # V=10000, node 0 -> 1..9999 plus 0->? keep total <= 10000 edges
    dense = empty_adj(MAX_V)
    dense[0] = list(range(1, MAX_EDGES))  # 9999 edges, all 0->k (k>=1), acyclic
    cases.append((MAX_V, dense))                          # False

    # Same dense but add a back edge 1->0 to create a cycle (total 10000 edges)
    dense2 = empty_adj(MAX_V)
    dense2[0] = list(range(1, MAX_EDGES))  # 9999 edges
    dense2[1] = [0]                        # +1 = 10000 edges, cycle 0->1->0
    cases.append((MAX_V, dense2))                         # True

    return cases


def validate(V, adj):
    assert 1 <= V <= MAX_V, f"V out of range: {V}"
    assert len(adj) == V, f"adj size {len(adj)} != V {V}"
    total = 0
    for row in adj:
        for x in row:
            assert 0 <= x < V, f"edge target {x} out of range for V={V}"
            total += 1
    assert 1 <= total <= MAX_EDGES, f"total edges {total} out of [1,{MAX_EDGES}]"


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    rows = []

    # Edge cases first.
    edge = gen_edge_cases()
    for (V, adj) in edge:
        validate(V, adj)
        rows.append((V, adj))

    # Random cases until we reach N_CASES, balancing forced acyclic/cyclic.
    while len(rows) < N_CASES:
        force = random.choice([None, None, 'acyclic', 'cyclic'])
        V, adj = gen_random(force)
        total = sum(len(x) for x in adj)
        if total == 0:
            # ensure constraint sum >= 1; skip degenerate
            continue
        if total > MAX_EDGES:
            continue
        try:
            validate(V, adj)
        except AssertionError:
            continue
        rows.append((V, adj))

    rows = rows[:N_CASES]

    n_true = 0
    with open(OUT_PATH, "w") as f:
        for (V, adj) in rows:
            exp = has_cycle(V, adj)
            if exp:
                n_true += 1
            obj = {
                "inputs": {"V": str(V), "adj": fmt_adj(adj)},
                "expected": "True" if exp else "False",
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(rows)} cases to {OUT_PATH}")
    print(f"  cyclic (True): {n_true}   acyclic (False): {len(rows) - n_true}")


if __name__ == "__main__":
    main()
