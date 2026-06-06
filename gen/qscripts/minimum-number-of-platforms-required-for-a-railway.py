#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
  "Minimum number of platforms required for a railway"
  slug: minimum-number-of-platforms-required-for-a-railway

Signature: int findPlatform(vector<int>& Arrival, vector<int>& Departure)

Constraints:
  1 <= N <= 1e5
  0000 <= Arrival[i] <= Departure[i] <= 2359   (HHMM clock times, in minutes)

Strategy:
  - Generate N pairs. For each train pick a valid arrival HHMM time and a
    departure HHMM time with departure >= arrival.
  - "Valid HHMM time" => hours 00..23, minutes 00..59 (since times are clock
    times in HHMM form, e.g. 0900, 2359). This keeps every value within
    [0000, 2359] and matches the dataset's zero-padded 4-digit format.
  - Expected output computed by an embedded C++ reference (greedy two-pointer).
  - Inputs are emitted as JSON arrays of zero-padded 4-digit strings, exactly
    like the dataset testcases.

Output: one JSON object per line:
  {"inputs": {"Arrival": "[...]", "Departure": "[...]"}, "expected": "3"}
"""
import json, os, random, subprocess, tempfile, shutil

SLUG = "minimum-number-of-platforms-required-for-a-railway"
OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/%s.jsonl" % SLUG
N_CASES = 2000

REF_CPP = r'''
#include <iostream>
#include <vector>
#include <algorithm>
#include <sstream>
#include <string>
using namespace std;
int findPlatform(vector<int>& Arrival, vector<int>& Departure){
    int n = Arrival.size();
    sort(Arrival.begin(), Arrival.end());
    sort(Departure.begin(), Departure.end());
    int i=0,j=0,plat=0,ans=0;
    while(i<n){
        if(Arrival[i]<=Departure[j]){ i++; plat++; ans=max(ans,plat); }
        else { j++; plat--; }
    }
    return ans;
}
int main(){
    int T; if(!(cin>>T)) return 0;
    while(T--){
        int n; cin>>n;
        vector<int> a(n), d(n);
        for(int i=0;i<n;i++) cin>>a[i];
        for(int i=0;i<n;i++) cin>>d[i];
        cout<<findPlatform(a,d)<<"\n";
    }
    return 0;
}
'''

VALID_TIMES = [h*100 + m for h in range(24) for m in range(60)]  # all HHMM clock times
VALID_TIMES.sort()

def fmt4(v):
    return "%04d" % v

def rand_pair():
    a = random.choice(VALID_TIMES)
    # departure >= arrival, also a valid clock time
    choices = [t for t in VALID_TIMES if t >= a]
    d = random.choice(choices)
    return a, d

def make_case(n):
    arr = []
    dep = []
    for _ in range(n):
        a, d = rand_pair()
        arr.append(a); dep.append(d)
    return arr, dep

def build_cases():
    cases = []
    # ---- edge cases ----
    # min size N=1
    cases.append(([900], [1000]))
    cases.append(([0], [0]))            # min value 0000
    cases.append(([2359], [2359]))      # max value
    cases.append(([0], [2359]))         # full span single train
    # arrival == departure of another -> needs separate platforms
    cases.append(([900, 1000, 1100], [1000, 1100, 1200]))
    # all identical (all overlap) -> N platforms
    cases.append(([1000]*10, [1100]*10))
    # all disjoint sequential -> 1 platform
    cases.append(([0, 200, 400, 600], [100, 300, 500, 700]))
    # dataset examples
    cases.append(([900, 940, 950, 1100, 1500, 1800], [910, 1200, 1120, 1130, 1900, 2000]))
    cases.append(([900, 1100, 1235], [1000, 1200, 1240]))
    cases.append(([900, 1100, 1235], [1300, 1200, 1240]))
    # extremes: many trains all at 0000..2359
    cases.append(([0]*50, [2359]*50))
    # a couple of moderately large cases for coverage
    for n in (1000, 5000):
        cases.append(make_case(n))

    # ---- random cases to fill up to N_CASES ----
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 12)        # small
        elif r < 0.85:
            n = random.randint(13, 100)      # medium
        else:
            n = random.randint(100, 1000)    # larger
        cases.append(make_case(n))
    return cases[:N_CASES]

def main():
    random.seed(20240606)
    tmp = tempfile.mkdtemp(prefix="platgen_")
    try:
        cpp = os.path.join(tmp, "ref.cpp")
        binp = os.path.join(tmp, "ref")
        with open(cpp, "w") as f:
            f.write(REF_CPP)
        subprocess.run(["clang++", "-std=c++17", "-O2", "-w", cpp, "-o", binp], check=True)

        cases = build_cases()

        # feed all cases to reference in one batch
        lines = [str(len(cases))]
        for arr, dep in cases:
            lines.append(str(len(arr)))
            lines.append(" ".join(str(x) for x in arr))
            lines.append(" ".join(str(x) for x in dep))
        inp = "\n".join(lines) + "\n"
        proc = subprocess.run([binp], input=inp, capture_output=True, text=True, check=True)
        outs = proc.stdout.strip().split("\n")
        assert len(outs) == len(cases), "ref output count mismatch %d vs %d" % (len(outs), len(cases))

        with open(OUT, "w") as f:
            for (arr, dep), exp in zip(cases, outs):
                arr_s = "[" + ", ".join('"%s"' % fmt4(x) for x in arr) + "]"
                dep_s = "[" + ", ".join('"%s"' % fmt4(x) for x in dep) + "]"
                obj = {"inputs": {"Arrival": arr_s, "Departure": dep_s},
                       "expected": exp.strip()}
                f.write(json.dumps(obj) + "\n")
        print("Wrote %d cases to %s" % (len(cases), OUT))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
