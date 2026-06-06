// Generator for: Check if there exists a subsequence with sum K
// Problem: bool checkSubsequenceSum(vector<int>& nums, int k)
// Constraints: 1 <= nums.length <= 20 ; 1 <= nums[i] <= 100 ; 1 <= k <= 2000
// Output format: "Yes" / "No"
//
// Self-contained: includes reference oracle + random input generation.
// Writes 2000 JSONL lines to the generated-tests path.
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:     ./gen

#include <vector>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
#include <algorithm>
using namespace std;

// ---------- Reference oracle ----------
// Subset-sum (subsequence sum) existence via DP boolean reachability.
// Returns true if some subsequence sums exactly to k.
bool checkSubsequenceSum(const vector<int>& nums, int k) {
    if (k < 0) return false;
    // reachable[s] = can we form sum s using a subset
    vector<char> reachable(k + 1, 0);
    reachable[0] = 1; // empty subset sums to 0
    for (int x : nums) {
        if (x > k) continue;
        for (int s = k; s >= x; --s) {
            if (reachable[s - x]) reachable[s] = 1;
        }
    }
    // k >= 1 per constraints, so empty subset (sum 0) never counts toward k>=1.
    return reachable[k] != 0;
}

// ---------- Helpers ----------
string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

string jsonEscape(const string& in) {
    string out;
    for (char c : in) {
        if (c == '"' || c == '\\') { out += '\\'; out += c; }
        else out += c;
    }
    return out;
}

int main() {
    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/"
        "check-if-there-exists-a-subsequence-with-sum-k.jsonl";

    ofstream out(outPath);
    if (!out) {
        cerr << "Cannot open output file: " << outPath << "\n";
        return 1;
    }

    mt19937 rng(987654321u);
    auto randInt = [&](int lo, int hi) {
        return uniform_int_distribution<int>(lo, hi)(rng);
    };

    const int TOTAL = 2000;
    int produced = 0;
    int yesCount = 0, noCount = 0;

    auto emit = [&](const vector<int>& nums, int k) {
        bool ans = checkSubsequenceSum(nums, k);
        if (ans) yesCount++; else noCount++;
        out << "{\"inputs\": {\"nums\": \"" << jsonEscape(arrToStr(nums))
            << "\", \"k\": \"" << k << "\"}, \"expected\": \""
            << (ans ? "Yes" : "No") << "\"}\n";
        produced++;
    };

    // ---- Deterministic edge cases first ----
    // 1) min size, single element equal to k
    emit({1}, 1);
    // 2) single element less than k -> No
    emit({5}, 7);
    // 3) single element greater than k -> No
    emit({100}, 50);
    // 4) k = 1, array has a 1 -> Yes
    emit({1, 2, 3}, 1);
    // 5) k = 1, no 1 present -> No
    emit({2, 3, 4}, 1);
    // 6) dataset examples
    emit({1, 2, 3, 4, 5}, 8);   // Yes
    emit({4, 3, 9, 2}, 10);     // No
    emit({1, 10, 4, 5}, 16);    // Yes (1+10+5=16)
    // 7) max size all 100, k = 2000 (sum = 2000) -> Yes
    {
        vector<int> v(20, 100);
        emit(v, 2000);
    }
    // 8) max size all 100, k = 1999 (cannot form, multiples of 100) -> No
    {
        vector<int> v(20, 100);
        emit(v, 1999);
    }
    // 9) max size all 1, k = 20 -> Yes (sum=20)
    {
        vector<int> v(20, 1);
        emit(v, 20);
    }
    // 10) max size all 1, k = 21 -> No (total sum only 20)
    {
        vector<int> v(20, 1);
        emit(v, 21);
    }
    // 11) k larger than total sum -> No
    {
        vector<int> v(5, 2); // sum 10
        emit(v, 2000);
    }
    // 12) k = 2000 with array summing to exactly 2000 reachable
    {
        vector<int> v(20, 100); // 2000
        emit(v, 1900); // drop one 100 -> Yes
    }

    // ---- Randomized cases ----
    // Strategy mix to get both Yes and No outcomes:
    //  A) Pure random nums + random k in [1,2000]  (often No when k large)
    //  B) Construct nums then pick k = sum of a random subset (guaranteed Yes,
    //     as long as that subset is non-empty)
    //  C) Random nums, k = total sum +/- small (boundary)
    while (produced < TOTAL) {
        int mode = randInt(0, 9);
        int n = randInt(1, 20);
        vector<int> nums(n);
        for (int i = 0; i < n; ++i) nums[i] = randInt(1, 100);
        long long total = 0;
        for (int x : nums) total += x;

        int k;
        if (mode <= 3) {
            // B) guaranteed-reachable k: sum of a random non-empty subset
            // pick at least one index
            int subsetSum = 0;
            bool any = false;
            for (int i = 0; i < n; ++i) {
                if (randInt(0, 1)) { subsetSum += nums[i]; any = true; }
            }
            if (!any) { subsetSum = nums[randInt(0, n - 1)]; }
            k = subsetSum;
            if (k < 1) k = nums[randInt(0, n - 1)]; // safety, nums>=1 so >=1
            if (k > 2000) k = 2000; // clamp to constraint (still likely reachable, oracle decides)
        } else if (mode <= 6) {
            // A) fully random k within constraints
            k = randInt(1, 2000);
        } else if (mode == 7) {
            // total sum exactly (Yes if total <= 2000)
            k = (int)min<long long>(total, 2000);
            if (k < 1) k = 1;
        } else if (mode == 8) {
            // just above total sum -> typically No (clamped to 2000)
            k = (int)min<long long>(total + randInt(1, 50), 2000);
            if (k < 1) k = 1;
        } else {
            // small k in [1, 200], more likely Yes for varied arrays
            k = randInt(1, 200);
        }

        emit(nums, k);
    }

    out.close();
    cerr << "Produced " << produced << " cases. Yes=" << yesCount
         << " No=" << noCount << "\n";
    return 0;
}
