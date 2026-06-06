// Generator + reference for "Number of Greater Elements to the Right"
//
// Problem: given arr[] (length n) and indices[] (queries), for each query i
// count elements strictly greater than arr[indices[i]] appearing to the right
// of position indices[i]. Return array of answers (one per query).
//
// Constraints:
//   1 <= n <= 10^4
//   1 <= arr[i] <= 10^5
//   1 <= number of queries <= 100
//   0 <= indices[i] <= n - 1
//
// Signature (starterCpp):
//   vector<int> count_NGE(vector<int> &arr, vector<int> &indices)
//
// Writes 2000 JSONL lines to the generated-tests path. One object per line:
//   {"inputs": {"arr": "[...]", "indices": "[...]"}, "expected": "[...]"}
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:     ./gen

#include <vector>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
#include <sstream>
using namespace std;

// ---- Reference (ground-truth oracle) ----
vector<int> count_NGE(vector<int> &arr, vector<int> &indices) {
    vector<int> ans;
    int n = (int)arr.size();
    for (int idx : indices) {
        int cnt = 0;
        int v = arr[idx];
        for (int j = idx + 1; j < n; ++j) {
            if (arr[j] > v) ++cnt;
        }
        ans.push_back(cnt);
    }
    return ans;
}

static string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// expected formatting: space-separated numbers on one line (judge is lenient)
static string expectedStr(const vector<int>& v) {
    string s;
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += " ";
        s += to_string(v[i]);
    }
    return s;
}

int main() {
    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-greater-elements-to-the-right.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    mt19937 rng(123456789u);
    auto randInt = [&](int lo, int hi) {
        return uniform_int_distribution<int>(lo, hi)(rng);
    };

    const int TOTAL = 2000;

    // --- a handful of deterministic edge cases first ---
    vector<pair<vector<int>, vector<int>>> seeds;
    // dataset examples
    seeds.push_back({{3,4,2,7,5,8,10,6}, {0,5}});
    seeds.push_back({{1,2,3,4,1}, {0,3}});
    seeds.push_back({{10,3,6,1,8,2}, {1,2,4}});
    // n = 1, min size
    seeds.push_back({{1}, {0}});
    seeds.push_back({{100000}, {0}});
    // all equal (strictly greater => 0)
    seeds.push_back({{5,5,5,5}, {0,1,2,3}});
    // strictly increasing
    seeds.push_back({{1,2,3,4,5,6,7,8,9,10}, {0,4,9}});
    // strictly decreasing
    seeds.push_back({{10,9,8,7,6,5,4,3,2,1}, {0,4,9}});
    // value extremes
    seeds.push_back({{1,100000,1,100000,1}, {0,1,4}});
    // last index query (always 0)
    seeds.push_back({{7,3,9,2}, {3}});

    int written = 0;
    auto emit = [&](vector<int> arr, vector<int> indices) {
        vector<int> exp = count_NGE(arr, indices);
        out << "{\"inputs\": {\"arr\": \"" << vecToStr(arr)
            << "\", \"indices\": \"" << vecToStr(indices)
            << "\"}, \"expected\": \"" << expectedStr(exp) << "\"}\n";
        ++written;
    };

    for (auto& s : seeds) {
        if (written >= TOTAL) break;
        emit(s.first, s.second);
    }

    // --- random cases ---
    while (written < TOTAL) {
        // choose n: bias toward small for variety, occasionally large
        int n;
        int roll = randInt(0, 99);
        if (roll < 60)       n = randInt(1, 50);
        else if (roll < 85)  n = randInt(50, 500);
        else if (roll < 97)  n = randInt(500, 3000);
        else                 n = randInt(3000, 10000);

        // value range: sometimes narrow (forces ties), sometimes full
        int vmax;
        int vr = randInt(0, 99);
        if (vr < 30)      vmax = randInt(1, 5);     // many ties
        else if (vr < 70) vmax = randInt(1, 1000);
        else              vmax = 100000;            // full range

        vector<int> arr(n);
        for (int i = 0; i < n; ++i) arr[i] = randInt(1, vmax);

        // number of queries: 1..min(100, ...). Constraint says 1<=queries<=100.
        int q = randInt(1, 100);
        vector<int> indices(q);
        for (int i = 0; i < q; ++i) indices[i] = randInt(0, n - 1);

        emit(arr, indices);
    }

    out.close();
    cerr << "wrote " << written << " cases to " << outPath << "\n";
    return 0;
}
