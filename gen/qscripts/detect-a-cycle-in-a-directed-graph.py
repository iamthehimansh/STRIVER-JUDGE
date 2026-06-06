#!/usr/bin/env python3
"""
Test-case generator for Striver problem: detect-a-cycle-in-a-directed-graph
( "Cycle Detection in Directed Graph (DFS)" )

starterCpp signature:  bool isCyclic(int N, vector<int> adj[])
The judge harness does NOT support `vector<int> adj[]` (array param). A working
submission must use `vector<vector<int>>& adj`; the adjacency LIST is passed as
a 2D array string "[[1],[2,5],...]". This generator therefore emits, per line:

    {"inputs": {"N": "<V>", "adj": "[[...],[...],...]"}, "expected": "<true|false>"}

Param names from the signature are N and adj (in signature order). The judge
binds inputs to params by name first, then positionally, so keys N / adj map
cleanly onto the params.

Constraints enforced for EVERY generated case:
    1 <= V <= 10^4
    adj.size() == V
    0 <= adj[i][j] < V
    1 <= sum(adj[i].size()) <= 10^4

Expected output is computed with the canonical DFS (visited + path/recursion
stack) cycle-detection algorithm — the same algorithm submitted to the live
judge.
"""

import json
import os
import random
import sys

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/detect-a-cycle-in-a-directed-graph.jsonl"

V_MAX = 10**4
EDGE_MAX = 10**4

# ---------------------------------------------------------------------------
# Reference oracle: directed-cycle detection via DFS with a recursion-stack
# ("path") marker. Iterative to avoid Python recursion limits at V up to 10^4.
# ---------------------------------------------------------------------------
def is_cyclic(V, adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * V
    for start in range(V):
        if color[start] != WHITE:
            continue
        # iterative DFS; stack holds (node, index-into-adj)
        stack = [(start, 0)]
        color[start] = GRAY
        while stack:
            node, idx = stack[-1]
            if idx < len(adj[node]):
                stack[-1] = (node, idx + 1)
                nxt = adj[node][idx]
                if color[nxt] == GRAY:
                    return True
                if color[nxt] == WHITE:
                    color[nxt] = GRAY
                    stack.append((nxt, 0))
            else:
                color[node] = BLACK
                stack.pop()
    return False


def fmt_adj(adj):
    # 2D array string, e.g. [[1],[2,5],[]]
    return "[" + ",".join("[" + ",".join(str(x) for x in row) + "]" for row in adj) + "]"


def total_edges(adj):
    return sum(len(r) for r in adj)


# ---------------------------------------------------------------------------
# Random graph builders. Each must yield 1 <= sum(adj[i].size()) <= 10^4 and
# 0 <= target < V.
# ---------------------------------------------------------------------------
def rand_edges_budget(V):
    # max edges we can add while respecting EDGE_MAX
    return min(EDGE_MAX, V * V)


def gen_random_graph(V, edge_density, allow_self_loop=True):
    """Generic random directed multigraph-free-ish graph with a target edge count."""
    budget = rand_edges_budget(V)
    target = max(1, min(budget, int(edge_density * V) + random.randint(0, V)))
    target = min(target, EDGE_MAX)
    adj = [[] for _ in range(V)]
    seen = set()
    attempts = 0
    e = 0
    while e < target and attempts < target * 8 + 50:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if not allow_self_loop and u == v:
            continue
        key = (u, v)
        if key in seen:
            continue
        seen.add(key)
        adj[u].append(v)
        e += 1
    # guarantee at least one edge (constraint: sum >= 1)
    if total_edges(adj) == 0:
        u = random.randrange(V)
        v = random.randrange(V)
        adj[u].append(v)
    return adj


def gen_dag(V):
    """Directed ACYCLIC graph: only edges u->v with u<v (topologically sorted)."""
    if V == 1:
        # single vertex DAG needs >=1 edge -> only possible edge is self-loop,
        # which is a cycle. So a V==1 acyclic graph is impossible with >=1 edge.
        # Fall back to a self-loop (cyclic) — caller handles label via oracle.
        return [[0]]
    budget = rand_edges_budget(V)
    target = max(1, min(budget, random.randint(1, min(EDGE_MAX, 3 * V))))
    adj = [[] for _ in range(V)]
    seen = set()
    e = 0
    attempts = 0
    while e < target and attempts < target * 8 + 50:
        attempts += 1
        u = random.randrange(V - 1)
        v = random.randint(u + 1, V - 1)
        if (u, v) in seen:
            continue
        seen.add((u, v))
        adj[u].append(v)
        e += 1
    if total_edges(adj) == 0:
        adj[0].append(V - 1)
    return adj


def gen_cyclic(V):
    """Graph guaranteed to contain a cycle."""
    if V == 1:
        return [[0]]  # self-loop
    adj = [[] for _ in range(V)]
    seen = set()
    # build a back-edge cycle among a random subset
    k = random.randint(2, min(V, 50))
    nodes = random.sample(range(V), k)
    for i in range(k):
        u = nodes[i]
        v = nodes[(i + 1) % k]
        if (u, v) not in seen:
            seen.add((u, v))
            adj[u].append(v)
    # sprinkle extra random edges within budget
    budget = rand_edges_budget(V)
    extra = random.randint(0, min(2 * V, max(0, EDGE_MAX - total_edges(adj))))
    attempts = 0
    while extra > 0 and attempts < extra * 8 + 50 and total_edges(adj) < EDGE_MAX:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if (u, v) in seen:
            continue
        seen.add((u, v))
        adj[u].append(v)
        extra -= 1
    return adj


def gen_self_loop(V):
    adj = [[] for _ in range(V)]
    adj[random.randrange(V)].append(random.randrange(V))  # at least one edge
    adj[random.randrange(V)].append(random.randrange(V))
    # force a self loop
    s = random.randrange(V)
    if s not in adj[s]:
        adj[s].append(s)
    return adj


def trim_to_budget(adj):
    """Ensure sum of out-degrees <= EDGE_MAX (defensive)."""
    e = total_edges(adj)
    if e <= EDGE_MAX:
        return adj
    over = e - EDGE_MAX
    for row in adj:
        while over > 0 and row:
            row.pop()
            over -= 1
        if over == 0:
            break
    if total_edges(adj) == 0:
        adj[0].append(0)
    return adj


def make_case(idx, n_total):
    """Return (V, adj) honoring all constraints, with edge cases up front."""
    # --- deterministic edge cases ---
    if idx == 0:
        return 1, [[0]]                       # min V, self-loop (cyclic)
    if idx == 1:
        return 2, [[1], []]                    # tiny acyclic
    if idx == 2:
        return 2, [[1], [0]]                   # 2-cycle
    if idx == 3:
        return 3, [[1], [2], [0]]              # 3-cycle (the nowYourTurn case)
    if idx == 4:
        return 4, [[1, 2], [2], [], [0, 2]]    # example 2 (acyclic)
    if idx == 5:
        return 6, [[1], [2, 5], [3], [4], [1], []]  # example 1 (cyclic)
    if idx == 6:
        return 5, [[0], [], [], [], []]        # single self-loop, rest empty
    if idx == 7:
        return 5, [[1], [2], [3], [4], []]     # simple chain, acyclic

    r = random.random()
    # pick a V with a spread: many small, some medium, a few large
    pv = random.random()
    if pv < 0.55:
        V = random.randint(1, 12)
    elif pv < 0.85:
        V = random.randint(13, 300)
    elif pv < 0.97:
        V = random.randint(301, 3000)
    else:
        V = random.randint(3001, V_MAX)

    if r < 0.30:
        adj = gen_dag(V)
    elif r < 0.62:
        adj = gen_cyclic(V)
    elif r < 0.72:
        adj = gen_self_loop(V)
    else:
        adj = gen_random_graph(V, edge_density=random.uniform(0.5, 2.5))

    adj = trim_to_budget(adj)
    return V, adj


def validate(V, adj):
    assert 1 <= V <= V_MAX, f"V out of range: {V}"
    assert len(adj) == V, f"adj.size {len(adj)} != V {V}"
    te = total_edges(adj)
    assert 1 <= te <= EDGE_MAX, f"sum edges out of range: {te}"
    for row in adj:
        for x in row:
            assert 0 <= x < V, f"target {x} out of range for V={V}"


def main():
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
    random.seed(seed)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = []
    for i in range(n):
        V, adj = make_case(i, n)
        validate(V, adj)
        exp = is_cyclic(V, adj)
        rec = {
            "inputs": {"N": str(V), "adj": fmt_adj(adj)},
            "expected": "true" if exp else "false",
        }
        lines.append(json.dumps(rec))

    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases -> {OUT}")


if __name__ == "__main__":
    main()
