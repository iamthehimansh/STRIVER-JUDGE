#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Why priority Queue is used in Dijkstra's Algorithm"
slug: dijkstra's-algorithm-1

Signature:
    vector<int> dijkstra(int V, vector<vector<int>> edges, int S)

Param order -> jsonl input keys (signature order): V, edges, S

Constraints:
    1 <= V <= 10000
    0 <= edges[i][j] <= 10000        (weights; vertex ids are 0..V-1 < V <= 10000 anyway)
    1 <= edges.size() <= V*(V-1)/2   (simple graph: no self loops, no duplicate undirected edges)
    0 <= S < V

Because edges.size() >= 1, we need at least one edge => V >= 2.

This script:
  1. Generates random simple undirected weighted graphs strictly within constraints.
  2. Computes expected shortest-distance arrays with a compiled C++ reference
     (Dijkstra via priority_queue), unreachable = 1e9.
  3. Writes one JSON object per line to the generated-tests jsonl file.

Output line format:
  {"inputs": {"V": "..", "edges": "[[u,v,w],...]", "S": ".."}, "expected": "[d0, d1, ...]"}
"""
import json
import os
import random
import subprocess
import sys

SLUG = "dijkstra's-algorithm-1"
PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", SLUG + ".jsonl")
TMP = "/tmp/dijref"
RUNNER = os.path.join(TMP, "runner")

N_CASES = 2000
random.seed(20260606)

REF_SRC = r'''
#include <vector>
#include <queue>
using namespace std;
class Solution{
public:
    vector<int> dijkstra(int V, vector<vector<int>> edges, int S) {
        vector<vector<pair<int,int>>> adj(V);
        for(auto &e : edges){
            int u=e[0], v=e[1], w=e[2];
            adj[u].push_back({v,w});
            adj[v].push_back({u,w});
        }
        vector<int> dis(V, 1000000000);
        priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
        dis[S]=0;
        pq.push({0,S});
        while(!pq.empty()){
            int d=pq.top().first;
            int u=pq.top().second;
            pq.pop();
            if(d>dis[u]) continue;
            for(auto &p : adj[u]){
                int v=p.first, w=p.second;
                if(dis[u]+w < dis[v]){
                    dis[v]=dis[u]+w;
                    pq.push({dis[v],v});
                }
            }
        }
        return dis;
    }
};
'''

RUNNER_SRC = r'''
#include <vector>
#include <queue>
#include <iostream>
using namespace std;
#include "sol.h"
int main(){
    int V,S,E;
    if(!(cin>>V)) return 0;
    cin>>S>>E;
    vector<vector<int>> edges(E, vector<int>(3));
    for(int i=0;i<E;i++) cin>>edges[i][0]>>edges[i][1]>>edges[i][2];
    Solution sol;
    vector<int> res = sol.dijkstra(V, edges, S);
    cout<<"[";
    for(int i=0;i<(int)res.size();i++){ if(i) cout<<", "; cout<<res[i]; }
    cout<<"]\n";
    return 0;
}
'''


def build_runner():
    os.makedirs(TMP, exist_ok=True)
    with open(os.path.join(TMP, "sol.h"), "w") as f:
        f.write(REF_SRC)
    with open(os.path.join(TMP, "runner.cpp"), "w") as f:
        f.write(RUNNER_SRC)
    r = subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", "-I" + TMP,
         os.path.join(TMP, "runner.cpp"), "-o", RUNNER],
        capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit("compile failed")


def run_ref(V, S, edges):
    lines = [str(V), str(S), str(len(edges))]
    for u, v, w in edges:
        lines.append(f"{u} {v} {w}")
    inp = "\n".join(lines) + "\n"
    out = subprocess.run([RUNNER], input=inp, capture_output=True, text=True)
    return out.stdout.strip()


def max_edges(V):
    return V * (V - 1) // 2


def gen_simple_graph(V, num_edges):
    """Generate `num_edges` distinct undirected simple edges (no self loops)
    among V vertices, with random weights in [0,10000]."""
    cap = max_edges(V)
    num_edges = min(num_edges, cap)
    num_edges = max(num_edges, 1)
    seen = set()
    edges = []
    # If num_edges is close to cap, just enumerate all and sample.
    if num_edges >= cap or (cap <= 5000 and num_edges > cap * 0.6):
        allp = [(a, b) for a in range(V) for b in range(a + 1, V)]
        random.shuffle(allp)
        chosen = allp[:num_edges]
        for a, b in chosen:
            edges.append([a, b, random.randint(0, 10000)])
        return edges
    while len(edges) < num_edges:
        a = random.randint(0, V - 1)
        b = random.randint(0, V - 1)
        if a == b:
            continue
        if a > b:
            a, b = b, a
        if (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append([a, b, random.randint(0, 10000)])
    return edges


def case_iter():
    """Yield (V, S, edges) tuples covering edge cases + random."""
    # ---- Explicit edge cases ----
    # Minimum: V=2, single edge
    yield (2, 0, [[0, 1, 9]])
    yield (2, 1, [[0, 1, 0]])             # weight 0
    yield (2, 0, [[0, 1, 10000]])         # max weight
    # dataset examples
    yield (3, 2, [[0, 1, 1], [0, 2, 6], [1, 2, 3]])
    yield (4, 0, [[0, 1, 1], [0, 3, 2], [1, 2, 4], [2, 3, 3]])
    # unreachable vertex: V=3 but only edge 0-1, vertex 2 isolated -> 1e9
    yield (3, 0, [[0, 1, 5]])
    yield (4, 0, [[0, 1, 5], [2, 3, 7]])  # two components
    # all weights zero
    yield (5, 0, [[0, 1, 0], [1, 2, 0], [2, 3, 0], [3, 4, 0]])
    # complete tiny graph K4
    yield (4, 1, [[0, 1, 3], [0, 2, 7], [0, 3, 2], [1, 2, 5], [1, 3, 9], [2, 3, 4]])

    # ---- Random cases ----
    # IMPORTANT: the judge captures at most 256 KB of TOTAL stdout across ALL
    # batched cases (scripts/judge_exec.py OUT_CAP = 256*1024). Each case prints
    # V numbers (~up to 11 chars incl. the 1e9 sentinel + a space). With ~2000
    # cases that budget is ~128 bytes/case on average, so we keep V SMALL. The
    # algorithm is identical regardless of V, so small graphs fully exercise it
    # while keeping the combined output safely under the cap.
    for _ in range(N_CASES):
        bucket = random.random()
        if bucket < 0.55:
            V = random.randint(2, 10)        # tiny (often dense)
        elif bucket < 0.85:
            V = random.randint(2, 20)        # small
        else:
            V = random.randint(2, 35)        # medium-small (still tiny output)

        cap = max_edges(V)
        # decide edge count (bounded so output/ref stay small)
        if V <= 10:
            num = random.randint(1, cap)               # may be complete
        else:
            num = random.randint(1, min(cap, V * 3))   # up to ~moderately dense
        edges = gen_simple_graph(V, num)
        S = random.randint(0, V - 1)
        yield (V, S, edges)


def edges_to_str(edges):
    parts = []
    for u, v, w in edges:
        parts.append(f"[{u},{v},{w}]")
    return "[" + ",".join(parts) + "]"


def main():
    build_runner()
    cases = list(case_iter())
    # We only want N_CASES total lines; explicit edge cases are extra but fine.
    # Trim to exactly N_CASES (keep the explicit edge cases at front).
    cases = cases[:N_CASES]

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    n = 0
    with open(OUT_PATH, "w") as out:
        for (V, S, edges) in cases:
            # constraint guards
            assert 1 <= V <= 10000
            assert 0 <= S < V
            assert 1 <= len(edges) <= max_edges(V)
            for u, v, w in edges:
                assert 0 <= u < V and 0 <= v < V and u != v
                assert 0 <= w <= 10000
            expected = run_ref(V, S, edges)
            assert expected.startswith("[") and expected.endswith("]")
            rec = {
                "inputs": {
                    "V": str(V),
                    "edges": edges_to_str(edges),
                    "S": str(S),
                },
                "expected": expected,
            }
            out.write(json.dumps(rec) + "\n")
            n += 1
    print(f"wrote {n} cases -> {OUT_PATH}")


if __name__ == "__main__":
    main()
