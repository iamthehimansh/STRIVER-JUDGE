#!/usr/bin/env python3
"""
Generator for "Find eventual safe states".

Signature: vector<int> eventualSafeNodes(int V, vector<int> adj[])
 - V   : number of vertices
 - adj : adjacency list (adj[i] = sorted strictly-increasing list of neighbors of i)

Constraints:
 - 1 <= V <= 1e4
 - 0 <= adj[i].length <= V
 - 0 <= adj[i][j] <= V-1
 - adj[i] is sorted strictly increasing (so neighbors are distinct)
 - self-loops allowed
 - total number of edges in [1, 4e4]

Output: safe nodes (every path from node leads to a terminal node) in ascending order.

Writes generated-tests/find-eventual-safe-states.jsonl with 2000 cases.
"""
import json
import random
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-eventual-safe-states.jsonl"
N_CASES = 2000
MAX_V = 10000
MAX_EDGES = 40000

# The judge batches all cases into ONE process whose TOTAL captured stdout is
# capped at 256 KiB (scripts/judge_exec.py: OUT_CAP = 256*1024). Output beyond
# that is silently dropped, so every case after the cap fails. The per-case
# output is the list of safe nodes, so we must keep the SUM of all per-case
# stdout lengths comfortably under 256 KiB. The judge prints space-separated
# numbers + a newline (no brackets/commas), which is SMALLER than our bracketed
# "expected" string — we budget against the bracketed length to stay safe.
TOTAL_OUT_BUDGET = 200_000   # bytes of (bracketed) expected output across all cases (<< 256 KiB)
PER_CASE_OUT_CAP = 3_000     # max expected-output length for a single case


def eventual_safe_nodes(V, adj):
    """Reference: reverse-graph topo sort (Kahn on outdegree)."""
    outdeg = [0] * V
    revadj = [[] for _ in range(V)]
    for i in range(V):
        outdeg[i] = len(adj[i])
        for j in adj[i]:
            revadj[j].append(i)
    q = deque(i for i in range(V) if outdeg[i] == 0)
    safe = []
    while q:
        node = q.popleft()
        safe.append(node)
        for v in revadj[node]:
            outdeg[v] -= 1
            if outdeg[v] == 0:
                q.append(v)
    safe.sort()
    return safe


def make_graph(V, target_edges):
    """Build adj with at most target_edges edges, sorted strictly increasing per row.
    Guarantees at least 1 edge total."""
    adj = [set() for _ in range(V)]
    edges = 0
    # cap target by V*V (max simple edges incl self loops)
    max_possible = V * V
    target_edges = min(target_edges, max_possible, MAX_EDGES)
    target_edges = max(1, target_edges)
    attempts = 0
    while edges < target_edges and attempts < target_edges * 8 + 50:
        attempts += 1
        u = random.randrange(V)
        w = random.randrange(V)  # self-loops allowed (w == u ok)
        if w not in adj[u]:
            adj[u].add(w)
            edges += 1
    # ensure at least one edge
    if edges == 0:
        u = random.randrange(V)
        w = random.randrange(V)
        adj[u].add(w)
    return [sorted(s) for s in adj]


def total_edges(adj):
    return sum(len(r) for r in adj)


def fmt_adj(adj):
    return "[" + ", ".join("[" + ", ".join(str(x) for x in row) + "]" for row in adj) + "]"


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def gen_case(i):
    r = random.random()
    if i == 0:
        # smallest: V=1 with a self loop (1 edge minimum) -> node 0 unsafe
        adj = [[0]]
        V = 1
    elif i == 1:
        # V=1 cannot be terminal-only because >=1 edge required; self loop => unsafe
        adj = [[0]]
        V = 1
    elif i == 2:
        # example 1
        V = 7
        adj = [[1, 2], [2, 3], [5], [0], [5], [], []]
    elif i == 3:
        V = 4
        adj = [[1], [2], [0, 3], []]
    elif i == 4:
        # pure DAG chain -> all safe
        V = random.randint(2, 30)
        adj = [[j for j in range(k + 1, V)] for k in range(V)]
        # too many edges? trim: keep only next node to bound edges
        if total_edges(adj) > MAX_EDGES:
            adj = [([k + 1] if k + 1 < V else []) for k in range(V)]
    elif i == 5:
        # one big cycle -> nobody safe
        V = random.randint(2, 50)
        adj = [sorted([(k + 1) % V]) for k in range(V)]
    elif r < 0.18:
        # small dense-ish (full range of safe/unsafe)
        V = random.randint(1, 8)
        target = random.randint(1, min(MAX_EDGES, V * V))
        adj = make_graph(V, target)
    elif r < 0.45:
        # medium random
        V = random.randint(5, 200)
        target = random.randint(1, min(MAX_EDGES, V * 3))
        adj = make_graph(V, target)
    elif r < 0.50:
        # DAG-flavored (more safe nodes): edges only forward => every node safe.
        # Keep V small so the all-safe output stays well under the per-case cap.
        V = random.randint(5, 80)
        adj = [set() for _ in range(V)]
        e = 0
        cap = random.randint(1, min(MAX_EDGES, V * 3))
        tries = 0
        while e < cap and tries < cap * 6 + 50:
            tries += 1
            u = random.randrange(V)
            w = random.randrange(V)
            if u < w and w not in adj[u]:
                adj[u].add(w)
                e += 1
        if e == 0:
            adj[0].add(min(1, V - 1) if V > 1 else 0)
        adj = [sorted(s) for s in adj]
    elif r < 0.80:
        # LARGE V, structurally almost-all-unsafe (tiny output): every node points
        # forward to its successor, and the LAST node points back to node 0,
        # forming one big cycle that swallows everyone. A small "safe tail" of a
        # few terminal nodes is appended so the output is non-empty but bounded.
        V = random.randint(1000, MAX_V)
        safe_tail = random.randint(0, 30)         # at most ~30 safe nodes
        safe_tail = min(safe_tail, V - 2)
        cyc = V - safe_tail                       # nodes 0..cyc-1 in one cycle
        adj = [set() for _ in range(V)]
        for k in range(cyc):
            adj[k].add((k + 1) % cyc)             # cycle => all unsafe
        # safe tail: nodes cyc..V-1 each point only forward toward a terminal
        for k in range(cyc, V):
            if k + 1 < V:
                adj[k].add(k + 1)                 # forward chain -> terminal at V-1
            # else: terminal (no edge)
        adj = [sorted(s) for s in adj]
    else:
        # MEDIUM "half cycle, half tail": a cycle (unsafe) plus a small DAG appendix
        # with a controlled, modest number of safe nodes.
        V = random.randint(50, 2000)
        cyc = random.randint(2, V)                # nodes 0..cyc-1 form a cycle (unsafe)
        adj = [set() for _ in range(V)]
        for k in range(cyc):
            adj[k].add((k + 1) % cyc)
        safe_zone = min(V - cyc, 100)             # cap safe-node count
        for k in range(cyc, cyc + safe_zone):
            hi = min(V, k + 1 + random.randint(0, 3))
            for w in range(k + 1, hi):
                adj[k].add(w)
        adj = [sorted(s) for s in adj]
    # safety clamps
    assert 1 <= V <= MAX_V
    te = total_edges(adj)
    assert te <= MAX_EDGES, te
    if te == 0:
        # force one edge
        adj[0] = sorted(set(adj[0]) | {random.randrange(V)})
    for row in adj:
        assert all(0 <= x < V for x in row)
        assert row == sorted(set(row))  # strictly increasing
    return V, adj


def cheap_cycle_case():
    """A small all-cycle graph -> empty output (zero output cost)."""
    V = random.randint(2, 50)
    adj = [[(k + 1) % V] for k in range(V)]
    return V, adj, "[]"


def main():
    random.seed(20260606)
    lines = []
    total_out = 0
    for i in range(N_CASES):
        # At most a few cheap attempts; if the case's output is too big or would
        # blow the global budget, substitute a zero-output all-cycle graph rather
        # than expensively recomputing huge references.
        V, adj, expected = None, None, None
        for attempt in range(4):
            cV, cadj = gen_case(i if attempt == 0 else (10_000_000 + i * 97 + attempt))
            cexp = fmt_arr(eventual_safe_nodes(cV, cadj))
            if len(cexp) <= PER_CASE_OUT_CAP and total_out + len(cexp) <= TOTAL_OUT_BUDGET:
                V, adj, expected = cV, cadj, cexp
                break
        if expected is None:
            V, adj, expected = cheap_cycle_case()
        total_out += len(expected)
        obj = {
            "inputs": {"V": str(V), "adj": fmt_adj(adj)},
            "expected": expected,
        }
        lines.append(json.dumps(obj))
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", len(lines), "cases; total bracketed expected-output bytes =", total_out)


if __name__ == "__main__":
    main()
