// Generator + static test set for:
//   Kth largest element in a stream of running integers
//
// Problem: design class KthLargest(k, nums); add(val) appends val and returns
//          the kth largest element in the running stream.
//
// Input keys (match starterCpp ctor/add + problem testcases):
//   commands : [int...]   the sequence of vals passed to add()
//   k        : int        the k value
//   nums     : [int...]   the initial stream
// expected  : "[null, r1, r2, ...]"  ri = result of add(commands[i])
//
// Constraints enforced for every generated case:
//   1 <= number of instructions (1 ctor + adds) <= 1000  => 0 <= #adds <= 999
//   -1e4 <= val & all initial values <= 1e4
//   1 <= k <= 1e4
//   k - 1 <= nums.length <= 1e3
//   The stream has at least k elements after every add call.
//     Guaranteed by: nums.length >= k-1 and at least 1 add, so stream
//     length after the i-th add = nums.length + i+1 >= (k-1)+1 = k.
//     We always emit at least one add to honour this.
//
// Build & run:
//   clang++ -std=c++17 -O2 -w gen.cpp -o gen && ./gen
//
#include <vector>
#include <queue>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
using namespace std;

// ---- Reference oracle (min-heap of size k) ------------------------------
class KthLargest {
private:
    priority_queue<int, vector<int>, greater<int>> pq;
    int k;
public:
    KthLargest(int k_, const vector<int>& nums) {
        k = k_;
        for (size_t i = 0; i < nums.size(); i++) {
            pq.push(nums[i]);
            if ((int)pq.size() > k) pq.pop();
        }
    }
    int add(int val) {
        pq.push(val);
        if ((int)pq.size() > k) pq.pop();
        return pq.top();
    }
};

static string arrToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main() {
    mt19937 rng(987654321u);
    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/"
        "kth-largest-element-in-a-stream-of-running-integers.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    const int VLO = -10000, VHI = 10000;
    const int N = 2000;

    auto randVal = [&](int lo, int hi) {
        return (int)(uniform_int_distribution<int>(lo, hi)(rng));
    };

    // emit one test object
    auto emit = [&](const vector<int>& cmds, int k, const vector<int>& nums) {
        // compute expected
        KthLargest obj(k, nums);
        string exp = "[null";
        for (int v : cmds) {
            exp += ", ";
            exp += to_string(obj.add(v));
        }
        exp += "]";
        out << "{\"inputs\": {\"commands\": \"" << arrToStr(cmds)
            << "\", \"k\": \"" << k
            << "\", \"nums\": \"" << arrToStr(nums)
            << "\"}, \"expected\": \"" << exp << "\"}\n";
    };

    int produced = 0;

    // ---- Deterministic edge cases -------------------------------------
    {
        // The two dataset examples (sanity).
        emit({5, 2, 7}, 3, {1, 2, 3, 4}); produced++;
        emit({2, 6, 60}, 2, {5, 5, 5, 5}); produced++;
        // k=1: largest ever seen
        emit({10}, 1, {}); produced++;
        emit({-10000}, 1, {}); produced++;
        // nums length exactly k-1 (smallest allowed for given k)
        emit({0}, 3, {7, 9}); produced++;
        // extremes
        emit({10000}, 1, {-10000, 10000}); produced++;
        emit({-10000, -10000}, 2, {10000, -10000}); produced++;
        // k larger than initial but reached via adds
        {
            vector<int> nums(4, 5);   // len 4
            vector<int> cmds(6, 3);   // 6 adds -> stream len 10 >= k=5
            emit(cmds, 5, nums); produced++;
        }
        // single add, k == nums.length+1 (k-1 == nums.length)
        emit({42}, 5, {1, 2, 3, 4}); produced++;
        // all identical values
        emit({3, 3, 3}, 2, {3, 3, 3}); produced++;
        // max instruction count: 999 adds, large k
        {
            int k = 500;
            vector<int> nums;
            for (int i = 0; i < 600; i++) nums.push_back(randVal(VLO, VHI));
            vector<int> cmds;
            for (int i = 0; i < 999; i++) cmds.push_back(randVal(VLO, VHI));
            emit(cmds, k, nums); produced++;
        }
        // k at the upper bound 10000, reachable only via long stream is
        // impossible (nums<=1000, adds<=999 => max stream 1999 < 10000),
        // but constraint "stream has >= k after add" must hold, so k is
        // effectively bounded by stream length. We respect that by always
        // choosing k <= nums.length + #adds.
    }

    // ---- Randomized cases ---------------------------------------------
    while (produced < N) {
        // choose number of adds: 1..999 (at least 1 to satisfy stream>=k)
        int adds = uniform_int_distribution<int>(1, 999)(rng);
        // total instructions = 1 + adds <= 1000  (adds<=999 ok)

        // Decide nums length: 0..1000, but must satisfy nums.length >= k-1.
        // Strategy: pick numsLen first, then pick k in valid window so that
        // both (k-1 <= numsLen) and (stream after every add >= k) hold.
        int numsLen = uniform_int_distribution<int>(0, 1000)(rng);

        // After the i-th add (i from 0), stream length = numsLen + i + 1.
        // The minimum stream length over all adds is after the first add:
        //   numsLen + 1.
        // Requirement after EVERY add: stream >= k  => numsLen + 1 >= k.
        // Combined with k-1 <= numsLen  (i.e. k <= numsLen+1) -> same bound.
        // So valid k range: 1 <= k <= numsLen + 1, and also k <= 10000.
        int kHi = min(numsLen + 1, 10000);
        if (kHi < 1) kHi = 1; // numsLen==0 -> kHi=1
        int k = uniform_int_distribution<int>(1, kHi)(rng);

        // Build nums and commands within value range.
        vector<int> nums(numsLen);
        for (int i = 0; i < numsLen; i++) nums[i] = randVal(VLO, VHI);
        vector<int> cmds(adds);
        for (int i = 0; i < adds; i++) cmds[i] = randVal(VLO, VHI);

        emit(cmds, k, nums);
        produced++;
    }

    out.close();
    cerr << "wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
