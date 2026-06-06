#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Single Number - III"
(slug: single-number---iii).

Signature: vector<int> singleNumber(vector<int>& nums)
Constraints:
  2 <= nums.length <= 10^5
  -3*10^5 <= nums[i] <= 3*10^5
  Every integer in nums appears twice except exactly TWO integers, each of
  which appears exactly once. Return the two singletons in ascending order.

Strategy:
  - Compile a C++ reference oracle (XOR + rightmost-set-bit bucketing) once
    into a temp dir; the oracle sorts the two results ascending.
  - Construct each input to satisfy the structure precisely: choose a set of
    "pair" values (each duplicated) plus exactly two distinct singleton values,
    then shuffle. This guarantees every value appears twice except the two
    unique ones.
  - Run the oracle on each input to compute the expected output.
  - Write generated-tests/single-number---iii.jsonl with one JSON object per
    line: {"inputs": {"nums": "[...]"}, "expected": "[a, b]"}

Output values are formatted like the dataset examples (int arrays "[a, b]").
"""
import json
import os
import random
import subprocess
import tempfile

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", "single-number---iii.jsonl")
N_CASES = 2000
SEED = 20260606

VMIN, VMAX = -300000, 300000
NMAX = 100000

CPP_REF = r'''
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
using namespace std;

class Solution {
public:
    vector<int> singleNumber(vector<int>& nums) {
        long long xori = 0;
        for (auto it : nums) xori ^= it;
        long long temp = xori & (-xori);   // rightmost set bit
        long long num1 = 0, num2 = 0;
        for (auto it : nums) {
            if (((long long)it & temp) != 0) num1 ^= it;
            else num2 ^= it;
        }
        vector<int> ans{(int)num1, (int)num2};
        sort(ans.begin(), ans.end());      // ascending order
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
    vector<int> res = s.singleNumber(nums);
    string out = "[";
    for (size_t a = 0; a < res.size(); a++) {
        if (a) out += ", ";
        out += to_string(res[a]);
    }
    out += "]";
    cout << out << "\n";
    return 0;
}
'''


def build_ref(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_REF)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
                   check=True)
    return binp


def run_ref(binp, nums):
    line = "[" + ", ".join(str(x) for x in nums) + "]"
    p = subprocess.run([binp], input=line + "\n", capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ref failed: " + p.stderr)
    return p.stdout.strip()


def fmt_arr(nums):
    return "[" + ", ".join(str(x) for x in nums) + "]"


def make_case(rng):
    """
    Build a valid nums array: a multiset where every value appears exactly
    twice, plus exactly two DISTINCT singleton values appearing once each.
    Length = 2*num_pairs + 2, must satisfy 2 <= length <= NMAX.

    num_pairs in [0 .. (NMAX-2)//2]. Pair values and singleton values must all
    be distinct from each other (a "pair" value cannot also be a singleton,
    otherwise its count would change). We draw all chosen values distinct.
    """
    # how big is this case
    mode = rng.random()
    if mode < 0.25:
        num_pairs = rng.randint(0, 4)              # tiny
    elif mode < 0.55:
        num_pairs = rng.randint(0, 40)             # small
    elif mode < 0.80:
        num_pairs = rng.randint(0, 2000)           # medium
    elif mode < 0.93:
        num_pairs = rng.randint(0, 20000)          # large-ish
    else:
        num_pairs = rng.randint(0, (NMAX - 2) // 2)  # up to max length

    # decide a value window so we have enough distinct integers to draw
    need = num_pairs + 2
    full = VMAX - VMIN + 1  # 600001 distinct values available
    if need > full:
        num_pairs = full - 2
        need = full

    # pick a (possibly narrow) value range for variety, but wide enough
    if rng.random() < 0.5 and need <= 200:
        span = rng.randint(need, min(full, max(need, 50)))
        center = rng.randint(VMIN + span, VMAX - span) if VMAX - span > VMIN + span else 0
        lo = max(VMIN, center - span)
        hi = min(VMAX, center + span)
        if hi - lo + 1 < need:
            lo, hi = VMIN, VMAX
    else:
        lo, hi = VMIN, VMAX

    population = hi - lo + 1
    if population < need:
        lo, hi = VMIN, VMAX
        population = full

    # sample `need` distinct values (random.sample is efficient even for big ranges)
    chosen = rng.sample(range(lo, hi + 1), need)
    s1, s2 = chosen[0], chosen[1]          # the two singletons (distinct)
    pair_vals = chosen[2:]                 # each appears twice

    arr = [s1, s2]
    for v in pair_vals:
        arr.append(v)
        arr.append(v)
    rng.shuffle(arr)
    return arr, tuple(sorted((s1, s2)))


def main():
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as workdir:
        binp = build_ref(workdir)

        # sanity: reproduce dataset examples
        assert run_ref(binp, [1, 2, 1, 3, 5, 2]) == "[3, 5]", "example1 mismatch"
        assert run_ref(binp, [-1, 0]) == "[-1, 0]", "example2 mismatch"

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

        cases = []  # list of (arr, expected_str)

        def add(arr, expected_pair):
            expected = "[" + str(expected_pair[0]) + ", " + str(expected_pair[1]) + "]"
            cases.append((arr, expected))

        # explicit edge cases
        edge = [
            ([-1, 0], (-1, 0)),                         # min length, from example
            ([0, 1], (0, 1)),
            ([VMIN, VMAX], (VMIN, VMAX)),               # extremes, min length
            ([VMIN, VMIN + 1], (VMIN, VMIN + 1)),
            ([VMAX - 1, VMAX], (VMAX - 1, VMAX)),
            ([1, 2, 1, 3, 5, 2], (3, 5)),               # example1
            ([0, VMAX], (0, VMAX)),
            ([VMIN, 0], (VMIN, 0)),
            ([VMIN, VMAX, 7, 7], (VMIN, VMAX)),
            ([5, 5, -3, -3, 100, -100], (-100, 100)),
        ]
        for arr, exp in edge:
            add(list(arr), tuple(sorted(exp)))

        # one true max-length case (length == NMAX): 49999 pairs + 2 singletons
        max_pairs = (NMAX - 2) // 2
        chosen = rng.sample(range(VMIN, VMAX + 1), max_pairs + 2)
        s1, s2 = chosen[0], chosen[1]
        big = [s1, s2]
        for v in chosen[2:]:
            big.append(v); big.append(v)
        rng.shuffle(big)
        add(big, tuple(sorted((s1, s2))))

        while len(cases) < N_CASES:
            arr, exp = make_case(rng)
            # validate structurally + bounds
            if not (2 <= len(arr) <= NMAX):
                continue
            if not all(VMIN <= x <= VMAX for x in arr):
                continue
            add(arr, exp)

        cases = cases[:N_CASES]

        with open(OUT_PATH, "w") as f:
            for arr, expected in cases:
                got = run_ref(binp, arr)
                # cross-check oracle against our constructed expectation
                if got != expected:
                    raise RuntimeError(
                        "ORACLE/EXPECTED MISMATCH: got %s want %s for arr len %d"
                        % (got, expected, len(arr)))
                obj = {"inputs": {"nums": fmt_arr(arr)}, "expected": expected}
                f.write(json.dumps(obj) + "\n")

    print("Wrote %d cases to %s" % (len(cases), OUT_PATH))


if __name__ == "__main__":
    main()
