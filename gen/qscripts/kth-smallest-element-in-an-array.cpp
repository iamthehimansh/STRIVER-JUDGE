#include <vector>
#include <queue>
#include <algorithm>
#include <random>
#include <cstdio>
#include <cstdint>
#include <string>
#include <iostream>
using namespace std;

// ---- Reference oracle ----
// GFG: Kth smallest element in an array.
// Constraints: 1 <= N <= 1e5, 1 <= arr[i] <= 1e5, 1 <= k <= N.
// Returns the kth smallest (1-indexed) element.
int kthSmallest(vector<int>& arr, int k) {
    // max-heap of size k
    priority_queue<int> pq;
    for (int i = 0; i < (int)arr.size(); i++) {
        pq.push(arr[i]);
        if ((int)pq.size() > k) pq.pop();
    }
    return pq.top();
}

// brute-force cross-check
int kthSmallestBrute(vector<int> arr, int k) {
    sort(arr.begin(), arr.end());
    return arr[k - 1];
}

static string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); i++) {
        s += to_string(a[i]);
        if (i + 1 < a.size()) s += ", ";
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    // self-test on known examples
    {
        vector<int> e1 = {7,10,4,3,20,15};
        if (kthSmallest(e1, 3) != 7) { fprintf(stderr, "SELFTEST FAIL e1 k3\n"); return 2; }
        if (kthSmallest(e1, 4) != 10) { fprintf(stderr, "SELFTEST FAIL e1 k4\n"); return 2; }
        vector<int> e2 = {7,10,4,20,15};
        if (kthSmallest(e2, 4) != 15) { fprintf(stderr, "SELFTEST FAIL e2 k4\n"); return 2; }
        fprintf(stderr, "SELFTEST OK\n");
    }
    if (argc > 1 && string(argv[1]) == "--selftest") return 0;

    uint64_t seed = 12345;
    int N = 2000;
    FILE* f = fopen(argv[1], "w");
    if (!f) { fprintf(stderr, "cannot open output\n"); return 1; }

    mt19937_64 rng(seed);

    auto emit = [&](const vector<int>& arr, int k) {
        int ref = kthSmallest((vector<int>&)arr, k);
        int bru = kthSmallestBrute(arr, k);
        if (ref != bru) { fprintf(stderr, "MISMATCH ref=%d brute=%d\n", ref, bru); exit(3); }
        string line = "{\"inputs\": {\"arr\": \"" + arrToStr(arr) + "\", \"k\": \"" + to_string(k) + "\"}, \"expected\": \"" + to_string(ref) + "\"}\n";
        fputs(line.c_str(), f);
    };

    int count = 0;

    // ---- Edge cases ----
    // single element, k=1
    emit({1}, 1);
    emit({100000}, 1);
    emit({50000}, 1);
    count += 3;

    // k = 1 (min), k = N (max), with a small array
    {
        vector<int> a = {7,10,4,3,20,15};
        emit(a, 1); emit(a, 3); emit(a, 4); emit(a, 6);
        count += 4;
    }
    // all equal elements
    {
        vector<int> a(50, 7);
        emit(a, 1); emit(a, 25); emit(a, 50);
        count += 3;
    }
    // extremes: all min value
    {
        vector<int> a(100, 1);
        emit(a, 1); emit(a, 100);
        count += 2;
    }
    // all max value
    {
        vector<int> a(100, 100000);
        emit(a, 1); emit(a, 100);
        count += 2;
    }
    // sorted ascending
    {
        vector<int> a; for (int i = 1; i <= 200; i++) a.push_back(i);
        emit(a, 1); emit(a, 100); emit(a, 200);
        count += 3;
    }
    // sorted descending
    {
        vector<int> a; for (int i = 200; i >= 1; i--) a.push_back(i);
        emit(a, 1); emit(a, 100); emit(a, 200);
        count += 3;
    }

    // ---- Random cases until we hit 2000 total ----
    while (count < N) {
        // mix of sizes; cap at 1e5 but bias toward smaller for file size
        int sizeBucket = rng() % 100;
        int n;
        if (sizeBucket < 60) n = (int)(rng() % 50) + 1;        // 1..50
        else if (sizeBucket < 90) n = (int)(rng() % 500) + 1;  // 1..500
        else n = (int)(rng() % 5000) + 1;                      // 1..5000

        // value range bucket: sometimes narrow (forces duplicates), sometimes full
        int vmaxBucket = rng() % 3;
        int vmax;
        if (vmaxBucket == 0) vmax = 10;          // many duplicates
        else if (vmaxBucket == 1) vmax = 1000;
        else vmax = 100000;                       // full range

        vector<int> arr(n);
        for (int i = 0; i < n; i++) {
            arr[i] = (int)(rng() % vmax) + 1;     // 1..vmax  (>=1, <=1e5)
        }
        int k = (int)(rng() % n) + 1;             // 1..n
        emit(arr, k);
        count++;
    }

    fclose(f);
    fprintf(stderr, "WROTE %d cases\n", count);
    return 0;
}
