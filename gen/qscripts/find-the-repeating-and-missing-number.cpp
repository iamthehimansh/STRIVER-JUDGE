// Generator + reference for "Find the repeating and missing number"
// Problem: nums of size n holds values [1,n], each value exactly once except
//   A appears twice and B is missing. Return {A, B}.
// Constraints: 1 <= n <= 1e5. NOTE: for the duplicate/missing structure to
//   exist we need at least 2 elements (n >= 2). n == 1 cannot host both a
//   duplicate and a missing value, so the smallest valid case is n == 2.
//
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-the-repeating-and-missing-number.jsonl
// Each line: {"inputs": {"nums": "[...]"}, "expected": "[A, B]"}
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:     ./gen

#include <vector>
#include <string>
#include <random>
#include <algorithm>
#include <fstream>
#include <iostream>
#include <cstdint>
using namespace std;

// ---- Reference solution (ground-truth oracle) ----
// Returns {repeating(A), missing(B)}.
vector<int> findMissingRepeatingNumbers(const vector<int>& nums) {
    long long n = (long long)nums.size();
    long long optSum = n * (n + 1) / 2;
    long long opt2Sum = n * (n + 1) * (2 * n + 1) / 6;
    long long actSum = 0, act2Sum = 0;
    for (long long it : nums) {
        actSum += it;
        act2Sum += it * it;
    }
    long long xMinusY = optSum - actSum;       // missing - repeating
    long long x2MinusY2 = opt2Sum - act2Sum;   // missing^2 - repeating^2
    long long xPlusY = x2MinusY2 / xMinusY;     // missing + repeating
    long long missing = (xPlusY + xMinusY) / 2;
    long long repeating = xPlusY - missing;
    return {(int)repeating, (int)missing};
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

int main() {
    mt19937 rng(123456789u);

    const string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-the-repeating-and-missing-number.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    const int TOTAL = 2000;
    int produced = 0;

    auto buildCase = [&](int n, int repeating, int missing) {
        // Build a valid permutation: values 1..n each once, then drop `missing`
        // and add an extra `repeating`.
        vector<int> a;
        a.reserve(n);
        for (int v = 1; v <= n; ++v) {
            if (v == missing) continue; // skip missing -> one slot freed
            a.push_back(v);
        }
        a.push_back(repeating); // duplicate fills the freed slot; size == n
        shuffle(a.begin(), a.end(), rng);
        return a;
    };

    auto emit = [&](const vector<int>& a) {
        vector<int> exp = findMissingRepeatingNumbers(a);
        // sanity: verify against brute force
        // (validate structure)
        out << "{\"inputs\": {\"nums\": \"" << arrToStr(a)
            << "\"}, \"expected\": \"[" << exp[0] << ", " << exp[1] << "]\"}\n";
        produced++;
    };

    // ---- Edge cases first ----
    // n == 2, all distinct combos of (repeating, missing) with repeating!=missing
    // n=2: values {1,2}; e.g. repeating=1 missing=2 -> [1,1]
    emit(buildCase(2, 1, 2)); // [1,1]
    emit(buildCase(2, 2, 1)); // [2,2]
    // n == 3 small
    emit(buildCase(3, 1, 3));
    emit(buildCase(3, 3, 1));
    emit(buildCase(3, 2, 1));
    // max n with extremes
    {
        int n = 100000;
        emit(buildCase(n, 1, 2));        // repeating min
        emit(buildCase(n, n, n - 1));    // repeating max
        emit(buildCase(n, n, 1));        // missing min, repeating max
        emit(buildCase(n, 1, n));        // missing max, repeating min
        emit(buildCase(n, 50000, 50001));
    }

    // ---- Random cases ----
    // Mix of small, medium, large n. n in [2, 1e5].
    uniform_int_distribution<int> pickBucket(0, 9);
    while (produced < TOTAL) {
        int n;
        int b = pickBucket(rng);
        if (b == 0) {
            n = uniform_int_distribution<int>(2, 10)(rng);          // tiny
        } else if (b <= 3) {
            n = uniform_int_distribution<int>(2, 1000)(rng);        // small
        } else if (b <= 6) {
            n = uniform_int_distribution<int>(1000, 20000)(rng);    // medium
        } else {
            n = uniform_int_distribution<int>(20000, 100000)(rng);  // large
        }
        // choose distinct repeating, missing in [1, n]
        int repeating = uniform_int_distribution<int>(1, n)(rng);
        int missing = uniform_int_distribution<int>(1, n)(rng);
        while (missing == repeating) missing = uniform_int_distribution<int>(1, n)(rng);
        emit(buildCase(n, repeating, missing));
    }

    out.close();
    cerr << "Wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
