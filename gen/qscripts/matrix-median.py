#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Matrix Median" (slug: matrix-median).

Signature (starterCpp):
    int findMedian(vector<vector<int>>& matrix);

Constraints:
    N == matrix.size, M == matrix[0].size
    1 <= N, M <= 1e5
    1 <= N*M <= 1e6
    1 <= matrix[i] <= 1e9
    N*M is odd  ->  both N and M must be odd

Each row is row-wise sorted (non-decreasing). Output: the median (the
((N*M+1)/2)-th smallest element of the flattened sorted multiset).

Reference oracle: a C++ findMedian implementation (binary search on value
space, counting elements <= mid per row via upper_bound). It is compiled
once and fed every generated matrix; expected output is taken from it.

Writes:
    /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/matrix-median.jsonl
"""

import json
import os
import random
import subprocess
import sys
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/matrix-median.jsonl"
N_CASES = 2000
VAL_MAX = 10**9

CPP_REF = r"""
#include <bits/stdc++.h>
using namespace std;

class Solution {
public:
    int findMedian(vector<vector<int>>& matrix) {
        int R = matrix.size();
        int C = matrix[0].size();
        int low = INT_MAX, high = INT_MIN;
        long long opt_cnt = ((long long)R * C + 1) / 2;
        int ans = -1;
        for (int i = 0; i < R; i++) {
            low = min(low, matrix[i][0]);
            high = max(high, matrix[i][C - 1]);
        }
        while (low <= high) {
            int mid = low + (high - low) / 2;
            long long cnt = 0;
            for (int i = 0; i < R; i++) {
                cnt += upper_bound(matrix[i].begin(), matrix[i].end(), mid) - matrix[i].begin();
            }
            if (cnt < opt_cnt) low = mid + 1;
            else { ans = mid; high = mid - 1; }
        }
        return ans;
    }
};

int main() {
    // Input protocol (stdin):
    //   T
    //   for each test: R C, then R lines of C integers (each row sorted)
    int T;
    if (!(cin >> T)) return 0;
    Solution sol;
    while (T--) {
        int R, C;
        cin >> R >> C;
        vector<vector<int>> mat(R, vector<int>(C));
        for (int i = 0; i < R; i++)
            for (int j = 0; j < C; j++)
                cin >> mat[i][j];
        cout << sol.findMedian(mat) << "\n";
    }
    return 0;
}
"""

# A pure-python oracle used to cross-check the C++ reference (and as a fallback
# sanity check). Computes the true median by selecting the k-th smallest.
def py_median(mat):
    flat = []
    for row in mat:
        flat.extend(row)
    flat.sort()
    nm = len(flat)
    k = (nm + 1) // 2  # 1-indexed
    return flat[k - 1]


def build_reference(workdir):
    # macOS clang lacks <bits/stdc++.h>; create a shim header in an include dir.
    inc = os.path.join(workdir, "inc")
    os.makedirs(os.path.join(inc, "bits"), exist_ok=True)
    with open(os.path.join(inc, "bits", "stdc++.h"), "w") as f:
        f.write(
            "#include <algorithm>\n#include <vector>\n#include <climits>\n"
            "#include <iostream>\n#include <cstdint>\n#include <numeric>\n"
        )
    src = os.path.join(workdir, "ref.cpp")
    with open(src, "w") as f:
        f.write(CPP_REF)
    binp = os.path.join(workdir, "ref")
    cmd = ["clang++", "-std=c++17", "-O2", "-w", "-I", inc, src, "-o", binp]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit("Compilation of C++ reference failed")
    return binp


def make_row(C, lo=1, hi=VAL_MAX):
    """Random sorted row of length C with values in [lo, hi]."""
    vals = [random.randint(lo, hi) for _ in range(C)]
    vals.sort()
    return vals


def gen_odd(max_val, total_cap):
    """Pick a random odd dimension within [1, max_val] (cap by total_cap)."""
    hi = min(max_val, total_cap)
    if hi < 1:
        hi = 1
    if hi % 2 == 0:
        hi -= 1
    if hi < 1:
        hi = 1
    # random odd in [1, hi]
    return random.randrange(1, hi + 1, 2)


def gen_matrix():
    """Generate (R, C) odd dims with R*C odd, R*C <= ~ moderate, and a sorted matrix."""
    # Keep sizes modest so 2000 cases run fast, but cover a spread.
    bucket = random.random()
    if bucket < 0.04:
        R, C = 1, 1
    elif bucket < 0.10:
        R, C = 1, gen_odd(101, 101)
    elif bucket < 0.16:
        R, C = gen_odd(101, 101), 1
    elif bucket < 0.30:
        R = gen_odd(15, 999999)
        C = gen_odd(15, 999999)
    else:
        # Larger but bounded so total stays small. total <= 9999 (still odd*odd).
        R = gen_odd(99, 99)
        # cap C so R*C <= ~9999
        cmax = max(1, 9999 // max(1, R))
        C = gen_odd(cmax, cmax)

    # choose value-range style
    style = random.random()
    mat = []
    if style < 0.15:
        # tiny value range -> lots of duplicates
        lo, hi = 1, random.randint(1, 5)
        for _ in range(R):
            mat.append(make_row(C, lo, hi))
    elif style < 0.30:
        # extreme values near bounds
        for _ in range(R):
            mat.append(make_row(C, max(1, VAL_MAX - 1000), VAL_MAX))
    elif style < 0.45:
        # all same value
        v = random.randint(1, VAL_MAX)
        for _ in range(R):
            mat.append([v] * C)
    else:
        hi = random.choice([10, 100, 1000, 10**6, VAL_MAX])
        for _ in range(R):
            mat.append(make_row(C, 1, hi))
    return mat


def matrix_to_str(mat):
    # Format like examples: [[1, 4, 9], [2, 5, 6], ...]
    rows = ["[" + ", ".join(str(x) for x in row) + "]" for row in mat]
    return "[" + ", ".join(rows) + "]"


def main():
    random.seed(20260606)
    workdir = tempfile.mkdtemp(prefix="matmed_")
    binp = build_reference(workdir)

    # Build all matrices first, then batch them through the reference once.
    cases = []

    # Deterministic edge cases first.
    edge = []
    edge.append([[1]])                       # min size 1x1
    edge.append([[10**9]])                    # max value, 1x1
    edge.append([[1, 2, 3]])                  # single row
    edge.append([[1], [2], [3]])              # single column
    edge.append([[2, 2, 2], [2, 2, 2], [2, 2, 2]])  # all equal
    edge.append([[1, 4, 9], [2, 5, 6], [3, 7, 8]])  # example 1 -> 5
    edge.append([[1, 3, 8], [2, 3, 4], [1, 2, 5]])  # example 2 -> 3
    edge.append([[1, 4, 15], [2, 5, 6], [3, 8, 11]])  # nowYourTurn -> ?
    edge.append([[10**9, 10**9, 10**9]])      # row of max
    edge.append([[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    for e in edge:
        cases.append(e)

    while len(cases) < N_CASES:
        cases.append(gen_matrix())
    cases = cases[:N_CASES]

    # Prepare stdin for the C++ reference.
    sb = [str(len(cases))]
    for mat in cases:
        R = len(mat)
        C = len(mat[0])
        sb.append(f"{R} {C}")
        for row in mat:
            sb.append(" ".join(str(x) for x in row))
    stdin_data = "\n".join(sb) + "\n"

    r = subprocess.run([binp], input=stdin_data, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit("Reference run failed")
    out_lines = r.stdout.strip().split("\n")
    if len(out_lines) != len(cases):
        raise SystemExit(f"Expected {len(cases)} outputs, got {len(out_lines)}")

    # Cross-check against pure-python oracle on a sample and write file.
    with open(OUT_PATH, "w") as f:
        for idx, (mat, exp) in enumerate(zip(cases, out_lines)):
            exp = exp.strip()
            # validate constraints
            R = len(mat); C = len(mat[0])
            assert (R * C) % 2 == 1, "N*M must be odd"
            assert 1 <= R and 1 <= C
            for row in mat:
                assert len(row) == C
                assert all(1 <= v <= VAL_MAX for v in row)
                assert all(row[i] <= row[i + 1] for i in range(len(row) - 1)), "row not sorted"
            # cross-check every <=200 elems matrix, else sample
            if R * C <= 5000 or idx % 50 == 0:
                pm = py_median(mat)
                assert str(pm) == exp, f"Mismatch idx {idx}: py={pm} cpp={exp}"
            rec = {"inputs": {"matrix": matrix_to_str(mat)}, "expected": exp}
            f.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
