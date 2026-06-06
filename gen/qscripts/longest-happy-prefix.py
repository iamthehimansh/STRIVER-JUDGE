#!/usr/bin/env python3
"""
Test-case generator for Striver problem: longest-happy-prefix

Signature (starterCpp):  string lps(string s)
=> input key: "s" (raw string), output: longest happy prefix (proper prefix == proper suffix).

Constraints: 1 <= s.length <= 10^4

Reference oracle: KMP / LPS array (compiled C++ at /tmp/lhp_work/ref).
The reference reads one input string per stdin line and prints lps(s) per output line,
so generated strings never contain newlines (alphabet = lowercase English letters,
matching the LeetCode source of this problem).

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/longest-happy-prefix.jsonl
One JSON object per line: {"inputs": {"s": "<raw>"}, "expected": "<raw>"}
"""
import json
import os
import random
import subprocess
import sys

WORK = "/tmp/lhp_work"
REF_SRC = os.path.join(WORK, "ref.cpp")
REF_BIN = os.path.join(WORK, "ref")
OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/longest-happy-prefix.jsonl"

REF_CPP = r'''
#include <iostream>
#include <vector>
#include <string>
using namespace std;
class Solution{
  public:
  string lps(string s) {
    int n = s.size();
    vector<int> pi(n, 0);
    for(int i = 1; i < n; i++){
        int j = pi[i - 1];
        while(j > 0 && s[i] != s[j]) j = pi[j - 1];
        if(s[i] == s[j]) j++;
        pi[i] = j;
    }
    int length = n > 0 ? pi[n - 1] : 0;
    return s.substr(0, length);
  }
};
int main(){
    string line;
    Solution sol;
    while(getline(cin, line)){
        if(!line.empty() && line.back()=='\r') line.pop_back();
        cout << sol.lps(line) << "\n";
    }
    return 0;
}
'''

N_CASES = 2000
MAXLEN = 10000  # 10^4

def ensure_ref():
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(REF_BIN):
        with open(REF_SRC, "w") as f:
            f.write(REF_CPP)
        subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", "-o", REF_BIN, REF_SRC],
            check=True,
        )


def rand_string(rng):
    """Generate a string with length in [1, MAXLEN], lowercase letters,
    biased to produce many strings that actually have happy prefixes."""
    n = rng.randint(1, MAXLEN)
    kind = rng.random()
    if kind < 0.30:
        # small alphabet => more prefix/suffix overlaps
        k = rng.randint(1, 3)
        alpha = [chr(ord('a') + i) for i in range(k)]
        return "".join(rng.choice(alpha) for _ in range(n))
    elif kind < 0.50:
        # periodic-ish: repeat a small block then append a partial copy
        block_len = rng.randint(1, max(1, min(n, 50)))
        k = rng.randint(2, 6)
        alpha = [chr(ord('a') + i) for i in range(k)]
        block = "".join(rng.choice(alpha) for _ in range(block_len))
        reps = n // block_len + 1
        s = (block * reps)
        # cut at n, maybe at a boundary that creates a real prefix==suffix
        return s[:n]
    elif kind < 0.65:
        # prefix p + middle + p  -> guaranteed happy prefix of len |p|
        p_len = rng.randint(1, max(1, n // 2))
        k = rng.randint(2, 8)
        alpha = [chr(ord('a') + i) for i in range(k)]
        p = "".join(rng.choice(alpha) for _ in range(p_len))
        mid_len = n - 2 * p_len
        mid = "".join(rng.choice(alpha) for _ in range(max(0, mid_len)))
        s = (p + mid + p)
        return s[:n]
    else:
        # full lowercase alphabet, mostly no happy prefix
        return "".join(chr(ord('a') + rng.randint(0, 25)) for _ in range(n))


def build_inputs():
    rng = random.Random(20260606)
    inputs = []
    seen = set()

    # ---- explicit edge cases ----
    edge = []
    edge.append("a")                 # min length, single char -> ""
    edge.append("ab")                # no happy prefix -> ""
    edge.append("aa")                # -> "a"
    edge.append("aaa")               # -> "aa"
    edge.append("ababab")            # example -> "abab"
    edge.append("aaaa")              # example -> "aaa"
    edge.append("abc")               # example -> ""
    edge.append("level")             # -> "l"
    edge.append("abab")              # -> "ab"
    edge.append("aabaaab")
    edge.append("a" * MAXLEN)        # max length, all same -> a^(n-1)
    edge.append("ab" * (MAXLEN // 2))  # max even, period 2
    edge.append("abc" * (MAXLEN // 3) + "ab")
    edge.append("z" * (MAXLEN - 1) + "a")  # no happy prefix, max length
    edge.append("abcabcabcabc")
    edge.append("aabbaabbaabb")
    edge.append("xyzxyzxy")          # -> "xyzxy"
    edge.append("abacaba")           # palindrome-ish -> "aba"

    for s in edge:
        if 1 <= len(s) <= MAXLEN and s not in seen:
            seen.add(s)
            inputs.append(s)

    # ---- random cases ----
    while len(inputs) < N_CASES:
        s = rand_string(rng)
        if not (1 <= len(s) <= MAXLEN):
            continue
        if s in seen:
            continue
        # avoid generating only a handful of giant strings; allow dups-of-len but not exact dup
        seen.add(s)
        inputs.append(s)

    return inputs[:N_CASES]


def run_ref(inputs):
    payload = "\n".join(inputs) + "\n"
    res = subprocess.run([REF_BIN], input=payload, capture_output=True, text=True)
    if res.returncode != 0:
        sys.stderr.write(res.stderr)
        raise RuntimeError("reference crashed")
    out_lines = res.stdout.split("\n")
    # last element after final \n is empty
    if out_lines and out_lines[-1] == "":
        out_lines.pop()
    if len(out_lines) != len(inputs):
        raise RuntimeError(
            "mismatch: %d inputs vs %d outputs" % (len(inputs), len(out_lines))
        )
    return out_lines


def main():
    ensure_ref()
    inputs = build_inputs()
    expected = run_ref(inputs)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for s, e in zip(inputs, expected):
            obj = {"inputs": {"s": s}, "expected": e}
            f.write(json.dumps(obj, ensure_ascii=False))
            f.write("\n")

    print("wrote %d cases to %s" % (len(inputs), OUT))


if __name__ == "__main__":
    main()
