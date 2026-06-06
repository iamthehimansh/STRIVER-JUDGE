#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "N meetings in one room"
slug: n-meetings-in-one-room

Problem signature (starterCpp):
    int maxMeetings(vector<int>& start, vector<int>& end)

Constraints:
    1 <= N <= 10^5
    0 <= start[i] < end[i] <= 10^5

Output JSONL keys (signature order): "start", "end".
Values formatted like examples: int array -> "[1, 3, 0]".
"expected" is the integer answer as a string.

This script compiles an embedded C++ reference (the accepted greedy solution),
generates 2000 random/edge inputs strictly within constraints, runs the
reference to compute expected outputs, and writes:
    /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/n-meetings-in-one-room.jsonl
"""
import json
import os
import random
import subprocess
import tempfile

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/n-meetings-in-one-room.jsonl"
N_CASES = 2000
VAL_MAX = 10**5          # max end value
N_MAX = 10**5            # max number of meetings

REF_CPP = r'''
#include <iostream>
#include <vector>
#include <algorithm>
#include <utility>
using namespace std;

class Solution {
  public:
  static bool comp(pair<int,int>&p1,pair<int,int>&p2){
    return p1.second<p2.second;
  }
    int maxMeetings(vector<int>& start, vector<int>& end) {
        int n=start.size();
        if(n==0) return 0;
        vector<pair<int,int>>vec;
        for(int i=0;i<n;i++){
            vec.push_back({start[i],end[i]});
        }
        sort(vec.begin(),vec.end(),comp);
        int ans=1,lastfree=vec[0].second;
        for(int i=1;i<n;i++){
            if(vec[i].first>lastfree){
                ans+=1;
                lastfree=vec[i].second;
            }
        }
        return ans;
    }
};

int main(){
    int n;
    while(cin>>n){
        vector<int> start(n), end(n);
        for(int i=0;i<n;i++) cin>>start[i];
        for(int i=0;i<n;i++) cin>>end[i];
        Solution sol;
        cout<<sol.maxMeetings(start,end)<<"\n";
    }
    return 0;
}
'''


def rand_interval():
    """Return (s, e) with 0 <= s < e <= VAL_MAX."""
    s = random.randint(0, VAL_MAX - 1)
    e = random.randint(s + 1, VAL_MAX)
    return s, e


def make_case(idx):
    """Generate one (start_list, end_list) respecting constraints, with edge cases."""
    # A handful of explicit edge cases first.
    if idx == 0:
        return [1, 3, 0, 5, 8, 5], [2, 4, 6, 7, 9, 9]      # example 1
    if idx == 1:
        return [10, 12, 20], [20, 25, 30]                   # example 2
    if idx == 2:
        return [0], [1]                                     # min N, min values
    if idx == 3:
        return [0], [VAL_MAX]                               # min N, max end
    if idx == 4:
        return [VAL_MAX - 1], [VAL_MAX]                     # single tight interval at top
    if idx == 5:
        # all identical intervals -> answer 1
        s, e = 5, 10
        k = 50
        return [s] * k, [e] * k
    if idx == 6:
        # perfectly chained non-overlapping (touching) -> answer 1 (touch not allowed)
        st, en = [], []
        for i in range(20):
            st.append(i)
            en.append(i + 1)
        return st, en  # [0,1),[1,2)... touching -> start==prev end excluded
    if idx == 7:
        # strictly separated gaps -> all selectable
        st, en = [], []
        t = 0
        for i in range(20):
            st.append(t)
            en.append(t + 1)
            t += 3
        return st, en

    # Choose a size profile.
    r = random.random()
    if r < 0.55:
        n = random.randint(1, 30)            # many small cases
    elif r < 0.80:
        n = random.randint(1, 500)           # medium
    elif r < 0.95:
        n = random.randint(1, 5000)          # large
    else:
        n = random.randint(1, N_MAX)         # up to max constraint (sparingly)

    start = [0] * n
    end = [0] * n

    style = random.random()
    if style < 0.20:
        # Small value range to force many overlaps / ties.
        hi = random.randint(1, 20)
        for i in range(n):
            s = random.randint(0, max(0, min(hi - 1, VAL_MAX - 1)))
            e = random.randint(s + 1, min(hi, VAL_MAX))
            start[i] = s
            end[i] = e
    elif style < 0.40:
        # Many duplicates of a few intervals.
        pool = [rand_interval() for _ in range(random.randint(1, 5))]
        for i in range(n):
            s, e = random.choice(pool)
            start[i] = s
            end[i] = e
    else:
        # Fully random within full range.
        for i in range(n):
            s, e = rand_interval()
            start[i] = s
            end[i] = e
    return start, end


def main():
    random.seed(20240606)
    tmpdir = tempfile.mkdtemp(prefix="nmeet_")
    cpp_path = os.path.join(tmpdir, "ref.cpp")
    bin_path = os.path.join(tmpdir, "ref")
    with open(cpp_path, "w") as f:
        f.write(REF_CPP)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", cpp_path, "-o", bin_path],
        check=True,
    )

    cases = [make_case(i) for i in range(N_CASES)]

    # Build batched stdin for the reference (all cases in one run).
    lines = []
    for start, end in cases:
        lines.append(str(len(start)))
        lines.append(" ".join(map(str, start)))
        lines.append(" ".join(map(str, end)))
    stdin_data = "\n".join(lines) + "\n"

    proc = subprocess.run(
        [bin_path], input=stdin_data, capture_output=True, text=True, check=True
    )
    outs = proc.stdout.split()
    assert len(outs) == N_CASES, f"expected {N_CASES} outputs, got {len(outs)}"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for (start, end), expected in zip(cases, outs):
            # Validate constraints defensively.
            n = len(start)
            assert 1 <= n <= N_MAX
            for s, e in zip(start, end):
                assert 0 <= s < e <= VAL_MAX, (s, e)
            obj = {
                "inputs": {
                    "start": "[" + ", ".join(map(str, start)) + "]",
                    "end": "[" + ", ".join(map(str, end)) + "]",
                },
                "expected": str(expected),
            }
            f.write(json.dumps(obj) + "\n")

    print(f"wrote {N_CASES} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
