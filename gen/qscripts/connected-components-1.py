#!/usr/bin/env python3
"""
Generator for Striver problem: connected-components-1
Signature: int findNumberOfComponent(int V, vector<vector<int>> &edges)
  - V: number of vertices, labeled 0..V-1
  - edges: edge list; edges[i] = [u, v] undirected edge

Constraints:
  1 <= V, edges.length <= 1e4
  0 <= edges[i][0], edges[i][1] <= V-1
  All edges are unique

Output: number of connected components (an integer), e.g. "2".

Reference oracle: pure-Python DSU (union-find). The number of connected
components = (# of isolated vertices counted as their own component) + (# of
unioned clusters). Equivalently V minus the number of successful unions.

We keep edges unique as undirected pairs and avoid self-loops (a self-loop is
within the allowed value range but never changes the component count; keeping
them out keeps cases unambiguous). Edge count is capped well below 1e4 so the
file stays modest while still exercising the structure.
"""
import json
import os
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/connected-components-1.jsonl"

N_CASES = 2000
random.seed(20260606)


class DSU:
    def __init__(self, n):
        self.p = list(range(n))
        self.r = [0] * n
        self.comps = n

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.r[ra] < self.r[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        if self.r[ra] == self.r[rb]:
            self.r[ra] += 1
        self.comps -= 1
        return True


def count_components(V, edges):
    """Ground-truth: number of connected components in an undirected graph."""
    dsu = DSU(V)
    for e in edges:
        dsu.union(e[0], e[1])
    return dsu.comps


# ---------- edge generators (all produce UNIQUE undirected edges, no self loops)

def _max_possible_edges(V):
    # number of distinct undirected non-loop edges available
    return V * (V - 1) // 2


def gen_random_edges(V):
    """Random unique undirected edges, count modest."""
    maxE = min(_max_possible_edges(V), 3 * V + 5, 60)
    if maxE <= 0:
        return []  # V == 1: no non-loop edge possible
    E = random.randint(1, maxE)
    edges = []
    seen = set()
    attempts = 0
    while len(edges) < E and attempts < E * 12:
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


def gen_few_components(V):
    """Connect almost everything into a few big components via a spanning-ish tree."""
    if V <= 1:
        return []
    nodes = list(range(V))
    random.shuffle(nodes)
    # decide how many components we WANT by leaving some 'cut' gaps
    edges = []
    seen = set()
    # chain the shuffled nodes, occasionally skipping to create separate comps
    for i in range(1, V):
        if random.random() < 0.08:  # ~8% chance to start a new component
            continue
        u, w = nodes[i - 1], nodes[i]
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    # sprinkle a few extra cross edges (don't change comp count much)
    extra = random.randint(0, min(V, 10))
    avail = _max_possible_edges(V)
    for _ in range(extra):
        if len(seen) >= avail:
            break
        u = random.randint(0, V - 1)
        w = random.randint(0, V - 1)
        if u == w:
            continue
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    random.shuffle(edges)
    return edges


def gen_single_component(V):
    """Force exactly one component: a spanning tree (random) + maybe extras."""
    if V <= 1:
        return []
    nodes = list(range(V))
    random.shuffle(nodes)
    edges = []
    seen = set()
    for i in range(1, V):
        u, w = nodes[i - 1], nodes[i]
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    extra = random.randint(0, min(V, 15))
    avail = _max_possible_edges(V)
    for _ in range(extra):
        if len(seen) >= avail:
            break
        u = random.randint(0, V - 1)
        w = random.randint(0, V - 1)
        if u == w:
            continue
        key = (min(u, w), max(u, w))
        if key not in seen:
            seen.add(key)
            edges.append([u, w])
    random.shuffle(edges)
    return edges


def gen_many_singletons(V):
    """Mostly isolated vertices: only a handful of edges."""
    if V <= 1:
        return []
    maxE = min(_max_possible_edges(V), max(1, V // 5), 20)
    E = random.randint(1, maxE)
    edges = []
    seen = set()
    attempts = 0
    while len(edges) < E and attempts < E * 12:
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


def make_case():
    r = random.random()
    if r < 0.20:
        V = random.choice([1, 2, 3, 4, 5, 6])  # small / edge
    elif r < 0.55:
        V = random.randint(2, 80)
    else:
        V = random.randint(80, 600)

    bucket = random.random()
    if V == 1:
        return 1, []  # only isolated vertex possible (no non-loop edges)
    if bucket < 0.30:
        edges = gen_random_edges(V)
    elif bucket < 0.55:
        edges = gen_single_component(V)
    elif bucket < 0.80:
        edges = gen_few_components(V)
    else:
        edges = gen_many_singletons(V)
    return V, edges


def edges_to_str(edges):
    return "[" + ",".join("[" + ",".join(str(x) for x in e) + "]" for e in edges) + "]"


def main():
    cases = []

    # Explicit edge / example cases first.
    explicit = [
        (4, [[0, 1], [1, 2]]),                     # example 1 -> 2
        (7, [[0, 1], [1, 2], [2, 3], [4, 5]]),     # example 2 -> 3
        (5, [[0, 1], [1, 2], [3, 4]]),             # nowYourTurn -> 2
        (1, []),                                   # single vertex, no edges -> 1
        (2, [[0, 1]]),                             # single edge -> 1
        (3, []),                                   # 3 isolated -> 3
        (3, [[0, 1], [1, 2], [0, 2]]),             # triangle -> 1
        (6, [[0, 1], [2, 3], [4, 5]]),             # 3 disjoint pairs -> 3
        (10, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5],
              [5, 6], [6, 7], [7, 8], [8, 9]]),    # one chain -> 1
    ]
    cases.extend(explicit)

    seen_keys = set()

    def keyof(V, edges):
        norm = tuple(sorted((min(e[0], e[1]), max(e[0], e[1])) for e in edges))
        return (V, norm)

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
