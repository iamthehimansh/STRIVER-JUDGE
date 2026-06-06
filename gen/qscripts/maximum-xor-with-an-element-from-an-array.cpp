// Generator + reference for: Maximum Xor with an element from an array
// Reference: brute force per query (correct by definition).
// For each query [x, m]: answer = max over nums[j] <= m of (nums[j] XOR x), else -1.
//
// Generates random inputs strictly within constraints:
//   1 <= nums.length, queries.length <= 1e5  (kept small here for speed)
//   queries[i].length == 2
//   0 <= nums[i], x_i, m_i <= 1e9
//
// Outputs JSONL to the generated-tests path.
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run: ./gen > out.jsonl   (or it writes directly)

#include <cstdio>
#include <cstdlib>
#include <cstdint>
#include <vector>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
using namespace std;

static const long long VMAX = 1000000000LL; // 1e9

// Reference oracle (brute force).
vector<long long> solve(const vector<long long>& nums, const vector<pair<long long,long long>>& queries) {
    vector<long long> ans;
    ans.reserve(queries.size());
    for (auto& q : queries) {
        long long x = q.first, m = q.second;
        long long best = -1;
        for (long long v : nums) {
            if (v <= m) {
                long long xr = v ^ x;
                if (xr > best) best = xr;
            }
        }
        ans.push_back(best);
    }
    return ans;
}

string fmtArr(const vector<long long>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

string fmtQueries(const vector<pair<long long,long long>>& q) {
    string s = "[";
    for (size_t i = 0; i < q.size(); ++i) {
        if (i) s += ", ";
        s += "[" + to_string(q[i].first) + ", " + to_string(q[i].second) + "]";
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    long long seed = 12345;
    int N = 2000;
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/maximum-xor-with-an-element-from-an-array.jsonl";
    if (argc > 1) N = atoi(argv[1]);
    if (argc > 2) seed = atoll(argv[2]);
    if (argc > 3) outPath = argv[3];

    mt19937_64 rng(seed);

    ofstream out(outPath);
    if (!out) { fprintf(stderr, "cannot open out\n"); return 1; }

    auto randVal = [&](long long lo, long long hi) -> long long {
        uniform_int_distribution<long long> d(lo, hi);
        return d(rng);
    };

    for (int tc = 0; tc < N; ++tc) {
        // Decide sizes. Keep small for fast brute-force, but cover edges.
        int n, qn;
        int kind = tc % 50;
        if (tc == 0) { n = 1; qn = 1; }              // min size
        else if (tc == 1) { n = 1; qn = 5; }
        else if (tc == 2) { n = 5; qn = 1; }
        else if (kind < 5)  { n = (int)randVal(1, 3);  qn = (int)randVal(1, 3); }
        else if (kind < 40) { n = (int)randVal(1, 30); qn = (int)randVal(1, 30); }
        else                { n = (int)randVal(1, 60); qn = (int)randVal(1, 60); }

        // Choose value ranges. Mix small-range (more collisions / m boundaries hit)
        // and full-range values to exercise XOR bits up to 1e9.
        long long vhi;
        int rk = (int)randVal(0, 4);
        if (rk == 0) vhi = randVal(0, 5);            // tiny values incl 0
        else if (rk == 1) vhi = randVal(0, 20);
        else if (rk == 2) vhi = randVal(0, 1000);
        else if (rk == 3) vhi = randVal(0, 1000000);
        else vhi = VMAX;                             // full range

        vector<long long> nums(n);
        for (int i = 0; i < n; ++i) nums[i] = randVal(0, vhi);

        // ensure some edge: occasionally include 0 and VMAX
        if (tc % 7 == 0 && n > 0) nums[0] = 0;
        if (tc % 11 == 0 && n > 0) nums[n-1] = VMAX;

        vector<pair<long long,long long>> queries(qn);
        for (int i = 0; i < qn; ++i) {
            long long x = randVal(0, (rk == 4 ? VMAX : max(1LL, vhi)));
            long long m;
            int mk = (int)randVal(0, 6);
            if (mk == 0) m = 0;                       // boundary low (often -1 paths)
            else if (mk == 1) m = VMAX;               // everything allowed
            else if (mk == 2) m = randVal(0, vhi);    // around value range
            else if (mk == 3) m = (n>0 ? nums[randVal(0,n-1)] : 0); // equal to some element
            else m = randVal(0, VMAX);
            queries[i] = {x, m};
        }

        vector<long long> ans = solve(nums, queries);

        out << "{\"inputs\": {\"nums\": \"" << fmtArr(nums)
            << "\", \"queries\": \"" << fmtQueries(queries)
            << "\"}, \"expected\": \"" << fmtArr(ans) << "\"}\n";
    }
    out.close();
    fprintf(stderr, "wrote %d cases to %s\n", N, outPath.c_str());
    return 0;
}
