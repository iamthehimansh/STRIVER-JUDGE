// Generator + reference oracle for "Majority Element-II"
// Returns all elements appearing more than n/3 times (strictly > floor(n/3)).
// Output formatted sorted ascending to match dataset examples ([1], [1, 2]).
//
// Build (macOS): clang++ -std=c++17 -O2 -w -o /tmp/mej2/gen majority-element-ii.cpp
// Run:           /tmp/mej2/gen > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/majority-element-ii.jsonl"
//
// Constraints enforced:
//   2 <= n <= 1e5
//   -1e4 <= nums[i] <= 1e4

#include <vector>
#include <string>
#include <iostream>
#include <sstream>
#include <algorithm>
#include <random>
#include <cstdint>
#include <map>

using namespace std;

// ---- reference oracle: pure count-based, exact, sorted ascending ----
// Foolproof: frequency map, keep values strictly > floor(n/3).
vector<int> majorityElementTwo(vector<int>& nums) {
    int n = (int)nums.size();
    map<int,int> freq; // ordered map -> result naturally sorted ascending
    for (int x : nums) freq[x]++;
    vector<int> ans;
    for (auto& kv : freq) {
        if (kv.second > n / 3) ans.push_back(kv.first);
    }
    // map iteration is already sorted ascending; keep explicit sort for safety
    sort(ans.begin(), ans.end());
    return ans;
}

string arrToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    uint64_t seed = 1234567ULL;
    int TOTAL = 2000;
    if (argc > 1) seed = strtoull(argv[1], nullptr, 10);
    if (argc > 2) TOTAL = atoi(argv[2]);
    mt19937_64 rng(seed);

    auto emit = [&](vector<int> nums) {
        // build a copy because oracle takes by ref (does not mutate, but safe)
        vector<int> in = nums;
        vector<int> out = majorityElementTwo(in);
        cout << "{\"inputs\": {\"nums\": \"" << arrToStr(nums)
             << "\"}, \"expected\": \"" << arrToStr(out) << "\"}\n";
    };

    int produced = 0;

    // ---- deterministic edge cases first ----
    vector<vector<int>> edges = {
        {1, 2, 1, 1, 3, 2},          // example 1 -> [1]
        {1, 2, 1, 1, 3, 2, 2},       // example 2 -> [1, 2]
        {1, 2, 1, 1, 3, 2, 2, 3},    // now-your-turn -> [1, 2]
        {1, 1},                      // n=2 min, one elem -> [1]
        {1, 2},                      // n=2, none > 0 -> []  (n/3=0, count 1>0 each) => [1,2]
        {0, 0},                      // -> [0]
        {-10000, -10000},            // extreme negatives -> [-10000]
        {10000, 10000},              // extreme positives -> [10000]
        {-10000, 10000},             // -> [-10000, 10000]
        {3, 2, 3},                   // -> [3]
        {1, 1, 1, 1},                // -> [1]
        {1, 2, 3, 4, 5, 6},          // n=6 n/3=2, all once -> []
        {1, 1, 2, 2, 3, 3},          // n=6 n/3=2, each twice, none>2 -> []
        {1, 1, 1, 2, 2, 2},          // each 3 > 2 -> [1, 2]
        {5, 5, 5},                   // -> [5]
        {-1, -1, -1, 2, 2, 2, 3},    // -> [-1, 2]
        {0, 1, 0, 1, 0, 1, 0},       // 0 four times, 1 three times, n=7 n/3=2 -> [0, 1]
    };
    for (auto& e : edges) { emit(e); ++produced; }

    // ---- helper to pick a value in [-10000, 10000] ----
    uniform_int_distribution<int> valDist(-10000, 10000);

    // ---- structured cases: plant 0/1/2 true majority elements ----
    // probability mix of small/medium/large n
    auto pickN = [&](int maxN) {
        // bias towards small for variety but include large
        int bucket = rng() % 10;
        if (bucket < 4) return (int)(2 + rng() % 30);          // small 2..31
        if (bucket < 7) return (int)(2 + rng() % 1000);        // medium
        if (bucket < 9) return (int)(2 + rng() % 20000);       // large-ish
        return (int)(2 + rng() % maxN);                        // up to 1e5
    };

    while (produced < TOTAL) {
        int mode = rng() % 4;
        int n = pickN(99999); // ensures <= 1e5
        if (n < 2) n = 2;
        if (n > 100000) n = 100000;

        vector<int> nums;
        nums.reserve(n);

        if (mode == 0) {
            // fully random
            for (int i = 0; i < n; ++i) nums.push_back(valDist(rng));
        } else if (mode == 1) {
            // small value alphabet so majorities likely appear
            int alpha = 2 + rng() % 5; // 2..6 distinct values
            vector<int> vals;
            for (int i = 0; i < alpha; ++i) vals.push_back(valDist(rng));
            for (int i = 0; i < n; ++i) nums.push_back(vals[rng() % alpha]);
        } else if (mode == 2) {
            // plant 1 majority element > n/3
            int majVal = valDist(rng);
            int majCount = n / 3 + 1 + (rng() % (max(1, n / 3 + 1))); // > n/3
            if (majCount > n) majCount = n;
            for (int i = 0; i < majCount; ++i) nums.push_back(majVal);
            for (int i = (int)nums.size(); i < n; ++i) {
                int v = valDist(rng);
                nums.push_back(v);
            }
            shuffle(nums.begin(), nums.end(), rng);
        } else {
            // plant 2 majority elements > n/3 (only possible when each ~ n/3)
            int a = valDist(rng), b = valDist(rng);
            while (b == a) b = valDist(rng);
            int cA = n / 3 + 1;
            int cB = n / 3 + 1;
            if (cA + cB > n) { cA = n / 3 + 1; cB = n - cA; }
            for (int i = 0; i < cA; ++i) nums.push_back(a);
            for (int i = 0; i < cB; ++i) nums.push_back(b);
            for (int i = (int)nums.size(); i < n; ++i) nums.push_back(valDist(rng));
            shuffle(nums.begin(), nums.end(), rng);
        }

        emit(nums);
        ++produced;
    }

    return 0;
}
