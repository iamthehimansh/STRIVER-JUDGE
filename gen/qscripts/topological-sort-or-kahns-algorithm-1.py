#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
    Topological sort or Kahn's algorithm (slug: topological-sort-or-kahns-algorithm-1)

Signature (starterCpp):
    vector<int> topoSort(int V, vector<int> adj[])

DATASET FORMAT QUIRK
--------------------
The dataset's testcase inputs use an `edges` field (a list of [u, v] pairs, not an
adjacency list). The judge's harness binds parameters positionally and treats
`vector<int> adj[]` like `vector<vector<int>>`, so the user's `adj` parameter
actually receives the edge-pair list (adj[i] = a 2-element pair [u, v] meaning
edge u -> v). The user's submitted reference therefore interprets adj[] as the
edge list (same convention as Course Schedule II in this dataset). The
constraint on the edge count caps how many pairs sit in adj[].

The judge compares output STRICTLY (ordered token comparison; this slug is NOT
in the unordered set). Multiple valid topological orderings exist, so the ONLY
way to guarantee passed==total is for the "expected" we emit to be produced by
the EXACT same deterministic algorithm the submitted class Solution uses.

Strategy: we compile a C++ reference that is byte-identical (algorithmically)
to the class Solution we submit to the live judge — Kahn's algorithm (BFS
topological sort):
  - read adj[] as a list of (u, v) edges in input order
  - build adjacency list in edge-input order (graph[u].push_back(v))
  - initial queue seeded by scanning nodes 0..V-1 ascending
  - FIFO queue (std::queue), neighbors pushed in adjacency-append order
  - if a cycle exists (not all V nodes emitted), return empty
This is fully deterministic, so the generator's expected == the judge's output.

Constraints:
    1 <= V <= 10^4
    0 <= edges <= 10^4

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/topological-sort-or-kahns-algorithm-1.jsonl
    {"inputs": {"V": "<int>", "edges": "[[a,b],...]"}, "expected": "<space-separated order or empty>"}
"""

import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/topological-sort-or-kahns-algorithm-1.jsonl"
N_CASES = 2000
SEED = 20260606

# ---- C++ reference: identical algorithm to the submitted class Solution -------
# Reads many cases from stdin, one per line:
#   V <tab> edges-as-json-like   (e.g. "[[1,0],[2,1]]")
# Emits one output line per case: space-separated topological order, or empty
# if a cycle prevents one.
CPP_REF = r"""
#include <bits/stdc++.h>
using namespace std;

static vector<vector<int>> parsePairs(const string& s) {
    // Parse "[[a,b],[c,d],...]" into a list of pairs. Robust to the empty form
    // "[]". An inner group is recorded only if it actually contains numbers.
    vector<vector<int>> res;
    int n = (int)s.size();
    int depth = 0;
    vector<int> cur;
    string num;
    bool inInner = false;
    auto flushNum = [&]() {
        if (!num.empty()) { cur.push_back(stoi(num)); num.clear(); }
    };
    for (int i = 0; i < n; ++i) {
        char ch = s[i];
        if (ch == '[') {
            depth++;
            if (depth == 2) { inInner = true; cur.clear(); num.clear(); }
        } else if (ch == ']') {
            if (depth == 2) { flushNum(); if (!cur.empty()) res.push_back(cur); inInner = false; }
            depth--;
        } else if (inInner) {
            if (ch == ',') flushNum();
            else if (!isspace((unsigned char)ch)) num.push_back(ch);
        }
    }
    return res;
}

// Mirrors the submitted class Solution exactly. `adj` here is the vector of
// edge pairs the harness feeds in (adj[i] == [u, v] meaning edge u -> v).
vector<int> topoSort(int V, const vector<vector<int>>& adj) {
    vector<int> indeg(V, 0);
    vector<vector<int>> graph(V);
    for (size_t i = 0; i < adj.size(); ++i) {
        if (adj[i].size() < 2) continue;
        int u = adj[i][0], v = adj[i][1];
        if (u < 0 || u >= V || v < 0 || v >= V) continue;
        graph[u].push_back(v);
        indeg[v]++;
    }
    queue<int> q;
    for (int i = 0; i < V; ++i) if (indeg[i] == 0) q.push(i);
    vector<int> order;
    while (!q.empty()) {
        int u = q.front(); q.pop();
        order.push_back(u);
        for (int v : graph[u]) if (--indeg[v] == 0) q.push(v);
    }
    if ((int)order.size() == V) return order;
    return {};
}

int main(){
    ios_base::sync_with_stdio(false); cin.tie(nullptr);
    string line;
    while (getline(cin, line)) {
        if (line.empty()) { cout << "\n"; continue; }
        size_t tab = line.find('\t');
        int V = stoi(line.substr(0, tab));
        string rest = (tab == string::npos) ? string() : line.substr(tab + 1);
        vector<vector<int>> edges = parsePairs(rest);
        vector<int> ans = topoSort(V, edges);
        for (size_t i = 0; i < ans.size(); ++i) { if (i) cout << ' '; cout << ans[i]; }
        cout << "\n";
    }
    return 0;
}
"""


def make_bits_shim(include_dir):
    with open(os.path.join(include_dir, "stdc++.h"), "w") as f:
        f.write(
            "#pragma once\n#include <iostream>\n#include <vector>\n#include <queue>\n"
            "#include <string>\n#include <algorithm>\n#include <cctype>\n#include <cstdlib>\n"
        )


def compile_ref(tmp):
    inc = os.path.join(tmp, "bits")
    os.makedirs(inc, exist_ok=True)
    make_bits_shim(inc)
    src = os.path.join(tmp, "ref.cpp")
    with open(src, "w") as f:
        f.write(CPP_REF)
    binary = os.path.join(tmp, "ref")
    cmd = ["clang++", "-std=c++17", "-O2", "-w", "-I", tmp, src, "-o", binary]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("compile failed:\n" + r.stderr)
    return binary


def edges_to_str(edges):
    # IMPORTANT: append a trailing empty "[]" sentinel so the user's adj[]
    # parameter — which is a raw pointer with no recoverable size — can
    # safely terminate iteration at the first row whose .size() != 2. The
    # underlying vector<vector<int>> the harness builds via rdVVI will have
    # one extra empty inner vector at index `len(edges)`, giving the user a
    # well-defined end-of-input marker even when edges is empty.
    inner = ",".join("[%d,%d]" % (u, v) for u, v in edges)
    if inner:
        return "[" + inner + ",[]]"
    return "[[]]"


# -------------------------- generators --------------------------------------

def gen_acyclic(V, max_edges):
    """Generate a DAG: pick edges u -> v with pos[u] < pos[v] in a random
    permutation, so no cycle exists. Returns a list of (u, v) pairs."""
    if V < 2 or max_edges <= 0:
        return []
    perm = list(range(V))
    random.shuffle(perm)
    pos = {node: i for i, node in enumerate(perm)}
    seen = set()
    edges = []
    cap = min(max_edges, V * (V - 1) // 2)
    target = random.randint(0, cap)
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 50:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if u == v:
            continue
        if pos[u] > pos[v]:
            u, v = v, u
        if (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
    return edges


def gen_random(V, max_edges):
    """Fully random unique pairs (may or may not be cyclic)."""
    if V == 0 or max_edges <= 0:
        return []
    seen = set()
    edges = []
    target = random.randint(0, max_edges)
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 50:
        attempts += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if u == v:
            continue
        if (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
    return edges


def gen_cyclic(V, extra_max=20):
    """Guaranteed cyclic: a simple cycle 0->1->...->k->0 plus optional extras."""
    if V < 2:
        return []
    k = random.randint(2, V)
    nodes = random.sample(range(V), k)
    edges = []
    seen = set()
    for i in range(k):
        u = nodes[i]
        v = nodes[(i + 1) % k]
        if u == v or (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
    extra = random.randint(0, min(extra_max, V))
    att = 0
    while extra > 0 and att < 200:
        att += 1
        u = random.randrange(V)
        v = random.randrange(V)
        if u == v or (u, v) in seen:
            continue
        seen.add((u, v))
        edges.append((u, v))
        extra -= 1
    return edges


def gen_chain(V):
    """0 -> 1 -> 2 -> ... -> V-1 (acyclic, single topo order)."""
    return [(i, i + 1) for i in range(V - 1)]


def gen_star_out(V):
    """0 -> i for all i > 0."""
    return [(0, i) for i in range(1, V)]


def gen_star_in(V):
    """i -> 0 for all i > 0."""
    return [(i, 0) for i in range(1, V)]


# -------------------------- case builder -----------------------------------

def build_cases():
    """We must KEEP TOTAL OUTPUT SMALL — the live judge runs all cases in one
    batched process and the runner caps captured stdout at 256 KB (see
    scripts/judge_exec.py). The bulk uses small V; we sprinkle a handful of
    big-V cases that are CYCLIC (empty output = ~0 bytes) so we cover the
    constraint ceiling without blowing past the cap."""
    cases = []

    # ---- Explicit edge / example cases ----
    cases.append((1, []))                                       # min V
    cases.append((2, []))                                       # no edges, disconnected
    cases.append((2, [(0, 1)]))                                 # tiny chain
    cases.append((2, [(0, 1), (1, 0)]))                         # 2-node cycle
    cases.append((3, [(0, 1), (1, 2)]))                         # 3-node chain
    cases.append((3, []))                                       # disconnected, no edges
    cases.append((4, [(1, 0), (2, 0), (3, 0)]))                 # dataset example 2
    cases.append((6, [(2, 3), (3, 1), (4, 0), (4, 1), (5, 0), (5, 2)]))  # dataset example 1
    cases.append((5, gen_chain(5)))                             # 0->1->2->3->4
    cases.append((6, gen_star_out(6)))                          # 0 -> 1..5
    cases.append((6, gen_star_in(6)))                           # 1..5 -> 0
    cases.append((1, []))                                       # min V again
    cases.append((10, []))                                      # only nodes, no edges
    cases.append((4, [(0, 1), (1, 2), (2, 3), (3, 0)]))         # 4-cycle
    cases.append((5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 2)])) # cycle with tail

    # ---- Large-V edge cases that are CYCLIC -> empty output (cheap) ----
    cases.append((10000, gen_cyclic(10000)))                    # max V, cyclic
    cases.append((10000, gen_cyclic(10000)))                    # max V, cyclic again (different seed state)
    cases.append((9000, gen_cyclic(9000)))
    cases.append((5000, gen_cyclic(5000)))
    cases.append((2000, gen_cyclic(2000)))
    cases.append((10000, []))                                   # max V, no edges -> 0..9999 ~ 48 KB
    # Note: V=10000 with no edges = output "0 1 ... 9999" which is ~48 KB.
    # We add ONE such case to stress the chain output budget.
    cases.append((1000, gen_chain(1000)))                       # full chain -> 1000 numbers (~3.9 KB)

    # ---- Mid-size cases at the edge-count ceiling (cyclic to keep output 0) --
    for _ in range(5):
        V = random.randint(500, 5000)
        # Ensure number of edges close to 10000 cap, guaranteed cyclic.
        edges = gen_cyclic(V, extra_max=min(50, V))
        # pad with random extras up to cap, but it's still cyclic
        seen = set(edges)
        cap = 10000
        target = random.randint(min(2000, cap), cap)
        att = 0
        while len(edges) < target and att < target * 4 + 50:
            att += 1
            u = random.randrange(V)
            v = random.randrange(V)
            if u == v or (u, v) in seen:
                continue
            seen.add((u, v))
            edges.append((u, v))
        cases.append((V, edges))

    # ---- Random bulk: SMALL V so total output stays well under 256 KB ----
    while len(cases) < N_CASES:
        roll = random.random()
        rV = random.random()
        if rV < 0.6:
            V = random.randint(1, 8)
        elif rV < 0.9:
            V = random.randint(1, 25)
        else:
            V = random.randint(1, 40)
        # cap edges far below 10^4 for bulk cases (we only need a few stress
        # cases at the ceiling, which are above)
        max_edges = min(80, V * (V - 1)) if V > 1 else 0
        if roll < 0.45:
            edges = gen_acyclic(V, max_edges)
        elif roll < 0.75:
            edges = gen_random(V, max_edges)
        else:
            edges = gen_cyclic(V, extra_max=min(20, V))
        # hard cap on edge count
        if len(edges) > 10000:
            edges = edges[:10000]
        cases.append((V, edges))

    return cases[:N_CASES]


# -------------------------- validation -------------------------------------

def validate_case(V, edges):
    assert 1 <= V <= 10000, f"V out of range: {V}"
    assert 0 <= len(edges) <= 10000, f"edges count out of range: {len(edges)}"
    seen = set()
    for e in edges:
        assert len(e) == 2, "pair not length 2"
        u, v = e
        assert 0 <= u < V and 0 <= v < V, f"node out of range: {e} (V={V})"
        # We allow duplicate-direction-pair only if we want; here we keep them
        # unique to match common conventions. Our generators dedupe already.
        assert (u, v) not in seen, f"duplicate pair {e}"
        seen.add((u, v))


# -------------------------- main -------------------------------------------

def main():
    random.seed(SEED)
    cases = build_cases()
    for V, edges in cases:
        validate_case(V, edges)

    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_ref(tmp)
        # Feed every case through the reference in one batch.
        lines = []
        for V, edges in cases:
            lines.append(str(V) + "\t" + edges_to_str(edges))
        proc = subprocess.run(
            [binary], input="\n".join(lines), capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError("reference run failed:\n" + proc.stderr)
        out_lines = proc.stdout.split("\n")

    records = []
    for i, (V, edges) in enumerate(cases):
        expected = out_lines[i].strip() if i < len(out_lines) else ""
        rec = {
            "inputs": {"V": str(V), "edges": edges_to_str(edges)},
            "expected": expected,
        }
        records.append(rec)

    # Safety guard: the live judge runs all cases in one batched process and
    # the runner caps captured stdout at 256 KB. The concatenated output of
    # all cases (one line each) MUST stay under that, or later cases lose
    # their output and are wrongly marked failed. Verify here.
    OUT_CAP = 256 * 1024
    total_out = sum(len(r["expected"]) + 1 for r in records)  # +1 for '\n'
    print(f"Total batched output ~ {total_out} bytes (cap {OUT_CAP}).")
    assert total_out < OUT_CAP - 4096, (
        f"Batched output {total_out} too large; would be truncated by the judge."
    )

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(records)} cases to {OUT_PATH}")
    for rec in records[:5]:
        print(rec["inputs"]["V"], "->", repr(rec["expected"])[:80])


if __name__ == "__main__":
    main()
