#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Non-overlapping Intervals
(slug: non-overlapping-intervals)

Method signature (starterCpp):
    int MaximumNonOverlappingIntervals(vector<vector<int>>& Intervals)

Returns the MINIMUM number of intervals to remove to make the remaining
intervals non-overlapping. Intervals touching at a point (e.g. [1,3] & [3,4])
are considered non-overlapping, so two intervals overlap iff
    a.start < b.end  AND  b.start < a.end   (strict).

Constraints enforced by this generator:
    1 <= Intervals.length <= 1e5   (we cap sizes modestly for the static set)
    0 <= start[i] < end[i] <= 1e5
    Intervals[i].length == 2

Reference oracle: greedy — sort by end, count overlaps where start < running end.
This is implemented in C++ (compiled here) AND independently in Python below;
both are cross-checked to guard against bugs.

Output: generated-tests/non-overlapping-intervals.jsonl, one object per line:
    {"inputs": {"Intervals": "[[1, 2], [2, 3]]"}, "expected": "1"}
"""
import json
import os
import random
import subprocess
import tempfile

SLUG = "non-overlapping-intervals"
BASE = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(BASE, "generated-tests", SLUG + ".jsonl")
N_CASES = 2000
MAX_COORD = 100000  # 1e5 constraint upper bound
SEED = 20260606

random.seed(SEED)

# ----------------------------------------------------------------------------
# Python reference oracle (greedy). Used as primary; C++ used to double-check.
# ----------------------------------------------------------------------------
def solve(intervals):
    n = len(intervals)
    if n < 2:
        return 0
    iv = sorted(intervals, key=lambda x: x[1])
    cnt = 0
    end = iv[0][1]
    for i in range(1, n):
        if iv[i][0] < end:
            cnt += 1
        else:
            end = iv[i][1]
    return cnt


def rand_interval():
    # 0 <= start < end <= MAX_COORD
    s = random.randint(0, MAX_COORD - 1)
    e = random.randint(s + 1, MAX_COORD)
    return [s, e]


def gen_case(idx):
    """Return a list of intervals respecting constraints, with variety."""
    r = idx % 20
    if idx == 0:
        return [[0, 1]]                                  # min size
    if idx == 1:
        return [[0, MAX_COORD]]                          # extremes single
    if idx == 2:
        return [[0, 1], [1, 2], [2, 3], [3, 4]]          # all touching -> 0
    if idx == 3:
        return [[0, MAX_COORD]] * 1  # placeholder, overwritten below
    if r == 0:
        # small random
        k = random.randint(1, 5)
        return [rand_interval() for _ in range(k)]
    if r == 1:
        # many identical intervals -> remove all but one
        k = random.randint(2, 30)
        s = random.randint(0, MAX_COORD - 1)
        e = random.randint(s + 1, MAX_COORD)
        return [[s, e] for _ in range(k)]
    if r == 2:
        # perfectly chained non-overlapping (touching) -> answer 0
        k = random.randint(2, 40)
        pts = sorted(random.sample(range(0, MAX_COORD + 1), k + 1))
        return [[pts[i], pts[i + 1]] for i in range(k)]
    if r == 3:
        # all overlap a common point -> remove all but one
        k = random.randint(2, 30)
        mid = random.randint(1, MAX_COORD - 1)
        out = []
        for _ in range(k):
            s = random.randint(0, mid)
            e = random.randint(mid + 1, MAX_COORD)
            out.append([s, e])
        return out
    if r == 4:
        # tiny coordinate space -> lots of duplicates/overlaps
        k = random.randint(2, 50)
        out = []
        for _ in range(k):
            s = random.randint(0, 4)
            e = random.randint(s + 1, 5)
            out.append([s, e])
        return out
    if r in (5, 6):
        # medium random
        k = random.randint(5, 60)
        return [rand_interval() for _ in range(k)]
    if r == 7:
        # large set, small coord space (dense)
        k = random.randint(80, 300)
        out = []
        for _ in range(k):
            s = random.randint(0, 50)
            e = random.randint(s + 1, 51)
            out.append([s, e])
        return out
    if r == 8:
        # nested intervals
        k = random.randint(2, 20)
        lo = random.randint(0, MAX_COORD // 2 - 1)
        hi = random.randint(MAX_COORD // 2, MAX_COORD)
        out = []
        for _ in range(k):
            s = random.randint(lo, (lo + hi) // 2)
            e = random.randint((lo + hi) // 2 + 1, hi)
            out.append([s, e])
        return out
    if r == 9:
        # large random, wide coords
        k = random.randint(100, 500)
        return [rand_interval() for _ in range(k)]
    # default: general random
    k = random.randint(1, 80)
    return [rand_interval() for _ in range(k)]


def fmt_intervals(iv):
    return "[" + ", ".join("[" + ", ".join(str(x) for x in p) + "]" for p in iv) + "]"


def build_cpp_oracle(workdir):
    inc = os.path.join(workdir, "include", "bits")
    os.makedirs(inc, exist_ok=True)
    with open(os.path.join(inc, "stdc++.h"), "w") as f:
        f.write("#include <algorithm>\n#include <iostream>\n#include <vector>\n"
                "#include <string>\n#include <cctype>\n#include <cstdlib>\n")
    src = os.path.join(workdir, "ref.cpp")
    with open(src, "w") as f:
        f.write(r'''
#include <bits/stdc++.h>
using namespace std;
class Solution {
public:
    int MaximumNonOverlappingIntervals(vector<vector<int>>& Intervals) {
        int n = Intervals.size();
        if (n < 2) return 0;
        sort(Intervals.begin(), Intervals.end(),
             [](const vector<int>&a, const vector<int>&b){ return a[1] < b[1]; });
        int cnt = 0, end = Intervals[0][1];
        for (int i = 1; i < n; i++) {
            if (Intervals[i][0] < end) cnt++;
            else end = Intervals[i][1];
        }
        return cnt;
    }
};
int main(){
    string line;
    while (getline(cin, line)) {
        if (line.empty()) { continue; }
        vector<int> nums; int i=0, n=line.size();
        while (i<n){
            if (line[i]=='-'||isdigit((unsigned char)line[i])){
                int sign=1; if(line[i]=='-'){sign=-1;i++;}
                long v=0; while(i<n&&isdigit((unsigned char)line[i])){v=v*10+(line[i]-'0');i++;}
                nums.push_back((int)(sign*v));
            } else i++;
        }
        vector<vector<int>> iv;
        for (size_t k=0;k+1<nums.size();k+=2) iv.push_back({nums[k],nums[k+1]});
        Solution s; cout << s.MaximumNonOverlappingIntervals(iv) << "\n";
    }
    return 0;
}
''')
    exe = os.path.join(workdir, "ref")
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w",
         "-I" + os.path.join(workdir, "include"), src, "-o", exe],
        check=True)
    return exe


def main():
    workdir = tempfile.mkdtemp(prefix="noi_")
    cpp_exe = None
    try:
        cpp_exe = build_cpp_oracle(workdir)
    except Exception as e:
        print("WARN: C++ oracle unavailable (%s); using Python oracle only." % e)

    cases = [gen_case(i) for i in range(N_CASES)]
    # fix index-3 placeholder special case: a couple of widely separated singletons
    cases[3] = [[0, 1], [MAX_COORD - 1, MAX_COORD]]

    py_ans = [solve(iv) for iv in cases]

    # Cross-check with C++ oracle if available
    if cpp_exe:
        stdin = "\n".join(fmt_intervals(iv) for iv in cases) + "\n"
        proc = subprocess.run([cpp_exe], input=stdin, capture_output=True, text=True)
        cpp_ans = [int(x) for x in proc.stdout.split()]
        assert len(cpp_ans) == len(cases), \
            "C++ produced %d answers, expected %d" % (len(cpp_ans), len(cases))
        mism = [(i, py_ans[i], cpp_ans[i]) for i in range(len(cases))
                if py_ans[i] != cpp_ans[i]]
        assert not mism, "Oracle mismatch (py vs cpp): %s" % mism[:5]
        print("Cross-check passed: Python oracle == C++ oracle on all %d cases."
              % len(cases))

    with open(OUT, "w") as f:
        for iv, ans in zip(cases, py_ans):
            # constraint validation
            assert 1 <= len(iv), "empty interval list"
            for p in iv:
                assert len(p) == 2, "interval not length 2"
                assert 0 <= p[0] < p[1] <= MAX_COORD, "coord out of bounds: %s" % p
            obj = {"inputs": {"Intervals": fmt_intervals(iv)}, "expected": str(ans)}
            f.write(json.dumps(obj) + "\n")

    print("Wrote %d cases to %s" % (len(cases), OUT))


if __name__ == "__main__":
    main()
