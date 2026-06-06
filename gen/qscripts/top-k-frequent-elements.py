#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Top K Frequent Elements (slug: top-k-frequent-elements)

starterCpp signature:
    vector<int> topKFrequent(const vector<int>& nums, int k)

Constraints:
    1 <= nums.length <= 1e5
    -1e4 <= nums[i] <= 1e4   (so at most 20001 distinct values)
    1 <= k <= number of distinct elements in nums
    The answer is guaranteed to be unique.

"unique" means: the set of the k most frequent elements is unambiguous, i.e. the
frequency of the k-th most frequent distinct value is STRICTLY greater than the
frequency of the (k+1)-th most frequent distinct value. The generator enforces
this by giving every distinct value a strictly distinct frequency.

Output file (one JSON object per line):
    {"inputs": {"nums": "[...]", "k": "N"}, "expected": "v1 v2 ..."}
expected is the top-k values sorted ascending (matches the example outputs which
are sorted ascending), space-separated; the judge compares leniently.

The C++ reference oracle (compiled once) is the ground truth for "expected".
"""
import json, os, random, subprocess, tempfile, sys

SLUG = "top-k-frequent-elements"
ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT  = os.path.join(ROOT, "generated-tests", SLUG + ".jsonl")
N_CASES = 2000
VMIN, VMAX = -10000, 10000        # nums[i] range
MAXLEN = 100000                   # nums.length cap
MAX_DISTINCT = VMAX - VMIN + 1    # 20001 possible distinct values

REF_SRC = r'''
#include <iostream>
#include <vector>
#include <unordered_map>
#include <algorithm>
using namespace std;
class Solution {
public:
    vector<int> topKFrequent(const vector<int>& nums, int k) {
        unordered_map<int,int> mp;
        for (int x : nums) mp[x]++;
        vector<pair<int,int>> v(mp.begin(), mp.end());
        sort(v.begin(), v.end(), [](const pair<int,int>&a, const pair<int,int>&b){
            if (a.second != b.second) return a.second > b.second;
            return a.first < b.first;
        });
        vector<int> ans;
        for (int i = 0; i < k && i < (int)v.size(); i++) ans.push_back(v[i].first);
        return ans;
    }
};
int main(){
    int k, n;
    if(!(cin >> k)) return 0;
    cin >> n;
    vector<int> nums(n);
    for (int i = 0; i < n; i++) cin >> nums[i];
    Solution s;
    vector<int> res = s.topKFrequent(nums, k);
    sort(res.begin(), res.end());
    for (size_t i = 0; i < res.size(); i++){ if (i) cout << " "; cout << res[i]; }
    cout << "\n";
    return 0;
}
'''

def build_ref(tmp):
    src = os.path.join(tmp, "ref.cpp")
    exe = os.path.join(tmp, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", exe], check=True)
    return exe

def run_ref(exe, nums, k):
    payload = f"{k}\n{len(nums)}\n{' '.join(map(str, nums))}\n"
    p = subprocess.run([exe], input=payload, capture_output=True, text=True, check=True)
    return p.stdout.strip()

def make_distinct_freqs(num_distinct, total_len):
    """Pick `num_distinct` strictly-distinct positive frequencies summing to <= total_len,
       then distribute the remaining length onto the single most-frequent value so all
       frequencies stay strictly distinct and the sum == total_len."""
    # base distinct freqs: 1,2,...,num_distinct
    base = list(range(1, num_distinct + 1))
    s = sum(base)
    # we need s <= total_len; caller guarantees feasibility
    rem = total_len - s
    # add all remaining to the largest, keeping it the unique max -> still distinct
    base[-1] += rem
    return base  # ascending; index -1 is the most frequent

def gen_case(rng):
    # choose number of distinct values d, then k in [1, d-1] (need a strict boundary,
    # so we need at least d>=2 to have a (k+1)-th distinct element; but k can also
    # equal d when k == all distinct elements -> answer is the whole multiset, still unique).
    # To always satisfy "answer unique", we make every freq distinct so any k is fine.

    style = rng.random()
    if style < 0.25:
        # tiny / edge cases
        d = rng.randint(1, 4)
    elif style < 0.7:
        d = rng.randint(2, 20)
    elif style < 0.95:
        d = rng.randint(2, 60)
    else:
        # rare larger cases
        d = rng.randint(2, 140)

    d = min(d, MAX_DISTINCT)

    # minimal total length if freqs are 1..d
    min_len = d * (d + 1) // 2
    # If min_len already exceeds MAXLEN, shrink d.
    while min_len > MAXLEN and d > 1:
        d -= 1
        min_len = d * (d + 1) // 2

    # choose total length: at least min_len. Keep lengths modest so the .jsonl
    # stays small; the bulk of cases are short, with a slim tail of larger ones.
    upper = MAXLEN
    r = rng.random()
    if r < 0.6:
        cap = min(upper, min_len + 30)
    elif r < 0.9:
        cap = min(upper, min_len + 300)
    else:
        cap = min(upper, min_len + 2000)
    total = rng.randint(min_len, max(min_len, cap))

    freqs = make_distinct_freqs(d, total)  # ascending, strictly distinct

    # pick d distinct values in [VMIN, VMAX]
    values = rng.sample(range(VMIN, VMAX + 1), d)
    # pair values with freqs randomly (shuffle values; freqs distinct so order irrelevant)
    rng.shuffle(values)

    nums = []
    for val, fr in zip(values, freqs):
        nums.extend([val] * fr)
    rng.shuffle(nums)
    assert len(nums) == total

    # k between 1 and d
    k = rng.randint(1, d)
    return nums, k

def fmt_arr(a):
    return "[" + ", ".join(map(str, a)) + "]"

def main():
    rng = random.Random(20260606)
    with tempfile.TemporaryDirectory() as tmp:
        exe = build_ref(tmp)

        # sanity check on dataset examples before trusting the oracle
        assert run_ref(exe, [1,1,1,2,2,3], 2) == "1 2", "example1 mismatch"
        assert run_ref(exe, [4,4,6,6,7], 2) == "4 6", "example2 mismatch"
        assert run_ref(exe, [-1,-1,-2,-2,-2,-3], 1) == "-2", "nyt mismatch"

        seen = set()
        lines = []

        # explicit edge cases first
        edge = [
            ([1], 1),
            ([7, 7, 7], 1),
            ([VMIN], 1),
            ([VMAX], 1),
            ([VMIN, VMIN, VMAX], 1),
            ([VMIN, VMIN, VMAX], 2),
            ([0]*100000, 1),                       # max length, single value
            ([5,5,3,3,3,1], 2),
            (list(range(-10, 10)) + [0], 1),       # 0 appears twice, unique top1
        ]
        for nums, k in edge:
            key = (tuple(nums), k)
            if key in seen: continue
            seen.add(key)
            exp = run_ref(exe, nums, k)
            lines.append(json.dumps({"inputs": {"nums": fmt_arr(nums), "k": str(k)}, "expected": exp}))

        tries = 0
        while len(lines) < N_CASES and tries < N_CASES * 50:
            tries += 1
            nums, k = gen_case(rng)
            key = (tuple(nums), k)
            if key in seen:
                continue
            seen.add(key)
            exp = run_ref(exe, nums, k)
            if exp == "":
                continue
            lines.append(json.dumps({"inputs": {"nums": fmt_arr(nums), "k": str(k)}, "expected": exp}))

        lines = lines[:N_CASES]
        with open(OUT, "w") as f:
            f.write("\n".join(lines) + "\n")

    print(f"wrote {len(lines)} cases -> {OUT}")

if __name__ == "__main__":
    main()
