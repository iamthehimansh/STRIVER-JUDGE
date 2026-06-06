#!/usr/bin/env python3
"""
Test-case generator for Striver problem: bridges-in-graph (Critical Connections).

Signature: vector<vector<int>> criticalConnections(int V, vector<vector<int>>& E)
Param order: V (int), E (2D int array of edges).

Constraints:
  2 <= V, E <= 10^4
  0 <= a_i, b_i <= V-1
  Undirected CONNECTED graph.

The reference (Tarjan's bridge-finding) DFS-traverses the graph. We generate
CONNECTED graphs only (as the statement requires). Expected outputs are computed
by compiling and running the EXACT same C++ reference that is submitted to the
live judge, guaranteeing self-consistency (pair order, tokenization).

Output: one JSON object per line:
  {"inputs": {"V": "<int>", "E": "[[a,b],...]"}, "expected": "<flattened bridges>"}
"""
import json
import os
import random
import subprocess
import tempfile

SLUG = "bridges-in-graph"
ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(ROOT, "generated-tests", SLUG + ".jsonl")
N_CASES = 2000

# Keep sizes well within 10^4 but cover small + large. The reference uses
# recursion; deep chains near 10^4 can overflow the stack, so cap structural
# depth modestly while still exercising large graphs.
random.seed(20240606)

REF_CPP = r'''#include <vector>
#include <algorithm>
#include <iostream>
#include <string>
#include <sstream>
using namespace std;
class Solution {
public:
    int timer;
    void dfs(int node, int parent, vector<int>& tin, vector<int>& low,
             vector<vector<int>>& adj, vector<vector<int>>& ans, vector<bool>& vis) {
        vis[node] = true; low[node] = tin[node] = timer; timer++;
        for (auto v : adj[node]) {
            if (v == parent) continue;
            if (vis[v]) low[node] = min(low[node], low[v]);
            else {
                dfs(v, node, tin, low, adj, ans, vis);
                low[node] = min(low[node], low[v]);
                if (low[v] > tin[node]) ans.push_back({v, node});
            }
        }
    }
    vector<vector<int>> criticalConnections(int V, vector<vector<int>>& E) {
        timer = 0;
        vector<vector<int>> adj(V);
        for (auto& c : E) { adj[c[0]].push_back(c[1]); adj[c[1]].push_back(c[0]); }
        vector<vector<int>> ans;
        vector<bool> vis(V, false);
        vector<int> tin(V, 0), low(V, 0);
        for (int i = 0; i < V; i++) if (!vis[i]) dfs(i, -1, tin, low, adj, ans, vis);
        return ans;
    }
};
int main() {
    int T; if(!(cin >> T)) return 0;
    while (T--) {
        int V, M; cin >> V >> M;
        vector<vector<int>> E(M, vector<int>(2));
        for (int i = 0; i < M; i++) cin >> E[i][0] >> E[i][1];
        Solution s;
        auto res = s.criticalConnections(V, E);
        ostringstream os;
        for (size_t i = 0; i < res.size(); i++) {
            os << res[i][0] << " " << res[i][1];
            if (i + 1 < res.size()) os << " ";
        }
        cout << os.str() << "\n";
    }
    return 0;
}
'''


def build_ref():
    d = tempfile.mkdtemp(prefix="bridgegen_")
    src = os.path.join(d, "ref.cpp")
    binp = os.path.join(d, "ref")
    with open(src, "w") as f:
        f.write(REF_CPP)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp], check=True)
    return binp


def gen_connected_graph():
    """Return (V, edges) for a connected undirected SIMPLE graph within bounds.

    Strategy: pick V, build a random spanning tree (guarantees connected), then
    optionally add extra non-duplicate edges.

    NOTE on sizing: the live judge batches all 2000 cases into one process and
    truncates total stdout at ~1MB. The bridge output can be large (a tree on V
    nodes yields V-1 bridges = 2(V-1) numbers). We therefore cap V modestly and,
    for larger V, force enough cycle edges that the bridge count stays small —
    keeping each case's output bounded. Constraints (2<=V,E<=1e4) are still met.
    Capping V also keeps the reference's recursive DFS well within the stack.
    """
    shape = random.random()
    if shape < 0.18:
        V = random.choice([2, 3, 4, 5, 6])
    elif shape < 0.70:
        V = random.randint(2, 40)
    elif shape < 0.92:
        V = random.randint(40, 120)
    else:
        V = random.randint(120, 250)

    nodes = list(range(V))
    random.shuffle(nodes)
    edge_set = set()
    edges = []

    def add(a, b):
        if a == b:
            return False
        key = (min(a, b), max(a, b))
        if key in edge_set:
            return False
        edge_set.add(key)
        edges.append([a, b])
        return True

    # Spanning tree connecting all nodes (random attach -> avoids pure-chain
    # worst case which could blow recursion; attach each node to a random
    # earlier node).
    for i in range(1, V):
        # bias toward shallow trees: attach to a recent-ish earlier node
        j = random.randint(max(0, i - 30), i - 1) if random.random() < 0.5 else random.randint(0, i - 1)
        add(nodes[i], nodes[j])

    # Add extra edges (cycles -> remove bridges). Edge count must stay <= 10^4
    # and >= 1 (we already have V-1 >= 1 since V>=2).
    max_extra = 10000 - len(edges)
    if max_extra > 0:
        # number of extra edges: vary to create graphs with many vs few bridges.
        # For larger graphs, lean denser so the bridge OUTPUT stays small (the
        # judge's batched stdout is capped at ~1MB across all cases).
        density = random.random()
        if V <= 40 and density < 0.30:
            target_extra = 0  # small tree -> every edge is a bridge (good edge case)
        elif V <= 40:
            target_extra = random.randint(0, min(max_extra, V * 2))
        elif density < 0.5:
            # medium/large: ensure a fair number of cycles to bound bridges
            target_extra = random.randint(V // 2, min(max_extra, V * 3))
        else:
            target_extra = random.randint(0, max_extra)
        attempts = 0
        while target_extra > 0 and attempts < target_extra * 5 + 50:
            a = random.randrange(V)
            b = random.randrange(V)
            if add(a, b):
                target_extra -= 1
            attempts += 1

    # Ensure E within [2, 10^4]; if only V-1 == 1 edge (V==2), constraint says
    # E >= 2. Add a duplicate? Graph is simple normally, but to satisfy E>=2 for
    # V==2 we can add a parallel edge (multigraph). Tarjan ref treats parent
    # skip only once -> a parallel edge makes the single edge NOT a bridge.
    # To stay simple & valid, for V==2 we keep E==1 only if that's acceptable;
    # constraint demands E>=2. So for V==2 add a second parallel edge.
    if len(edges) < 2:
        # V == 2 case, add parallel edge 0-1
        edges.append([edges[0][0], edges[0][1]])

    random.shuffle(edges)
    return V, edges


# The live judge batches all cases into a single process and truncates total
# stdout at ~1MB. Keep total expected output comfortably under that, and bound
# any single case so one giant tree can't dominate.
TOTAL_OUTPUT_BUDGET = 800_000  # bytes across all cases (safe < 1MB cap)
PER_CASE_OUTPUT_CAP = 4_000    # bytes for one case's expected string


def run_ref(binp, cases):
    """Run the C++ reference on a list of (V, edges); return list of output strings."""
    sin = [str(len(cases))]
    for V, E in cases:
        sin.append(f"{V} {len(E)}")
        for a, b in E:
            sin.append(f"{a} {b}")
    stdin_str = "\n".join(sin) + "\n"
    proc = subprocess.run([binp], input=stdin_str, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("reference run failed: " + proc.stderr[:2000])
    lines = proc.stdout.split("\n")
    return [lines[i].strip() if i < len(lines) else "" for i in range(len(cases))]


def main():
    binp = build_ref()

    # deterministic edge cases first (min sizes, extremes, dataset example)
    edge_cases = [
        (2, [[0, 1], [0, 1]]),          # two nodes, parallel edge -> no bridge
        (2, [[0, 1], [1, 0]]),          # parallel reversed -> no bridge
        (3, [[0, 1], [1, 2], [2, 0]]),  # triangle -> no bridge
        (3, [[0, 1], [1, 2]]),          # path -> 2 bridges
        (4, [[0, 1], [1, 2], [2, 0], [1, 3]]),  # dataset example -> bridge [1,3]
        (5, [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]),  # cycle -> no bridge
        (5, [[0, 1], [1, 2], [2, 3], [3, 4]]),  # path -> 4 bridges
        (6, [[0, 1], [1, 2], [2, 0], [3, 4], [4, 5], [5, 3], [2, 3]]),  # two triangles + 1 bridge
    ]
    cases = list(edge_cases)
    while len(cases) < N_CASES:
        cases.append(gen_connected_graph())
    cases = cases[:N_CASES]

    # Compute outputs; enforce per-case + total output budget by resampling any
    # case whose output is too large. Loop until everything fits.
    for attempt in range(60):
        outs = run_ref(binp, cases)
        total = sum(len(o) for o in outs)
        over_idx = [i for i, o in enumerate(outs) if len(o) > PER_CASE_OUTPUT_CAP]
        if total <= TOTAL_OUTPUT_BUDGET and not over_idx:
            break
        # resample oversized cases first
        targets = set(over_idx)
        if total > TOTAL_OUTPUT_BUDGET:
            # additionally resample the largest-output cases (skip the 8 fixed
            # edge cases, which are tiny) until projected total fits
            order = sorted(range(len(outs)), key=lambda i: len(outs[i]), reverse=True)
            running = total
            for i in order:
                if running <= TOTAL_OUTPUT_BUDGET:
                    break
                if i < len(edge_cases):
                    continue
                targets.add(i)
                running -= len(outs[i])  # new case will be smaller in expectation
        for i in targets:
            if i < len(edge_cases):
                continue
            cases[i] = gen_connected_graph()
    else:
        # final safety: hard-replace any still-oversized case with a tiny one
        outs = run_ref(binp, cases)
        for i, o in enumerate(outs):
            if len(o) > PER_CASE_OUTPUT_CAP and i >= len(edge_cases):
                cases[i] = (4, [[0, 1], [1, 2], [2, 0], [1, 3]])
        outs = run_ref(binp, cases)

    with open(OUT, "w") as f:
        for idx, (V, E) in enumerate(cases):
            expected = outs[idx]
            e_str = "[" + ",".join("[" + str(a) + "," + str(b) + "]" for a, b in E) + "]"
            obj = {"inputs": {"V": str(V), "E": e_str}, "expected": expected}
            f.write(json.dumps(obj) + "\n")

    total = sum(len(o) for o in outs)
    print(f"Wrote {len(cases)} cases to {OUT}; total expected output bytes = {total}")


if __name__ == "__main__":
    main()
