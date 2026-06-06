// Generator + reference oracle for "Minimum cost to cut the stick"
// Reference: Striver MCM/Partition DP solution.
// Builds 2000 valid cases and writes generated-tests/minimum-cost-to-cut-the-stick.jsonl
//
// Constraints enforced:
//   2 <= n <= 1e5
//   1 <= cuts.length <= min(n-1, 100)
//   1 <= cuts[i] <= n-1
//   all cuts unique
//
// Output keys follow the dataset testcases: "n" and "nums" (the cuts array).
//
// Compile: clang++ -std=c++17 -O2 -w minimum-cost-to-cut-the-stick.cpp -o gen
// Run:     ./gen > minimum-cost-to-cut-the-stick.jsonl

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <random>
#include <set>
#include <string>
#include <iostream>
using namespace std;

// ---- Reference solution (Partition DP) ----
long long minCost(int n, vector<int>& cuts) {
    vector<long long> cut;
    cut.push_back(0);
    for (int x : cuts) cut.push_back(x);
    cut.push_back(n);
    sort(cut.begin(), cut.end());
    int s = (int)cut.size();          // = m + 2, m = cuts.size()
    int m = (int)cuts.size();
    // dp over intervals [i..j] in 1..m (indices into cut)
    const long long INF = (long long)4e18;
    vector<vector<long long>> dp(s + 2, vector<long long>(s + 2, 0));
    // length of interval
    for (int len = 1; len <= m; len++) {
        for (int i = 1; i + len - 1 <= m; i++) {
            int j = i + len - 1;
            long long best = INF;
            long long span = cut[j + 1] - cut[i - 1];
            for (int k = i; k <= j; k++) {
                long long left  = (k - 1 >= i) ? dp[i][k - 1] : 0;
                long long right = (k + 1 <= j) ? dp[k + 1][j] : 0;
                best = min(best, span + left + right);
            }
            dp[i][j] = best;
        }
    }
    if (m == 0) return 0;
    return dp[1][m];
}

int main(int argc, char** argv) {
    unsigned seed = 12345u;
    int N = 2000;
    if (argc > 1) seed = (unsigned)strtoul(argv[1], nullptr, 10);
    if (argc > 2) N = atoi(argv[2]);
    mt19937 rng(seed);

    auto emit = [](int n, vector<int>& cuts, long long ans, string& out) {
        // inputs: {"n":"...","nums":"[...]"}
        out += "{\"inputs\": {\"n\": \"";
        out += to_string(n);
        out += "\", \"nums\": \"[";
        for (size_t i = 0; i < cuts.size(); i++) {
            if (i) out += ", ";
            out += to_string(cuts[i]);
        }
        out += "]\"}, \"expected\": \"";
        out += to_string(ans);
        out += "\"}\n";
    };

    string out;
    out.reserve(1 << 20);
    int produced = 0;

    // ---- Edge / fixed cases first ----
    vector<pair<int, vector<int>>> fixed;
    fixed.push_back({2, {1}});                       // min n, single cut
    fixed.push_back({7, {1,3,4,5}});                 // example 1 -> 16
    fixed.push_back({7, {1,3,6}});                   // example 2 -> 14
    fixed.push_back({6, {1,2,5}});                   // nowYourTurn
    fixed.push_back({10, {1,4,5,6,8}});              // case 3
    fixed.push_back({3, {1,2}});                     // small
    fixed.push_back({100000, {1}});                  // big n single cut
    fixed.push_back({100000, {99999}});              // big n cut near end
    {
        // big n, 100 cuts spread out
        vector<int> c; for (int i = 1; i <= 100; i++) c.push_back(i * 990 + 1);
        fixed.push_back({100000, c});
    }
    {
        // n where cuts.length == min(n-1,100) == n-1, all positions cut
        vector<int> c; for (int i = 1; i <= 50; i++) c.push_back(i);
        fixed.push_back({51, c});                    // n-1 = 50 cuts
    }

    for (auto& f : fixed) {
        int n = f.first;
        vector<int> cuts = f.second;
        long long ans = minCost(n, cuts);
        emit(n, cuts, ans, out);
        produced++;
    }

    // ---- Random cases ----
    while (produced < N) {
        // choose n. Mix of small and large.
        int n;
        int bucket = rng() % 10;
        if (bucket < 3) n = 2 + rng() % 20;          // small n
        else if (bucket < 6) n = 2 + rng() % 1000;   // medium
        else if (bucket < 9) n = 2 + rng() % 100000; // large up to 1e5
        else n = 100000;                             // exactly max
        if (n < 2) n = 2;
        if (n > 100000) n = 100000;

        int maxCuts = min(n - 1, 100);
        if (maxCuts < 1) continue;                   // shouldn't happen (n>=2)
        int m = 1 + rng() % maxCuts;                 // 1..maxCuts

        // pick m distinct values in [1, n-1]
        vector<int> cuts;
        if ((long long)m * 3 <= (long long)(n - 1) || (n - 1) <= 2000) {
            set<int> s;
            // if m close to available range, just take a sample
            int range = n - 1;                       // values 1..n-1
            if (m >= range) {
                for (int v = 1; v <= range && (int)cuts.size() < m; v++) cuts.push_back(v);
            } else {
                while ((int)s.size() < m) {
                    int v = 1 + rng() % range;
                    s.insert(v);
                }
                cuts.assign(s.begin(), s.end());
            }
        } else {
            // large range, sample distinct
            set<int> s;
            int range = n - 1;
            while ((int)s.size() < m) {
                int v = 1 + rng() % range;
                s.insert(v);
            }
            cuts.assign(s.begin(), s.end());
        }
        // shuffle order so cuts aren't always sorted (order shouldn't matter to answer)
        shuffle(cuts.begin(), cuts.end(), rng);

        long long ans = minCost(n, cuts);
        emit(n, cuts, ans, out);
        produced++;
    }

    fputs(out.c_str(), stdout);
    return 0;
}
