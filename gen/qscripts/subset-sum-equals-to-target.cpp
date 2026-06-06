// Generator + static test set for Striver problem: subset-sum-equals-to-target
// Problem: Given arr of n ints and target, is there a subset with sum == target?
// Signature: bool isSubsetSum(vector<int> arr, int target)
// Constraints: 1 <= n <= 100 ; 1 <= arr[i] <= 100 ; 0 <= target <= 5*10^3
// Output format (matching examples): "True" / "False"
//
// Writes 2000 lines to generated-tests/subset-sum-equals-to-target.jsonl
//   {"inputs": {"arr": "[...]", "target": "N"}, "expected": "True|False"}
//
// Build:  clang++ -std=c++17 -O2 -w subset-sum-equals-to-target.cpp -o gen
// Run  :  ./gen "/path/to/generated-tests/subset-sum-equals-to-target.jsonl"

#include <vector>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
#include <bitset>
using namespace std;

// Reference oracle: subset-sum DP using a bitset reachability over [0..target].
// arr[i] >= 1, target <= 5000. O(n * target / 64).
static bool isSubsetSum(const vector<int>& arr, int target) {
    // bitset of reachable sums; bit s set => sum s achievable by some subset
    static bitset<5001> dp;
    dp.reset();
    dp.set(0); // empty subset
    for (int v : arr) {
        if (v > target) continue; // cannot help reach <= target as part of a sum
        dp |= (dp << v);
        // keep only bits <= target (shift can overflow beyond 5000 -> trimmed by size)
    }
    return target <= 5000 && dp.test(target);
}

static string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/subset-sum-equals-to-target.jsonl";
    if (argc >= 2) outPath = argv[1];

    const int N_CASES = 2000;
    std::mt19937 rng(123456789u);

    ofstream out(outPath);
    if (!out) { cerr << "cannot open " << outPath << "\n"; return 1; }

    auto emit = [&](const vector<int>& arr, int target) {
        bool ans = isSubsetSum(arr, target);
        out << "{\"inputs\": {\"arr\": \"" << arrToStr(arr)
            << "\", \"target\": \"" << target << "\"}, \"expected\": \""
            << (ans ? "True" : "False") << "\"}\n";
    };

    int produced = 0;

    // ---- Deterministic edge cases first ----
    // single element, target equals it -> True
    emit({5}, 5);
    produced++;
    // single element, target 0 -> True (empty subset)
    emit({5}, 0);
    produced++;
    // single element, target not reachable
    emit({5}, 3);
    produced++;
    // min arr value, max-ish target unreachable
    emit({1}, 5000);
    produced++;
    // 100 ones -> reachable sums 0..100
    {
        vector<int> a(100, 1);
        emit(a, 100); produced++;
        emit(a, 101); produced++; // unreachable
        emit(a, 0);   produced++;
    }
    // 100 hundreds -> max sum 10000 but target capped at 5000; reachable multiples of 100
    {
        vector<int> a(100, 100);
        emit(a, 5000); produced++; // 50 elements
        emit(a, 4999); produced++; // not a multiple of 100 -> False
        emit(a, 100);  produced++;
    }
    // the dataset examples
    emit({1, 2, 7, 3}, 6); produced++;   // True
    emit({2, 3, 5}, 6);    produced++;   // False
    emit({7, 54, 4, 12, 15, 5}, 9); produced++; // ? (Case 3)

    // ---- Random cases ----
    std::uniform_int_distribution<int> sizeDist(1, 100);
    std::uniform_int_distribution<int> valDist(1, 100);
    std::uniform_int_distribution<int> kindDist(0, 3);

    while (produced < N_CASES) {
        int n = sizeDist(rng);
        vector<int> arr(n);
        long long total = 0;
        for (int i = 0; i < n; ++i) { arr[i] = valDist(rng); total += arr[i]; }

        int target;
        int kind = kindDist(rng);
        if (kind == 0) {
            // target 0 (always True)
            target = 0;
        } else if (kind == 1 && total > 0) {
            // pick a target that is the exact sum of a random sub-selection (guaranteed reachable, capped)
            long long s = 0;
            std::uniform_int_distribution<int> coin(0, 1);
            for (int i = 0; i < n; ++i) if (coin(rng)) s += arr[i];
            if (s > 5000) s = s % 5001;
            target = (int)s;
        } else {
            // uniformly random target in [0, 5000]
            std::uniform_int_distribution<int> tDist(0, 5000);
            target = tDist(rng);
        }
        emit(arr, target);
        produced++;
    }

    out.close();
    cerr << "wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
