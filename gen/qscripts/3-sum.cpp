// Generator + reference oracle for Striver problem "3 Sum" (slug: 3-sum)
//
// Reference: strivers two-pointer threeSum (sorted, dedup) -> class Solution::threeSum
// Output file: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/3-sum.jsonl
//   One JSON object per line: {"inputs": {"nums": "[...]"}, "expected": "[[...],[...]]"}
//
// Constraints enforced:
//   1 <= nums.length <= 3000
//   -10^4 <= nums[i] <= 10^4
//
// The expected output is canonicalized (each triplet sorted ascending -- already true from
// the algorithm -- and the list of triplets sorted) so the judge's lenient comparison is stable.
//
// Build:  clang++ -std=c++17 -O2 -w 3-sum.cpp -o gen3sum
// Run:    ./gen3sum > 3-sum.jsonl

#include <vector>
#include <algorithm>
#include <random>
#include <string>
#include <cstdio>
#include <set>
using namespace std;

// ----- Reference oracle (the "correct" solution) -----
vector<vector<int>> threeSum(vector<int>& nums) {
    sort(nums.begin(), nums.end());
    vector<vector<int>> ans;
    int n = (int)nums.size();
    for (int i = 0; i < n; i++) {
        if (i > 0 && nums[i] == nums[i - 1]) continue;
        int j = i + 1, k = n - 1;
        while (j < k) {
            long sum = (long)nums[i] + nums[j] + nums[k];
            if (sum < 0) j++;
            else if (sum > 0) k--;
            else {
                ans.push_back({nums[i], nums[j], nums[k]});
                j++; k--;
                while (j < k && nums[j] == nums[j - 1]) j++;
                while (j < k && nums[k] == nums[k + 1]) k--;
            }
        }
    }
    return ans;
}

static string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

static string tripletsToStr(vector<vector<int>> t) {
    // canonical order: sort the list of (already-ascending) triplets
    sort(t.begin(), t.end());
    string s = "[";
    for (size_t i = 0; i < t.size(); i++) {
        if (i) s += ", ";
        s += vecToStr(t[i]);
    }
    s += "]";
    return s;
}

static void emit(vector<int> nums) {
    string in = vecToStr(nums);
    vector<int> copy = nums;          // threeSum sorts in place
    auto res = threeSum(copy);
    string out = tripletsToStr(res);
    // JSON line; raw arrays are valid JSON-string-safe (only digits, -, [], spaces, commas)
    printf("{\"inputs\": {\"nums\": \"%s\"}, \"expected\": \"%s\"}\n", in.c_str(), out.c_str());
}

int main() {
    std::mt19937 rng(987654321u);

    const int LO = -10000, HI = 10000;
    int produced = 0;
    set<string> seen;  // avoid identical lines (dedup on input string)

    auto tryEmit = [&](vector<int> nums) {
        string key = vecToStr(nums);
        if (seen.count(key)) return false;
        seen.insert(key);
        emit(nums);
        produced++;
        return true;
    };

    // ---- 1) Curated edge cases ----
    vector<vector<int>> edges = {
        {0},                 // min size, single elem, no triplet
        {1},
        {-10000},
        {10000},
        {0, 0},              // size 2, no triplet
        {1, -1},
        {0, 0, 0},           // smallest triplet summing to 0
        {1, -1, 0},
        {-1, 0, 1, 2, -1, -4},   // classic leetcode example
        {2, -2, 0, 3, -3, 5},    // dataset example 1
        {2, -1, -1, 3, -1},      // dataset example 2
        {8, -6, 5, 4},           // dataset example 3 -> []
        {-10000, 0, 10000},      // extremes summing to 0
        {-10000, 5000, 5000},
        {10000, -5000, -5000},
        {0, 0, 0, 0, 0},         // all zeros -> one triplet
        {3, 3, 3},               // no triplet
        {-1, -1, -1},
        {10000, 10000, 10000},   // would overflow int if naive; tests long sum
        {-10000, -10000, -10000},
        {-10000, -10000, 10000}, // sum -10000
        {1, 2, -3, 1, 2, -3},    // duplicates producing dedup
    };
    for (auto& e : edges) tryEmit(e);

    // ---- 2) Small arrays with small value range (dense in solutions) ----
    {
        uniform_int_distribution<int> nDist(1, 12);
        uniform_int_distribution<int> vDist(-8, 8);
        int target = 600;
        for (int c = 0; c < target * 4 && produced < 22 + 600; c++) {
            int n = nDist(rng);
            vector<int> nums(n);
            for (int i = 0; i < n; i++) nums[i] = vDist(rng);
            tryEmit(nums);
        }
    }

    // ---- 3) Medium arrays, moderate range ----
    {
        uniform_int_distribution<int> nDist(3, 60);
        uniform_int_distribution<int> vDist(-50, 50);
        while (produced < 1200) {
            int n = nDist(rng);
            vector<int> nums(n);
            for (int i = 0; i < n; i++) nums[i] = vDist(rng);
            tryEmit(nums);
        }
    }

    // ---- 4) Larger arrays, wider range incl. extremes ----
    {
        uniform_int_distribution<int> nDist(50, 600);
        uniform_int_distribution<int> vDist(LO, HI);
        while (produced < 1700) {
            int n = nDist(rng);
            vector<int> nums(n);
            for (int i = 0; i < n; i++) nums[i] = vDist(rng);
            // occasionally bias toward small magnitudes so triplets exist
            if ((rng() & 3) == 0) {
                uniform_int_distribution<int> small(-30, 30);
                for (int i = 0; i < n; i++) nums[i] = small(rng);
            }
            tryEmit(nums);
        }
    }

    // ---- 5) A few near-max-size arrays to exercise constraints ----
    {
        uniform_int_distribution<int> nDist(2500, 3000);
        uniform_int_distribution<int> small(-200, 200); // small range => many triplets
        while (produced < 1740) {
            int n = nDist(rng);
            vector<int> nums(n);
            for (int i = 0; i < n; i++) nums[i] = small(rng);
            tryEmit(nums);
        }
    }

    // ---- 6) Fill remaining up to 2000 with varied random arrays ----
    {
        uniform_int_distribution<int> nDist(1, 200);
        while (produced < 2000) {
            int n = nDist(rng);
            // random range width
            int width = 1 << (uniform_int_distribution<int>(0, 13)(rng)); // up to 8192
            int lo = max(LO, -width), hi = min(HI, width);
            uniform_int_distribution<int> vDist(lo, hi);
            vector<int> nums(n);
            for (int i = 0; i < n; i++) nums[i] = vDist(rng);
            tryEmit(nums);
        }
    }

    return 0;
}
