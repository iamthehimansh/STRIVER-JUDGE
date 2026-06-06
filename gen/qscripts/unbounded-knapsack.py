#!/usr/bin/env python3
"""
Test-case generator for Striver problem: unbounded-knapsack

Problem: Given two integer arrays val and wt of size N, and capacity W,
find the maximum value achievable with an infinite supply of each item
such that total weight <= W.

Method signature (starterCpp):
    int unboundedKnapsack(vector<int>& wt, vector<int>& val, int n, int W)

Output keys = parameter names in signature order, dropping the trailing
size param `n` (equals array length). So keys are: wt, val, W.

Constraints:
    1 <= N <= 500
    1 <= W <= 1000
    1 <= wt[i] <= 500
    1 <= val[i] <= 500

Reference: standard unbounded knapsack DP (O(N*W)) implemented in C++,
compiled and run on each generated case to produce ground-truth output.
"""
import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/unbounded-knapsack.jsonl"
N_CASES = 2000
SEED = 20260606

CPP_SOURCE = r'''
#include <vector>
#include <iostream>
#include <algorithm>
using namespace std;

// Standard unbounded knapsack DP, O(N*W).
int unboundedKnapsack(vector<int>& wt, vector<int>& val, int n, int W) {
    vector<long long> dp(W + 1, 0);
    for (int cap = 1; cap <= W; ++cap) {
        for (int i = 0; i < n; ++i) {
            if (wt[i] <= cap) {
                long long cand = (long long)val[i] + dp[cap - wt[i]];
                if (cand > dp[cap]) dp[cap] = cand;
            }
        }
    }
    return (int)dp[W];
}

int main() {
    // Input format (stdin):
    //   n W
    //   wt[0..n-1]
    //   val[0..n-1]
    // Repeat until EOF.
    int n, W;
    while (cin >> n >> W) {
        vector<int> wt(n), val(n);
        for (int i = 0; i < n; ++i) cin >> wt[i];
        for (int i = 0; i < n; ++i) cin >> val[i];
        cout << unboundedKnapsack(wt, val, n, W) << "\n";
    }
    return 0;
}
'''


def compile_reference(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_SOURCE)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def gen_case(rng):
    """Generate one (wt, val, W) case within constraints."""
    # mix of sizes including edges
    r = rng.random()
    if r < 0.05:
        n = 1
    elif r < 0.10:
        n = 500
    elif r < 0.4:
        n = rng.randint(1, 10)
    else:
        n = rng.randint(1, 500)

    W = rng.randint(1, 1000)

    wt = [rng.randint(1, 500) for _ in range(n)]
    val = [rng.randint(1, 500) for _ in range(n)]
    return wt, val, W


def edge_cases():
    cases = []
    # dataset examples (note signature order wt, val)
    cases.append(([2, 4, 6], [5, 11, 13], 10))            # expected 27
    cases.append(([1, 3, 4, 5], [10, 40, 50, 70], 8))     # expected 110
    cases.append(([10, 20, 30], [60, 100, 120], 60))      # expected 360
    # minimal
    cases.append(([1], [1], 1))
    cases.append(([1], [500], 1000))
    cases.append(([500], [500], 1000))
    cases.append(([500], [500], 1))      # nothing fits -> 0
    cases.append(([500], [1], 499))      # nothing fits -> 0
    # all weights heavier than W
    cases.append(([100, 200, 300], [10, 20, 30], 50))
    # single best item repeated
    cases.append(([1], [500], 1000))
    return cases


def main():
    rng = random.Random(SEED)

    cases = []
    cases.extend(edge_cases())
    while len(cases) < N_CASES:
        cases.append(gen_case(rng))
    cases = cases[:N_CASES]

    with tempfile.TemporaryDirectory() as tmpdir:
        binp = compile_reference(tmpdir)

        # Feed all cases to the reference in one batched run.
        stdin_lines = []
        for wt, val, W in cases:
            n = len(wt)
            stdin_lines.append(f"{n} {W}")
            stdin_lines.append(" ".join(str(x) for x in wt))
            stdin_lines.append(" ".join(str(x) for x in val))
        stdin_data = "\n".join(stdin_lines) + "\n"

        proc = subprocess.run(
            [binp], input=stdin_data, capture_output=True, text=True, check=True
        )
        outputs = proc.stdout.strip().split("\n")

    assert len(outputs) == len(cases), (
        f"expected {len(cases)} outputs, got {len(outputs)}"
    )

    with open(OUT_PATH, "w") as f:
        for (wt, val, W), exp in zip(cases, outputs):
            obj = {
                "inputs": {
                    "wt": fmt_arr(wt),
                    "val": fmt_arr(val),
                    "W": str(W),
                },
                "expected": exp.strip(),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")
    # quick sanity print of first 3
    for (wt, val, W), exp in list(zip(cases, outputs))[:3]:
        print(f"  wt={wt} val={val} W={W} -> {exp}")


if __name__ == "__main__":
    main()
