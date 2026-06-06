#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Count Inversions (slug: count-inversions)

Problem:
  long long int numberOfInversions(vector<int> nums)
  Return the number of inversions: pairs (i, j) with i < j and nums[i] > nums[j].

Constraints:
  1 <= nums.length <= 1e5
  -1e4 <= nums[i] <= 1e4

Output line format (.jsonl):
  {"inputs": {"nums": "[...]"}, "expected": "<count>"}

This script:
  1. Compiles a C++ merge-sort oracle (reference algorithm verified against the
     dataset's example outputs).
  2. Generates random + edge-case inputs strictly within constraints.
  3. Runs the oracle to get expected outputs.
  4. Writes the .jsonl file.

Re-runnable; deterministic via fixed RNG seed.
"""

import os
import random
import subprocess
import tempfile
import json

SEED = 20240606
N_CASES = 2000
LEN_MAX = 100_000          # nums.length <= 1e5
VAL_LO, VAL_HI = -10_000, 10_000  # -1e4 <= nums[i] <= 1e4

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-inversions.jsonl"

ORACLE_SRC = r'''
#include <iostream>
#include <vector>
#include <string>
using namespace std;
long long mergeCount(vector<int>& a, int s, int e){
    if(s>=e) return 0;
    int m=s+(e-s)/2; long long c=0;
    c+=mergeCount(a,s,m); c+=mergeCount(a,m+1,e);
    vector<int> L(a.begin()+s,a.begin()+m+1), R(a.begin()+m+1,a.begin()+e+1);
    int i=0,j=0,k=s,ls=L.size(),rs=R.size();
    while(i<ls&&j<rs){ if(L[i]>R[j]){c+=(long long)(ls-i);a[k++]=R[j++];} else a[k++]=L[i++]; }
    while(i<ls)a[k++]=L[i++]; while(j<rs)a[k++]=R[j++];
    return c;
}
int main(){
    string line;
    while(getline(cin,line)){
        vector<int> nums; string cur;
        for(char ch: line){
            if(ch=='-'||(ch>='0'&&ch<='9')) cur.push_back(ch);
            else { if(!cur.empty()){nums.push_back(stoi(cur));cur.clear();} }
        }
        if(!cur.empty()) nums.push_back(stoi(cur));
        cout << mergeCount(nums,0,(int)nums.size()-1) << "\n";
    }
    return 0;
}
'''


def build_oracle(workdir):
    src = os.path.join(workdir, "oracle.cpp")
    exe = os.path.join(workdir, "oracle")
    with open(src, "w") as f:
        f.write(ORACLE_SRC)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", exe],
        check=True,
    )
    return exe


def rand_len(rng):
    """Pick an array length biased toward small/medium, but include big ones."""
    r = rng.random()
    if r < 0.55:
        return rng.randint(1, 50)        # many tiny/small cases
    elif r < 0.80:
        return rng.randint(51, 500)
    elif r < 0.93:
        return rng.randint(501, 5000)
    else:
        return rng.randint(5001, LEN_MAX)


def rand_array(rng):
    """Random array within value bounds; varied distributions."""
    n = rand_len(rng)
    mode = rng.random()
    if mode < 0.25:
        # full range random
        return [rng.randint(VAL_LO, VAL_HI) for _ in range(n)]
    elif mode < 0.45:
        # small value range -> many duplicates / ties
        lo = rng.randint(VAL_LO, VAL_HI - 5)
        hi = min(VAL_HI, lo + rng.randint(1, 10))
        return [rng.randint(lo, hi) for _ in range(n)]
    elif mode < 0.60:
        # nearly sorted ascending with small perturbations
        base = sorted(rng.randint(VAL_LO, VAL_HI) for _ in range(n))
        for _ in range(max(1, n // 20)):
            i, j = rng.randrange(n), rng.randrange(n)
            base[i], base[j] = base[j], base[i]
        return base
    elif mode < 0.72:
        # sorted ascending (0 inversions)
        return sorted(rng.randint(VAL_LO, VAL_HI) for _ in range(n))
    elif mode < 0.84:
        # sorted descending (max inversions)
        return sorted((rng.randint(VAL_LO, VAL_HI) for _ in range(n)), reverse=True)
    elif mode < 0.92:
        # all same value (0 inversions)
        v = rng.randint(VAL_LO, VAL_HI)
        return [v] * n
    else:
        # negatives heavy / extremes mix
        return [rng.choice([VAL_LO, VAL_HI, 0, rng.randint(VAL_LO, VAL_HI)]) for _ in range(n)]


def edge_cases():
    cases = []
    cases.append([0])                                  # min length, single
    cases.append([VAL_LO])                             # single extreme low
    cases.append([VAL_HI])                             # single extreme high
    cases.append([VAL_LO, VAL_HI])                     # sorted pair, 0 inv
    cases.append([VAL_HI, VAL_LO])                     # reversed pair, 1 inv
    cases.append([5, 5])                               # equal pair, 0 inv
    cases.append([1, 2, 3, 4, 5])                      # sorted, 0
    cases.append([5, 4, 3, 2, 1])                      # reversed, 10
    cases.append([2, 3, 7, 1, 3, 5])                   # dataset example 1 -> 5
    cases.append([-10, -5, 6, 11, 15, 17])             # dataset example 2 -> 0
    cases.append([9, 5, 4, 2])                         # nowYourTurn -> 6
    cases.append([VAL_HI] * 1000)                      # all equal large block
    cases.append(list(range(VAL_LO, VAL_LO + 1000)))   # ascending block
    cases.append(list(range(VAL_HI, VAL_HI - 1000, -1)))  # descending block (max inv)
    # max-size all-equal (cheap, valid)
    cases.append([0] * LEN_MAX)
    # max-size sorted ascending (0 inv) using clamped values
    asc = [VAL_LO + (i % (VAL_HI - VAL_LO + 1)) for i in range(LEN_MAX)]
    cases.append(asc)
    return cases


def to_array_str(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def main():
    rng = random.Random(SEED)
    workdir = tempfile.mkdtemp(prefix="invgen_")
    exe = build_oracle(workdir)

    # Build the list of input arrays
    inputs = []
    edges = edge_cases()
    inputs.extend(edges)
    while len(inputs) < N_CASES:
        inputs.append(rand_array(rng))
    inputs = inputs[:N_CASES]

    # Feed all arrays to the oracle (one per line)
    stdin_lines = "\n".join(to_array_str(a) for a in inputs) + "\n"
    proc = subprocess.run([exe], input=stdin_lines, capture_output=True, text=True, check=True)
    outputs = proc.stdout.strip("\n").split("\n")
    assert len(outputs) == len(inputs), f"oracle produced {len(outputs)} outputs for {len(inputs)} inputs"

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        for arr, exp in zip(inputs, outputs):
            obj = {"inputs": {"nums": to_array_str(arr)}, "expected": exp}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(inputs)} cases to {OUT_PATH}")
    print(f"Oracle: {exe}")


if __name__ == "__main__":
    main()
