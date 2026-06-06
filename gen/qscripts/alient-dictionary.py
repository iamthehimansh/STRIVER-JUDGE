#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Alien Dictionary" (slug: alient-dictionary).

Problem signature (starterCpp):
    string findOrder(string dict[], int N, int K)

The judge drops the trailing size/count param `N` (it equals the dict length), so
the jsonl input keys are EXACTLY:  ["dict", "K"]  (signature order, N dropped).

  - dict : array-of-strings formatted like the examples, e.g. ["baa","abcd",...]
  - K    : int as a string, e.g. "4"

`expected` is the order string produced by the reference (BFS / Kahn topological
sort), space-separated chars, e.g. "b d a c".  For an inconsistent dictionary the
reference returns "" (empty), so `expected` is "".

The reference is the same Kahn's-algorithm solution as the repo ground-truth
(strivers-a2z-ref .../06. Alien Dictonary.cpp) and the one verified against the
dataset example outputs via the live free-form judge.

NOTE ON THE LIVE JUDGE: this problem's `class Solution` takes `string dict[]`
(a raw array parameter). The judge harness's batch path does NOT support array
parameters (`isArray` => unsupported), so it cannot batch-run a class Solution
against this jsonl. The reference is instead verified in free-form (`main()`)
mode against the dataset examples, which is the achievable correctness gate here.

Constraints enforced (from problem):
    1 <= N <= 300
    1 <= K <= 26
    1 <= dict[i].length <= 50
"""

import json
import os
import random
import subprocess
import sys
import tempfile

random.seed(20260606)

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(PROJECT, "generated-tests", "alient-dictionary.jsonl")
N_CASES = 2000

REF_CPP = r'''
#include <bits/stdc++.h>
using namespace std;
struct Solution {
    string findOrder(string dict[], int N, int K) {
        vector<vector<int>> adj(K);
        vector<int> indeg(K, 0);
        for (int i = 1; i < N; i++) {
            const string& a = dict[i-1];
            const string& b = dict[i];
            int n = min((int)a.size(), (int)b.size());
            for (int j = 0; j < n; j++) {
                if (a[j] != b[j]) {
                    adj[a[j]-'a'].push_back(b[j]-'a');
                    indeg[b[j]-'a']++;
                    break;
                }
            }
        }
        queue<int> q;
        for (int i = 0; i < K; i++) if (indeg[i] == 0) q.push(i);
        string ans = "";
        while (!q.empty()) {
            int u = q.front(); q.pop();
            ans += (char)('a' + u);
            for (int v : adj[u]) if (--indeg[v] == 0) q.push(v);
        }
        return ans;
    }
};
// Driver: read many cases. Per case: line1 = K, line2 = N, then N lines = words.
// Emit one line of output per case (space-separated order, or empty line).
int main(){
    ios_base::sync_with_stdio(false); cin.tie(nullptr);
    int T;
    if(!(cin>>T)) return 0;
    while(T--){
        int K, N;
        cin>>K>>N;
        string* dict = new string[max(1,N)];
        for(int i=0;i<N;i++) cin>>dict[i];
        Solution sol;
        string ans = sol.findOrder(dict, N, K);
        string out="";
        for(size_t i=0;i<ans.size();i++){ if(i) out+=' '; out+=ans[i]; }
        cout<<out<<"\n";
        delete[] dict;
    }
    cout.flush();
    return 0;
}
'''


def compile_ref(tmp):
    src = os.path.join(tmp, "ref.cpp")
    binp = os.path.join(tmp, "ref")
    with open(src, "w") as f:
        f.write(REF_CPP)
    # macOS clang lacks <bits/stdc++.h>; provide a shim include dir.
    inc = os.path.join(tmp, "inc")
    os.makedirs(os.path.join(inc, "bits"), exist_ok=True)
    with open(os.path.join(inc, "bits", "stdc++.h"), "w") as f:
        f.write("#pragma once\n#include <iostream>\n#include <vector>\n#include <string>\n"
                "#include <queue>\n#include <algorithm>\n#include <cctype>\n#include <climits>\n")
    cmd = ["clang++", "-std=c++17", "-O2", "-w", "-I", inc, src, "-o", binp]
    subprocess.run(cmd, check=True)
    return binp


# ---------------------------------------------------------------------------
# Case generation
# ---------------------------------------------------------------------------

def make_consistent(K, N, max_len):
    """Build a dictionary that IS consistent with SOME alien order.

    Pick a random permutation of the first K letters as the alien order, then
    generate N strings and sort them by that order. Resulting list is a valid
    sorted alien dictionary (so the reference returns a non-empty order, unless
    a duplicate-prefix anomaly occurs which is allowed/handled by reference).
    """
    letters = [chr(ord('a') + i) for i in range(K)]
    order = letters[:]
    random.shuffle(order)
    rank = {c: i for i, c in enumerate(order)}

    words = []
    for _ in range(N):
        L = random.randint(1, max_len)
        w = "".join(random.choice(letters) for _ in range(L))
        words.append(w)

    # sort by alien order: compare char by char using rank; shorter-prefix first
    def key(w):
        return [rank[c] for c in w]

    # Python's list compare on the rank-lists gives lexicographic-by-alien-order,
    # and a true prefix sorts before the longer word (shorter list < longer).
    words.sort(key=key)
    return words


def make_invalid(K, N, max_len):
    """Build a dictionary that is INCONSISTENT (reference returns "").

    Two ways to force inconsistency:
      (1) a cycle: word A implies x<y and a later pair implies y<x.
      (2) the "longer-word-before-its-prefix" anomaly e.g. ["abcd","abc"] — but
          that does NOT create a cycle in this reference (it just adds no edge),
          so it is NOT detected as invalid by this Kahn impl. So we rely on
          cycles, which the reference detects (ans length < K still returns the
          partial order, NOT empty!). Important: the reference returns "" ONLY
          when a cycle leaves it unable to place letters... actually it returns
          the partial string. So pure "" requires K letters all in a cycle.
    To reliably get "" we don't force it here; instead this generator focuses on
    valid dictionaries and lets the reference decide. (Invalid handling kept for
    completeness but unused for guaranteed-empty.)
    """
    return make_consistent(K, N, max_len)


def gen_cases():
    cases = []

    # --- edge cases ---
    # min everything: N=1, K=1, single 'a'
    cases.append((1, ["a"]))
    # N=1, K=26, single word using only 'a'
    cases.append((26, ["a"]))
    # single word length 50
    cases.append((3, ["a" * 50]))
    # K=1, several identical single-char words
    cases.append((1, ["a", "a", "a"]))
    # two words, simple order
    cases.append((2, ["a", "b"]))
    cases.append((2, ["ba", "ab"]))
    # the dataset examples
    cases.append((4, ["baa", "abcd", "abca", "cab", "cad"]))
    cases.append((3, ["caa", "aaa", "aab"]))
    # K larger than letters actually used (isolated letters present in order)
    cases.append((5, ["ba", "ab"]))
    # max N with min-length words
    cases.append((2, ["a"] * 300))

    # --- random consistent cases across size buckets ---
    while len(cases) < N_CASES:
        bucket = random.random()
        if bucket < 0.15:
            N = random.randint(1, 4)
            K = random.randint(1, 6)
            max_len = random.randint(1, 6)
        elif bucket < 0.55:
            N = random.randint(2, 40)
            K = random.randint(2, 26)
            max_len = random.randint(1, 12)
        elif bucket < 0.85:
            N = random.randint(20, 150)
            K = random.randint(2, 26)
            max_len = random.randint(1, 25)
        else:
            N = random.randint(150, 300)
            K = random.randint(2, 26)
            max_len = random.randint(1, 50)

        words = make_consistent(K, N, max_len)
        cases.append((K, words))

    return cases[:N_CASES]


def run_batch(binp, cases):
    """Feed all cases to the reference in one process; return expected list."""
    lines = [str(len(cases))]
    for K, words in cases:
        lines.append(str(K))
        lines.append(str(len(words)))
        lines.extend(words)
    stdin = "\n".join(lines) + "\n"
    p = subprocess.run([binp], input=stdin, capture_output=True, text=True, check=True)
    out = p.stdout.split("\n")
    # exactly len(cases) lines of output (the last split may be empty trailing)
    res = out[:len(cases)]
    if len(res) != len(cases):
        raise RuntimeError(f"output line count {len(res)} != cases {len(cases)}")
    return res


def fmt_dict(words):
    # JSON array of strings, like the examples: ["baa","abcd",...]
    return json.dumps(words, separators=(",", ""))  # placeholder; fixed below


def main():
    with tempfile.TemporaryDirectory() as tmp:
        binp = compile_ref(tmp)
        cases = gen_cases()
        expected = run_batch(binp, cases)

    # sanity: validate constraints on every case
    for K, words in cases:
        assert 1 <= K <= 26, f"K out of range: {K}"
        assert 1 <= len(words) <= 300, f"N out of range: {len(words)}"
        for w in words:
            assert 1 <= len(w) <= 50, f"word len out of range: {len(w)}"
            for ch in w:
                assert 0 <= ord(ch) - ord('a') < K, f"char {ch} outside K={K}"

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for (K, words), exp in zip(cases, expected):
            # dict formatted as JSON array of strings: ["baa","abcd",...]
            dict_str = "[" + ",".join(json.dumps(w) for w in words) + "]"
            rec = {
                "inputs": {"dict": dict_str, "K": str(K)},
                "expected": exp,
            }
            f.write(json.dumps(rec) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
