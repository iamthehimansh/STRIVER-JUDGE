// Generator + reference oracle for Striver problem "4 Sum" (slug: 4-sum)
//
// Reference solution (sorted two-pointer, O(n^3)) taken from
//   /Users/iamthehimansh/Downloads/ref2/4 sum.cpp
// Verified against the dataset's example outputs.
//
// This single binary:
//   - generates random `nums` arrays + `target` strictly within constraints
//     (1 <= n <= 200, -1e4 <= nums[i] <= 1e4, -1e4 <= target <= 1e4),
//   - includes edge cases (n=1, extremes, all-equal, target-rich arrays),
//   - computes the correct expected output with the reference,
//   - emits ONE JSON object per line to stdout:
//       {"inputs": {"nums": "[...]", "target": "7"}, "expected": "<flattened>"}
//
// Build:  clang++ -std=c++17 -O2 -w -o gen4sum 4-sum.cpp
// Run:    ./gen4sum <numCases> <seed> > 4-sum.jsonl
//
// Output formatting:
//   nums     -> "[a, b, c]" (matches dataset example style)
//   target   -> "7"
//   expected -> all quadruplet numbers, sorted, flattened to one
//               space-separated line. Empty result -> "" (judge is lenient,
//               ignoring brackets/commas/whitespace).

#include <algorithm>
#include <cstdint>
#include <iostream>
#include <random>
#include <sstream>
#include <string>
#include <vector>

using namespace std;

// ---- Reference oracle (from ref2/4 sum.cpp) ----
static vector<vector<int>> fourSum(vector<int> nums, int target) {
    int n = nums.size();
    vector<vector<int>> ans;
    sort(nums.begin(), nums.end());
    for (int i = 0; i < n; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        for (int j = i + 1; j < n; j++) {
            if (j > i + 1 && nums[j] == nums[j - 1]) continue;
            int k = j + 1;
            int l = n - 1;
            while (k < l) {
                long long sum = (long long)nums[i] + nums[j];
                sum += (long long)nums[k] + nums[l];
                if (sum == (long long)target) {
                    ans.push_back({nums[i], nums[j], nums[k], nums[l]});
                    k++;
                    l--;
                    while (k < l && nums[k] == nums[k - 1]) k++;
                    while (k < l && nums[l] == nums[l + 1]) l--;
                } else if (sum < (long long)target) {
                    k++;
                } else {
                    l--;
                }
            }
        }
    }
    return ans;
}

// ---- formatting helpers ----
static string arrToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// Flatten quadruplets to one space-separated line, deterministically sorted
// (each quadruplet already ascending from the reference; sort the list too).
static string expectedStr(vector<vector<int>> quads) {
    sort(quads.begin(), quads.end());
    string s;
    for (size_t i = 0; i < quads.size(); i++) {
        for (size_t j = 0; j < quads[i].size(); j++) {
            if (!s.empty()) s += " ";
            s += to_string(quads[i][j]);
        }
    }
    return s;
}

static string jsonEscape(const string& in) {
    string out;
    for (char c : in) {
        if (c == '"' || c == '\\') out += '\\';
        out += c;
    }
    return out;
}

int main(int argc, char** argv) {
    long long numCases = (argc > 1) ? stoll(argv[1]) : 2000;
    uint64_t seed = (argc > 2) ? stoull(argv[2]) : 12345ULL;
    mt19937_64 rng(seed);

    const int LO = -10000, HI = 10000;

    // Curated edge cases first (must respect constraints).
    vector<pair<vector<int>, int>> edge;
    edge.push_back({{1, -2, 3, 5, 7, 9}, 7});            // example 1
    edge.push_back({{7, -7, 1, 2, 14, 3}, 9});           // example 2
    edge.push_back({{1, 1, 3, 4, -3}, 5});               // nowYourTurn
    edge.push_back({{1}, 0});                            // n=1, no quad
    edge.push_back({{1, 2}, 3});                         // n=2, no quad
    edge.push_back({{1, 2, 3}, 6});                      // n=3, no quad
    edge.push_back({{0, 0, 0, 0}, 0});                  // all zeros
    edge.push_back({{2, 2, 2, 2, 2}, 8});               // all equal -> one quad
    edge.push_back({{1, 0, -1, 0, -2, 2}, 0});          // classic
    edge.push_back({{10000, 10000, 10000, 10000}, 10000}); // extremes high
    edge.push_back({{-10000, -10000, -10000, -10000}, -10000}); // extremes low
    edge.push_back({{10000, -10000, 10000, -10000}, 0});
    edge.push_back({{-10000, -10000, 10000, 10000}, 0});
    edge.push_back({{5, 5, 5, 5, 5, 5, 5}, 20});        // many duplicate quads collapse to 1

    ostringstream out;

    auto emit = [&](const vector<int>& nums, int target) {
        vector<vector<int>> res = fourSum(nums, target);
        out << "{\"inputs\": {\"nums\": \"" << jsonEscape(arrToStr(nums))
            << "\", \"target\": \"" << target << "\"}, \"expected\": \""
            << jsonEscape(expectedStr(res)) << "\"}\n";
    };

    long long produced = 0;
    for (auto& e : edge) {
        if (produced >= numCases) break;
        emit(e.first, e.second);
        produced++;
    }

    // Random cases. Bias toward smaller arrays and clustered values so that
    // quadruplets actually occur a good fraction of the time, while still
    // covering large/sparse cases.
    while (produced < numCases) {
        int mode = rng() % 10;
        int n;
        int valLo = LO, valHi = HI;
        if (mode < 4) {
            // small dense clustered -> likely to have matches
            n = 4 + (int)(rng() % 12);          // 4..15
            int center = (int)(rng() % 41) - 20; // -20..20
            int spread = 1 + (int)(rng() % 15);  // small spread
            valLo = max(LO, center - spread);
            valHi = min(HI, center + spread);
        } else if (mode < 7) {
            // medium arrays, moderate range
            n = 4 + (int)(rng() % 40);          // 4..43
            int spread = 1 + (int)(rng() % 100);
            int center = (int)((long long)(rng() % 401) - 200);
            valLo = max(LO, center - spread);
            valHi = min(HI, center + spread);
        } else if (mode < 9) {
            // larger arrays, wide range
            n = 50 + (int)(rng() % 151);        // 50..200
            valLo = LO; valHi = HI;
        } else {
            // tiny arrays (incl. n=1,2,3 -> empty result) for variety
            n = 1 + (int)(rng() % 5);           // 1..5
            valLo = LO; valHi = HI;
        }

        uniform_int_distribution<int> valDist(valLo, valHi);
        vector<int> nums(n);
        for (int i = 0; i < n; i++) nums[i] = valDist(rng);

        // target: bias to a sum of 4 random elements (when possible) to
        // generate non-empty answers, otherwise random in range.
        int target;
        int tmode = rng() % 3;
        if (n >= 4 && tmode != 0) {
            long long s = 0;
            for (int t = 0; t < 4; t++) s += nums[rng() % n];
            // clamp into valid target range
            if (s < LO) s = LO;
            if (s > HI) s = HI;
            target = (int)s;
        } else {
            uniform_int_distribution<int> tDist(LO, HI);
            target = tDist(rng);
        }

        emit(nums, target);
        produced++;
    }

    cout << out.str();
    return 0;
}
