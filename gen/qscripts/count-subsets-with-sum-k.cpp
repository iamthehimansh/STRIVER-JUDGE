// Generator + static test set for Striver problem: count-subsets-with-sum-k
// Signature: int perfectSum(vector<int>& arr, int K)
// Constraints: 1 <= n <= 100 ; 1 <= arr[i] <= 1000 ; 1 <= K <= 1000
// Output: number of subsets summing to K, modulo 1e9+7
//
// Build: clang++ -std=c++17 -O2 -w count-subsets-with-sum-k.cpp -o gen
// Run:   ./gen > out.jsonl   (writes 2000 JSONL lines)

#include <vector>
#include <string>
#include <random>
#include <iostream>
#include <cstdint>
using namespace std;

static const long long MOD = 1000000000LL + 7;

// Reference oracle: count subsets with sum == K, modulo 1e9+7.
// Standard 1D DP over targets. arr[i] >= 1 per constraints.
long long perfectSum(const vector<int>& arr, int K) {
    vector<long long> dp(K + 1, 0);
    dp[0] = 1; // empty subset
    for (int x : arr) {
        if (x > K) continue; // cannot contribute to any target <= K
        for (int t = K; t >= x; --t) {
            dp[t] = (dp[t] + dp[t - x]) % MOD;
        }
    }
    return dp[K] % MOD;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

void emit(const vector<int>& arr, int K) {
    long long ans = perfectSum(arr, K);
    // keys in signature order: arr, K
    cout << "{\"inputs\": {\"arr\": \"" << arrToStr(arr)
         << "\", \"K\": \"" << K
         << "\"}, \"expected\": \"" << ans << "\"}\n";
}

int main() {
    std::mt19937 rng(123456789u);
    vector<pair<vector<int>,int>> cases;

    // ---- Edge cases ----
    cases.push_back({{1}, 1});            // min n, K reachable
    cases.push_back({{1}, 1000});         // K large, single small element -> 0
    cases.push_back({{1000}, 1000});      // single max element exactly K
    cases.push_back({{1000}, 1});         // element > K -> 0
    cases.push_back({{2,3,5,16,8,10}, 10}); // example 1 -> 3
    cases.push_back({{1,2,3,4,5}, 5});      // example 2 -> 3
    cases.push_back({{2,2,2,2}, 4});        // nowYourTurn -> 6
    {
        // n=100 of all 1s, K=50 -> C(100,50) mod p
        vector<int> a(100, 1);
        cases.push_back({a, 50});
        cases.push_back({a, 100}); // all ones sum exactly -> 1
        cases.push_back({a, 1000}); // unreachable -> 0
    }
    {
        // 100 elements all equal 10, K=1000 -> all of them -> 1
        vector<int> a(100, 10);
        cases.push_back({a, 1000});
        cases.push_back({a, 500}); // choose 50 of 100 -> C(100,50)
    }
    {
        // max values: 100 elements of 1000, K=1000 -> count of single picks = 100
        vector<int> a(100, 1000);
        cases.push_back({a, 1000});
    }

    // ---- Random cases to fill up to 2000 ----
    auto randInt = [&](int lo, int hi) {
        std::uniform_int_distribution<int> d(lo, hi);
        return d(rng);
    };

    while ((int)cases.size() < 2000) {
        int n = randInt(1, 100);
        // Mix value ranges: sometimes small values (more reachable sums),
        // sometimes full range up to 1000.
        int mode = randInt(0, 3);
        int vmax;
        if (mode == 0) vmax = randInt(1, 10);
        else if (mode == 1) vmax = randInt(1, 50);
        else if (mode == 2) vmax = randInt(1, 200);
        else vmax = 1000;
        vector<int> a(n);
        for (int i = 0; i < n; ++i) a[i] = randInt(1, vmax);
        int K = randInt(1, 1000);
        // Occasionally bias K to be a sum of a random prefix so answers are nonzero.
        if (randInt(0, 2) == 0 && !a.empty()) {
            int sub = randInt(1, n);
            long long s = 0;
            for (int i = 0; i < sub; ++i) s += a[i];
            if (s >= 1 && s <= 1000) K = (int)s;
        }
        cases.push_back({a, K});
    }

    for (auto& c : cases) emit(c.first, c.second);
    return 0;
}
