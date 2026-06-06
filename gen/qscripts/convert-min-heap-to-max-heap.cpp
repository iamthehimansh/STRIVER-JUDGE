// Generator for "Convert Min Heap to Max Heap"
// - Builds VALID random min-heaps (input) within constraints.
// - Converts each to a max-heap using the SAME deterministic algorithm
//   used by the submitted class Solution (build-max-heap, heapify down).
// - Emits generated-tests/convert-min-heap-to-max-heap.jsonl
#include <vector>
#include <string>
#include <random>
#include <iostream>
#include <fstream>
#include <algorithm>
using namespace std;

// ---- min-heapify (to produce a VALID min-heap input) ----
static void minHeapify(vector<int>& a, int node) {
    int n = (int)a.size();
    while (true) {
        int l = 2*node+1, r = 2*node+2, small = node;
        if (l < n && a[l] < a[small]) small = l;
        if (r < n && a[r] < a[small]) small = r;
        if (small == node) break;
        swap(a[node], a[small]);
        node = small;
    }
}
static void buildMinHeap(vector<int>& a) {
    for (int i = (int)a.size()/2 - 1; i >= 0; i--) minHeapify(a, i);
}

// ---- REFERENCE: convert min-heap to max-heap (deterministic) ----
// Exactly mirrors the submitted class Solution.
static void maxHeapify(vector<int>& a, int node) {
    int n = (int)a.size();
    int l = 2*node+1, r = 2*node+2, largest = node;
    if (l < n && a[l] > a[largest]) largest = l;
    if (r < n && a[r] > a[largest]) largest = r;
    if (largest != node) {
        swap(a[node], a[largest]);
        maxHeapify(a, largest);
    }
}
static vector<int> minToMaxHeap(vector<int> nums) {
    for (int i = (int)nums.size()/2 - 1; i >= 0; i--) maxHeapify(nums, i);
    return nums;
}

static string arrStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/convert-min-heap-to-max-heap.jsonl";
    if (argc > 1) outPath = argv[1];
    int N = 2000;
    if (argc > 2) N = atoi(argv[2]);

    mt19937 rng(12345);
    const int LO = -10000, HI = 10000;
    uniform_int_distribution<int> valDist(LO, HI);

    ofstream out(outPath);
    if (!out) { cerr << "cannot open " << outPath << "\n"; return 1; }

    auto emit = [&](vector<int> raw) {
        buildMinHeap(raw);                  // make it a valid min-heap (input)
        vector<int> exp = minToMaxHeap(raw);// reference output
        out << "{\"inputs\": {\"nums\": \"" << arrStr(raw)
            << "\"}, \"expected\": \"" << arrStr(exp) << "\"}\n";
    };

    int produced = 0;

    // The judge captures the batched run's stdout with a 256 KB cap (one output
    // line per case). To keep ALL 2000 lines within budget we keep arrays small;
    // a few moderately large cases still exercise the upper-bound logic without
    // blowing the stdout budget.

    // ---- Deterministic edge cases first ----
    // size 1, extremes
    { vector<int> v = {0}; emit(v); produced++; }
    { vector<int> v = {-10000}; emit(v); produced++; }
    { vector<int> v = {10000}; emit(v); produced++; }
    // all equal
    for (int n : {1,2,3,5,8,16,31}) { vector<int> v(n, 7); emit(v); produced++; }
    for (int n : {2,4,7,10}) { vector<int> v(n, -10000); emit(v); produced++; }
    for (int n : {2,4,7,10}) { vector<int> v(n, 10000); emit(v); produced++; }
    // value-bound extremes mixed in small arrays
    { vector<int> v = {-10000, 10000, 0, 9999, -9999}; emit(v); produced++; }
    { vector<int> v = {10000, 10000, 10000}; emit(v); produced++; }
    { vector<int> v = {-10000, -10000, -10000, -10000}; emit(v); produced++; }
    // strictly increasing (already a min-heap)
    for (int n : {2,3,5,10,30,60}) {
        vector<int> v(n);
        for (int i = 0; i < n; ++i) v[i] = -10000 + i;
        emit(v); produced++;
    }
    // strictly decreasing values placed then min-heapified
    for (int n : {3,7,15,31}) {
        vector<int> v(n);
        for (int i = 0; i < n; ++i) v[i] = 10000 - i;
        emit(v); produced++;
    }
    // the two dataset examples (sanity)
    { vector<int> v = {10,20,30,21,23}; emit(v); produced++; }
    { vector<int> v = {-5,-4,-3,-2,-1}; emit(v); produced++; }
    // a few moderately large cases (upper-bound exercise, output stays small enough)
    { vector<int> v(200);  for (auto& x : v) x = valDist(rng); emit(v); produced++; }
    { vector<int> v(150);  for (auto& x : v) x = valDist(rng); emit(v); produced++; }
    { vector<int> v(100);  for (auto& x : v) x = valDist(rng); emit(v); produced++; }
    { vector<int> v(100);  for (auto& x : v) x = uniform_int_distribution<int>(-3,3)(rng); emit(v); produced++; }

    // ---- Random cases, mostly small sizes to respect the stdout budget ----
    while (produced < N) {
        int bucket = produced % 20;
        int n;
        if (bucket < 10)      n = uniform_int_distribution<int>(1, 12)(rng);
        else if (bucket < 17) n = uniform_int_distribution<int>(1, 30)(rng);
        else if (bucket < 19) n = uniform_int_distribution<int>(30, 60)(rng);
        else                  n = uniform_int_distribution<int>(60, 100)(rng);

        vector<int> v(n);
        // vary the value distribution to mix duplicates and full-range values
        int mode = produced % 4;
        for (int i = 0; i < n; ++i) {
            if (mode == 0) v[i] = valDist(rng);
            else if (mode == 1) v[i] = uniform_int_distribution<int>(-5, 5)(rng);
            else if (mode == 2) v[i] = uniform_int_distribution<int>(-10000, -9990)(rng);
            else v[i] = uniform_int_distribution<int>(9990, 10000)(rng);
        }
        emit(v);
        produced++;
    }

    out.close();
    cerr << "wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
