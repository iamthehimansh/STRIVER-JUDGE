#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Course Schedule II (slug: course-schedule-ii)

Signature (starterCpp):
    vector<int> findOrder(int N, vector<vector<int>> arr)

The judge compares output STRICTLY (ordered token comparison; this slug is NOT in
the unordered set). Multiple valid topological orderings exist, so the ONLY way to
guarantee passed==total is for the "expected" we emit to be produced by the EXACT
same deterministic algorithm the submitted class Solution uses.

Strategy: we compile a C++ reference that is byte-identical (algorithmically) to the
class Solution we submit to the live judge — Kahn's algorithm (BFS topological sort):
  - adjacency list built in edge-input order
  - initial queue seeded by scanning nodes 0..N-1 ascending
  - FIFO queue (std::queue), neighbors pushed in adjacency-append order
This is fully deterministic, so the generator's expected == the judge's output.

Constraints:
    1 <= N <= 2000
    0 <= arr.length <= 5000
    arr[i].length == 2
    0 <= arr[i][0], arr[i][1] < N
    All the pairs arr[i] are unique.

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/course-schedule-ii.jsonl
    {"inputs": {"N": "<int>", "arr": "[[a,b],...]"}, "expected": "<space-separated order or empty>"}
"""

import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/course-schedule-ii.jsonl"
N_CASES = 2000
SEED = 20260606

# ---- C++ reference: identical algorithm to the submitted class Solution -------
CPP_REF = r"""
#include <bits/stdc++.h>
using namespace std;
// Kahn's algorithm (deterministic). Reads many cases from stdin, one per line:
//   N <tab> arr-as-json-like  (e.g. "[[1,0],[2,1]]")
// Emits one output line per case: space-separated order, or empty if a cycle.
static vector<vector<int>> parsePairs(const string& s) {
    // Parse "[[a,b],[c,d],...]" into a list of pairs. Robust to the empty form
    // "[]". An inner group is recorded only if it actually contains numbers.
    vector<vector<int>> res;
    int i = 0, n = (int)s.size();
    int depth = 0;
    vector<int> cur;       // numbers collected in the current inner group
    string num;
    bool inInner = false;
    auto flushNum = [&]() {
        if (!num.empty()) { cur.push_back(stoi(num)); num.clear(); }
    };
    for (i = 0; i < n; ++i) {
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
vector<int> findOrder(int N, vector<vector<int>> arr) {
    vector<int> indeg(N, 0);
    vector<vector<int>> adj(N);
    for (auto &it : arr) { indeg[it[0]]++; adj[it[1]].push_back(it[0]); }
    queue<int> q;
    for (int i = 0; i < N; i++) if (indeg[i] == 0) q.push(i);
    vector<int> order;
    while (!q.empty()) {
        int node = q.front(); q.pop();
        order.push_back(node);
        for (int v : adj[node]) { if (--indeg[v] == 0) q.push(v); }
    }
    if ((int)order.size() == N) return order;
    return {};
}
int main(){
    ios_base::sync_with_stdio(false); cin.tie(nullptr);
    string line;
    while (getline(cin, line)) {
        if (line.empty()) { cout << "\n"; continue; }
        size_t tab = line.find('\t');
        int N = stoi(line.substr(0, tab));
        string rest = line.substr(tab + 1);
        vector<vector<int>> arr = parsePairs(rest);
        vector<int> ans = findOrder(N, arr);
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


def arr_to_str(arr):
    return "[" + ",".join("[%d,%d]" % (a, b) for a, b in arr) + "]"


def gen_acyclic(N, max_edges):
    """Generate a DAG (guaranteed solvable): edges only from a later-in-perm node
    to an earlier one in a random topological permutation, so no cycle exists."""
    perm = list(range(N))
    random.shuffle(perm)
    pos = {node: i for i, node in enumerate(perm)}
    # arr[i] = [a, b] means b must come before a -> edge b->a, b earlier than a.
    # We pick pairs (a, b) with pos[b] < pos[a] to keep it acyclic.
    seen = set()
    edges = []
    target = random.randint(0, min(max_edges, N * (N - 1) // 2 if N > 1 else 0))
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 50:
        attempts += 1
        a = random.randrange(N)
        b = random.randrange(N)
        if a == b:
            continue
        if pos[b] >= pos[a]:
            a, b = b, a  # ensure b earlier than a
        if pos[b] >= pos[a]:
            continue
        if (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append((a, b))
    return edges


def gen_random(N, max_edges):
    """Fully random unique pairs (may or may not be cyclic)."""
    seen = set()
    edges = []
    target = random.randint(0, max_edges)
    attempts = 0
    while len(edges) < target and attempts < target * 8 + 50:
        attempts += 1
        a = random.randrange(N)
        b = random.randrange(N)
        if a == b:
            continue
        if (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append((a, b))
    return edges


def gen_cyclic(N):
    """Guaranteed cyclic: a simple cycle 0->1->...->k->0 (as prerequisite pairs)."""
    if N < 2:
        return []
    k = random.randint(2, N)
    nodes = random.sample(range(N), k)
    edges = []
    seen = set()
    for i in range(k):
        a = nodes[i]
        b = nodes[(i + 1) % k]
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append((a, b))
    # add a few extra random unique edges
    extra = random.randint(0, min(20, N))
    att = 0
    while extra > 0 and att < 100:
        att += 1
        a = random.randrange(N)
        b = random.randrange(N)
        if a == b or (a, b) in seen:
            continue
        seen.add((a, b))
        edges.append((a, b))
        extra -= 1
    return edges


def build_cases():
    # IMPORTANT: the live judge runs all cases in ONE batched process and the
    # local runner caps captured stdout at 256 KB (scripts/judge_exec.py
    # OUT_CAP). If the concatenated output of all cases exceeds that, later
    # cases lose their output line and are scored as failures even though they
    # are correct. So we KEEP TOTAL OUTPUT SMALL: the bulk uses small N (whose
    # acyclic output is short), plus a few important large-N edge cases that we
    # deliberately make CYCLIC (empty output) so they cost ~0 output bytes.
    cases = []  # list of (N, edges)

    # ---- Edge cases (small output) ----
    cases.append((1, []))                       # min N, no edges
    cases.append((2, [(1, 0)]))                 # the "now your turn" example
    cases.append((2, [(0, 1), (1, 0)]))         # 2-node cycle -> empty
    cases.append((4, [(1, 0), (2, 1), (3, 2)])) # example 1
    cases.append((4, [(0, 1), (3, 2), (1, 3), (3, 0)]))  # example 2 -> empty
    cases.append((3, []))                       # disconnected, no edges
    cases.append((1, []))                       # again min

    # ---- Large-N edge cases that are CYCLIC -> empty output (cheap) ----
    cases.append((2000, gen_cyclic(2000)))      # max N, guaranteed cycle -> ""
    cases.append((1500, gen_cyclic(1500)))      # large cyclic -> ""
    # large acyclic with MANY edges but still empty?  no — acyclic prints N
    # numbers. We include ONE big acyclic chain to exercise a full ordering;
    # 2000 numbers ~ 8.8 KB, affordable as a single case.
    chain = [(i, i - 1) for i in range(1, 2000)]
    cases.append((2000, chain[:1999]))          # full chain -> 2000 numbers
    # max edges near 5000 on a moderate N (acyclic): output is N numbers.
    cases.append((400, gen_acyclic(400, 5000))) # ~400 numbers, lots of edges

    # ---- Random bulk: SMALL N so total output stays well under 256 KB ----
    # avg acyclic output for N<=12 is < ~40 bytes; ~2000 cases -> well within
    # budget. We still mix in cyclic (empty) and medium-N (<=40) cases.
    while len(cases) < N_CASES:
        roll = random.random()
        rN = random.random()
        if rN < 0.6:
            N = random.randint(1, 8)
        elif rN < 0.9:
            N = random.randint(1, 25)
        else:
            N = random.randint(1, 40)
        max_edges = min(60, N * (N - 1)) if N > 1 else 0
        if roll < 0.4:
            edges = gen_acyclic(N, max_edges)
        elif roll < 0.7:
            edges = gen_random(N, max_edges)
        else:
            edges = gen_cyclic(N)
        if len(edges) > 5000:
            edges = edges[:5000]
        cases.append((N, edges))

    return cases[:N_CASES]


def validate_case(N, edges):
    assert 1 <= N <= 2000, f"N out of range: {N}"
    assert 0 <= len(edges) <= 5000, f"arr.length out of range: {len(edges)}"
    seen = set()
    for e in edges:
        assert len(e) == 2, "pair not length 2"
        a, b = e
        assert 0 <= a < N and 0 <= b < N, f"node out of range: {e} (N={N})"
        assert (a, b) not in seen, f"duplicate pair {e}"
        seen.add((a, b))


def main():
    random.seed(SEED)
    cases = build_cases()
    for N, edges in cases:
        validate_case(N, edges)

    with tempfile.TemporaryDirectory() as tmp:
        binary = compile_ref(tmp)
        # feed all cases through the reference in one batch
        lines = []
        for N, edges in cases:
            lines.append(str(N) + "\t" + arr_to_str(edges))
        proc = subprocess.run(
            [binary], input="\n".join(lines), capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise RuntimeError("reference run failed:\n" + proc.stderr)
        out_lines = proc.stdout.split("\n")

    records = []
    for i, (N, edges) in enumerate(cases):
        expected = out_lines[i].strip() if i < len(out_lines) else ""
        rec = {
            "inputs": {"N": str(N), "arr": arr_to_str(edges)},
            "expected": expected,
        }
        records.append(rec)

    # Safety guard: the live judge runs all cases in one batched process and
    # the runner caps captured stdout at 256 KB. The concatenated output of all
    # cases (one line each) MUST stay under that, or later cases lose their
    # output and are wrongly marked failed. Verify here.
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
    # quick self-check on example outputs
    for rec in records[:5]:
        print(rec["inputs"]["N"], "->", repr(rec["expected"])[:60])


if __name__ == "__main__":
    main()
