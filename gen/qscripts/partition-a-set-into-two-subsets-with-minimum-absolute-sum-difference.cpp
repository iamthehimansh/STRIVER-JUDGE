// Generator + reference oracle for:
//   "Partition a set into two subsets with minimum absolute sum difference"
//
// Method signature (starterCpp):
//   int minDifference(vector<int>& arr, int n)
//
// Constraints:
//   1 <= n * (sum of array elements) <= 10^6
//   0 <  arr[i] <= 10^4
//
// Output JSONL line format:
//   {"inputs": {"arr": "[...]"}, "expected": "<int>"}
//
// Build:  clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:    ./gen > out.jsonl
//
#include <bits/stdc++.h>
using namespace std;

// ---- Reference oracle (subset-sum DP over total sum) ----
// Partition arr into two subsets minimizing |sumA - sumB|.
// Find all achievable subset sums s1 in [0..sum]; answer = min over achievable
// s1 <= sum/2 of (sum - 2*s1).
long long minDifferenceRef(const vector<int>& arr, int n) {
    long long sum = 0;
    for (int i = 0; i < n; i++) sum += arr[i];
    int K = (int)sum;
    // dp[t] = true if subset sum t achievable using items processed so far.
    vector<char> dp(K + 1, 0);
    dp[0] = 1;
    for (int i = 0; i < n; i++) {
        int v = arr[i];
        for (int t = K; t >= v; t--) {
            if (dp[t - v]) dp[t] = 1;
        }
    }
    long long mini = LLONG_MAX;
    for (long long s1 = 0; s1 <= sum / 2; s1++) {
        if (dp[(int)s1]) {
            long long diff = sum - 2 * s1; // s1 <= sum/2 so non-negative
            mini = min(mini, diff);
        }
    }
    return mini;
}

mt19937_64 rng(0xC0FFEEULL);
long long randint(long long lo, long long hi) {
    return lo + (long long)(rng() % (unsigned long long)(hi - lo + 1));
}

int main(int argc, char** argv) {
    int TOTAL = 2000;
    if (argc > 1) TOTAL = atoi(argv[1]);

    auto emit = [&](const vector<int>& arr) {
        int n = (int)arr.size();
        long long ans = minDifferenceRef(arr, n);
        // build "arr" string
        string s = "[";
        for (int i = 0; i < n; i++) {
            if (i) s += ", ";
            s += to_string(arr[i]);
        }
        s += "]";
        printf("{\"inputs\": {\"arr\": \"%s\"}, \"expected\": \"%lld\"}\n", s.c_str(), ans);
    };

    // ---- Fixed edge cases first ----
    vector<vector<int>> edges;
    edges.push_back({1});                 // n=1, single element
    edges.push_back({10000});             // n=1, max value
    edges.push_back({1, 1});              // diff 0
    edges.push_back({1, 7, 14, 5});       // example 1 -> 1
    edges.push_back({3, 1, 6, 2, 2});     // example 2 -> 0
    edges.push_back({2, 2, 2, 9});        // nowYourTurn -> 3
    edges.push_back({10000, 10000});      // diff 0
    edges.push_back({10000, 1});          // diff 9999
    edges.push_back({1, 2, 3, 4, 5, 6, 7}); // sum 28 -> 0
    edges.push_back({5, 5, 5, 5, 5});     // odd count equal -> 5

    for (auto& e : edges) emit(e);
    int produced = (int)edges.size();

    // ---- Random cases honoring 1 <= n*sum <= 10^6, 0 < arr[i] <= 10^4 ----
    // Strategy: pick n, pick a per-element max so that n*sum stays <= 1e6.
    // Worst case n*sum: choose n then ensure sum <= 1e6/n.
    while (produced < TOTAL) {
        // bias n across small..large
        int nChoice = (int)randint(0, 9);
        int n;
        if (nChoice == 0) n = 1;
        else if (nChoice == 1) n = (int)randint(1, 3);
        else if (nChoice <= 4) n = (int)randint(2, 30);
        else if (nChoice <= 7) n = (int)randint(2, 300);
        else n = (int)randint(2, 1000);

        // max allowed total sum so that n*sum <= 1e6
        long long maxSum = 1000000LL / n; // floor
        if (maxSum < 1) maxSum = 1;       // n could be up to 1e6 in theory but here <=1000
        // each element in [1, 10000]; also bounded so cumulative sum stays <= maxSum
        // and sum >= n (since each >=1). If n > maxSum impossible (n<=1000, maxSum>=1000) ok.
        // Build array element by element keeping running sum under maxSum, leaving room
        // for remaining mandatory minimum (each remaining elem needs >=1).
        vector<int> arr;
        long long sum = 0;
        bool ok = true;
        for (int i = 0; i < n; i++) {
            int remaining = n - i - 1; // elements after this one, each needs >=1
            long long room = maxSum - sum - remaining; // max this element may be
            if (room < 1) { ok = false; break; }
            long long hi = min<long long>(10000, room);
            int v = (int)randint(1, hi);
            arr.push_back(v);
            sum += v;
        }
        if (!ok || arr.empty()) continue;
        // sanity: enforce constraints strictly
        if ((long long)arr.size() * sum > 1000000LL) continue;
        for (int v : arr) if (v < 1 || v > 10000) { ok = false; break; }
        if (!ok) continue;

        emit(arr);
        produced++;
    }
    return 0;
}
