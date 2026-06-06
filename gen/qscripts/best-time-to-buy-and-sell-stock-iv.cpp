// Generator + static test set for: best-time-to-buy-and-sell-stock-iv
// Signature: int stockBuySell(vector<int> arr, int n, int k)
// Constraints: 1 <= n <= 1000, 0 <= arr[i] <= 1e4, 0 <= k <= 100
//
// Reference oracle: classic O(n*k) space-optimized DP for "at most k transactions".
// Build/run:
//   clang++ -std=c++17 -O2 -w gen/qscripts/best-time-to-buy-and-sell-stock-iv.cpp -o /tmp/gen_stockiv && /tmp/gen_stockiv
#include <vector>
#include <climits>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
#include <algorithm>
using namespace std;

// Oracle: max profit with at most k transactions.
// buy[j]  = best balance after having bought up to j-th transaction (currently holding)
// sell[j] = best profit after having completed up to j-th transaction (not holding)
int stockBuySell(const vector<int>& arr, int n, int k) {
    if (n == 0 || k == 0) return 0;
    vector<long long> buy(k + 1, LLONG_MIN / 4);
    vector<long long> sell(k + 1, 0);
    for (int i = 0; i < n; ++i) {
        int price = arr[i];
        for (int j = 1; j <= k; ++j) {
            // buy for the j-th transaction (uses sell[j-1])
            buy[j]  = max(buy[j],  sell[j - 1] - (long long)price);
            // sell to complete the j-th transaction
            sell[j] = max(sell[j], buy[j] + (long long)price);
        }
    }
    return (int)sell[k];
}

static string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

int main() {
    const string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/best-time-to-buy-and-sell-stock-iv.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    mt19937 rng(1234567u);

    vector<pair<vector<int>,int>> cases; // (arr, k)

    // ---- Hand-crafted edge cases ----
    auto add = [&](vector<int> a, int k){ cases.push_back({a, k}); };

    // dataset examples (sanity)
    add({3,2,6,5,0,3}, 2);
    add({1,2,4,2,5,7,2,4,9,0}, 3);
    add({1,3,2,8,4,9}, 2);

    // min size n=1
    add({0}, 0);
    add({0}, 100);
    add({10000}, 1);
    add({5}, 5);
    // k=0 -> always 0
    add({1,2,3,4,5}, 0);
    add({5,4,3,2,1}, 0);
    // strictly increasing (best = single big transaction)
    add({1,2,3,4,5,6,7,8,9,10}, 1);
    add({1,2,3,4,5,6,7,8,9,10}, 100);
    // strictly decreasing -> profit 0
    add({10,9,8,7,6,5,4,3,2,1}, 5);
    // all equal -> 0
    add({7,7,7,7,7,7}, 4);
    // all zeros
    add({0,0,0,0}, 3);
    // all max
    add({10000,10000,10000}, 2);
    // extreme swings
    add({0,10000,0,10000,0,10000}, 3);
    add({0,10000,0,10000,0,10000}, 1);
    add({10000,0,10000,0,10000,0}, 100);
    // k larger than possible transactions
    add({2,4,1}, 2);
    add({3,3,5,0,0,3,1,4}, 2);

    // ---- Randomized cases ----
    // Generate a spread of (n, k, value-range) combos.
    auto randCase = [&](int maxN, int maxVal, int maxK) {
        uniform_int_distribution<int> nd(1, maxN);
        int n = nd(rng);
        uniform_int_distribution<int> kd(0, maxK);
        int k = kd(rng);
        uniform_int_distribution<int> vd(0, maxVal);
        vector<int> a(n);
        for (int i = 0; i < n; ++i) a[i] = vd(rng);
        cases.push_back({a, k});
    };

    int target = 2000;
    // small arrays, many transactions feasible
    while ((int)cases.size() < 500)  randCase(15, 50, 20);
    // medium arrays
    while ((int)cases.size() < 1000) randCase(120, 1000, 100);
    // small value range -> lots of repeats
    while ((int)cases.size() < 1300) randCase(200, 5, 100);
    // large arrays near max n, full value range
    while ((int)cases.size() < 1700) randCase(1000, 10000, 100);
    // tiny n with big k
    while ((int)cases.size() < 1850) randCase(3, 10000, 100);
    // mid value range
    while ((int)cases.size() < (size_t)target) randCase(500, 200, 50);

    // Trim to exactly target.
    if ((int)cases.size() > target) cases.resize(target);

    for (auto& c : cases) {
        const vector<int>& a = c.first;
        int k = c.second;
        int ans = stockBuySell(a, (int)a.size(), k);
        // JSON line. arr value and k are strings per dataset format.
        out << "{\"inputs\": {\"arr\": \"" << arrToStr(a)
            << "\", \"k\": \"" << k << "\"}, \"expected\": \"" << ans << "\"}\n";
    }
    out.close();
    cerr << "wrote " << cases.size() << " cases to " << outPath << "\n";
    return 0;
}
