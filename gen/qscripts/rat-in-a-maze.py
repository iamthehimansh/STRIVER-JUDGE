#!/usr/bin/env python3
"""
Test-case generator for the Striver problem "Rat in a Maze" (slug: rat-in-a-maze).

Signature (starterCpp):
    vector<string> findPath(vector<vector<int>> &grid)

Constraints:
    2 <= n <= 5
    0 <= grid[i][j] <= 1
The rat starts at (0,0), target (n-1,n-1). Returns ALL paths (U/D/L/R) with no
cell visited twice, in SORTED (lexicographic) order. No path -> empty vector.

Output file: generated-tests/rat-in-a-maze.jsonl
  {"inputs": {"grid": "[[1,0],[1,1]]"}, "expected": "DDRDRR DRDDRR"}

The expected output is produced by the SAME reference the live judge will run
(see /tmp build below), serialized the SAME way the judge serializes a
vector<string> (values space-separated). Comparison for this slug is ORDERED,
so the reference recurses in D,L,R,U order which yields lexicographically sorted
output (matching the dataset examples).
"""

import json
import os
import random
import subprocess
import tempfile

SLUG = "rat-in-a-maze"
PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", f"{SLUG}.jsonl")
N_CASES = 2000

# ---------------------------------------------------------------------------
# Reference solution (matches the judge's expected `class Solution` exactly).
# Reads each case as a single grid string on stdin (e.g. "[[1,0],[1,1]]"),
# prints one line per case: the paths space-separated, or empty line for none.
# ---------------------------------------------------------------------------
REF_CPP = r'''
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

class Solution {
public:
    void solve(int i, int j, vector<vector<int>>& m, int n, string move,
               vector<string>& ans, vector<vector<int>>& vis) {
        if (i == n - 1 && j == n - 1) { ans.push_back(move); return; }
        int di[] = {1, 0, 0, -1};   // D, L, R, U  (lexicographic order)
        int dj[] = {0, -1, 1, 0};
        char dc[] = {'D', 'L', 'R', 'U'};
        vis[i][j] = 1;
        for (int k = 0; k < 4; k++) {
            int ni = i + di[k], nj = j + dj[k];
            if (ni >= 0 && ni < n && nj >= 0 && nj < n && !vis[ni][nj] && m[ni][nj] == 1)
                solve(ni, nj, m, n, move + dc[k], ans, vis);
        }
        vis[i][j] = 0;
    }
    vector<string> findPath(vector<vector<int>>& grid) {
        int n = grid.size();
        vector<string> ans;
        if (grid[0][0] == 0 || grid[n - 1][n - 1] == 0) return ans;
        vector<vector<int>> vis(n, vector<int>(n, 0));
        solve(0, 0, grid, n, "", ans, vis);
        return ans;
    }
};

// Parse a grid string like "[[1,0],[1,1]]" -> vector<vector<int>>.
static vector<vector<int>> parseGrid(const string& s) {
    vector<vector<int>> g;
    vector<int> row;
    int depth = 0;
    string num;
    auto flushNum = [&]() {
        if (!num.empty()) { row.push_back(stoi(num)); num.clear(); }
    };
    for (char ch : s) {
        if (ch == '[') { depth++; if (depth == 2) row.clear(); }
        else if (ch == ']') {
            if (depth == 2) { flushNum(); g.push_back(row); }
            depth--;
        }
        else if (ch == ',') { flushNum(); }
        else if (ch == '-' || (ch >= '0' && ch <= '9')) { num += ch; }
    }
    return g;
}

int main() {
    string line;
    while (getline(cin, line)) {
        // skip fully blank separator lines but still emit output per data line
        vector<vector<int>> g = parseGrid(line);
        if (g.empty()) { cout << "\n"; continue; }
        Solution sol;
        vector<string> r = sol.findPath(g);
        for (size_t i = 0; i < r.size(); i++) { if (i) cout << ' '; cout << r[i]; }
        cout << "\n";
    }
    return 0;
}
'''


def compile_ref(tmp):
    src = os.path.join(tmp, "ref.cpp")
    binp = os.path.join(tmp, "ref")
    with open(src, "w") as f:
        f.write(REF_CPP)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def grid_to_str(g):
    """Format like the dataset examples: [[1,0],[1,1]] (compact)."""
    return "[" + ",".join("[" + ",".join(str(v) for v in row) + "]" for row in g) + "]"


# The judge judges the WHOLE set in ONE batched process: it concatenates every
# case's output (one line each) into a single stdout stream that is capped at
# 256 KB (scripts/judge_exec.py: OUT_CAP). If the combined output exceeds that,
# later cases get truncated and silently fail. So we enforce BOTH:
#   * a per-case cap (skip individual pathologically dense grids), and
#   * a global byte budget across all cases (well under 256 KB for safety).
MAX_OUTPUT_CHARS = 800           # per-case expected-output cap
GLOBAL_BUDGET = 220 * 1024       # total chars (incl. per-case newline) budget


def output_len(g):
    """Length (in chars) of the serialized expected output (paths joined by
    spaces), computed with an early-exit DFS so dense grids bail fast. Returns
    a value > MAX_OUTPUT_CHARS as soon as the cap is exceeded."""
    n = len(g)
    if n == 0 or g[0][0] == 0 or g[n - 1][n - 1] == 0:
        return 0
    vis = [[0] * n for _ in range(n)]
    total = [0]  # running char count: sum(len(path)) + (#paths - 1) spaces
    count = [0]
    cap = MAX_OUTPUT_CHARS

    # D, L, R, U (lexicographic) — same order as the reference.
    moves = ((1, 0), (0, -1), (0, 1), (-1, 0))

    def dfs(i, j, plen):
        if total[0] > cap:
            return
        if i == n - 1 and j == n - 1:
            count[0] += 1
            total[0] += plen + (1 if count[0] > 1 else 0)
            return
        vis[i][j] = 1
        for di, dj in moves:
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n and not vis[ni][nj] and g[ni][nj] == 1:
                dfs(ni, nj, plen + 1)
                if total[0] > cap:
                    break
        vis[i][j] = 0

    dfs(0, 0, 0)
    return total[0]


def gen_grid(rng, n, p_one):
    """Random n x n grid of 0/1 with given probability of a 1."""
    return [[1 if rng.random() < p_one else 0 for _ in range(n)] for _ in range(n)]


def gen_grid_with_path(rng, n, p_one):
    """Random grid that is guaranteed to contain at least one (0,0)->(n-1,n-1)
    path, by first carving a monotone (right/down) path of 1s then sprinkling
    extra 1s. Keeps start/end open so 'expected' is usually non-empty."""
    g = [[1 if rng.random() < p_one else 0 for _ in range(n)] for _ in range(n)]
    i = j = 0
    g[0][0] = 1
    while i != n - 1 or j != n - 1:
        if i == n - 1:
            j += 1
        elif j == n - 1:
            i += 1
        elif rng.random() < 0.5:
            i += 1
        else:
            j += 1
        g[i][j] = 1
    return g


def make_cases():
    rng = random.Random(20240606)
    cases = []  # list of grids (list of list of int)

    budget = [0]  # running total of output chars (+1 newline per case)

    def add(g):
        """Append a grid only if (a) its own output is within the per-case cap
        and (b) adding it keeps the whole set under the global byte budget."""
        L = output_len(g)
        if L > MAX_OUTPUT_CHARS:
            return False
        if budget[0] + L + 1 > GLOBAL_BUDGET:
            return False
        budget[0] += L + 1
        cases.append([row[:] for row in g])
        return True

    # ---- explicit edge cases ----
    # dataset examples
    add([[1, 0, 0, 0], [1, 1, 0, 1], [1, 1, 0, 0], [0, 1, 1, 1]])
    add([[1, 0], [1, 0]])
    add([[1, 1, 0], [0, 1, 0], [0, 1, 1]])
    add([[1, 0, 0], [1, 1, 0], [0, 1, 1]])

    # minimal grids n=2 (all 16 combinations)
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                for d in (0, 1):
                    add([[a, b], [c, d]])

    # all-ones grids: n=2,3,4 are fine; n=5 all-ones is excluded by the cap
    for n in range(2, 6):
        add([[1] * n for _ in range(n)])

    # all-zeros (blocked start/end) for each n
    for n in range(2, 6):
        add([[0] * n for _ in range(n)])

    # start blocked / end blocked specials
    for n in range(2, 6):
        g = [[1] * n for _ in range(n)]
        g[0][0] = 0
        add(g)
        g = [[1] * n for _ in range(n)]
        g[n - 1][n - 1] = 0
        add(g)

    # ---- random cases across all n and densities ----
    # ~70% guaranteed-path grids (interesting, non-empty answers), ~30% fully
    # random grids (exercise blocked / no-path cases too). Oversized grids and
    # grids that would blow the global budget are silently skipped & re-rolled.
    # Smaller/sparser grids are favoured so the whole 2000-case set fits the
    # 256 KB combined-output cap with room to spare.
    densities = [0.3, 0.4, 0.5, 0.5, 0.6, 0.6, 0.7, 0.8]
    n_weights = [2, 2, 2, 3, 3, 3, 4, 4, 5]  # bias toward smaller n
    guard = 0
    while len(cases) < N_CASES:
        guard += 1
        if guard > N_CASES * 400:
            raise RuntimeError("could not fill case set under output budget")
        n = rng.choice(n_weights)
        p = rng.choice(densities)
        if rng.random() < 0.7:
            g = gen_grid_with_path(rng, n, p)
        else:
            g = gen_grid(rng, n, p)
        add(g)

    return cases[:N_CASES]


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        binp = compile_ref(tmp)
        cases = make_cases()

        # feed all grids to the reference at once (one per line)
        stdin = "\n".join(grid_to_str(g) for g in cases) + "\n"
        proc = subprocess.run([binp], input=stdin, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"reference failed: {proc.stderr}")
        out_lines = proc.stdout.split("\n")

        with open(OUT_PATH, "w") as f:
            for i, g in enumerate(cases):
                expected = out_lines[i].rstrip("\r") if i < len(out_lines) else ""
                rec = {
                    "inputs": {"grid": grid_to_str(g)},
                    "expected": expected,
                }
                f.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
