// Generator + reference for "Sliding Window Maximum"
// Signature: vector<int> maxSlidingWindow(vector<int> &arr, int k)
// Constraints: 1 <= arr.length <= 1e5 ; -1e4 <= arr[i] <= 1e4 ; 1 <= k <= arr.length
//
// Writes 2000 JSONL cases to generated-tests/sliding-window-maximum.jsonl
// Build:  clang++ -std=c++17 -O2 -w sliding-window-maximum.cpp -o gen
// Run:    ./gen > /path/to/sliding-window-maximum.jsonl
#include <vector>
#include <string>
#include <deque>
#include <random>
#include <iostream>
#include <sstream>
using namespace std;

// ---- Reference (monotonic deque) ----
vector<int> maxSlidingWindow(vector<int> &arr, int k) {
    vector<int> res;
    deque<int> dq; // stores indices, decreasing values
    int n = (int)arr.size();
    for (int i = 0; i < n; i++) {
        if (!dq.empty() && dq.front() <= i - k) dq.pop_front();
        while (!dq.empty() && arr[dq.back()] <= arr[i]) dq.pop_back();
        dq.push_back(i);
        if (i >= k - 1) res.push_back(arr[dq.front()]);
    }
    return res;
}

string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

mt19937 rng(123456789u);
int randInt(int lo, int hi) {
    return uniform_int_distribution<int>(lo, hi)(rng);
}

void emit(vector<int> arr, int k) {
    vector<int> out = maxSlidingWindow(arr, k);
    cout << "{\"inputs\": {\"arr\": \"" << vecToStr(arr)
         << "\", \"k\": \"" << k << "\"}, \"expected\": \""
         << vecToStr(out) << "\"}\n";
}

int main() {
    int total = 2000;
    int produced = 0;

    // ---- Edge / fixed cases ----
    // example cases
    { vector<int> a = {4,0,-1,3,5,3,6,8}; emit(a,3); produced++; }
    { vector<int> a = {20,25}; emit(a,2); produced++; }
    { vector<int> a = {1,3,-1,-3,5,3,6,7}; emit(a,3); produced++; }
    // min size n=1, k=1
    { vector<int> a = {0}; emit(a,1); produced++; }
    { vector<int> a = {10000}; emit(a,1); produced++; }
    { vector<int> a = {-10000}; emit(a,1); produced++; }
    // k == n (single window)
    { vector<int> a = {-10000, 10000, 0, -5, 7}; emit(a,5); produced++; }
    // all same value
    { vector<int> a(10, 7); emit(a,4); produced++; }
    // strictly increasing
    { vector<int> a; for(int i=-5;i<=5;i++) a.push_back(i); emit(a,3); produced++; }
    // strictly decreasing
    { vector<int> a; for(int i=5;i>=-5;i--) a.push_back(i); emit(a,3); produced++; }
    // extremes alternating
    { vector<int> a = {10000,-10000,10000,-10000,10000,-10000}; emit(a,2); produced++; }
    // k=1 over a few values
    { vector<int> a = {3,-2,5,-1,4}; emit(a,1); produced++; }

    // ---- Random small cases (good coverage of window positions) ----
    while (produced < total) {
        // mix of size regimes
        int r = randInt(0, 99);
        int n;
        if (r < 60) n = randInt(1, 30);          // small
        else if (r < 90) n = randInt(31, 300);   // medium
        else n = randInt(301, 2000);             // larger (keep value diversity manageable)

        // value range regimes
        int lo, hi;
        int vr = randInt(0, 99);
        if (vr < 50) { lo = -10; hi = 10; }       // many duplicates -> stress deque popping
        else if (vr < 80) { lo = -100; hi = 100; }
        else { lo = -10000; hi = 10000; }         // full range

        vector<int> a(n);
        for (int i = 0; i < n; i++) a[i] = randInt(lo, hi);

        int k = randInt(1, n);
        emit(a, k);
        produced++;
    }

    return 0;
}
