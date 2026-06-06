#!/usr/bin/env python3
"""
Generator for problem: topological-sort-or-kahns-algorithm
- Method: vector<int> topoSort(int V, vector<int> adj[])
- Constraints: 1 <= V <= 1e4, 0 <= |edges| <= 1e4
- Input keys (matching method param names): V, adj
- adj is an adjacency list of a DAG.
- Expected output: result of Kahn's BFS topo sort with the smallest-index
  initial frontier (pushed in order 0..V-1). The user reference solution is run
  via the judge harness against this exact same input format, so a correct
  Kahn-based solution will reproduce the order exactly.
"""

import json
import os
import random
import subprocess
import sys
import tempfile
from collections import deque

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/topological-sort-or-kahns-algorithm.jsonl"
N_CASES = 2000
SEED = 12345

# Reference C++ solution (matches what the judge runs the user's submission as).
REF_CPP = r'''
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <queue>
using namespace std;
class Solution{
public:
    vector<int> topoSort(int V, vector<int> adj[]){
        vector<int> indeg(V,0);
        for(int i=0;i<V;i++) for(int x:adj[i]) indeg[x]++;
        queue<int> q;
        for(int i=0;i<V;i++) if(indeg[i]==0) q.push(i);
        vector<int> r;
        while(!q.empty()){
            int u=q.front(); q.pop();
            r.push_back(u);
            for(int v:adj[u]){
                if(--indeg[v]==0) q.push(v);
            }
        }
        return r;
    }
};
// Driver: reads V on first line and adjacency list on following V lines as
// space-separated neighbour lists. Prints the topo order space-separated.
int main(){
    int V; if(!(cin>>V)) return 0;
    vector<vector<int>> adj(V);
    string line; getline(cin, line); // eat newline
    for(int i=0;i<V;i++){
        getline(cin, line);
        stringstream ss(line);
        int x;
        while(ss>>x) adj[i].push_back(x);
    }
    Solution sol;
    vector<int> r = sol.topoSort(V, adj.data());
    for(size_t i=0;i<r.size();i++){
        if(i) cout<<' ';
        cout<<r[i];
    }
    cout<<'\n';
    return 0;
}
'''


def compile_ref():
    tmpdir = tempfile.mkdtemp(prefix="topo_ref_")
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(REF_CPP)
    r = subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("Compile error:\n", r.stderr, file=sys.stderr)
        sys.exit(1)
    return binp


def run_ref(binp, V, adj):
    """Run reference and return list of ints output by Kahn's."""
    lines = [str(V)]
    for nbrs in adj:
        lines.append(" ".join(str(x) for x in nbrs))
    stdin = "\n".join(lines) + "\n"
    r = subprocess.run([binp], input=stdin, capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise RuntimeError(f"ref crashed: {r.stderr}")
    out = r.stdout.strip()
    if not out:
        return []
    return [int(x) for x in out.split()]


def random_dag(V, max_edges):
    """Generate a random DAG with V vertices and up to max_edges edges.
    Uses a random permutation to fix a topological order, then samples edges
    only from earlier-in-permutation to later (guaranteeing acyclicity).
    Returns adjacency list adj where adj[u] = list of v with edge u->v."""
    perm = list(range(V))
    random.shuffle(perm)
    pos = [0]*V
    for i, v in enumerate(perm):
        pos[v] = i
    # Cap max possible edges by V*(V-1)/2 (DAG, simple, no multi-edge).
    max_possible = V*(V-1)//2
    target = min(max_edges, max_possible)
    if target <= 0:
        return [[] for _ in range(V)]
    edges = set()
    # If target is dense relative to all pairs, enumerate; else sample.
    if target * 4 >= max_possible and max_possible <= 200000:
        all_pairs = []
        for i in range(V):
            for j in range(i+1, V):
                u = perm[i]; v = perm[j]
                all_pairs.append((u, v))
        random.shuffle(all_pairs)
        for (u, v) in all_pairs[:target]:
            edges.add((u, v))
    else:
        attempts = 0
        while len(edges) < target and attempts < target * 10:
            i = random.randrange(V)
            j = random.randrange(V)
            if i == j:
                attempts += 1
                continue
            u, v = perm[min(i, j)], perm[max(i, j)]
            if (u, v) in edges:
                attempts += 1
                continue
            edges.add((u, v))
            attempts += 1
    adj = [[] for _ in range(V)]
    for (u, v) in edges:
        adj[u].append(v)
    # Sort neighbours for determinism in the harness call as well.
    for u in range(V):
        adj[u].sort()
    return adj


def adj_to_str(adj):
    """Serialize adj as a JSON-ish [[..],[..]] string for the judge's rdVVI."""
    parts = []
    for nbrs in adj:
        parts.append("[" + ",".join(str(x) for x in nbrs) + "]")
    return "[" + ",".join(parts) + "]"


def main():
    random.seed(SEED)
    binp = compile_ref()
    print(f"Reference compiled at {binp}")

    # Sanity-check against the dataset examples first.
    samples = [
        # Example 1: V=6, adj=[[],[],[3],[1],[0,1],[0,2]]
        (6, [[],[],[3],[1],[0,1],[0,2]]),
        # Example 2: V=4, adj=[[],[0],[0],[0]]
        (4, [[],[0],[0],[0]]),
    ]
    for V, adj in samples:
        out = run_ref(binp, V, adj)
        print(f"V={V} adj={adj} -> {out}")

    cases = []
    # Hand-picked edges
    cases.append((1, [[]]))           # min V
    cases.append((2, [[],[]]))        # 2 isolated
    cases.append((2, [[1],[]]))       # one edge
    cases.append((3, [[1],[2],[]]))   # chain
    cases.append((4, [[],[0],[0],[0]]))
    cases.append((6, [[],[],[3],[1],[0,1],[0,2]]))

    # NOTE: keep cumulative output well below the judge's 256KB stdout cap
    # (judge_exec.py truncates captured stdout to 256 KB, and the batch
    # submit mode runs ALL cases in one process). With 2000 cases we budget
    # ~100 bytes of output per case on average. Most cases are small, with
    # a handful of medium/larger ones at the tail for coverage.
    while len(cases) < N_CASES:
        idx = len(cases)
        remaining = N_CASES - len(cases)
        r = random.random()
        if remaining <= 5:
            # tail: a few mid-sized cases for coverage
            V = random.randint(200, 400)
        elif r < 0.7:
            V = random.randint(1, 15)
        elif r < 0.92:
            V = random.randint(15, 40)
        elif r < 0.99:
            V = random.randint(40, 80)
        else:
            V = random.randint(80, 150)
        # Edge count: 0..min(1e4, V*(V-1)/2). Bias toward sparse-ish.
        max_e = min(10000, V*(V-1)//2)
        if max_e <= 0:
            E = 0
        else:
            r2 = random.random()
            if r2 < 0.1:
                E = 0
            elif r2 < 0.5:
                E = random.randint(0, min(max_e, V))           # sparse
            elif r2 < 0.85:
                E = random.randint(0, min(max_e, 2*V))         # medium
            else:
                E = random.randint(0, max_e)                   # dense up to cap
        adj = random_dag(V, E)
        cases.append((V, adj))

    # Write jsonl
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for i, (V, adj) in enumerate(cases):
            out = run_ref(binp, V, adj)
            # Sanity: must include all V nodes for a valid DAG (no cycles).
            if len(out) != V:
                raise RuntimeError(f"case {i}: ref returned {len(out)} of {V} nodes (cycle?)")
            expected = "[" + ", ".join(str(x) for x in out) + "]"
            line = {
                "inputs": {"V": str(V), "adj": adj_to_str(adj)},
                "expected": expected,
            }
            f.write(json.dumps(line) + "\n")
            if i % 200 == 0:
                print(f"  case {i}: V={V}, E={sum(len(x) for x in adj)}")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
