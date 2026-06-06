#!/usr/bin/env python3
"""
Test-case generator for Striver problem "3 Sum" (slug: 3-sum).

Signature: vector<vector<int>> threeSum(vector<int>& nums)
Constraints:
  1 <= nums.length <= 3000
  -10^4 <= nums[i] <= 10^4

Strategy:
  - Compile a C++ reference oracle (two-pointer 3-sum, dedup) once into a temp dir.
  - Generate random arrays strictly within constraints, biased toward many
    zero-sum triplets (small value ranges, duplicates, +/- pairs) plus edge cases.
  - Run the oracle on each input to compute expected output.
  - Write generated-tests/3-sum.jsonl with one JSON object per line:
        {"inputs": {"nums": "[...]"}, "expected": "[[...], ...]"}

Output values are formatted like the dataset examples (int arrays as "[a, b, c]").
The expected triplets are each sorted ascending and the triplet list is sorted,
giving a deterministic canonical form (the judge compares leniently anyway).
"""
import json
import os
import random
import subprocess
import tempfile

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", "3-sum.jsonl")
N_CASES = 2000
SEED = 20260606

CPP_REF = r'''
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

class Solution {
public:
    vector<vector<int>> threeSum(vector<int>& nums) {
        vector<vector<int>> ans;
        sort(nums.begin(), nums.end());
        int n = nums.size();
        for (int k = 0; k < n; k++) {
            if (k > 0 && nums[k] == nums[k-1]) continue;
            int i = k + 1;
            int j = n - 1;
            int target = -nums[k];
            while (i < j) {
                int sum = nums[i] + nums[j];
                if (sum == target) {
                    ans.push_back({nums[k], nums[i], nums[j]});
                    i++; j--;
                    while (i < j && nums[i] == nums[i-1]) i++;
                    while (i < j && nums[j] == nums[j+1]) j--;
                } else if (sum < target) {
                    i++;
                } else {
                    j--;
                }
            }
        }
        return ans;
    }
};

int main() {
    string line;
    getline(cin, line);
    vector<int> nums;
    string num;
    bool inNum = false;
    for (size_t idx = 0; idx < line.size(); idx++) {
        char c = line[idx];
        if (c == '-' || (c >= '0' && c <= '9')) { num += c; inNum = true; }
        else { if (inNum) { nums.push_back(stoi(num)); num.clear(); inNum = false; } }
    }
    if (inNum) nums.push_back(stoi(num));

    Solution s;
    vector<vector<int>> res = s.threeSum(nums);
    for (auto &t : res) sort(t.begin(), t.end());
    sort(res.begin(), res.end());

    string out = "[";
    for (size_t a = 0; a < res.size(); a++) {
        if (a) out += ", ";
        out += "[";
        for (size_t b = 0; b < res[a].size(); b++) {
            if (b) out += ", ";
            out += to_string(res[a][b]);
        }
        out += "]";
    }
    out += "]";
    cout << out << "\n";
    return 0;
}
'''

VMIN, VMAX = -10000, 10000
NMAX = 3000


def build_ref(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_REF)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def run_ref(binp, nums):
    line = "[" + ", ".join(str(x) for x in nums) + "]"
    p = subprocess.run([binp], input=line + "\n", capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ref failed: " + p.stderr)
    return p.stdout.strip()


def fmt_arr(nums):
    return "[" + ", ".join(str(x) for x in nums) + "]"


def gen_case(rng):
    """Generate one nums array strictly within constraints, with variety."""
    mode = rng.random()
    if mode < 0.10:
        # tiny edge cases
        n = rng.randint(1, 4)
        return [rng.randint(-5, 5) for _ in range(n)]
    elif mode < 0.45:
        # small value range -> many zero-sum triplets, lots of dups
        n = rng.randint(3, 60)
        lo = rng.choice([-3, -5, -8, -10, -20])
        return [rng.randint(lo, -lo) for _ in range(n)]
    elif mode < 0.65:
        # moderate size, moderate range
        n = rng.randint(20, 300)
        r = rng.choice([50, 100, 500, 1000])
        return [rng.randint(-r, r) for _ in range(n)]
    elif mode < 0.78:
        # all same value
        n = rng.randint(1, 50)
        v = rng.randint(VMIN, VMAX)
        return [v] * n
    elif mode < 0.88:
        # full value range, small/medium size (likely few/no triplets)
        n = rng.randint(2, 80)
        return [rng.randint(VMIN, VMAX) for _ in range(n)]
    elif mode < 0.95:
        # constructed: insert explicit zero-sum triplets among noise
        n = rng.randint(6, 120)
        arr = []
        ntrip = rng.randint(1, n // 3)
        for _ in range(ntrip):
            a = rng.randint(-VMAX, VMAX)
            b = rng.randint(max(VMIN, -VMAX - a), min(VMAX, VMAX - a))
            c = -a - b
            if VMIN <= c <= VMAX:
                arr.extend([a, b, c])
        while len(arr) < n:
            arr.append(rng.randint(VMIN, VMAX))
        rng.shuffle(arr)
        return arr[:n]
    else:
        # large array (stress) within bounds, smallish range so it stays fast
        n = rng.randint(1000, NMAX)
        r = rng.choice([100, 1000, 10000])
        return [rng.randint(-r, r) for _ in range(n)]


def main():
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as workdir:
        binp = build_ref(workdir)

        # sanity: reproduce dataset examples
        assert run_ref(binp, [2, -1, -1, 3, -1]) == "[[-1, -1, 2]]", "example2 mismatch"
        assert run_ref(binp, [8, -6, 5, 4]) == "[]", "example3 mismatch"

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

        # explicit edge cases first
        edge = [
            [0],
            [0, 0, 0],
            [0, 0, 0, 0],
            [1],
            [-10000],
            [10000],
            [1, -1],
            [10000, -10000],
            [1, 2, -3],
            [-1, 0, 1, 2, -1, -4],
            [10000, 10000, -10000, -10000, 0],
            [VMIN] * 5,
            [VMAX] * 5,
        ]

        seen = set()
        cases = []
        for e in edge:
            key = tuple(e)
            if key not in seen and 1 <= len(e) <= NMAX:
                seen.add(key)
                cases.append(e)

        while len(cases) < N_CASES:
            arr = gen_case(rng)
            if not (1 <= len(arr) <= NMAX):
                continue
            if not all(VMIN <= x <= VMAX for x in arr):
                continue
            cases.append(arr)

        cases = cases[:N_CASES]

        with open(OUT_PATH, "w") as f:
            for arr in cases:
                expected = run_ref(binp, arr)
                obj = {"inputs": {"nums": fmt_arr(arr)}, "expected": expected}
                f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
