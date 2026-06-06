#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
    detect-a-cycle-in-an-undirected-graph
    bool isCycle(int V, vector<int> adj[])

Generates valid UNDIRECTED graphs (no self-loops, no multi-edges, symmetric
adjacency list) within constraints (1 <= V, E <= 1e4) and computes the expected
answer ("True"/"False") with a compiled C++ BFS reference.

Output line format (judge-consumed):
  {"inputs": {"V": "<int>", "adj": "[[...],[...]]"}, "expected": "True"|"False"}

The adjacency list `adj` has exactly V rows; row i lists neighbours of vertex i.
Edges are stored symmetrically (j in adj[i] iff i in adj[j]).
"""
import json
import os
import random
import subprocess
import tempfile

SLUG = "detect-a-cycle-in-an-undirected-graph"
OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/%s.jsonl" % SLUG
N_CASES = 2000
MAX_V = 10000
MAX_E = 10000

REF_SRC = r'''
#include <iostream>
#include <vector>
#include <queue>
using namespace std;
bool isCycle(int V, const vector<vector<int>>& adj) {
    vector<char> vis(V, 0);
    for (int s = 0; s < V; s++) {
        if (vis[s]) continue;
        queue<pair<int,int>> q; q.push({s, -1}); vis[s] = 1;
        while (!q.empty()) {
            int node = q.front().first, parent = q.front().second; q.pop();
            for (int nb : adj[node]) {
                if (!vis[nb]) { vis[nb] = 1; q.push({nb, node}); }
                else if (nb != parent) return true;
            }
        }
    }
    return false;
}
int main(){
    ios_base::sync_with_stdio(false); cin.tie(nullptr);
    int T; if(!(cin>>T)) return 0;
    while(T--){
        int V; cin>>V; vector<vector<int>> adj(V);
        for(int i=0;i<V;i++){ int d; cin>>d; adj[i].resize(d); for(int j=0;j<d;j++) cin>>adj[i][j]; }
        cout << (isCycle(V,adj)?"True":"False") << "\n";
    }
    return 0;
}
'''


def compile_ref(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp], check=True)
    return binp


def adj_to_str(adj):
    """Format adjacency list like the dataset examples: [[1, 3], [0, 2, 4], ...]."""
    return "[" + ", ".join("[" + ", ".join(str(x) for x in row) + "]" for row in adj) + "]"


def build_adj_from_edges(V, edges):
    """edges: set of frozenset({u,v}); return adjacency list (each row sorted)."""
    adj = [[] for _ in range(V)]
    for e in edges:
        a, b = tuple(e)
        adj[a].append(b)
        adj[b].append(a)
    for row in adj:
        row.sort()
    return adj


def gen_random_edges(V, target_E, force_acyclic):
    """Generate up to target_E distinct undirected edges (no self-loop, no multi).
    If force_acyclic, only add edges that don't create a cycle (union-find)."""
    edges = set()
    if force_acyclic:
        parent = list(range(V))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        attempts = 0
        max_attempts = target_E * 30 + 200
        while len(edges) < target_E and attempts < max_attempts:
            attempts += 1
            u = random.randrange(V)
            w = random.randrange(V)
            if u == w:
                continue
            ru, rw = find(u), find(w)
            if ru == rw:
                continue  # would form cycle
            parent[ru] = rw
            edges.add(frozenset((u, w)))
        return edges
    else:
        attempts = 0
        max_attempts = target_E * 30 + 200
        while len(edges) < target_E and attempts < max_attempts:
            attempts += 1
            u = random.randrange(V)
            w = random.randrange(V)
            if u == w:
                continue
            edges.add(frozenset((u, w)))
        return edges


def max_simple_edges(V):
    # complete simple graph edge count, capped at MAX_E
    full = V * (V - 1) // 2
    return min(full, MAX_E)


def make_case(idx):
    """Return adjacency list (list of lists) for one valid graph."""
    r = random.random()

    # Edge cases sprinkled deterministically among first cases.
    if idx == 0:
        # smallest: single vertex, no edges -> acyclic
        return [[]]
    if idx == 1:
        # two vertices, single edge -> acyclic (tree)
        return [[1], [0]]
    if idx == 2:
        # triangle -> cycle
        return [[1, 2], [0, 2], [0, 1]]
    if idx == 3:
        # two isolated vertices, no edges -> acyclic
        return [[], []]
    if idx == 4:
        # self-loops are forbidden; a simple path of 3 -> acyclic
        return [[1], [0, 2], [1]]

    # Choose V
    pick = random.random()
    if pick < 0.10:
        V = random.randint(1, 5)            # tiny
    elif pick < 0.30:
        V = random.randint(2, 50)           # small
    elif pick < 0.55:
        V = random.randint(2, 500)          # medium
    elif pick < 0.80:
        V = random.randint(2, 3000)         # large
    else:
        V = random.randint(2, MAX_V)        # up to max

    cap = max_simple_edges(V)

    if r < 0.42:
        # Acyclic forest/tree: edges < V, guaranteed no cycle.
        # number of tree edges at most V-1 and at most MAX_E.
        max_tree = min(V - 1, MAX_E)
        if max_tree <= 0:
            return [[] for _ in range(V)]   # single vertex
        target_E = random.randint(0, max_tree)
        edges = gen_random_edges(V, target_E, force_acyclic=True)
        return build_adj_from_edges(V, edges)
    else:
        # Possibly-cyclic random graph. Pick E up to cap (and MAX_E).
        if cap <= 0:
            return [[] for _ in range(V)]
        # bias toward having enough edges to likely create a cycle, but keep within cap
        hi = cap
        target_E = random.randint(0, hi)
        edges = gen_random_edges(V, target_E, force_acyclic=False)
        return build_adj_from_edges(V, edges)


def validate(V, adj):
    assert len(adj) == V, "adj rows != V"
    assert 1 <= V <= MAX_V, "V out of range"
    edgeset = set()
    for i, row in enumerate(adj):
        seen = set()
        for nb in row:
            assert 0 <= nb < V, "neighbour out of range"
            assert nb != i, "self-loop present"
            assert nb not in seen, "multi-edge in a row"
            seen.add(nb)
            edgeset.add(frozenset((i, nb)))
    # symmetry: i in adj[j] iff j in adj[i]
    for i, row in enumerate(adj):
        for nb in row:
            assert i in adj[nb], "asymmetric edge"
    E = len(edgeset)
    assert E <= MAX_E, "E out of range (%d)" % E
    return E


def main():
    random.seed(20260606)
    with tempfile.TemporaryDirectory() as tmp:
        ref = compile_ref(tmp)

        cases = []          # adjacency lists
        for idx in range(N_CASES):
            adj = make_case(idx)
            V = len(adj)
            validate(V, adj)
            cases.append(adj)

        # Build one big stdin for the reference: T then each case.
        lines = [str(len(cases))]
        for adj in cases:
            V = len(adj)
            lines.append(str(V))
            for row in adj:
                lines.append(str(len(row)) + ("" if not row else " " + " ".join(map(str, row))))
        stdin = "\n".join(lines) + "\n"

        proc = subprocess.run([ref], input=stdin, capture_output=True, text=True)
        outs = proc.stdout.strip().split("\n")
        assert len(outs) == len(cases), "ref output count %d != %d" % (len(outs), len(cases))

        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w") as f:
            for adj, exp in zip(cases, outs):
                exp = exp.strip()
                assert exp in ("True", "False"), "bad expected %r" % exp
                V = len(adj)
                rec = {
                    "inputs": {"V": str(V), "adj": adj_to_str(adj)},
                    "expected": exp,
                }
                f.write(json.dumps(rec) + "\n")

        n_true = sum(1 for o in outs if o.strip() == "True")
        print("wrote %d cases -> %s" % (len(cases), OUT))
        print("True: %d  False: %d" % (n_true, len(outs) - n_true))


if __name__ == "__main__":
    main()
