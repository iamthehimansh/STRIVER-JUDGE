#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Combination Sum" (slug: combination-sum).

Signature: vector<vector<int>> combinationSum(vector<int>& candidates, int target)

Constraints (from problem JSON):
  1 <= candidates.length <= 30
  2 <= candidates[i] <= 40
  All elements of candidates are distinct.
  1 <= target <= 40
  (Test cases guarantee fewer than 150 valid combinations.)

Strategy:
  - Compile a C++ reference oracle once into a temp dir. The oracle sorts the
    candidates and uses the canonical "pick / not-pick" recursion (numbers may be
    reused), which yields combinations in a deterministic, fully ascending and
    lexicographically ordered form. This matches the dataset's authoritative
    `nowYourTurn` answer for candidates=[3,4,5,6], target=10 -> [[3,3,4],[4,6],[5,5]]
    and matches the SET of the example outputs. The judge compares the flattened
    token sequence leniently (ignoring brackets/commas/whitespace).
  - Generate random inputs strictly inside the constraints, with distinct
    candidate values drawn from [2, 40] and target in [1, 40]. Heavily seed
    edge cases (min sizes, extremes, no-solution inputs, single elements).
  - To respect the "< 150 combinations" guarantee, every generated case is run
    through the oracle and rejected if it produces >= 150 combinations.
  - Run the oracle on each input to compute expected output.
  - Write generated-tests/combination-sum.jsonl, one JSON object per line:
        {"inputs": {"candidates": "[...]", "target": "7"}, "expected": "[[...], ...]"}

Output formatting mirrors the dataset examples: int arrays as "[a, b, c]" and the
2D expected as "[[a, b], [c]]".
"""
import json
import os
import random
import subprocess
import tempfile

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", "combination-sum.jsonl")
N_CASES = 2000
SEED = 20260606

# constraint bounds
LEN_MIN, LEN_MAX = 1, 30
VAL_MIN, VAL_MAX = 2, 40
TGT_MIN, TGT_MAX = 1, 40
MAX_COMBOS = 150  # problem guarantees strictly fewer than 150

CPP_REF = r'''
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include <sstream>
using namespace std;

class Solution {
public:
    void solve(int idx, vector<int>& cand, int target,
               vector<int>& cur, vector<vector<int>>& ans) {
        if (target == 0) { ans.push_back(cur); return; }
        if (idx == (int)cand.size() || target < 0) return;
        if (cand[idx] <= target) {
            cur.push_back(cand[idx]);
            solve(idx, cand, target - cand[idx], cur, ans);
            cur.pop_back();
        }
        solve(idx + 1, cand, target, cur, ans);
    }
    vector<vector<int>> combinationSum(vector<int>& candidates, int target) {
        vector<vector<int>> ans;
        vector<int> cand = candidates;
        sort(cand.begin(), cand.end());
        vector<int> cur;
        solve(0, cand, target, cur, ans);
        return ans;
    }
};

// read one input line: "v1 v2 ... vn | target"  (candidates left of '|')
int main() {
    string line;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        // split on '|'
        size_t bar = line.find('|');
        string left = line.substr(0, bar);
        string right = (bar == string::npos) ? "" : line.substr(bar + 1);
        vector<int> cand;
        { istringstream ss(left); int x; while (ss >> x) cand.push_back(x); }
        int target = 0;
        { istringstream ss(right); ss >> target; }

        Solution sol;
        vector<vector<int>> res = sol.combinationSum(cand, target);

        // emit canonical bracketed form: [[a, b], [c]]  (empty -> [])
        ostringstream out;
        out << "[";
        for (size_t i = 0; i < res.size(); ++i) {
            if (i) out << ", ";
            out << "[";
            for (size_t j = 0; j < res[i].size(); ++j) {
                if (j) out << ", ";
                out << res[i][j];
            }
            out << "]";
        }
        out << "]";
        cout << out.str() << "\n";
    }
    return 0;
}
'''


def build_ref(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_REF)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def run_ref(binp, candidates, target):
    payload = " ".join(str(x) for x in candidates) + " | " + str(target) + "\n"
    r = subprocess.run([binp], input=payload, capture_output=True, text=True, check=True)
    return r.stdout.strip()


def count_combos(expected):
    """Number of top-level combinations in the bracketed expected string."""
    if expected == "[]":
        return 0
    # count '[' that open an inner list (depth-1 opens)
    depth = 0
    n = 0
    for ch in expected:
        if ch == "[":
            depth += 1
            if depth == 2:
                n += 1
        elif ch == "]":
            depth -= 1
    return n


def fmt_arr(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def gen_candidates(rng):
    """Distinct values in [2,40], length in [1,30]."""
    n = rng.randint(LEN_MIN, LEN_MAX)
    pool = list(range(VAL_MIN, VAL_MAX + 1))  # 39 distinct values available
    n = min(n, len(pool))
    return rng.sample(pool, n)


def main():
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as workdir:
        binp = build_ref(workdir)

        # sanity: reproduce dataset example SETS / nowYourTurn answer
        ex1 = run_ref(binp, [2, 3, 5, 4], 7)
        assert ex1 == "[[2, 2, 3], [2, 5], [3, 4]]", "example1 set mismatch: " + ex1
        ex2 = run_ref(binp, [2], 1)
        assert ex2 == "[]", "example2 mismatch: " + ex2
        nyt = run_ref(binp, [3, 4, 5, 6], 10)
        assert nyt == "[[3, 3, 4], [4, 6], [5, 5]]", "nowYourTurn mismatch: " + nyt

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

        # explicit edge cases (candidates, target)
        edges = [
            ([2], 1),                 # no solution (val > target impossible since val>=2,tgt=1)
            ([2], 2),                 # single, exact
            ([2], 40),                # single, many repeats -> [2]*20
            ([40], 40),               # single max value, exact
            ([40], 1),                # impossible
            ([2, 3, 5, 4], 7),        # example 1
            ([3, 4, 5, 6], 10),       # nowYourTurn
            ([2, 3], 6),
            ([3, 5, 8], 11),
            ([2, 40], 40),
            ([40, 39, 38], 40),       # only one fits
            ([7, 3, 2], 18),
            (list(range(2, 32)), 1),  # 30 candidates, target=1 -> impossible
            (list(range(2, 32)), 4),  # 30 candidates, small target
            ([2, 3, 4, 5, 6, 7], 8),
        ]

        seen = set()
        cases = []

        def add(cand, target):
            key = (tuple(sorted(cand)), target)
            if key in seen:
                return False
            # validate constraints
            if not (LEN_MIN <= len(cand) <= LEN_MAX):
                return False
            if len(set(cand)) != len(cand):
                return False
            if not all(VAL_MIN <= v <= VAL_MAX for v in cand):
                return False
            if not (TGT_MIN <= target <= TGT_MAX):
                return False
            expected = run_ref(binp, cand, target)
            if count_combos(expected) >= MAX_COMBOS:
                return False  # honor "< 150 combinations" guarantee
            seen.add(key)
            cases.append((cand, target, expected))
            return True

        for cand, target in edges:
            add(cand, target)

        attempts = 0
        while len(cases) < N_CASES and attempts < N_CASES * 50:
            attempts += 1
            cand = gen_candidates(rng)
            target = rng.randint(TGT_MIN, TGT_MAX)
            add(cand, target)

        cases = cases[:N_CASES]

        with open(OUT_PATH, "w") as f:
            for cand, target, expected in cases:
                obj = {
                    "inputs": {
                        "candidates": fmt_arr(cand),
                        "target": str(target),
                    },
                    "expected": expected,
                }
                f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
