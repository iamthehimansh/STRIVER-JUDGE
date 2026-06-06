#!/usr/bin/env python3
"""
Generator for "Kosaraju's algorithm" (slug: kosaraju's-algorithm).

Judge-facing signature (what a submission must use so the harness can bind it):
    int kosaraju(int V, vector<vector<int>> E)
The dataset testcases provide keys {"V", "E"} (V = number of vertices,
E = directed edge list [[a,b],...]) and the harness binds them by name.

The ORIGINAL starter `int kosaraju(int V, vector<int> adj[])` is NOT bindable by
the judge harness (array-of-vector params, `vector<int> adj[]`, are unsupported --
verified live: the judge returns "Unsupported parameter type: vector<int>"). So the
judgeable reference takes the directed edge list E and rebuilds the adjacency
itself. Input keys are V then E, matching starter param order (V) and the dataset's
existing example testcases (which use keys "E" and "V").

jsonl line format (one object per line):
    {"inputs": {"V": "<int>", "E": "[[a,b],...]"}, "expected": "<scc_count>"}

Constraints (from problem):
    1 <= V <= 5000
    0 <= E <= V*(V-1)          (E may be 0 -> empty edge list "[]")
    0 <= a_i, b_i <= V-1       (directed edge a -> b, zero-based)

Expected output is the number of strongly connected components (SCCs), computed by
an external C++ reference (Kosaraju, ITERATIVE DFS so a V=5000 path cannot blow the
stack) compiled at runtime. A single integer per case -- exactly the form the
judge's _io::pr(int) produces and the dataset examples (3, 4) show.
"""

import json
import os
import random
import subprocess
import sys
import tempfile

SLUG = "kosaraju's-algorithm"
ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(ROOT, "generated-tests", f"{SLUG}.jsonl")
N_CASES = 2000
SEED = 20260606

# Keep typical graphs modest so 2000 cases compute fast and the edge-list strings
# stay small; we still include large-V / large-E edge cases up to the real bounds.
MAX_V_TYPICAL = 60
MAX_E_TYPICAL = 200

REF_SRC = r"""
#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
using namespace std;

// Iterative Kosaraju so a long path (V up to 5000) never overflows the stack.
static int kosaraju(int V, vector<vector<int>>& E) {
    vector<vector<int>> adj(V), radj(V);
    for (auto& e : E) {
        int a = e[0], b = e[1];
        if (a < 0 || a >= V || b < 0 || b >= V) continue;
        adj[a].push_back(b);
        radj[b].push_back(a);
    }
    // Pass 1: iterative DFS, push node to order stack on finish (post-order).
    vector<char> vis(V, 0);
    vector<int> order;
    order.reserve(V);
    vector<size_t> it(V, 0);
    for (int s = 0; s < V; s++) {
        if (vis[s]) continue;
        vector<int> stk;
        stk.push_back(s);
        vis[s] = 1;
        while (!stk.empty()) {
            int u = stk.back();
            if (it[u] < adj[u].size()) {
                int v = adj[u][it[u]++];
                if (!vis[v]) { vis[v] = 1; stk.push_back(v); }
            } else {
                order.push_back(u);
                stk.pop_back();
            }
        }
    }
    // Pass 2: process nodes in reverse finish order over the transpose graph.
    vector<char> vis2(V, 0);
    int scc = 0;
    for (int i = V - 1; i >= 0; i--) {
        int s = order[i];
        if (vis2[s]) continue;
        scc++;
        vector<int> stk;
        stk.push_back(s);
        vis2[s] = 1;
        while (!stk.empty()) {
            int u = stk.back();
            stk.pop_back();
            for (int v : radj[u]) if (!vis2[v]) { vis2[v] = 1; stk.push_back(v); }
        }
    }
    return scc;
}

int main() {
    int V, m;
    if (!(cin >> V >> m)) return 0;
    vector<vector<int>> E(m, vector<int>(2));
    for (int i = 0; i < m; i++) cin >> E[i][0] >> E[i][1];
    cout << kosaraju(V, E) << "\n";
    return 0;
}
"""


def build_ref(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", "-o", binp, src],
        check=True,
    )
    return binp


def run_ref(binp, V, edges):
    lines = [f"{V} {len(edges)}"]
    for u, v in edges:
        lines.append(f"{u} {v}")
    inp = "\n".join(lines) + "\n"
    out = subprocess.run(
        [binp], input=inp, capture_output=True, text=True, timeout=60
    ).stdout
    return out.strip()


def rand_edges(V, E, rng):
    """E directed edges between DISTINCT nodes 0..V-1 (a -> b, a != b).
    Multi-edges (duplicate ordered pairs) are allowed; self loops are NOT emitted
    so the edge count stays strictly within 0 <= E <= V*(V-1). Requires V >= 2."""
    edges = []
    if V < 2:
        return edges
    for _ in range(E):
        u = rng.randrange(V)
        v = rng.randrange(V - 1)
        if v >= u:
            v += 1  # remap to avoid u == v -> uniform over the V-1 distinct targets
        edges.append((u, v))
    return edges


def gen_case(i, rng):
    """Return (V, directed_edges) within constraints, edge cases sprinkled in."""
    r = rng.random()
    # ---- deterministic edge cases ----
    if i == 0:
        return 1, []                       # single node, no edges -> 1 SCC
    if i == 1:
        return 2, [(0, 1), (1, 0)]         # smallest cycle pair -> 1 SCC
    if i == 2:
        return 2, []                       # two isolated nodes -> 2 SCCs
    if i == 3:
        return 2, [(0, 1)]                 # one directed edge -> 2 SCCs
    if i == 4:
        return 2, [(0, 1), (1, 0)]         # 2-cycle -> 1 SCC
    if i == 5:
        return 3, [(0, 1), (1, 2)]         # path (the dataset's "your turn") -> 3
    if i == 6:
        # dataset example 1: 5 nodes, 3 SCCs
        return 5, [(0, 2), (1, 0), (2, 1), (0, 3), (3, 4)]
    if i == 7:
        # dataset example 2: 8 nodes, 4 SCCs
        return 8, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4),
                   (4, 5), (4, 7), (5, 6), (6, 4), (6, 7)]
    if i == 8:
        # MAX V, no edges -> every vertex its own SCC -> 5000 SCCs
        return 5000, []
    if i == 9:
        # MAX V single big directed cycle -> 1 SCC. E = V = 5000.
        V = 5000
        return V, [(k, (k + 1) % V) for k in range(V)]
    if i == 10:
        # MAX V directed path -> V SCCs (5000). Stress for stack depth (iterative ref).
        V = 5000
        return V, [(k, k + 1) for k in range(V - 1)]
    if i == 11:
        # Two cycles joined by a one-way bridge -> 2 SCCs, large V.
        V = 5000
        half = V // 2
        e = [(k, (k + 1) % half) for k in range(half)]              # cycle A
        e += [(half + k, half + ((k + 1) % (V - half))) for k in range(V - half)]  # cycle B
        e.append((0, half))                                        # bridge A->B
        return V, e
    if i == 12:
        # Star out of node 0 (0 -> k), acyclic -> V SCCs (each node alone).
        V = rng.randint(2, 30)
        return V, [(0, k) for k in range(1, V)]

    # ---- randomized families ----
    if r < 0.14:
        # single directed cycle -> 1 SCC
        V = rng.randint(2, MAX_V_TYPICAL)
        return V, [(k, (k + 1) % V) for k in range(V)]
    if r < 0.26:
        # directed acyclic path -> V SCCs
        V = rng.randint(2, MAX_V_TYPICAL)
        edges = [(k, k + 1) for k in range(V - 1)]
        rng.shuffle(edges)
        return V, edges
    if r < 0.40:
        # several disjoint directed cycles (each cycle = 1 SCC, plus singletons)
        V = rng.randint(4, MAX_V_TYPICAL)
        nodes = list(range(V))
        rng.shuffle(nodes)
        edges = []
        idx = 0
        while idx < V:
            clen = rng.randint(1, min(5, V - idx))
            grp = nodes[idx:idx + clen]
            if clen >= 2:
                for k in range(clen):
                    edges.append((grp[k], grp[(k + 1) % clen]))
            idx += clen
        rng.shuffle(edges)
        return V, edges
    if r < 0.52:
        # random DAG-ish: edges only from lower to higher index (acyclic) -> V SCCs
        V = rng.randint(2, MAX_V_TYPICAL)
        E = rng.randint(0, min(MAX_E_TYPICAL, V * (V - 1) // 2))
        edges = []
        for _ in range(E):
            a = rng.randrange(V)
            b = rng.randrange(V)
            if a == b:
                continue
            if a > b:
                a, b = b, a
            edges.append((a, b))
        return V, edges
    if r < 0.62:
        # complete directed graph on small V -> 1 SCC (a->b for all a!=b)
        V = rng.randint(2, 12)
        edges = [(a, b) for a in range(V) for b in range(V) if a != b]
        return V, edges
    if r < 0.70:
        # empty edge list -> V SCCs (exercise E == 0 boundary)
        V = rng.randint(1, MAX_V_TYPICAL)
        return V, []
    if r < 0.80:
        # larger sparse random directed graph (stress, bigger V)
        V = rng.randint(150, 600)
        E = rng.randint(V, 3 * V)
        E = min(E, V * (V - 1))
        return V, rand_edges(V, E, rng)
    if r < 0.88:
        # dense small directed graph with self loops & multi-edges
        V = rng.randint(2, 15)
        cap = V * (V - 1)
        E = rng.randint(0, max(1, min(MAX_E_TYPICAL, cap)))
        return V, rand_edges(V, E, rng)
    # general random directed graph
    V = rng.randint(1, MAX_V_TYPICAL)
    cap = V * (V - 1)
    E = rng.randint(0, max(0, min(MAX_E_TYPICAL, cap)))
    return V, rand_edges(V, E, rng)


def edges_to_str(edges):
    if not edges:
        return "[]"
    return "[" + ", ".join(f"[{u}, {v}]" for u, v in edges) + "]"


def main():
    rng = random.Random(SEED)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        binp = build_ref(tmp)
        with open(OUT, "w") as f:
            for i in range(N_CASES):
                V, edges = gen_case(i, rng)
                # ---- constraint validation: never emit an out-of-bounds input ----
                assert 1 <= V <= 5000, V
                cap = V * (V - 1)
                assert 0 <= len(edges) <= cap, (V, len(edges), cap)
                for u, v in edges:
                    assert 0 <= u <= V - 1, (V, u)
                    assert 0 <= v <= V - 1, (V, v)
                    assert u != v, (V, u, v)  # no self loops (keep E <= V*(V-1))
                expected = run_ref(binp, V, edges)
                assert expected != "", f"empty expected for case {i}"
                line = {
                    "inputs": {"V": str(V), "E": edges_to_str(edges)},
                    "expected": expected,
                }
                f.write(json.dumps(line) + "\n")
                if (i + 1) % 250 == 0:
                    print(f"  {i+1}/{N_CASES}", file=sys.stderr)
    print(f"wrote {N_CASES} cases to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
