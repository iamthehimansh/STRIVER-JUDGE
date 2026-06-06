// Generator for Striver problem: minimum-coins (Coin Change - fewest coins)
// Signature: int MinimumCoins(vector<int>& coins, int amount)
// Constraints: 1 <= n <= 100 ; 1 <= coins[i], amount <= 1000
//
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-coins.jsonl
//   one JSON object per line: {"inputs":{"coins":"[...]","amount":"N"},"expected":"K"}
//
// Build: clang++ -std=c++17 -O2 -w minimum-coins.cpp -o gen && ./gen
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <random>
#include <algorithm>
using namespace std;

// Reference oracle: minimum coins to make `amount` using unlimited `coins`.
// Unbounded-knapsack DP. Returns -1 if impossible.
int MinimumCoins(vector<int>& coins, int amount) {
    const long long INF = 1e9;
    vector<long long> dp(amount + 1, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++) {
        for (int c : coins) {
            if (c <= a && dp[a - c] + 1 < dp[a])
                dp[a] = dp[a - c] + 1;
        }
    }
    return dp[amount] >= INF ? -1 : (int)dp[amount];
}

static string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main() {
    const char* outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-coins.jsonl";
    FILE* f = fopen(outPath, "w");
    if (!f) { fprintf(stderr, "cannot open output\n"); return 1; }

    mt19937 rng(123456789u);

    struct Case { vector<int> coins; int amount; };
    vector<Case> cases;

    // ---- Edge / structured cases ----
    cases.push_back({{1}, 1});                 // smallest
    cases.push_back({{1000}, 1000});           // single coin == amount
    cases.push_back({{1000}, 1});              // impossible (coin too big)
    cases.push_back({{2}, 999});               // impossible (odd amount)
    cases.push_back({{2}, 1000});              // exactly divisible
    cases.push_back({{1}, 1000});              // all ones -> 1000 coins
    cases.push_back({{1, 2, 5}, 11});          // example 1 -> 3
    cases.push_back({{2, 5}, 3});              // example 2 -> -1
    cases.push_back({{10}, 5});                // now-your-turn -> -1
    cases.push_back({{7, 11}, 1});             // impossible
    cases.push_back({{1000, 999}, 1});         // impossible
    cases.push_back({{3, 7}, 1000});           // mix
    cases.push_back({{5, 10, 25}, 1000});      // canonical-ish
    cases.push_back({{1000}, 1000});

    // 100 distinct coins from 1..1000, large amount
    {
        vector<int> c;
        for (int i = 1; i <= 100; i++) c.push_back(i * 10); // 10,20,...,1000 (100 distinct)
        cases.push_back({c, 1000});
    }

    auto pickAmount = [&](){ return (int)(uniform_int_distribution<int>(1, 1000)(rng)); };
    auto pickCoinVal = [&](){ return (int)(uniform_int_distribution<int>(1, 1000)(rng)); };

    // ---- Random cases ----
    // Strategy variety so we get a good mix of solvable and unsolvable.
    // Modes 0-3 lean solvable; mode 4 (impossible-leaning) and mode 5 (single
    // coin) are sampled less often to avoid -1 dominating the set.
    while ((int)cases.size() < 2000) {
        // weighted mode selection: solvable-leaning modes more frequent
        int r = uniform_int_distribution<int>(0, 99)(rng);
        int mode;
        if      (r < 30) mode = 0;   // 30%
        else if (r < 55) mode = 1;   // 25%
        else if (r < 75) mode = 2;   // 20%
        else if (r < 82) mode = 3;   // 7%
        else if (r < 92) mode = 4;   // 10% impossible-leaning
        else             mode = 5;   // 8% single coin
        int n;
        vector<int> coins;
        int amount = pickAmount();

        if (mode == 0) {
            // small n, small coin values (likely solvable). Include a 1 often
            // so most are solvable but not always.
            n = uniform_int_distribution<int>(1, 8)(rng);
            for (int i = 0; i < n; i++) coins.push_back(uniform_int_distribution<int>(1, 20)(rng));
        } else if (mode == 1) {
            // medium n, full range coins, force a small coin to bias solvable
            n = uniform_int_distribution<int>(1, 30)(rng);
            for (int i = 0; i < n; i++) coins.push_back(pickCoinVal());
            if (!coins.empty()) coins[0] = uniform_int_distribution<int>(1, 5)(rng);
        } else if (mode == 2) {
            // large n up to 100, full range coins
            n = uniform_int_distribution<int>(50, 100)(rng);
            for (int i = 0; i < n; i++) coins.push_back(pickCoinVal());
        } else if (mode == 3) {
            // mid n, mid coin values
            n = uniform_int_distribution<int>(2, 15)(rng);
            for (int i = 0; i < n; i++) coins.push_back(uniform_int_distribution<int>(1, 100)(rng));
        } else if (mode == 4) {
            // coins all > amount sometimes -> impossible-leaning
            amount = uniform_int_distribution<int>(1, 50)(rng);
            n = uniform_int_distribution<int>(1, 10)(rng);
            for (int i = 0; i < n; i++) coins.push_back(uniform_int_distribution<int>(51, 1000)(rng));
        } else {
            // single coin, parity/divisibility edge
            n = 1;
            coins.push_back(uniform_int_distribution<int>(1, 1000)(rng));
        }

        // sanity clamp (defensive; all generators already within [1,1000])
        for (int& c : coins) { if (c < 1) c = 1; if (c > 1000) c = 1000; }
        if (amount < 1) amount = 1; if (amount > 1000) amount = 1000;

        cases.push_back({coins, amount});
    }

    // ---- Emit ----
    for (auto& cs : cases) {
        vector<int> coins = cs.coins;     // copy (oracle takes non-const ref)
        int ans = MinimumCoins(coins, cs.amount);
        // Write inputs in signature order: coins, amount
        fprintf(f, "{\"inputs\": {\"coins\": \"%s\", \"amount\": \"%d\"}, \"expected\": \"%d\"}\n",
                vecToStr(cs.coins).c_str(), cs.amount, ans);
    }

    fclose(f);
    fprintf(stderr, "wrote %zu cases to %s\n", cases.size(), outPath);
    return 0;
}
