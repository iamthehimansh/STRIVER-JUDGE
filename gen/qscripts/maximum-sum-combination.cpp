// Generator + reference oracle for "Maximum Sum Combination" (slug: maximum-sum-combination)
//
// Problem: Given nums1, nums2 (size n each) and k, return the maximum k valid
// sum combinations (one element from nums1 + one from nums2, by index pair) in
// non-increasing order.
//
// Constraints:
//   n == size of nums1 & nums2,  1 <= n <= 1e5
//   1 <= each element of nums1 & nums2 <= 1e4
//   1 <= k <= n*n
//
// Reference verified against dataset examples:
//   nums1=[7,3], nums2=[1,6], k=2 -> [13, 9]
//   nums1=[3,4,5], nums2=[2,6,3], k=2 -> [11, 10]
//
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/maximum-sum-combination.jsonl
//   Each line: {"inputs": {"nums1": "[...]", "nums2": "[...]", "k": "N"}, "expected": "[a, b, ...]"}
//
// Note on output size: k can be as large as n*n, but the answer vector then has
// k entries which would make each line huge. To keep the file modest we cap k so
// the answer length stays bounded, while still exercising the full structural
// constraint space (small n with k = n*n, larger n with moderate k, value extremes).

#include <algorithm>
#include <iostream>
#include <fstream>
#include <vector>
#include <queue>
#include <random>
#include <string>
using namespace std;

// ---- Reference oracle (index-pair semantics; duplicates of same value allowed) ----
vector<int> maxSumCombinations(vector<int> A, vector<int> B, int K) {
    int N = (int)A.size();
    sort(A.begin(), A.end());
    sort(B.begin(), B.end());
    // max-heap on sum; each state is (i in A, j in B). Start every i paired with last j.
    priority_queue<pair<int, pair<int,int>>> pq;
    for (int i = 0; i < N; i++) pq.push({A[i] + B[N-1], {i, N-1}});
    vector<int> ans;
    while (!pq.empty() && K--) {
        auto it = pq.top(); pq.pop();
        int data = it.first;
        int x = it.second.first;
        int y = it.second.second;
        ans.push_back(data);
        if (y != 0) pq.push({A[x] + B[y-1], {x, y-1}});
    }
    return ans;
}

string arrToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        s += to_string(v[i]);
        if (i + 1 < v.size()) s += ", ";
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    const char* OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/maximum-sum-combination.jsonl";
    int TOTAL = 2000;
    if (argc > 1) TOTAL = atoi(argv[1]);

    mt19937 rng(12345);
    ofstream out(OUT);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    // To keep output lines modest, cap k by a budget on the answer length.
    const int K_CAP = 200;     // never emit more than this many answers per case
    const int VAL_MIN = 1, VAL_MAX = 10000;

    int produced = 0;

    auto emit = [&](vector<int>& a, vector<int>& b, int k) {
        // clamp k to valid range [1, n*n] and to K_CAP for output size
        int n = (int)a.size();
        long long maxK = (long long)n * (long long)n;
        if (k < 1) k = 1;
        if (k > maxK) k = (int)maxK;
        if (k > K_CAP) k = K_CAP;
        vector<int> exp = maxSumCombinations(a, b, k);
        out << "{\"inputs\": {\"nums1\": \"" << arrToStr(a)
            << "\", \"nums2\": \"" << arrToStr(b)
            << "\", \"k\": \"" << k << "\"}, \"expected\": \""
            << arrToStr(exp) << "\"}\n";
        produced++;
    };

    auto randVal = [&]() { return (int)(rng() % (VAL_MAX - VAL_MIN + 1)) + VAL_MIN; };

    // ---------- Hand-crafted edge cases ----------
    {
        // dataset examples
        vector<int> a = {7,3}, b = {1,6}; emit(a,b,2);
        a = {3,4,5}; b = {2,6,3}; emit(a,b,2);
        // n=1 (min size), k must be 1
        a = {1}; b = {1}; emit(a,b,1);
        a = {10000}; b = {10000}; emit(a,b,1);
        a = {1}; b = {10000}; emit(a,b,1);
        // all equal values
        a = {2,2}; b = {5,5}; emit(a,b,2);
        a = {5,5,5}; b = {5,5,5}; emit(a,b,9); // k = n*n
        // value extremes mixed
        a = {1,10000,1,10000}; b = {10000,1,10000,1}; emit(a,b,16); // k = n*n
        // small n, k = n*n
        a = {3,1,2}; b = {6,4,5}; emit(a,b,9);
        // k = 1 only top
        a = {1,2,3,4,5}; b = {5,4,3,2,1}; emit(a,b,1);
    }

    // ---------- Tiny random cases: n in [1..10], k up to n*n (full range, capped by K_CAP) ----------
    while (produced < 400) {
        int n = 1 + (int)(rng() % 10);
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = randVal();
        for (int i = 0; i < n; i++) b[i] = randVal();
        long long maxK = (long long)n * n;
        int k = 1 + (int)(rng() % (long long)min<long long>(maxK, K_CAP));
        emit(a, b, k);
    }

    // ---------- Small random cases: n in [2..50] ----------
    while (produced < 1000) {
        int n = 2 + (int)(rng() % 49);
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = randVal();
        for (int i = 0; i < n; i++) b[i] = randVal();
        long long maxK = (long long)n * n;
        int hi = (int)min<long long>(maxK, K_CAP);
        int k = 1 + (int)(rng() % hi);
        emit(a, b, k);
    }

    // ---------- Medium random cases: n in [50..500] ----------
    while (produced < 1700) {
        int n = 50 + (int)(rng() % 451);
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = randVal();
        for (int i = 0; i < n; i++) b[i] = randVal();
        // k anywhere in [1, K_CAP] (well within n*n for these n)
        int k = 1 + (int)(rng() % K_CAP);
        emit(a, b, k);
    }

    // ---------- Larger random cases: n in [500..3000] ----------
    while (produced < 1900) {
        int n = 500 + (int)(rng() % 2501);
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = randVal();
        for (int i = 0; i < n; i++) b[i] = randVal();
        int k = 1 + (int)(rng() % K_CAP);
        emit(a, b, k);
    }

    // ---------- A few max-constraint cases: n up to 1e5 (kept few to bound file size) ----------
    // These exercise the upper bound n=1e5 with small k. Keep the count low so the
    // .jsonl stays a reasonable size (each such input line is ~1MB).
    while (produced < TOTAL) {
        int n;
        int idx = produced - 1900; // 0..99
        if (idx == 0) n = 100000;            // exact max
        else if (idx == 1) n = 100000;       // another at max with different values
        else n = 5000 + (int)(rng() % 25001); // up to ~30000
        vector<int> a(n), b(n);
        for (int i = 0; i < n; i++) a[i] = randVal();
        for (int i = 0; i < n; i++) b[i] = randVal();
        int k = 1 + (int)(rng() % K_CAP);
        emit(a, b, k);
    }

    out.close();
    cerr << "produced " << produced << " cases\n";
    return 0;
}
