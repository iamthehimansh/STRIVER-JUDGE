#!/usr/bin/env python3
"""
Generator for Striver problem: bipartite-graph
Signature: bool isBipartite(int V, vector<vector<int>> edges)
  - V: number of vertices, labeled 0..V-1
  - edges: edge list; edges[i] = [u, v] undirected edge
Constraints: 1 <= V, E <= 1e4

Output: "True" / "False" (matching the dataset example output capitalization).

The reference is implemented in pure Python (graph coloring / BFS bipartite check),
which is the ground-truth oracle. We build adjacency from the edge list.
"""
import json
import os
import random
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/bipartite-graph.jsonl"

N_CASES = 2000
random.seed(20240606)


def is_bipartite(V, edges):
    """Ground-truth bipartite check on an edge list with V vertices (0..V-1)."""
    adj = [[] for _ in range(V)]
    for e in edges:
        u, w = e[0], e[1]
        adj[u].append(w)
        adj[w].append(u)
    color = [-1] * V
    for start in range(V):
        if color[start] != -1:
            continue
        color[start] = 0
        q = deque([start])
        while q:
            node = q.popleft()
            for nei in adj[node]:
                if color[nei] == -1:
                    color[nei] = color[node] ^ 1
                    q.append(nei)
                elif color[nei] == color[node]:
                    return False
    return True


def gen_bipartite_edges(V):
    """Build a guaranteed-bipartite graph: random 2-coloring, only cross edges."""
    side = [random.randint(0, 1) for _ in range(V)]
    A = [i for i in range(V) if side[i] == 0]
    B = [i for i in range(V) if side[i] == 1]
    edges = []
    seen = set()
    if A and B:
        # at least one edge
        target = random.randint(1, min(2 * V, 30))
        attempts = 0
        while len(edges) < target and attempts < target * 6:
            attempts += 1
            u = random.choice(A)
            w = random.choice(B)
            key = (min(u, w), max(u, w))
            if key in seen:
                continue
            seen.add(key)
            edges.append([u, w])
    if not edges:
        # need at least 1 edge (E>=1). If only one side populated, just add a
        # self-ish safe edge between two distinct vertices (an edge inside a side
        # would make it odd? a single edge u-w is always bipartite). Pick any two.
        if V >= 2:
            edges.append([0, 1])
        else:
            edges.append([0, 0])  # only when V==1; self loop -> not bipartite handled below
    return edges


def gen_random_edges(V):
    """Random graph (may or may not be bipartite)."""
    maxE = min(2 * V + 5, 40)
    E = random.randint(1, maxE)
    edges = []
    seen = set()
    attempts = 0
    while len(edges) < E and attempts < E * 8:
        attempts += 1
        u = random.randint(0, V - 1)
        w = random.randint(0, V - 1)
        if u == w:
            # allow self loops occasionally (makes it non-bipartite), rarely
            if random.random() < 0.05:
                edges.append([u, w])
            continue
        key = (min(u, w), max(u, w))
        if key in seen:
            continue
        seen.add(key)
        edges.append([u, w])
    if not edges:
        if V >= 2:
            edges.append([0, 1])
        else:
            edges.append([0, 0])
    return edges


def gen_odd_cycle(V):
    """Force a non-bipartite graph by embedding an odd cycle (if V>=3)."""
    if V < 3:
        return [[0, 0]] if V >= 1 else [[0, 0]]
    # pick odd cycle length
    L = random.choice([3, 5, 7])
    L = min(L, V if V % 2 == 1 else V - 1)
    if L < 3:
        L = 3
    if L > V:
        L = V if V % 2 == 1 else V - 1
    if L < 3:
        # fall back to self loop
        return [[0, 0]]
    nodes = random.sample(range(V), L)
    edges = []
    seen = set()
    for i in range(L):
        u = nodes[i]
        w = nodes[(i + 1) % L]
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    # add some extra random cross edges (still leaves the odd cycle non-bipartite)
    extra = random.randint(0, min(V, 10))
    for _ in range(extra):
        u = random.randint(0, V - 1)
        w = random.randint(0, V - 1)
        if u == w:
            continue
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    return edges


def make_case():
    r = random.random()
    if r < 0.20:
        V = random.choice([1, 2, 3, 4, 5])  # small / edge
    elif r < 0.55:
        V = random.randint(2, 60)
    else:
        V = random.randint(60, 400)

    bucket = random.random()
    if bucket < 0.40:
        edges = gen_bipartite_edges(V)
    elif bucket < 0.75:
        edges = gen_odd_cycle(V)
    else:
        edges = gen_random_edges(V)
    return V, edges


def edges_to_str(edges):
    return "[" + ",".join("[" + ",".join(str(x) for x in e) + "]" for e in edges) + "]"


def main():
    cases = []

    # Explicit edge / example cases first.
    explicit = [
        (4, [[0, 1], [0, 3], [1, 2], [2, 3]]),   # bipartite -> True (example 1)
        (4, [[0, 1], [0, 2], [0, 3], [1, 2], [2, 3]]),  # False (example 2)
        (5, [[0, 1], [0, 3], [1, 2], [2, 4], [3, 4]]),  # nowYourTurn case
        (1, [[0, 0]]),   # single vertex self loop -> not bipartite
        (2, [[0, 1]]),   # single edge -> bipartite
        (3, [[0, 1], [1, 2], [2, 0]]),  # triangle -> False
        (3, [[0, 1], [1, 2]]),          # path -> True
        (2, [[0, 0]]),                  # self loop -> False
    ]
    cases.extend(explicit)

    seen_keys = set()

    def keyof(V, edges):
        return (V, tuple(tuple(e) for e in edges))

    for c in cases:
        seen_keys.add(keyof(*c))

    while len(cases) < N_CASES:
        V, edges = make_case()
        k = keyof(V, edges)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        cases.append((V, edges))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for V, edges in cases:
            res = is_bipartite(V, edges)
            expected = "True" if res else "False"
            obj = {
                "inputs": {
                    "V": str(V),
                    "edges": edges_to_str(edges),
                },
                "expected": expected,
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
