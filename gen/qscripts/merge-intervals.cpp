// Generator + reference oracle for "Merge Intervals" (Striver).
// starterCpp signature: vector<vector<int>> mergeIntervals(vector<vector<int>>& intervals)
// Param key: "intervals" (2D array). Output: merged intervals flattened to space-separated numbers.
//
// Constraints:
//   1 <= intervals.length <= 10^4
//   intervals[i].length == 2
//   0 <= start_i <= end_i <= 10^4
//
// Writes 2000 JSONL lines to the generated-tests path. To keep the file modest we cap
// the array length to a few hundred for most random cases while still covering edge sizes.
//
// Compile: clang++ -std=c++17 -O2 -w merge-intervals.cpp -o gen
// Run:     ./gen > merge-intervals.jsonl

#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <iostream>
#include <sstream>
using namespace std;

// ---- Reference oracle (standard sort + sweep) ----
vector<vector<int>> mergeIntervals(vector<vector<int>>& intervals) {
    int n = intervals.size();
    sort(intervals.begin(), intervals.end());
    vector<int> temp = intervals[0];
    vector<vector<int>> ans;
    for (auto& it : intervals) {
        if (it[0] <= temp[1]) {
            temp[1] = max(temp[1], it[1]);
        } else {
            ans.push_back(temp);
            temp = it;
        }
    }
    ans.push_back(temp);
    return ans;
}

string fmtIntervals(const vector<vector<int>>& v) {
    // "[[1,3],[2,6]]"
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ",";
        s += "[" + to_string(v[i][0]) + "," + to_string(v[i][1]) + "]";
    }
    s += "]";
    return s;
}

string fmtExpected(const vector<vector<int>>& v) {
    // Flatten to space-separated numbers on one line.
    string s;
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += " ";
        s += to_string(v[i][0]) + " " + to_string(v[i][1]);
    }
    return s;
}

int main(int argc, char** argv) {
    unsigned seed = 1234567u;
    if (argc > 1) seed = (unsigned)stoul(argv[1]);
    mt19937 rng(seed);

    const int VMAX = 10000;   // value cap per constraints
    const int TOTAL = 2000;

    auto randInt = [&](int lo, int hi) {
        uniform_int_distribution<int> d(lo, hi);
        return d(rng);
    };

    // Build a single random case with a given n and a value range cap (to control overlap density).
    auto makeCase = [&](int n, int cap) {
        vector<vector<int>> iv;
        iv.reserve(n);
        for (int i = 0; i < n; ++i) {
            int a = randInt(0, cap);
            int b = randInt(a, cap);   // ensures start <= end
            iv.push_back({a, b});
        }
        return iv;
    };

    for (int t = 0; t < TOTAL; ++t) {
        vector<vector<int>> iv;

        if (t == 0) {
            iv = {{1,3},{2,6},{8,10},{15,18}};          // example 1
        } else if (t == 1) {
            iv = {{1,4},{4,5}};                          // example 2 (touching)
        } else if (t == 2) {
            iv = {{0,0}};                                // min size, min values
        } else if (t == 3) {
            iv = {{VMAX,VMAX}};                          // single, max value
        } else if (t == 4) {
            iv = {{0,VMAX}};                             // covers whole range
        } else if (t == 5) {
            iv = {{1,4},{5,6}};                          // disjoint, no merge
        } else if (t == 6) {
            // many identical intervals
            int n = randInt(2, 50);
            int a = randInt(0, VMAX), b = randInt(a, VMAX);
            for (int i = 0; i < n; ++i) iv.push_back({a, b});
        } else if (t == 7) {
            // nested intervals -> all merge into outer
            iv = {{0,VMAX},{10,20},{500,600},{9000,9001}};
        } else if (t == 8) {
            // chain of touching intervals [0,1],[1,2],...
            int n = randInt(2, 200);
            for (int i = 0; i < n; ++i) iv.push_back({i, i+1});
        } else if (t % 7 == 0) {
            // dense overlap: small value cap so many merges
            int n = randInt(1, 300);
            iv = makeCase(n, randInt(5, 50));
        } else if (t % 7 == 1) {
            // sparse: large value cap, mostly disjoint
            int n = randInt(1, 300);
            iv = makeCase(n, VMAX);
        } else if (t % 11 == 0) {
            // large size near constraint-ish (kept to 1000 to keep file modest)
            int n = randInt(800, 2000);
            iv = makeCase(n, VMAX);
        } else {
            // general random
            int n = randInt(1, 400);
            iv = makeCase(n, randInt(50, VMAX));
        }

        // Defensive validity check (should always hold by construction).
        for (auto& it : iv) {
            if (it.size() != 2) { cerr << "bad interval size\n"; return 1; }
            if (!(0 <= it[0] && it[0] <= it[1] && it[1] <= VMAX)) {
                cerr << "constraint violation: [" << it[0] << "," << it[1] << "]\n";
                return 1;
            }
        }
        if (iv.empty() || (int)iv.size() > 10000) { cerr << "bad size\n"; return 1; }

        string inputStr = fmtIntervals(iv);
        vector<vector<int>> copy = iv;       // mergeIntervals sorts in place
        vector<vector<int>> res = mergeIntervals(copy);
        string expected = fmtExpected(res);

        // Emit JSONL. inputStr/expected contain only digits, brackets, commas, spaces -> JSON-safe.
        cout << "{\"inputs\": {\"intervals\": \"" << inputStr
             << "\"}, \"expected\": \"" << expected << "\"}\n";
    }
    return 0;
}
