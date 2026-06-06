// Generator + reference oracle for "Combination Sum III"
// Signature: vector<vector<int>> combinationSum3(int k, int n)
// Constraints: 2 <= k <= 9, 1 <= n <= 60
//
// Output: one JSON object per line:
//   {"inputs": {"k": "3", "n": "7"}, "expected": "[ [1, 2, 4] ]"}
// The judge compares leniently (ignores brackets/commas/whitespace), so we
// flatten the 2D result to space-separated numbers in row order.
//
// Compile: clang++ -std=c++17 -O2 -w combination-sum-iii.cpp -o gen
// Run:     ./gen > output.jsonl

#include <vector>
#include <string>
#include <iostream>
#include <random>
#include <set>
using namespace std;

// ---- Reference (ground truth), matches strivers-a2z-ref solution ----
void solve(int i, int k, int tar, vector<int>& nums, vector<int>& temp, vector<vector<int>>& ans) {
    if (tar == 0 && (int)temp.size() == k) {
        ans.push_back(temp);
        return;
    }
    if (i == (int)nums.size() || tar < 0)
        return;
    if (nums[i] <= tar) {
        temp.push_back(nums[i]);
        solve(i + 1, k, tar - nums[i], nums, temp, ans);
        temp.pop_back();
    }
    solve(i + 1, k, tar, nums, temp, ans);
}

vector<vector<int>> combinationSum3(int k, int n) {
    vector<int> nums;
    for (int i = 1; i <= 9; i++) nums.push_back(i);
    vector<vector<int>> ans;
    vector<int> temp;
    solve(0, k, n, nums, temp, ans);
    return ans;
}

// ---- Helpers ----
// Flatten a 2D vector to a space-separated string of numbers (row order).
// Empty result -> empty string (judge treats blank as empty list).
string flatten(const vector<vector<int>>& v) {
    string s;
    bool first = true;
    for (const auto& row : v) {
        for (int x : row) {
            if (!first) s += " ";
            s += to_string(x);
            first = false;
        }
    }
    return s;
}

int main() {
    // Full deterministic coverage of the entire valid input space:
    //   k in [2,9], n in [1,60]  -> 8 * 60 = 480 distinct cases.
    // Then fill up to 2000 with random (k,n) draws so the file has
    // exactly 2000 lines while every distinct case appears at least once.
    const int TOTAL = 2000;

    vector<pair<int,int>> cases;
    for (int k = 2; k <= 9; ++k)
        for (int n = 1; n <= 60; ++n)
            cases.push_back({k, n});

    mt19937 rng(123456789u);
    uniform_int_distribution<int> dk(2, 9);
    uniform_int_distribution<int> dn(1, 60);
    while ((int)cases.size() < TOTAL) {
        cases.push_back({dk(rng), dn(rng)});
    }

    for (int idx = 0; idx < TOTAL; ++idx) {
        int k = cases[idx].first;
        int n = cases[idx].second;
        vector<vector<int>> res = combinationSum3(k, n);
        string expected = flatten(res);

        cout << "{\"inputs\": {\"k\": \"" << k << "\", \"n\": \"" << n
             << "\"}, \"expected\": \"" << expected << "\"}\n";
    }
    return 0;
}
