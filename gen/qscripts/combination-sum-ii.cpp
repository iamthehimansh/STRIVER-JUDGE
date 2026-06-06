// Generator + reference oracle for "Combination Sum II" (Striver).
// Reference solution adapted from strivers-a2z-ref.
// Builds 2000 random test cases strictly within constraints:
//   1 <= candidates.length <= 100
//   1 <= candidates[i] <= 50
//   1 <= target <= 30
// Output JSONL line: {"inputs": {"candidates": "[..]", "target": "N"}, "expected": "<flattened combos>"}
// Expected is flattened to space-separated numbers, combinations in the order the
// reference (sorted candidates, in-order recursion) produces them.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <random>
#include <string>
#include <vector>
using namespace std;

// ---- reference oracle ----
static void solve(int index, int target, vector<int>& candidates,
                  vector<int>& temp, vector<vector<int>>& ans) {
    if (target == 0) { ans.push_back(temp); return; }
    if (index == (int)candidates.size() || target < 0) return;
    if (candidates[index] <= target) {
        temp.push_back(candidates[index]);
        solve(index + 1, target - candidates[index], candidates, temp, ans);
        temp.pop_back();
    }
    while (index + 1 < (int)candidates.size() &&
           candidates[index] == candidates[index + 1])
        index++;
    solve(index + 1, target, candidates, temp, ans);
}

static vector<vector<int>> combinationSum2(vector<int> candidates, int target) {
    vector<vector<int>> ans;
    vector<int> temp;
    sort(candidates.begin(), candidates.end());
    solve(0, target, candidates, temp, ans);
    return ans;
}

// ---- formatting helpers ----
static string vecToBracket(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// Flatten the 2D answer to space-separated numbers on one line (judge ignores
// brackets/commas/whitespace; token sequence is what matters).
static string flatten(const vector<vector<int>>& ans) {
    string s;
    bool first = true;
    for (const auto& row : ans)
        for (int x : row) {
            if (!first) s += ' ';
            s += to_string(x);
            first = false;
        }
    return s;
}

int main(int argc, char** argv) {
    string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/combination-sum-ii.jsonl";
    int N = 2000;
    if (argc > 1) outPath = argv[1];
    if (argc > 2) N = atoi(argv[2]);

    ofstream out(outPath);
    if (!out) { cerr << "cannot open " << outPath << "\n"; return 1; }

    std::mt19937 rng(12345);

    auto emit = [&](vector<int> cands, int target) {
        vector<vector<int>> ans = combinationSum2(cands, target);
        out << "{\"inputs\": {\"candidates\": \"" << vecToBracket(cands)
            << "\", \"target\": \"" << target << "\"}, \"expected\": \""
            << flatten(ans) << "\"}\n";
    };

    int produced = 0;

    // ---- deterministic edge cases first ----
    // dataset examples
    emit({2, 1, 2, 7, 6, 1, 5}, 8); ++produced;
    emit({2, 5, 2, 1, 2}, 5);       ++produced;
    // min size single element, hits / misses target
    emit({1}, 1);   ++produced;
    emit({50}, 30); ++produced;  // value > target, no combo
    emit({30}, 30); ++produced;
    emit({1}, 30);  ++produced;  // can't reach
    // all ones, max-ish length
    emit(vector<int>(100, 1), 30); ++produced;
    emit(vector<int>(30, 1), 30);  ++produced;
    // all equal large values
    emit(vector<int>(100, 50), 30); ++produced; // no combo
    emit(vector<int>(10, 5), 30);  ++produced;
    // all values above target
    emit({31, 40, 45, 50}, 30); ++produced;
    // target 1 with many duplicates
    emit({1, 1, 1, 1, 1}, 1); ++produced;
    // mixed dups
    emit({2, 2, 2, 2, 3, 3, 3, 5, 7, 7}, 10); ++produced;

    // ---- random cases ----
    std::uniform_int_distribution<int> lenDist(1, 100);
    std::uniform_int_distribution<int> valDist(1, 50);
    std::uniform_int_distribution<int> tgtDist(1, 30);
    // For richer combination structure, bias many candidates to small values so
    // combinations actually exist (still strictly within [1,50]).
    std::uniform_int_distribution<int> smallValDist(1, 12);
    std::uniform_int_distribution<int> coin(0, 99);

    while (produced < N) {
        int len = lenDist(rng);
        int target = tgtDist(rng);
        // choose a value distribution mode
        int mode = coin(rng);
        vector<int> cands(len);
        for (int i = 0; i < len; ++i) {
            if (mode < 60) {
                // mostly small values -> denser combination space
                cands[i] = smallValDist(rng);
            } else if (mode < 80) {
                // full range
                cands[i] = valDist(rng);
            } else {
                // few distinct values to force duplicates
                static const int pool[] = {1, 2, 2, 3, 5, 5, 7, 10};
                cands[i] = pool[coin(rng) % 8];
            }
        }
        emit(cands, target);
        ++produced;
    }

    out.close();
    cerr << "wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
