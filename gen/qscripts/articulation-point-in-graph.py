#!/usr/bin/env python3
"""
Generator for "Articulation point in graph" (slug: articulation-point-in-graph).

Judge-facing signature (what a submission must use so the harness can bind it):
    vector<int> articulationPoints(int n, vector<vector<int>>& edges)
The dataset testcases provide keys {"n", "edges"} and the harness binds them by
name. The original starter `vector<int> adj[]` is NOT bindable by the judge
harness (array-of-vector params are unsupported), so the judgeable form takes the
edge list and rebuilds the adjacency itself.

jsonl line format:
    {"inputs": {"n": "<int>", "edges": "[[u,v],...]"}, "expected": "<v0 v1 ...>"}

Constraints (from problem): 1 <= V, E <= 1e4 ; zero-based nodes 0..V-1 ;
undirected; loops (self edges) may be present; graph may be disconnected.

Expected output is computed by an external C++ reference (Tarjan articulation
points, iterative to survive V=1e4) compiled at runtime. Output is space-separated
articulation vertices in ascending order, or "-1" if there are none -- exactly the
form the judge's _io::pr(vector<int>) produces and the dataset examples show.
"""

import json
import os
import random
import subprocess
import sys
import tempfile

SLUG = "articulation-point-in-graph"
ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(ROOT, "generated-tests", f"{SLUG}.jsonl")
N_CASES = 2000
SEED = 20260606

# Keep total edges modest so 2000 cases compute fast while still exercising the
# constraint space; constraints allow up to 1e4 but huge dense graphs are slow
# and add little coverage. We still include large-V edge cases.
MAX_V_TYPICAL = 60
MAX_E_TYPICAL = 200

REF_SRC = r"""
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
static vector<int> articulationPoints(int n, vector<vector<int>>& edges) {
    int V = n;
    vector<vector<int>> adj(V);
    for (auto& e : edges) {
        int a = e[0], b = e[1];
        if (a < 0 || a >= V || b < 0 || b >= V) continue;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<int> disc(V, -1), low(V, -1), parent(V, -2);
    vector<size_t> idx(V, 0);
    vector<char> isAP(V, 0);
    int timer = 0;
    for (int s = 0; s < V; s++) {
        if (disc[s] != -1) continue;
        vector<int> callStack;
        callStack.push_back(s);
        disc[s] = low[s] = timer++;
        parent[s] = -1;
        int rootChildren = 0;
        while (!callStack.empty()) {
            int u = callStack.back();
            if (idx[u] < adj[u].size()) {
                int v = adj[u][idx[u]++];
                if (v == u) continue; // self loop ignored
                if (disc[v] == -1) {
                    parent[v] = u;
                    if (u == s) rootChildren++;
                    disc[v] = low[v] = timer++;
                    callStack.push_back(v);
                } else if (v != parent[u]) {
                    low[u] = min(low[u], disc[v]);
                }
            } else {
                callStack.pop_back();
                int p = parent[u];
                if (p != -1) {
                    low[p] = min(low[p], low[u]);
                    if (low[u] >= disc[p] && p != s) isAP[p] = 1;
                }
            }
        }
        if (rootChildren > 1) isAP[s] = 1;
    }
    vector<int> res;
    for (int i = 0; i < V; i++) if (isAP[i]) res.push_back(i);
    if (res.empty()) res.push_back(-1);
    return res;
}
int main() {
    int n, m;
    if (!(cin >> n >> m)) return 0;
    vector<vector<int>> edges(m, vector<int>(2));
    for (int i = 0; i < m; i++) cin >> edges[i][0] >> edges[i][1];
    vector<int> r = articulationPoints(n, edges);
    for (size_t i = 0; i < r.size(); i++) { if (i) cout << ' '; cout << r[i]; }
    cout << "\n";
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


def run_ref(binp, n, edges):
    lines = [f"{n} {len(edges)}"]
    for u, v in edges:
        lines.append(f"{u} {v}")
    inp = "\n".join(lines) + "\n"
    out = subprocess.run(
        [binp], input=inp, capture_output=True, text=True, timeout=30
    ).stdout
    return out.strip()


def rand_edges(V, E, rng):
    """E undirected edges over nodes 0..V-1; self loops & multi-edges allowed
    (problem says loops may be present)."""
    edges = []
    for _ in range(E):
        u = rng.randrange(V)
        v = rng.randrange(V)
        edges.append((u, v))
    return edges


def gen_case(i, rng):
    """Return (n, edges) within constraints, with edge cases sprinkled in."""
    r = rng.random()
    if i == 0:
        return 1, [(0, 0)]  # single node, self loop (E>=1 per constraints)
    if i == 1:
        return 2, [(0, 1)]  # two nodes one edge
    if i == 2:
        return 3, [(0, 1), (1, 2)]  # path -> middle is AP
    if i == 3:
        return 3, [(0, 1), (0, 2), (1, 2)]  # triangle -> none
    if i == 4:
        return 1, [(0, 0)]  # self loop only
    if i == 5:
        # MAX-V cycle: V=E=1e4, no articulation points -> output "-1" (tiny)
        V = 10000
        return V, [(k, (k + 1) % V) for k in range(V)]
    if i == 6:
        # MAX-V star: center 0 is the only AP -> output "0" (tiny). E=V-1=9999.
        V = 10000
        return V, [(0, k) for k in range(1, V)]
    if i == 7:
        # MAX-E: 1e4 edges on a big cycle of 5000 nodes (multi/extra edges)
        V = 5000
        e = [(k, (k + 1) % V) for k in range(V)]
        while len(e) < 10000:
            e.append((rng.randrange(V), rng.randrange(V)))
        return V, e[:10000]
    if r < 0.12:
        # path / chain graph (every internal node is an AP)
        V = rng.randint(2, MAX_V_TYPICAL)
        edges = [(k, k + 1) for k in range(V - 1)]
        rng.shuffle(edges)
        return V, edges
    if r < 0.22:
        # cycle (no APs)
        V = rng.randint(3, MAX_V_TYPICAL)
        edges = [(k, (k + 1) % V) for k in range(V)]
        return V, edges
    if r < 0.34:
        # tree (random parent) -> internal nodes are APs
        V = rng.randint(2, MAX_V_TYPICAL)
        edges = [(rng.randrange(k), k) for k in range(1, V)]
        rng.shuffle(edges)
        return V, edges
    if r < 0.44:
        # star -> center is the only AP
        V = rng.randint(3, MAX_V_TYPICAL)
        edges = [(0, k) for k in range(1, V)]
        return V, edges
    if r < 0.52:
        # disconnected: a few components
        V = rng.randint(4, MAX_V_TYPICAL)
        comps = rng.randint(2, 4)
        edges = []
        nodes = list(range(V))
        rng.shuffle(nodes)
        parts = [nodes[k::comps] for k in range(comps)]
        for part in parts:
            for a in range(1, len(part)):
                edges.append((part[rng.randrange(a)], part[a]))
        rng.shuffle(edges)
        return V, edges
    if r < 0.58:
        # larger sparse graph (stress, bigger V). Capped at 300 so the batched
        # judge output line (the list of APs) stays well under the judge's
        # 256 KB cumulative stdout cap; the algorithm is identical for any V<=1e4.
        V = rng.randint(150, 300)
        E = rng.randint(V // 2, 2 * V)
        return V, rand_edges(V, E, rng)
    if r < 0.62:
        # dense-ish small graph with self loops & multi-edges
        V = rng.randint(2, 15)
        E = rng.randint(1, MAX_E_TYPICAL)
        return V, rand_edges(V, E, rng)
    # general random graph
    V = rng.randint(1, MAX_V_TYPICAL)
    E = rng.randint(1, MAX_E_TYPICAL)
    return V, rand_edges(V, E, rng)


def edges_to_str(edges):
    return "[" + ", ".join(f"[{u}, {v}]" for u, v in edges) + "]"


def main():
    rng = random.Random(SEED)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # The judge runs all cases in ONE batched process and captures stdout with a
    # 256 KB cap (scripts/judge_exec.py OUT_CAP). One output line per case; if the
    # cumulative output exceeds the cap it is truncated and trailing cases fail.
    # We budget the expected-output bytes to stay safely under that.
    OUT_BUDGET = 200 * 1024
    out_bytes = 0
    with tempfile.TemporaryDirectory() as tmp:
        binp = build_ref(tmp)
        with open(OUT, "w") as f:
            for i in range(N_CASES):
                V, edges = gen_case(i, rng)
                # safety: constraints 1<=V,E<=1e4 (E>=1 -> ensure an edge)
                if len(edges) == 0:
                    edges = [(0, 0)]  # self loop keeps E>=1, adds no AP
                assert 1 <= V <= 10000, V
                assert 1 <= len(edges) <= 10000, len(edges)
                for u, v in edges:
                    assert 0 <= u < V and 0 <= v < V
                expected = run_ref(binp, V, edges)
                out_bytes += len(expected) + 1  # +newline in batched stdout
                line = {
                    "inputs": {"n": str(V), "edges": edges_to_str(edges)},
                    "expected": expected,
                }
                f.write(json.dumps(line) + "\n")
                if (i + 1) % 250 == 0:
                    print(f"  {i+1}/{N_CASES} (out~{out_bytes} bytes)", file=sys.stderr)
    assert out_bytes < OUT_BUDGET, (
        f"cumulative expected output {out_bytes} exceeds judge cap budget "
        f"{OUT_BUDGET}; reduce graph sizes"
    )
    print(f"wrote {N_CASES} cases to {OUT} (total expected stdout ~{out_bytes} bytes)",
          file=sys.stderr)


if __name__ == "__main__":
    main()
