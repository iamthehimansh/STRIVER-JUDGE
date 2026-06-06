// Generator + reference for "Count partitions with given difference"
// Signature: int countPartitions(int n, int diff, vector<int>& arr)
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-partitions-with-given-difference.jsonl
//
// Constraints:
//   1 <= n <= 200
//   0 <= diff <= 10^4
//   0 <= arr[i] <= 50
//
// Reference logic (subset-sum count with proper zero handling), answer mod 1e9+7.
// Count number of subsets with sum target = (totalSum - diff) / 2.
// If (totalSum - diff) < 0 or (totalSum - diff) is odd -> 0.

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <cstdint>

using namespace std;

static const long long MOD = 1000000007LL;

// Count subsets of arr (with zeros handled) that sum to target.
long long countSubsets(const vector<int>& arr, int target) {
    if (target < 0) return 0;
    int n = (int)arr.size();
    // dp over sum from 0..target. Standard 0/1 knapsack count, zeros multiply.
    // Use 1D dp.
    vector<long long> dp(target + 1, 0);
    dp[0] = 1; // empty subset
    for (int i = 0; i < n; i++) {
        int v = arr[i];
        if (v == 0) {
            // each zero can be in or out -> doubles every count
            for (int s = 0; s <= target; s++) dp[s] = (dp[s] * 2) % MOD;
        } else {
            for (int s = target; s >= v; s--) {
                dp[s] = (dp[s] + dp[s - v]) % MOD;
            }
        }
    }
    return dp[target] % MOD;
}

long long countPartitions(int n, int diff, const vector<int>& arr) {
    long long totalSum = 0;
    for (int x : arr) totalSum += x;
    long long rem = totalSum - (long long)diff;
    if (rem < 0 || (rem % 2 != 0)) return 0;
    long long target = rem / 2;
    if (target > totalSum) return 0; // safety
    return countSubsets(arr, (int)target) % MOD;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); i++) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-partitions-with-given-difference.jsonl";
    int total = 2000;
    uint64_t seed = 1234567ULL;
    if (argc > 1) total = atoi(argv[1]);
    if (argc > 2) outPath = argv[2];
    if (argc > 3) seed = strtoull(argv[3], nullptr, 10);

    mt19937_64 rng(seed);

    ofstream fout(outPath);
    if (!fout) { cerr << "cannot open " << outPath << "\n"; return 1; }

    int written = 0;

    auto emit = [&](int n, int diff, vector<int>& arr) {
        long long ans = countPartitions(n, diff, arr);
        fout << "{\"inputs\": {\"n\": \"" << n << "\", \"diff\": \"" << diff
             << "\", \"arr\": \"" << arrToStr(arr) << "\"}, \"expected\": \""
             << ans << "\"}\n";
        written++;
    };

    // --- Edge cases first ---
    {
        // n=1, arr=[0], diff=0 -> subsets {} and {0}, both sum 0; |S1-S2|=0 ... count partitions with diff 0
        vector<int> a = {0}; emit(1, 0, a);
        // n=1, arr=[5], diff=5
        vector<int> b = {5}; emit(1, 5, b);
        // n=1, arr=[0], diff=1 -> impossible
        vector<int> c = {0}; emit(1, 1, c);
        // n=1, arr=[50], diff=50
        vector<int> d = {50}; emit(1, 50, d);
        // example 1
        vector<int> e = {1,1,2,3}; emit(4, 1, e);
        // example 2
        vector<int> f = {1,2,3,4}; emit(4, 2, f);
        // now your turn
        vector<int> g = {5,2,6,4}; emit(4, 3, g);
        // all zeros, various diff
        vector<int> h(10, 0); emit(10, 0, h);
        vector<int> h2(5, 0); emit(5, 0, h2);
        // diff larger than sum -> 0
        vector<int> k = {1,2,3}; emit(3, 100, k);
        // diff making rem odd -> 0 (sum=7, diff=0 -> rem 7 odd)
        vector<int> l = {1,2,4}; emit(3, 0, l);
        // max-ish: n=200 all 50, diff such that rem even
        vector<int> m(200, 50); emit(200, 0, m); // sum=10000, rem=10000, target=5000
        // n=200 all 50, diff=10000 -> rem=0 target=0 -> count subsets sum 0
        vector<int> m2(200, 50); emit(200, 10000, m2);
        // mix with zeros
        vector<int> z = {0,0,0,1,2,3}; emit(6, 0, z);
        vector<int> z2 = {0,0,1,1}; emit(4, 0, z2);
    }

    // --- Random cases ---
    uniform_int_distribution<int> nSmall(1, 12);
    uniform_int_distribution<int> nMed(1, 40);
    uniform_int_distribution<int> nLarge(1, 200);
    uniform_int_distribution<int> valDist(0, 50);
    uniform_int_distribution<int> valSmall(0, 5); // more chance of zeros/overlap
    uniform_int_distribution<int> pickMode(0, 4);

    while (written < total) {
        int mode = pickMode(rng);
        int n;
        if (mode == 0) n = nSmall(rng);
        else if (mode == 1) n = nMed(rng);
        else n = nLarge(rng);

        vector<int> arr(n);
        long long sum = 0;
        bool useSmall = (mode == 0 || mode == 3);
        for (int i = 0; i < n; i++) {
            int v = useSmall ? valSmall(rng) : valDist(rng);
            arr[i] = v;
            sum += v;
        }

        // choose diff: bias toward valid (achievable) diffs but also some invalid.
        int diff;
        int dmode = pickMode(rng);
        if (dmode <= 2) {
            // valid-ish: pick a target subset sum t in [0,sum], diff = sum - 2t  (>=0 means t<=sum/2)
            uniform_int_distribution<int> tDist(0, (int)min<long long>(sum, 10000));
            int t = tDist(rng);
            long long dl = sum - 2LL * t;
            if (dl < 0) dl = -dl; // ensure non-negative; diff is |S1-S2|
            if (dl > 10000) dl = (int)(dl % 10001);
            diff = (int)dl;
        } else {
            // arbitrary diff within bounds
            uniform_int_distribution<int> dd(0, 10000);
            diff = dd(rng);
        }
        if (diff < 0) diff = 0;
        if (diff > 10000) diff = 10000;

        emit(n, diff, arr);
    }

    fout.close();
    cerr << "wrote " << written << " cases to " << outPath << "\n";
    return 0;
}
