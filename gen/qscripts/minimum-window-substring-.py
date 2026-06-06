#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Minimum Window Substring (slug: minimum-window-substring-)

Signature (starterCpp):  string minWindow(string s, string t)
Input keys (in signature order): s, t   (both raw strings)

Constraints:
  1 <= n, m <= 1e5,  n = s.length, m = t.length
  s and t consist of uppercase and lowercase letters (A-Z, a-z).

Output format (mirrors dataset examples): non-empty result wrapped in double quotes,
e.g. "BANC". No-match -> empty string "" (judge compares leniently, ignoring quotes/ws).

The expected output is produced by a verified C++ reference (sliding window),
compiled once to /tmp/mws/ref and invoked per case (s on line 1, t on line 2).
"""
import os, random, subprocess, sys

REF_SRC = """
#include <iostream>
#include <string>
#include <unordered_map>
#include <climits>
using namespace std;
string minWindow(string s, string t) {
    unordered_map<char, int> mp;
    for (auto it : t) mp[it]++;
    int count = mp.size();
    int start = 0, minlen = INT_MAX;
    int substrBegin = 0;
    for (int i = 0; i < (int)s.size(); i++) {
        mp[s[i]]--;
        if (mp[s[i]] == 0) count--;
        while (count == 0) {
            if (i - start + 1 < minlen) { substrBegin = start; minlen = i - start + 1; }
            mp[s[start]]++;
            if (mp[s[start]] > 0) count++;
            start++;
        }
    }
    return (minlen == INT_MAX) ? "" : s.substr(substrBegin, minlen);
}
int main(){
    string s, t;
    if(!getline(cin, s)) return 0;
    getline(cin, t);
    cout << minWindow(s, t) << "\\n";
    return 0;
}
"""

TMP = "/tmp/mws"
REF_BIN = os.path.join(TMP, "ref")
OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-window-substring-.jsonl"
N_CASES = 2000
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def build_ref():
    os.makedirs(TMP, exist_ok=True)
    src = os.path.join(TMP, "ref_gen.cpp")
    with open(src, "w") as f:
        f.write(REF_SRC)
    r = subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", REF_BIN])
    if r.returncode != 0:
        sys.exit("ref compile failed")

def run_ref(s, t):
    p = subprocess.run([REF_BIN], input=(s + "\n" + t + "\n"),
                       capture_output=True, text=True)
    # last line is the result (could be empty)
    return p.stdout.rstrip("\n")

def rand_str(n, alphabet=LETTERS):
    return "".join(random.choice(alphabet) for _ in range(n))

def make_case(idx):
    """Return (s, t). Mix of guaranteed-match and possibly-no-match cases."""
    r = random.random()
    if idx == 0:
        return "ADOBECODEBANC", "ABC"        # dataset example 1
    if idx == 1:
        return "a", "a"                       # dataset example 2 (min size)
    if idx == 2:
        return "aAbBDdcC", "Bc"               # nowYourTurn case
    if idx == 3:
        return "ABsd", "ABsdEh"               # dataset case 3 -> no match
    if r < 0.10:
        # tiny edge: single chars
        a = random.choice(LETTERS)
        b = random.choice(LETTERS)
        return a, b
    if r < 0.25:
        # small random alphabet, small lengths -> stresses matching/no-match
        alpha = "".join(random.sample(LETTERS, random.randint(2, 5)))
        n = random.randint(1, 30)
        m = random.randint(1, 6)
        return rand_str(n, alpha), rand_str(m, alpha)
    if r < 0.55:
        # guaranteed-match: embed t (shuffled, possibly with dup chars) somewhere in s
        alpha = "".join(random.sample(LETTERS, random.randint(3, 12)))
        m = random.randint(1, 15)
        t = rand_str(m, alpha)
        # build s = prefix + (chars of t interleaved with noise) + suffix
        pre = rand_str(random.randint(0, 40), alpha)
        suf = rand_str(random.randint(0, 40), alpha)
        tlist = list(t)
        random.shuffle(tlist)
        mid_parts = []
        for ch in tlist:
            mid_parts.append(ch)
            if random.random() < 0.5:
                mid_parts.append(rand_str(random.randint(0, 3), alpha))
        s = pre + "".join(mid_parts) + suf
        return s, t
    if r < 0.80:
        # medium random
        alpha = "".join(random.sample(LETTERS, random.randint(2, 20)))
        n = random.randint(10, 400)
        m = random.randint(1, 40)
        return rand_str(n, alpha), rand_str(m, alpha)
    if r < 0.92:
        # larger random over full alphabet
        n = random.randint(100, 2000)
        m = random.randint(1, 60)
        return rand_str(n), rand_str(m)
    # near-max stress (kept under control for speed): big s, modest t guaranteed match
    alpha = "".join(random.sample(LETTERS, random.randint(4, 26)))
    n = random.randint(2000, 20000)
    s = list(rand_str(n, alpha))
    m = random.randint(1, 30)
    t = rand_str(m, alpha)
    return "".join(s), t

def fmt_expected(res):
    # mirror dataset examples: wrap non-empty in quotes; empty -> ""
    if res == "":
        return '""'
    return '"' + res + '"'

def json_escape(x):
    out = []
    for ch in x:
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        else:
            out.append(ch)
    return "".join(out)

def main():
    build_ref()
    random.seed(20260606)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lines = []
    for i in range(N_CASES):
        s, t = make_case(i)
        # safety: enforce constraints (only letters, 1..1e5)
        assert 1 <= len(s) <= 100000 and 1 <= len(t) <= 100000
        assert all(c in LETTERS for c in s) and all(c in LETTERS for c in t)
        res = run_ref(s, t)
        exp = fmt_expected(res)
        line = ('{"inputs": {"s": "%s", "t": "%s"}, "expected": "%s"}'
                % (json_escape(s), json_escape(t), json_escape(exp)))
        lines.append(line)
    with open(OUT, "w") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", len(lines), "cases to", OUT)

if __name__ == "__main__":
    main()
