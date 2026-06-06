#!/usr/bin/env python3
"""Generator for 'Most stones removed with same row or column'.

starterCpp: int maxRemove(vector<vector<int>>& stones, int n)
 -> input keys: "stones" AND "n".
NOTE: The dev-server batch judge (lib/judge/harness.ts buildBatchHarness) REQUIRES
every method parameter to bind to an input column; an unbound trailing `n` makes it
fall back to the 2 example testcases instead of the generated set. So we EMIT `n`
(= number of stones) as a second key so all 2000 generated cases are actually judged.
Constraints: 1 <= n <= 1000 ; 0 <= x[i], y[i] <= 10^4 ; no two stones at same position.

Expected output computed by compiling the C++ reference (ref.cpp) and feeding
each test's stones (one per line) to it; output is the integer max removals.
"""
import os, sys, json, random, subprocess, tempfile, shutil

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/most-stones-removed-with-same-row-or-column.jsonl"
N_CASES = 2000
MAXC = 10000  # coordinate upper bound

REF_SRC = r'''
#include <vector>
#include <unordered_map>
#include <iostream>
#include <sstream>
#include <string>
using namespace std;
class Solution {
public:
    vector<int> parent, rnk;
    int find(int x){ while(parent[x]!=x){ parent[x]=parent[parent[x]]; x=parent[x]; } return x; }
    void uni(int a,int b){ a=find(a); b=find(b); if(a==b) return; if(rnk[a]<rnk[b]) swap(a,b); parent[b]=a; if(rnk[a]==rnk[b]) rnk[a]++; }
    int maxRemove(vector<vector<int>>& stones, int n) {
        int maxRow=0, maxCol=0;
        for(auto&s:stones){ maxRow=max(maxRow,s[0]); maxCol=max(maxCol,s[1]); }
        int total = (maxRow+1) + (maxCol+1);
        parent.resize(total); rnk.assign(total,0);
        for(int i=0;i<total;i++) parent[i]=i;
        unordered_map<int,bool> used;
        for(auto&s:stones){
            int rowNode = s[0];
            int colNode = (maxRow+1) + s[1];
            uni(rowNode, colNode);
            used[rowNode]=true; used[colNode]=true;
        }
        int comps=0;
        for(auto&p:used){ if(find(p.first)==p.first) comps++; }
        return n - comps;
    }
};
vector<vector<int>> parse2D(const string& s){
    vector<vector<int>> res; vector<int> cur; string num; int depth=0;
    for(char c: s){
        if(c=='['){ depth++; if(depth==2) cur.clear(); }
        else if(c==']'){ if(depth==2){ if(!num.empty()){ cur.push_back(stoi(num)); num.clear(); } res.push_back(cur); } depth--; }
        else if(c==','){ if(!num.empty()){ cur.push_back(stoi(num)); num.clear(); } }
        else if(c=='-'||(c>='0'&&c<='9')){ num+=c; }
    }
    return res;
}
int main(){
    string line;
    while(getline(cin,line)){
        if(line.empty()){ cout<<"\n"; continue; }
        vector<vector<int>> stones = parse2D(line);
        int n = stones.size();
        Solution sol;
        cout << sol.maxRemove(stones, n) << "\n";
    }
    return 0;
}
'''

def fmt_stones(stones):
    return "[" + ",".join("[" + str(x) + "," + str(y) + "]" for x, y in stones) + "]"

def gen_random(n, coord_max):
    """n distinct (x,y) points with coords in [0, coord_max]."""
    seen = set()
    pts = []
    # if the coordinate space is too small to hold n distinct points, shrink n
    cap = (coord_max + 1) * (coord_max + 1)
    n = min(n, cap)
    attempts = 0
    while len(pts) < n:
        x = random.randint(0, coord_max)
        y = random.randint(0, coord_max)
        if (x, y) not in seen:
            seen.add((x, y))
            pts.append((x, y))
        attempts += 1
        if attempts > n * 50:
            break
    return pts

def make_cases():
    cases = []
    # explicit edge cases
    cases.append([(0, 0)])                                   # single stone -> 0
    cases.append([(0, 0), (0, 1)])                           # same row -> 1
    cases.append([(0, 0), (1, 0)])                           # same col -> 1
    cases.append([(0, 0), (5, 5)])                           # isolated -> 0
    cases.append([(0, 0), (0, 10000), (10000, 0), (10000, 10000)])  # corners, connected square -> 3
    cases.append([(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 2)])  # example1
    cases.append([(0, 0), (0, 2), (1, 3), (3, 1), (3, 2), (4, 3)])  # example2
    cases.append([(0, 0), (0, 2)])                           # example3
    # a full row of 1000 stones at y from 0..999 (all share row 0) -> 999
    cases.append([(0, y) for y in range(1000)])
    # a full column of 1000 stones -> 999
    cases.append([(x, 0) for x in range(1000)])
    # 1000 stones all isolated (distinct rows & cols) -> 0
    cases.append([(i, i + 5000) for i in range(1000)])

    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.25:
            n = random.randint(1, 5)
            cmax = random.randint(1, 10)
        elif r < 0.55:
            n = random.randint(1, 50)
            cmax = random.randint(5, 50)
        elif r < 0.8:
            n = random.randint(50, 300)
            cmax = random.randint(10, 200)
        else:
            n = random.randint(300, 1000)
            cmax = random.randint(20, MAXC)
        pts = gen_random(n, cmax)
        if pts:
            cases.append(pts)
    return cases[:N_CASES]

def main():
    tmp = tempfile.mkdtemp(prefix="stones_gen_")
    try:
        src = os.path.join(tmp, "ref.cpp")
        exe = os.path.join(tmp, "ref")
        with open(src, "w") as f:
            f.write(REF_SRC)
        cc = shutil.which("clang++") or shutil.which("g++")
        subprocess.run([cc, "-std=c++17", "-O2", "-w", src, "-o", exe], check=True)

        cases = make_cases()
        stdin_lines = "\n".join(fmt_stones(c) for c in cases) + "\n"
        proc = subprocess.run([exe], input=stdin_lines, capture_output=True, text=True, check=True)
        outs = proc.stdout.splitlines()
        assert len(outs) == len(cases), f"out {len(outs)} != cases {len(cases)}"

        with open(OUT, "w") as f:
            for c, o in zip(cases, outs):
                obj = {"inputs": {"stones": fmt_stones(c), "n": str(len(c))}, "expected": o.strip()}
                f.write(json.dumps(obj) + "\n")
        print(f"Wrote {len(cases)} cases to {OUT}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    random.seed(12345)
    main()
