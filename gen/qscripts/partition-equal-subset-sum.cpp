// Generator + reference oracle for "Partition equal subset sum"
// Signature: bool equalPartition(int n, vector<int> arr)
// Constraints: 1 <= n <= 100 ; 1 <= arr[i] <= 1000 ; n*sum <= 1e5
// Output format: "True"/"False" (matches examples)
// Emits 2000 lines of {"inputs":{"arr":"[..]"},"expected":"True|False"}
#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <random>
#include <numeric>
using namespace std;

// ---- reference (subset-sum target = total/2) ----
bool equalPartition(int n, vector<int> arr) {
    long long tot = 0;
    for (int x : arr) tot += x;
    if (tot % 2) return false;
    long long target = tot / 2;
    // target <= sum <= 1e5/n <= 1e5, fits in vector<bool>
    vector<char> dp(target + 1, 0);
    dp[0] = 1;
    for (int i = 0; i < n; i++) {
        int a = arr[i];
        for (long long j = target; j >= a; j--)
            if (dp[j - a]) dp[j] = 1;
    }
    return dp[target] != 0;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); i++) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

int main() {
    mt19937 rng(987654321u);

    vector<vector<int>> cases;

    // ---- explicit edge cases ----
    cases.push_back({1});                 // n=1, odd sum -> false
    cases.push_back({2});                 // n=1, even but single -> false (can't split)
    cases.push_back({1000});              // max single value
    cases.push_back({1, 1});              // -> true
    cases.push_back({1, 2});              // odd -> false
    cases.push_back({1000, 1000});        // -> true
    cases.push_back({1, 10, 21, 10});     // example1 -> true
    cases.push_back({1, 2, 3, 5});        // example2 -> false
    cases.push_back({2, 2, 1, 1});        // nowYourTurn -> true (sum6, target3)
    // max n=100 all ones (sum=100, n*sum=10000 ok) -> even count -> true
    {
        vector<int> v(100, 1);
        cases.push_back(v);
    }
    // n=100 with value mix near n*sum bound: n=100 -> sum<=1000 -> avg<=10
    {
        vector<int> v(100, 10); // sum=1000, n*sum=100000 = 1e5 exactly OK
        cases.push_back(v);
    }
    // n=99 all ones -> odd sum -> false
    {
        vector<int> v(99, 1);
        cases.push_back(v);
    }

    // ---- random cases respecting n*sum <= 1e5 ----
    const long long LIMIT = 100000;
    while ((int)cases.size() < 2000) {
        int n = 1 + (int)(rng() % 100); // 1..100
        long long maxSum = LIMIT / n;   // sum must satisfy n*sum <= 1e5
        if (maxSum < 1) continue;       // n>1e5 impossible here since n<=100
        // each arr[i] >= 1 so sum >= n; need maxSum >= n
        if (maxSum < n) continue;
        // budget for "extra" above the mandatory 1 per element
        long long extraBudget = maxSum - n; // distribute extra (each up to 999)
        vector<int> a(n, 1);
        // distribute random extra across elements without exceeding per-elem 999 and total budget
        long long remaining = extraBudget;
        // To keep variety, cap how much we actually use sometimes
        long long useBudget = (long long)(rng() % (extraBudget + 1));
        remaining = useBudget;
        // random assignment
        for (int i = 0; i < n && remaining > 0; i++) {
            long long room = min<long long>(999, remaining);
            long long add = (long long)(rng() % (room + 1));
            a[i] += (int)add;
            remaining -= add;
        }
        // shuffle to avoid front-loading
        for (int i = n - 1; i > 0; i--) {
            int j = (int)(rng() % (i + 1));
            swap(a[i], a[j]);
        }
        // safety re-check constraints
        long long s = accumulate(a.begin(), a.end(), 0LL);
        bool ok = (n >= 1 && n <= 100);
        for (int x : a) if (x < 1 || x > 1000) ok = false;
        if ((long long)n * s > LIMIT) ok = false;
        if (!ok) continue;
        cases.push_back(a);
    }

    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/partition-equal-subset-sum.jsonl");
    int trueCount = 0;
    for (auto& a : cases) {
        int n = (int)a.size();
        bool res = equalPartition(n, a);
        if (res) trueCount++;
        out << "{\"inputs\": {\"arr\": \"" << arrToStr(a) << "\"}, \"expected\": \""
            << (res ? "True" : "False") << "\"}\n";
    }
    out.close();
    cerr << "wrote " << cases.size() << " cases, true=" << trueCount << "\n";
    return 0;
}
