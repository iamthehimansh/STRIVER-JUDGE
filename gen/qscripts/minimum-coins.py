#!/usr/bin/env python3
"""
Generator + static test set for Striver problem "minimum-coins" (Minimum Coins / Coin Change).

Problem: Given coins of different denominations and a target amount, return the
fewest number of coins needed to make up that amount, or -1 if impossible.
Infinite supply of each coin (unbounded knapsack / coin change).

starterCpp signature:  int MinimumCoins(vector<int>& coins, int amount)
=> input keys (signature order): "coins", "amount"

Constraints:
  1 <= n (number of distinct denominations) <= 100
  1 <= coins[i], amount <= 10^3

Output file (one JSON object per line):
  {"inputs": {"coins": "[1, 2, 5]", "amount": "11"}, "expected": "3"}

Strategy: compute the oracle in pure Python (standard unbounded coin-change DP),
which is trivially correct, and cross-check a handful of cases against a compiled
C++ reference derived from the Striver A2Z reference solution.
"""

import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-coins.jsonl"
N_CASES = 2000
SEED = 20250606

MAX_N = 100      # max number of distinct denominations
MAX_VAL = 1000   # max coin value and max amount (10^3)


def min_coins(coins, amount):
    """Unbounded coin change: fewest coins to reach `amount`, else -1."""
    INF = float("inf")
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        best = INF
        for c in coins:
            if c <= a and dp[a - c] + 1 < best:
                best = dp[a - c] + 1
        dp[a] = best
    return -1 if dp[amount] == INF else dp[amount]


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


# ---------- C++ reference (cross-check oracle) ----------
CPP_SRC = r"""
#include <vector>
#include <string>
#include <iostream>
#include <sstream>
#include <algorithm>
using namespace std;

class Solution{
public:
    int MinimumCoins(vector<int>& coins, int amount) {
        const long long INF = 1e15;
        vector<long long> dp(amount + 1, INF);
        dp[0] = 0;
        for (int a = 1; a <= amount; a++) {
            for (int c : coins) {
                if (c <= a && dp[a - c] + 1 < dp[a]) dp[a] = dp[a - c] + 1;
            }
        }
        return dp[amount] >= INF ? -1 : (int)dp[amount];
    }
};

int main(){
    int T;
    if(!(cin >> T)) return 0;
    while(T--){
        int n; cin >> n;
        vector<int> coins(n);
        for(int i=0;i<n;i++) cin >> coins[i];
        int amount; cin >> amount;
        Solution s;
        cout << s.MinimumCoins(coins, amount) << "\n";
    }
    return 0;
}
"""


def build_cpp(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_SRC)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def run_cpp(binp, cases):
    """cases: list of (coins, amount). Returns list of ints."""
    lines = [str(len(cases))]
    for coins, amount in cases:
        lines.append(str(len(coins)))
        lines.append(" ".join(str(c) for c in coins))
        lines.append(str(amount))
    inp = "\n".join(lines) + "\n"
    out = subprocess.run([binp], input=inp, capture_output=True, text=True, check=True)
    return [int(x) for x in out.stdout.split()]


def gen_case(rng):
    """Generate one (coins, amount) within constraints."""
    kind = rng.random()
    if kind < 0.10:
        n = 1
    elif kind < 0.20:
        n = rng.randint(2, 5)
    else:
        n = rng.randint(1, MAX_N)
    # Distinct? Statement says "distinct denominations" for n, but values can
    # technically repeat. Keep it safe & varied: usually distinct, occasionally
    # allow duplicates (correctness unaffected; constraints still hold).
    if rng.random() < 0.85 and n <= MAX_VAL:
        coins = rng.sample(range(1, MAX_VAL + 1), n)
    else:
        coins = [rng.randint(1, MAX_VAL) for _ in range(n)]
    amount = rng.randint(1, MAX_VAL)
    return coins, amount


def edge_cases():
    cases = []
    # min size, smallest values
    cases.append(([1], 1))
    cases.append(([1], 1000))
    cases.append(([1000], 1000))
    cases.append(([1000], 1))            # impossible -> -1
    cases.append(([2], 3))               # impossible -> -1
    cases.append(([2, 5], 3))            # example 2 -> -1
    cases.append(([1, 2, 5], 11))        # example 1 -> 3
    cases.append(([10], 50))             # nowYourTurn -> 5
    cases.append(([10], 5))              # -> -1
    cases.append(([1, 1000], 1000))      # -> 1
    cases.append(([999, 1000], 1))       # -> -1
    cases.append(([7], 1000))            # not divisible -> -1
    cases.append((list(range(1, 101)), 1000))   # n=100
    cases.append((list(range(2, 102)), 1000))   # n=100, no coin=1
    cases.append(([3, 7], 1000))
    cases.append(([1, 2], 1000))
    cases.append(([500, 1000], 1000))    # -> 1
    cases.append(([500, 1000], 999))     # -> -1
    cases.append(([1, 5, 6, 9], 11))
    cases.append(([2, 4, 6, 8, 10], 999))  # all even, odd amount -> -1
    return cases


def main():
    rng = random.Random(SEED)
    cases = []
    seen = set()

    for c in edge_cases():
        key = (tuple(c[0]), c[1])
        if key not in seen:
            seen.add(key)
            cases.append(c)

    while len(cases) < N_CASES:
        coins, amount = gen_case(rng)
        cases.append((coins, amount))

    cases = cases[:N_CASES]

    # Cross-check with compiled C++ reference on a sample (and a few notable cases).
    with tempfile.TemporaryDirectory() as tmp:
        binp = build_cpp(tmp)
        check_idx = list(range(min(len(cases), 25)))  # first 25 (edge cases)
        check_idx += rng.sample(range(len(cases)), min(200, len(cases)))
        check_idx = sorted(set(check_idx))
        sub = [cases[i] for i in check_idx]
        cpp_out = run_cpp(binp, sub)
        mismatches = 0
        for (coins, amount), cval in zip(sub, cpp_out):
            pval = min_coins(coins, amount)
            if pval != cval:
                mismatches += 1
                if mismatches <= 5:
                    print(f"MISMATCH coins={coins[:6]}... amount={amount} py={pval} cpp={cval}")
        if mismatches:
            raise SystemExit(f"Oracle mismatch on {mismatches} cases; aborting.")
        print(f"Cross-checked {len(sub)} cases against C++ reference: all match.")

    # Write output.
    with open(OUT_PATH, "w") as f:
        for coins, amount in cases:
            exp = min_coins(coins, amount)
            obj = {
                "inputs": {"coins": fmt_arr(coins), "amount": str(amount)},
                "expected": str(exp),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
