#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Job sequencing Problem (slug: job-sequencing-problem).

Method signature (starterCpp):
    vector<int> JobScheduling(vector<vector<int>>& Jobs)

Input param name: "Jobs"  (2D array, Jobs[i] = {JobID, Deadline, Profit})
Output: "<count> <maxProfit>" (two ints on one line)

Constraints:
    1 <= N <= 10^4
    1 <= Deadline <= N
    1 <= Profit <= 500
    JobID is 1..N (sequential, as in examples)

The reference oracle is a C++ solution compiled in a temp dir. We feed it each
generated Jobs array on stdin and capture "cnt profit" as the expected output.

Writes 2000 lines to:
    /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/job-sequencing-problem.jsonl
Each line: {"inputs": {"Jobs": "[[...],[...]]"}, "expected": "<cnt> <profit>"}
"""

import json
import os
import random
import subprocess
import tempfile

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests", "job-sequencing-problem.jsonl")
N_CASES = 2000
PROFIT_MAX = 500
N_MAX = 10**4  # absolute cap from constraints

REF_CPP = r'''
#include <vector>
#include <algorithm>
#include <iostream>
#include <string>
#include <cctype>
using namespace std;
static bool comp(const vector<int>&v1, const vector<int>&v2){ return v1[2] > v2[2]; }
class Solution {
public:
    vector<int> JobScheduling(vector<vector<int>>& jobs) {
        sort(jobs.begin(), jobs.end(), comp);
        int totprofit = 0, cnt = 0, maxdeadline = -1;
        int n = jobs.size();
        for (int i = 0; i < n; i++) maxdeadline = max(maxdeadline, jobs[i][1]);
        vector<int> hash(maxdeadline + 1, -1);
        for (int i = 0; i < n; i++) {
            for (int j = jobs[i][1]; j >= 1; j--) {
                if (hash[j] == -1) { cnt++; hash[j]=jobs[i][0]; totprofit+=jobs[i][2]; break; }
            }
        }
        return {cnt, totprofit};
    }
};
int main() {
    string s, line;
    while (getline(cin, line)) s += line + "\n";
    vector<vector<int>> jobs;
    int depth = 0; vector<int> cur;
    bool inNum=false; long long num=0; int sign=1;
    for (size_t i=0;i<s.size();i++){
        char c=s[i];
        if(c=='['){ depth++; if(depth==2) cur.clear(); }
        else if(c==']'){ if(inNum){cur.push_back((int)(sign*num));inNum=false;num=0;sign=1;} if(depth==2) jobs.push_back(cur); depth--; }
        else if(c=='-'){ sign=-1; inNum=true; }
        else if(isdigit((unsigned char)c)){ inNum=true; num=num*10+(c-'0'); }
        else { if(inNum){cur.push_back((int)(sign*num));inNum=false;num=0;sign=1;} }
    }
    Solution sol; vector<int> res = sol.JobScheduling(jobs);
    cout << res[0] << " " << res[1] << "\n";
    return 0;
}
'''


def build_ref(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(REF_CPP)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def fmt_jobs(jobs):
    # Compact JSON-style 2D array like examples: [[1, 4, 20], ...]
    return "[" + ", ".join("[" + ", ".join(str(x) for x in r) + "]" for r in jobs) + "]"


def run_ref(binp, jobs):
    inp = fmt_jobs(jobs)
    p = subprocess.run([binp], input=inp, capture_output=True, text=True, check=True)
    return p.stdout.strip()


def gen_jobs(n):
    """Generate a valid Jobs array of N jobs satisfying all constraints."""
    jobs = []
    for jid in range(1, n + 1):
        deadline = random.randint(1, n)  # 1 <= Deadline <= N
        profit = random.randint(1, PROFIT_MAX)  # 1 <= Profit <= 500
        jobs.append([jid, deadline, profit])
    return jobs


def make_size():
    # Mix of small and larger sizes; bias toward small/medium for variety,
    # occasionally large up to a practical cap (kept <= 1500 to keep file/time modest,
    # still well within constraint N <= 10^4).
    r = random.random()
    if r < 0.35:
        return random.randint(1, 8)
    elif r < 0.7:
        return random.randint(9, 50)
    elif r < 0.92:
        return random.randint(51, 300)
    else:
        return random.randint(301, 1500)


def main():
    random.seed(20260606)
    with tempfile.TemporaryDirectory() as tmp:
        binp = build_ref(tmp)

        cases = []

        # --- deterministic edge cases ---
        # 1) single job, min everything
        cases.append([[1, 1, 1]])
        # 2) single job, max profit
        cases.append([[1, 1, PROFIT_MAX]])
        # 3) all same deadline=1 -> only one job can run
        cases.append([[1, 1, 10], [2, 1, 40], [3, 1, 30], [4, 1, 20]])
        # 4) all deadline=N -> all jobs schedulable
        cases.append([[1, 4, 10], [2, 4, 40], [3, 4, 30], [4, 4, 20]])
        # 5) the dataset examples
        cases.append([[1, 4, 20], [2, 1, 10], [3, 1, 40], [4, 1, 30]])
        cases.append([[1, 2, 100], [2, 1, 19], [3, 2, 27], [4, 1, 25], [5, 1, 15]])
        cases.append([[1, 1, 100], [2, 2, 200], [3, 2, 150], [4, 3, 500], [5, 3, 450]])
        cases.append([[1, 1, 100], [2, 2, 200], [3, 3, 300], [4, 4, 400]])
        # 6) increasing deadlines, equal profit
        cases.append([[i, i, 100] for i in range(1, 11)])
        # 7) N=2 extremes
        cases.append([[1, 1, 500], [2, 2, 500]])
        cases.append([[1, 2, 1], [2, 1, 500]])
        # 8) all profit max, deadlines spread
        cases.append([[i, random.randint(1, 20), PROFIT_MAX] for i in range(1, 21)])

        # --- random cases ---
        while len(cases) < N_CASES:
            n = make_size()
            cases.append(gen_jobs(n))

        # truncate to exactly N_CASES
        cases = cases[:N_CASES]

        lines = []
        for jobs in cases:
            expected = run_ref(binp, jobs)
            obj = {"inputs": {"Jobs": fmt_jobs(jobs)}, "expected": expected}
            lines.append(json.dumps(obj))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Wrote {len(lines)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
