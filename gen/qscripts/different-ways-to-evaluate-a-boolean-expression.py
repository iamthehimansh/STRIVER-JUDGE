#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
  "Different Ways to Evaluate a Boolean Expression"  (Boolean Parenthesization, MCM/Partition DP)

starterCpp signature:  int countTrue(string s)
  -> the single input key is "s" (the raw expression string).

Constraints:
  - 1 <= expr.length <= 100
  - expr[i] in {'T','F','&','|','^'}
  - operands ('T'/'F') and operators ('&','|','^') alternate
  - expr always starts and ends with an operand => odd length
  - answer fits in a signed 32-bit integer (taken mod 1e9+7 per statement)

This script:
  1. Builds a C++ reference (Boolean Parenthesization DP, mod 1e9+7) in a temp dir.
  2. Generates 2000 random-but-valid expressions (incl. edge cases).
  3. Runs the reference to compute expected outputs.
  4. Writes JSONL: {"inputs": {"s": "<expr>"}, "expected": "<count>"} one per line.
"""

import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/different-ways-to-evaluate-a-boolean-expression.jsonl"
N_CASES = 2000

OPERANDS = ['T', 'F']
OPERATORS = ['&', '|', '^']

REF_CPP = r'''
#include <iostream>
#include <string>
#include <vector>
using namespace std;
const long long MOD = 1000000007LL;
class Solution {
public:
    vector<vector<vector<long long>>> dp;
    long long f(int i, int j, int isTrue, const string& s) {
        if (i > j) return 0;
        if (i == j) {
            if (isTrue) return s[i] == 'T' ? 1 : 0;
            else return s[i] == 'F' ? 1 : 0;
        }
        if (dp[i][j][isTrue] != -1) return dp[i][j][isTrue];
        long long ways = 0;
        for (int k = i + 1; k <= j - 1; k += 2) {
            char op = s[k];
            long long lt = f(i, k - 1, 1, s);
            long long lf = f(i, k - 1, 0, s);
            long long rt = f(k + 1, j, 1, s);
            long long rf = f(k + 1, j, 0, s);
            if (op == '&') {
                if (isTrue) ways += (lt * rt) % MOD;
                else ways += (lt * rf) % MOD + (lf * rt) % MOD + (lf * rf) % MOD;
            } else if (op == '|') {
                if (isTrue) ways += (lt * rt) % MOD + (lt * rf) % MOD + (lf * rt) % MOD;
                else ways += (lf * rf) % MOD;
            } else {
                if (isTrue) ways += (lt * rf) % MOD + (lf * rt) % MOD;
                else ways += (lt * rt) % MOD + (lf * rf) % MOD;
            }
            ways %= MOD;
        }
        return dp[i][j][isTrue] = ways % MOD;
    }
    int countTrue(string s) {
        int n = s.size();
        dp.assign(n, vector<vector<long long>>(n, vector<long long>(2, -1)));
        return (int)(f(0, n - 1, 1, s) % MOD);
    }
};
int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    string line;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty()) continue;
        Solution sol;
        cout << sol.countTrue(line) << "\n";
    }
    return 0;
}
'''


def make_expr(num_operands):
    """Build a valid expression with `num_operands` operands (operators between them)."""
    parts = [random.choice(OPERANDS)]
    for _ in range(num_operands - 1):
        parts.append(random.choice(OPERATORS))
        parts.append(random.choice(OPERANDS))
    return ''.join(parts)


def gen_cases():
    cases = []
    seen = set()

    def add(expr):
        if expr and expr not in seen:
            seen.add(expr)
            cases.append(expr)

    # --- Edge cases ---
    add("T")          # min size, single true
    add("F")          # min size, single false
    add("T^F")        # the nowYourTurn example
    add("T|T&F^T")    # example 1
    add("T^F|F")      # example 2
    # all same operand / operator extremes at max length (100 chars => 50 operands, 49 ops)
    # 50 operands -> length 99 (odd, <=100)
    add("T".join(["&"] * 0) or "T")  # noop guard
    add("T" + ("&T" * 49))   # length 99, all T &
    add("F" + ("|F" * 49))   # length 99, all F |
    add("T" + ("^T" * 49))   # length 99, all T ^
    add("T" + ("&F" * 49))   # alternating T&F...
    add("F" + ("&F" * 49))   # all F &
    add("T" + ("|T" * 49))   # all T |
    # a few small explicit ones
    for op in OPERATORS:
        for a in OPERANDS:
            for b in OPERANDS:
                add(a + op + b)

    # --- Random small lengths (good coverage of distinct structures) ---
    while len(cases) < 400:
        num_ops = random.randint(1, 5)  # 1..5 operands -> length 1..9
        add(make_expr(num_ops))

    # --- Random medium ---
    while len(cases) < 1000:
        num_ops = random.randint(1, 20)  # length up to 39
        add(make_expr(num_ops))

    # --- Random up to max constraint (length <= 100 => up to 50 operands) ---
    while len(cases) < N_CASES:
        num_ops = random.randint(1, 50)  # length 1..99 (odd, <=100)
        add(make_expr(num_ops))

    # validate all
    for e in cases:
        assert 1 <= len(e) <= 100, f"length out of bounds: {len(e)}"
        assert len(e) % 2 == 1, f"even length: {e}"
        for idx, ch in enumerate(e):
            if idx % 2 == 0:
                assert ch in ('T', 'F'), f"bad operand at {idx} in {e}"
            else:
                assert ch in ('&', '|', '^'), f"bad operator at {idx} in {e}"

    return cases[:N_CASES]


def main():
    random.seed(20260606)
    cases = gen_cases()

    with tempfile.TemporaryDirectory() as td:
        cpp = os.path.join(td, "ref.cpp")
        binp = os.path.join(td, "ref")
        with open(cpp, "w") as fh:
            fh.write(REF_CPP)
        subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", cpp, "-o", binp],
            check=True,
        )
        stdin_data = "\n".join(cases) + "\n"
        proc = subprocess.run(
            [binp], input=stdin_data, capture_output=True, text=True, check=True
        )
        outputs = proc.stdout.strip("\n").split("\n")
        assert len(outputs) == len(cases), f"output count {len(outputs)} != cases {len(cases)}"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as fh:
        for expr, exp in zip(cases, outputs):
            exp = exp.strip()
            assert exp != "", "empty expected"
            rec = {"inputs": {"s": expr}, "expected": exp}
            fh.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
