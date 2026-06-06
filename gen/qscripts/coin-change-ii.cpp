// Generator + reference oracle for Striver "Coin Change 2 (DP-22)" / slug: coin-change-ii
//
// Problem signature (starterCpp):
//   int count(vector<int>& coins, int N, int amount);
//   - N == coins.size(), so it is dropped from the emitted input keys.
//   - Emitted input keys (signature order, minus trailing size param): "coins", "amount".
//
// Constraints: 1 <= n, coins[i], amount <= 10^3 ; all coins values unique.
// Answer: number of distinct combinations (unbounded use of each coin) summing to amount,
//         taken modulo 1e9+7.
//
// Writes 2000 JSONL lines to generated-tests/coin-change-ii.jsonl :
//   {"inputs": {"coins": "[..]", "amount": "N"}, "expected": "X"}
//
// Build:  clang++ -std=c++17 -O2 -w coin-change-ii.cpp -o gen
// Run:    ./gen   (paths are hardcoded below)

#include <vector>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
#include <set>
#include <algorithm>

using namespace std;

static const long long MOD = 1000000007LL;

// Reference oracle: count of combinations (order-independent) to make `amount`
// using unlimited copies of each coin, modulo 1e9+7.
long long countCombinations(const vector<int>& coins, int amount) {
    vector<long long> dp(amount + 1, 0);
    dp[0] = 1;
    for (int c : coins) {
        for (int t = c; t <= amount; ++t) {
            dp[t] = (dp[t] + dp[t - c]) % MOD;
        }
    }
    return dp[amount];
}

string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main() {
    const string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/coin-change-ii.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    mt19937 rng(987654321u);

    const int TOTAL = 2000;
    int written = 0;

    // ---- Deterministic edge / structured cases first ----
    struct EC { vector<int> coins; int amount; };
    vector<EC> edges;
    edges.push_back({{2,4,10}, 10});        // example 1 -> 4
    edges.push_back({{5}, 5});              // example 2 -> 1
    edges.push_back({{1,2,3,5}, 5});       // nowYourTurn -> should be 5
    edges.push_back({{1}, 1});             // min everything -> 1
    edges.push_back({{1000}, 1000});       // single coin == amount -> 1
    edges.push_back({{1000}, 1});          // coin > amount, impossible -> 0
    edges.push_back({{2}, 1});             // odd amount with even coin -> 0
    edges.push_back({{1}, 1000});          // all ones, max amount -> 1
    edges.push_back({{3,7}, 1000});        // two coprime coins, large amount
    edges.push_back({{1,2}, 1000});        // classic, large modulo result

    // a coins vector that is all values 1..1000 with amount 1000 (max n)
    {
        vector<int> big;
        for (int v = 1; v <= 1000; ++v) big.push_back(v);
        edges.push_back({big, 1000});
        edges.push_back({big, 999});
        edges.push_back({big, 1});
    }
    // some coins all > amount -> impossible
    edges.push_back({{500,600,700,800}, 100});
    // exactly amount present plus others
    edges.push_back({{4,6,8,10}, 2});      // smallest coin 4 > 2 -> 0
    edges.push_back({{2,3}, 7});           // -> combos of 2,3 summing 7: (2*2+3),(2+... ) compute

    for (auto& e : edges) {
        if (written >= TOTAL) break;
        long long ans = countCombinations(e.coins, e.amount);
        out << "{\"inputs\": {\"coins\": \"" << vecToStr(e.coins)
            << "\", \"amount\": \"" << e.amount
            << "\"}, \"expected\": \"" << ans << "\"}\n";
        ++written;
    }

    // ---- Random cases within constraints ----
    // n in [1,1000], coins[i] in [1,1000] unique, amount in [1,1000].
    uniform_int_distribution<int> amtD(1, 1000);

    while (written < TOTAL) {
        int amount = amtD(rng);

        // choose n: bias toward smaller n but include large ones.
        int nMax = 1000;
        int n;
        int bucket = rng() % 10;
        if (bucket < 4)      n = 1 + (rng() % 8);          // small 1..8
        else if (bucket < 7) n = 1 + (rng() % 50);         // medium 1..50
        else if (bucket < 9) n = 1 + (rng() % 300);        // large
        else                 n = 1 + (rng() % nMax);       // up to 1000
        if (n > nMax) n = nMax;

        // pick n unique coin values in [1,1000]
        vector<int> coins;
        if (n >= 1000) {
            for (int v = 1; v <= 1000; ++v) coins.push_back(v);
        } else {
            set<int> chosen;
            uniform_int_distribution<int> coinD(1, 1000);
            while ((int)chosen.size() < n) chosen.insert(coinD(rng));
            coins.assign(chosen.begin(), chosen.end());
            // shuffle so order isn't always sorted (problem doesn't require sorted)
            shuffle(coins.begin(), coins.end(), rng);
        }

        long long ans = countCombinations(coins, amount);
        out << "{\"inputs\": {\"coins\": \"" << vecToStr(coins)
            << "\", \"amount\": \"" << amount
            << "\"}, \"expected\": \"" << ans << "\"}\n";
        ++written;
    }

    out.close();
    cerr << "wrote " << written << " cases to " << outPath << "\n";
    return 0;
}
