#!/usr/bin/env python3
"""
Generator for Striver problem: connected-components

Signature: int findNumberOfComponent(int V, vector<vector<int>> &edges)
  - V: number of vertices, labeled 0..V-1
  - edges: edge list; edges[i] = [u, v] undirected edge

Constraints:
  - 1 <= V, edges.length <= 1e4
  - 0 <= edges[i][0], edges[i][1] <= V-1
  - All edges are unique

Output: the number of connected components (isolated vertices each count as
their own component), printed as an int string e.g. "3".

Ground-truth oracle: Disjoint Set Union (DSU) implemented in pure Python.
This must match the C++ class Solution submitted to the live judge.
"""
import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/connected-components.jsonl"

N_CASES = 2000
random.seed(20260606)


def count_components(V, edges):
    """Ground-truth: number of connected components via DSU.

    Isolated vertices (with no incident edge) each form their own component.
    Self-loops and duplicate edges (shouldn't be generated) are harmless.
    """
    parent = list(range(V))
    rank = [0] * V

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rank[ra] < rank[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        if rank[ra] == rank[rb]:
            rank[ra] += 1

    for e in edges:
        union(e[0], e[1])

    return len({find(i) for i in range(V)})


def edges_to_str(edges):
    return "[" + ",".join("[" + ",".join(str(x) for x in e) + "]" for e in edges) + "]"


def gen_random_edges(V, density):
    """Random simple undirected edges (no self loops, all unique)."""
    if V < 2:
        return []
    # cap edge count: stay within constraint edges.length <= 1e4 and keep it modest
    max_possible = min(V * (V - 1) // 2, 10000)
    target = random.randint(0, min(max_possible, max(0, int(V * density))))
    edges = []
    seen = set()
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 20:
        attempts += 1
        u = random.randint(0, V - 1)
        w = random.randint(0, V - 1)
        if u == w:
            continue
        key = (min(u, w), max(u, w))
        if key in seen:
            continue
        seen.add(key)
        edges.append([u, w])
    return edges


def gen_chain(V):
    """A single path 0-1-2-...-(V-1): exactly 1 component (if V>=1)."""
    if V < 2:
        return []
    nodes = list(range(V))
    edges = []
    seen = set()
    for i in range(V - 1):
        u, w = nodes[i], nodes[i + 1]
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    return edges


def gen_k_components(V):
    """Partition vertices into k groups, connect each group internally."""
    if V < 2:
        return []
    k = random.randint(1, V)
    perm = list(range(V))
    random.shuffle(perm)
    # split perm into k non-empty groups
    cuts = sorted(random.sample(range(1, V), min(k - 1, V - 1))) if k > 1 else []
    groups = []
    prev = 0
    for c in cuts:
        groups.append(perm[prev:c])
        prev = c
    groups.append(perm[prev:])
    edges = []
    seen = set()
    for g in groups:
        # connect group as a chain
        for i in range(len(g) - 1):
            u, w = g[i], g[i + 1]
            key = (min(u, w), max(u, w))
            if key not in seen:
                seen.add(key)
                edges.append([u, w])
        # add a few random extra intra-group edges
        if len(g) >= 3:
            for _ in range(random.randint(0, min(3, len(g)))):
                a, b = random.sample(g, 2)
                key = (min(a, b), max(a, b))
                if key not in seen:
                    seen.add(key)
                    edges.append([a, b])
    return edges


def make_case():
    r = random.random()
    if r < 0.20:
        V = random.choice([1, 2, 3, 4, 5])  # small / edge
    elif r < 0.55:
        V = random.randint(2, 60)
    elif r < 0.85:
        V = random.randint(60, 500)
    else:
        V = random.randint(500, 3000)

    bucket = random.random()
    if bucket < 0.30:
        edges = gen_k_components(V)
    elif bucket < 0.55:
        edges = gen_chain(V)
    elif bucket < 0.85:
        edges = gen_random_edges(V, density=1.5)
    else:
        edges = gen_random_edges(V, density=0.4)  # sparse -> many components
    return V, edges


def main():
    cases = []

    # Explicit example / edge cases first.
    explicit = [
        (4, [[0, 1], [1, 2]]),                       # example 1 -> 2
        (7, [[0, 1], [1, 2], [2, 3], [4, 5]]),       # example 2 -> 3
        (5, [[0, 1], [1, 2], [3, 4]]),               # nowYourTurn -> 2
        (1, []),                                     # single isolated vertex -> 1
        (2, []),                                     # two isolated -> 2
        (2, [[0, 1]]),                               # one edge -> 1
        (3, [[0, 1], [1, 2], [0, 2]]),               # triangle -> 1
        (10, []),                                    # all isolated -> 10
        (6, [[0, 1], [2, 3], [4, 5]]),               # three pairs -> 3
        (5, [[0, 1], [1, 2], [2, 0], [3, 4]]),       # cycle + edge -> 2
    ]
    cases.extend(explicit)

    seen_keys = set()

    def keyof(V, edges):
        return (V, tuple(tuple(e) for e in edges))

    for c in cases:
        seen_keys.add(keyof(*c))

    guard = 0
    while len(cases) < N_CASES and guard < N_CASES * 40:
        guard += 1
        V, edges = make_case()
        k = keyof(V, edges)
        if k in seen_keys:
            continue
        seen_keys.add(k)
        cases.append((V, edges))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for V, edges in cases:
            res = count_components(V, edges)
            obj = {
                "inputs": {
                    "V": str(V),
                    "edges": edges_to_str(edges),
                },
                "expected": str(res),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
