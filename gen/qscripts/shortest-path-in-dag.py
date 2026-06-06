#!/usr/bin/env python3
"""
Generator for Striver problem: shortest-path-in-dag

Method signature (starterCpp):
    vector<int> shortestPath(int N, int M, vector<vector<int>>& edges)

Judge input keys (signature order: N, M, edges).
    "N"     -> int as string, e.g. "4"
    "M"     -> int as string (= number of edges), e.g. "2"
    "edges" -> 2D int array as string, e.g. "[[0,1,2],[0,2,1]]"

NOTE: M is NOT a trailing size param (it precedes `edges` in the signature),
and the batch judge requires every method parameter to be bound to an input
key. So we keep all three keys N, M, edges.

expected -> space-separated shortest distances from vertex 0 to every vertex,
            -1 for unreachable vertices.

Constraints (from problem):
    1 <= N, M <= 5*10^4
    0 <= edge[i][0], edge[i][1] < N     (problem text writes N-1 but examples
                                          clearly use indices up to N-1, i.e. valid
                                          vertex range [0, N-1])
    1 <= edge[i][2] < 10^4

We keep the graph a DAG by only adding edges u->v with u<v over a random
permutation of vertices. Weights in [1, 9999].

Expected outputs are produced by compiling/running the reference C++ solution
(the same algorithm the live judge uses), so a correct submission reproduces
them exactly.
"""
import json
import os
import random
import subprocess
import tempfile

REF_CPP = r'''
#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    void dfs(int node, vector<pair<int,int>> adj[], vector<bool>& vis, vector<int>& topo){
        vis[node]=true;
        for(auto v:adj[node]) if(!vis[v.first]) dfs(v.first,adj,vis,topo);
        topo.push_back(node);
    }
    vector<int> shortestPath(int N, int M, vector<vector<int>>& edges){
        vector<pair<int,int>> adj[N];
        for(auto e:edges) adj[e[0]].push_back({e[1],e[2]});
        vector<bool> vis(N,false);
        vector<int> topo;
        for(int i=0;i<N;i++) if(!vis[i]) dfs(i,adj,vis,topo);
        reverse(topo.begin(),topo.end());
        vector<int> dis(N,1e9);
        dis[0]=0;
        for(auto u:topo) for(auto p:adj[u]){
            int v=p.first,d=p.second;
            if(dis[u]+d<dis[v]) dis[v]=dis[u]+d;
        }
        for(int i=0;i<N;i++) if(dis[i]==1e9) dis[i]=-1;
        return dis;
    }
};
int main(){
    int T; if(!(cin>>T)) return 0;
    while(T--){
        int N,M; cin>>N>>M;
        vector<vector<int>> edges(M, vector<int>(3));
        for(int i=0;i<M;i++) cin>>edges[i][0]>>edges[i][1]>>edges[i][2];
        Solution s; auto r=s.shortestPath(N,M,edges);
        for(int i=0;i<(int)r.size();i++){ if(i) cout<<' '; cout<<r[i]; }
        cout<<'\n';
    }
    return 0;
}
'''

BITS_SHIM = """#include <algorithm>
#include <vector>
#include <iostream>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <string>
#include <cmath>
#include <climits>
#include <cstring>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <numeric>
#include <functional>
"""

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/shortest-path-in-dag.jsonl"
N_CASES = 2000
MAX_W = 9999  # 1 <= w < 10^4
HARD_CAP_M = 50000  # M <= 5*10^4
HARD_CAP_N = 50000  # N <= 5*10^4


def build_ref(tmp):
    inc = os.path.join(tmp, "inc", "bits")
    os.makedirs(inc, exist_ok=True)
    with open(os.path.join(inc, "stdc++.h"), "w") as f:
        f.write(BITS_SHIM)
    src = os.path.join(tmp, "ref.cpp")
    with open(src, "w") as f:
        f.write(REF_CPP)
    binp = os.path.join(tmp, "ref")
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w",
         "-I", os.path.join(tmp, "inc"), src, "-o", binp],
        check=True,
    )
    return binp


def gen_case(idx, rng):
    """Return (N, edges) as a valid DAG within constraints."""
    # Edge cases
    if idx == 0:
        # smallest valid DAG with one real edge: dist = 0 1
        return 2, [[0, 1, 1]]
    if idx == 1:
        return 2, [[0, 1, 1]]  # smallest meaningful: dist = 0 1
    if idx == 2:
        return 2, [[1, 0, 5]]  # vertex 1 has no in-edge from 0's reach side; dist = 0 -1
    if idx == 3:
        # disconnected: vertex 1 unreachable
        return 3, [[1, 2, 7]]
    if idx == 4:
        # max weight edges, chain
        return 5, [[0, 1, MAX_W], [1, 2, MAX_W], [2, 3, MAX_W], [3, 4, MAX_W]]
    if idx == 5:
        # all from 0
        return 6, [[0, 1, 3], [0, 2, 3], [0, 3, 3], [0, 4, 3], [0, 5, 3]]

    # Random sizing buckets
    bucket = rng.random()
    if bucket < 0.55:
        N = rng.randint(2, 30)
    elif bucket < 0.85:
        N = rng.randint(2, 300)
    elif bucket < 0.97:
        N = rng.randint(2, 3000)
    else:
        N = rng.randint(2, HARD_CAP_N)

    # Use a random permutation; edge only from earlier-in-perm to later-in-perm
    # => guaranteed acyclic. perm[pos] = vertex label.
    perm = list(range(N))
    rng.shuffle(perm)
    pos = {v: i for i, v in enumerate(perm)}  # position in topo order

    # number of edges
    max_possible = N * (N - 1) // 2
    # M must be >=1; cap at HARD_CAP_M and at max_possible (no dup needed but allowed)
    target = rng.randint(1, max(1, min(HARD_CAP_M, max(1, N * 3))))
    target = min(target, HARD_CAP_M)

    edges = []
    if max_possible == 0:
        # N == 1 -> no DAG edge possible; emit a valid edge 0->0 (endpoints in range)
        edges.append([0, 0, rng.randint(1, MAX_W)])
        return N, edges

    # Generate edges respecting topo order to ensure DAG.
    # We allow parallel edges (multi-edges) which is fine for shortest path.
    seen_limit = target
    attempts = 0
    while len(edges) < seen_limit and attempts < seen_limit * 5 + 50:
        attempts += 1
        a = rng.randint(0, N - 1)
        b = rng.randint(0, N - 1)
        if a == b:
            continue
        # orient earlier->later in perm to keep acyclic
        if pos[a] < pos[b]:
            u, v = a, b
        else:
            u, v = b, a
        w = rng.randint(1, MAX_W)
        edges.append([u, v, w])
    if not edges:
        # fallback guarantee at least one edge
        u = perm[0]
        v = perm[1]
        edges.append([u, v, rng.randint(1, MAX_W)])
    return N, edges


def main():
    rng = random.Random(20260606)
    with tempfile.TemporaryDirectory() as tmp:
        binp = build_ref(tmp)

        cases = []
        for i in range(N_CASES):
            N, edges = gen_case(i, rng)
            cases.append((N, edges))

        # Build batch stdin for the reference
        lines = [str(len(cases))]
        for N, edges in cases:
            M = len(edges)
            lines.append(f"{N} {M}")
            for e in edges:
                lines.append(f"{e[0]} {e[1]} {e[2]}")
        stdin_data = "\n".join(lines) + "\n"

        proc = subprocess.run([binp], input=stdin_data, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError("reference failed: " + proc.stderr)
        out_lines = proc.stdout.splitlines()
        assert len(out_lines) == len(cases), f"{len(out_lines)} vs {len(cases)}"

        with open(OUT_PATH, "w") as f:
            for (N, edges), exp in zip(cases, out_lines):
                edges_str = "[" + ",".join(
                    "[" + ",".join(str(x) for x in e) + "]" for e in edges
                ) + "]"
                obj = {
                    "inputs": {"N": str(N), "M": str(len(edges)), "edges": edges_str},
                    "expected": exp.strip(),
                }
                f.write(json.dumps(obj) + "\n")

    print(f"wrote {N_CASES} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
