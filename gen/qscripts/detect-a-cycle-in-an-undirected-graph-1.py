#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
    detect-a-cycle-in-an-undirected-graph-1
    ( "Detect a cycle in an undirected graph" )

starterCpp signature:  bool isCycle(int V, vector<int> adj[])

The graph is UNDIRECTED, given as an adjacency list. The adjacency list MUST be
symmetric: if v appears in adj[u], then u appears in adj[v]. There are no
self-edges (problem note: "The graph does not contain any self-edges").

Per line we emit:
    {"inputs": {"V": "<V>", "adj": "[[...],[...],...]"}, "expected": "True|False"}

Param names from the signature are V and adj (in signature order). The judge
binds inputs to params by name first.

Constraints enforced for EVERY generated case:
    1 <= V <= 10^4
    1 <= E <= 10^4               (E = number of UNDIRECTED edges)
    adj.size() == V
    0 <= adj[i][j] < V
    no self-edges (adj[i] never contains i)
    adjacency list symmetric (undirected)

Expected output is computed with iterative BFS cycle detection (parent tracking),
the SAME algorithm submitted to the live judge.

Output value matches the example format: "True" / "False" (capitalized). The
judge compares leniently (case/brackets/whitespace insensitive), but we mirror
the dataset examples exactly.
"""

import json
import os
import random
import sys
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/detect-a-cycle-in-an-undirected-graph-1.jsonl"

V_MAX = 10**4
EDGE_MAX = 10**4   # number of undirected edges


# ---------------------------------------------------------------------------
# Reference oracle: undirected-cycle detection via iterative BFS with parent
# tracking. A re-visit of an already-visited neighbour that is not the parent
# implies a cycle. (No self-edges by construction.)
# ---------------------------------------------------------------------------
def is_cycle(V, adj):
    vis = [False] * V
    for s in range(V):
        if vis[s]:
            continue
        vis[s] = True
        q = deque()
        q.append((s, -1))
        while q:
            node, par = q.popleft()
            for nb in adj[node]:
                if not vis[nb]:
                    vis[nb] = True
                    q.append((nb, node))
                elif nb != par:
                    return True
    return False


def fmt_adj(adj):
    # 2D array string, e.g. [[1,3],[0],[]]
    return "[" + ", ".join("[" + ", ".join(str(x) for x in row) + "]" for row in adj) + "]"


def edge_count(adj):
    # undirected edge count = (sum of degrees) / 2
    s = sum(len(r) for r in adj)
    assert s % 2 == 0
    return s // 2


# ---------------------------------------------------------------------------
# Edge management helpers. We build an undirected graph as a set of unordered
# pairs, then materialise a symmetric adjacency list.
# ---------------------------------------------------------------------------
def build_adj(V, edges):
    """edges: iterable of (u,v) unordered pairs, u!=v, deduped already."""
    adj = [[] for _ in range(V)]
    for (u, v) in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def add_edge(edge_set, u, v):
    if u == v:
        return False
    key = (u, v) if u < v else (v, u)
    if key in edge_set:
        return False
    edge_set.add(key)
    return True


# ---------------------------------------------------------------------------
# Random graph builders. Each yields a list of unordered edges (no self-edge,
# no duplicate), with 1 <= len(edges) <= EDGE_MAX.
# ---------------------------------------------------------------------------
def gen_tree(V):
    """A random spanning tree (V-1 edges) -> always ACYCLIC. Needs V>=2."""
    edges = set()
    perm = list(range(V))
    random.shuffle(perm)
    for i in range(1, V):
        # connect perm[i] to a random earlier node -> guaranteed tree
        j = random.randrange(i)
        add_edge(edges, perm[i], perm[j])
    return edges


def gen_forest(V, n_edges):
    """A random forest (acyclic) with up to n_edges edges. Acyclic guaranteed
    via union-find: never add an edge connecting two already-connected nodes."""
    parent = list(range(V))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    edges = set()
    attempts = 0
    target = min(n_edges, V - 1, EDGE_MAX)
    while len(edges) < target and attempts < target * 12 + 100:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if u == v:
            continue
        ru, rv = find(u), find(v)
        if ru == rv:
            continue
        key = (u, v) if u < v else (v, u)
        if key in edges:
            continue
        parent[ru] = rv
        edges.add(key)
    return edges


def gen_random_graph(V, target_edges):
    """Generic random undirected simple graph with up to target_edges edges.
    May or may not contain a cycle (oracle decides)."""
    edges = set()
    target = min(target_edges, EDGE_MAX, V * (V - 1) // 2)
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 100:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        add_edge(edges, u, v)
    return edges


def gen_with_cycle(V, extra):
    """Graph guaranteed to contain a cycle. Needs V>=3 for a simple cycle.
    Build a simple cycle on a random subset, then sprinkle extra edges."""
    edges = set()
    k = random.randint(3, min(V, 60))
    nodes = random.sample(range(V), k)
    for i in range(k):
        add_edge(edges, nodes[i], nodes[(i + 1) % k])
    # sprinkle extra random edges within budget
    attempts = 0
    extra = min(extra, max(0, EDGE_MAX - len(edges)))
    while extra > 0 and attempts < extra * 8 + 50 and len(edges) < EDGE_MAX:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if add_edge(edges, u, v):
            extra -= 1
    return edges


def gen_two_node_multi(V):
    """Special: only valid 'cycle' on 2 nodes would be a multi-edge, which the
    simple-graph model forbids. So with V==2 the graph is always acyclic.
    Just return the single edge."""
    edges = set()
    add_edge(edges, 0, 1)
    return edges


def trim_edges_to_budget(edges):
    if len(edges) <= EDGE_MAX:
        return edges
    lst = list(edges)
    random.shuffle(lst)
    return set(lst[:EDGE_MAX])


# ---------------------------------------------------------------------------
# Case construction. Edge cases up front, then a varied random spread.
# ---------------------------------------------------------------------------
def make_case(idx):
    # --- deterministic edge cases ---
    if idx == 0:
        # min V with at least one edge: V=2, single edge -> acyclic (no self-loop)
        return 2, [[1], [0]]
    if idx == 1:
        # example 1 (cyclic)
        return 6, [[1, 3], [0, 2, 4], [1, 5], [0, 4], [1, 3, 5], [2, 4]]
    if idx == 2:
        # example 2 (acyclic)
        return 4, [[1, 2], [0], [0, 3], [2]]
    if idx == 3:
        # nowYourTurn case: V=4 adj=[[1,2],[0,2],[0,1,3],[2]] -> triangle 0-1-2 cyclic
        return 4, [[1, 2], [0, 2], [0, 1, 3], [2]]
    if idx == 4:
        # triangle (smallest simple cycle)
        return 3, [[1, 2], [0, 2], [0, 1]]
    if idx == 5:
        # path of 3 nodes -> acyclic
        return 3, [[1], [0, 2], [1]]
    if idx == 6:
        # disconnected: a tree component + an isolated-ish edge -> acyclic
        return 5, [[1, 2], [0], [0], [4], [3]]
    if idx == 7:
        # disconnected with a cycle in one component
        return 5, [[1, 2], [0, 2], [0, 1], [4], [3]]

    # pick a V with a spread: many small, some medium, a few large
    pv = random.random()
    if pv < 0.55:
        V = random.randint(2, 12)
    elif pv < 0.85:
        V = random.randint(13, 300)
    elif pv < 0.97:
        V = random.randint(301, 3000)
    else:
        V = random.randint(3001, V_MAX)

    r = random.random()

    if V == 1:
        # V=1: no self-edges allowed and need E>=1 -> impossible. Bump to V=2.
        V = 2

    if V == 2:
        edges = gen_two_node_multi(V)
    elif r < 0.30:
        # spanning tree -> acyclic, E = V-1
        edges = gen_tree(V)
    elif r < 0.50:
        # forest -> acyclic, fewer edges
        ne = random.randint(1, max(1, V - 1))
        edges = gen_forest(V, ne)
        if not edges:
            edges = gen_tree(V)
    elif r < 0.80:
        # guaranteed cycle
        extra = random.randint(0, min(3 * V, EDGE_MAX))
        edges = gen_with_cycle(V, extra)
    else:
        # generic random graph (oracle decides)
        te = random.randint(1, min(EDGE_MAX, max(1, 2 * V)))
        edges = gen_random_graph(V, te)

    edges = trim_edges_to_budget(edges)
    if len(edges) == 0:
        # ensure E >= 1
        edges = set()
        u = random.randrange(V)
        v = (u + 1) % V
        add_edge(edges, u, v)

    adj = build_adj(V, edges)
    return V, adj


def validate(V, adj):
    assert 1 <= V <= V_MAX, f"V out of range: {V}"
    assert len(adj) == V, f"adj.size {len(adj)} != V {V}"
    # check value range, no self-edge
    pair_count = {}
    for i, row in enumerate(adj):
        for x in row:
            assert 0 <= x < V, f"target {x} out of range for V={V}"
            assert x != i, f"self-edge at {i}"
            key = (i, x) if i < x else (x, i)
            pair_count[key] = pair_count.get(key, 0) + 1
    # symmetry: every unordered pair must appear exactly twice (once each dir)
    for key, c in pair_count.items():
        assert c == 2, f"asymmetric/duplicate edge {key} count={c}"
    E = edge_count(adj)
    assert 1 <= E <= EDGE_MAX, f"E out of range: {E}"


def main():
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
    random.seed(seed)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = []
    cyc = 0
    for i in range(n):
        V, adj = make_case(i)
        validate(V, adj)
        exp = is_cycle(V, adj)
        if exp:
            cyc += 1
        rec = {
            "inputs": {"V": str(V), "adj": fmt_adj(adj)},
            "expected": "True" if exp else "False",
        }
        lines.append(json.dumps(rec))

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases -> {OUT}  (cyclic={cyc}, acyclic={n-cyc})")


if __name__ == "__main__":
    main()
