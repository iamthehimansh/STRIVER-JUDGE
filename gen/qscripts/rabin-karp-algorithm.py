#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Rabin Karp Algorithm.

Problem: vector<int> search(string pat, string txt)
  Given a text string `txt` and a pattern string `pat`, return the starting
  indices (0-based) of all occurrences of `pat` inside `txt`. If the pattern is
  not present, return an empty list.

Constraints:
  1 <= text.length, pattern.length <= 5*10^4

Method signature param names (in order): pat, txt.  These are used as the JSONL
input keys, matching the judge's `bindInputs` which name-matches first.

Output format (as in dataset examples): the occurrences as a list. The judge
compares leniently (ignoring brackets/commas/whitespace), and the batch harness
prints a vector<int> as space-separated numbers. We therefore emit the expected
value as space-separated indices, e.g. "2 5 10". An empty result is the empty
string "".

This script embeds a verified C++ reference (an actual Rabin-Karp rolling-hash
implementation), compiles it, and uses it as the ground-truth oracle for every
generated case. Every case is also cross-validated against a pure-python brute
force matcher (str.find loop).
"""

import os
import random
import subprocess
import tempfile
import json

SLUG = "rabin-karp-algorithm"
OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/rabin-karp-algorithm.jsonl"
N_CASES = 2000
MAX_LEN = 50000  # 5 * 10^4

# Reference uses lowercase ascii letters + a few symbols so it stays printable
# and round-trips cleanly through the raw-string / JSON pipeline. (The problem
# does not restrict the alphabet beyond "string", so any printable chars are
# fine; we deliberately avoid whitespace, brackets, commas, quotes and
# backslashes so the value never collides with the JSONL or harness tokenizers.)
ALPHABETS = {
    "binary": "ab",
    "tiny": "abc",
    "small": "abcde",
    "lower": "abcdefghijklmnopqrstuvwxyz",
}

REFERENCE_CPP = r"""
#include <iostream>
#include <string>
#include <vector>
using namespace std;

class Solution {
public:
    // Classic Rabin-Karp with double hashing to avoid spurious collisions.
    vector<int> search(string pat, string txt) {
        vector<int> res;
        int n = (int)txt.size();
        int m = (int)pat.size();
        if (m > n) return res;
        if (m == 0) return res;

        const long long MOD1 = 1000000007LL, MOD2 = 998244353LL;
        const long long B1 = 131, B2 = 137;

        long long ph1 = 0, ph2 = 0, th1 = 0, th2 = 0;
        long long pw1 = 1, pw2 = 1; // B^(m-1)
        for (int i = 0; i < m - 1; ++i) { pw1 = (pw1 * B1) % MOD1; pw2 = (pw2 * B2) % MOD2; }

        for (int i = 0; i < m; ++i) {
            ph1 = (ph1 * B1 + (unsigned char)pat[i]) % MOD1;
            ph2 = (ph2 * B2 + (unsigned char)pat[i]) % MOD2;
            th1 = (th1 * B1 + (unsigned char)txt[i]) % MOD1;
            th2 = (th2 * B2 + (unsigned char)txt[i]) % MOD2;
        }

        for (int i = 0; i + m <= n; ++i) {
            if (th1 == ph1 && th2 == ph2) {
                // verify to be 100% safe against rare collisions
                bool ok = true;
                for (int j = 0; j < m; ++j) {
                    if (txt[i + j] != pat[j]) { ok = false; break; }
                }
                if (ok) res.push_back(i);
            }
            if (i + m < n) {
                th1 = ((th1 - (unsigned char)txt[i] * pw1 % MOD1) % MOD1 + MOD1) % MOD1;
                th1 = (th1 * B1 + (unsigned char)txt[i + m]) % MOD1;
                th2 = ((th2 - (unsigned char)txt[i] * pw2 % MOD2) % MOD2 + MOD2) % MOD2;
                th2 = (th2 * B2 + (unsigned char)txt[i + m]) % MOD2;
            }
        }
        return res;
    }
};

// Batch driver: each line is "pat<TAB>txt"; prints space-separated indices.
static vector<string> splitTab(const string& s) {
    vector<string> o; string c;
    for (char ch : s) { if (ch == '\t') { o.push_back(c); c.clear(); } else c += ch; }
    o.push_back(c); return o;
}

int main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    Solution sol;
    string line;
    while (getline(cin, line)) {
        // do NOT skip empty lines blindly: a case could (in principle) be blank,
        // but our generator never emits length-0 strings, so a truly empty line
        // is only a trailing artifact. Guard by requiring a tab.
        size_t tab = line.find('\t');
        if (tab == string::npos) { cout << "\n"; continue; }
        vector<string> f = splitTab(line);
        string pat = f.size() > 0 ? f[0] : "";
        string txt = f.size() > 1 ? f[1] : "";
        vector<int> r = sol.search(pat, txt);
        for (size_t i = 0; i < r.size(); ++i) { if (i) cout << ' '; cout << r[i]; }
        cout << "\n";
    }
    cout.flush();
    return 0;
}
"""


def py_reference(pat: str, txt: str):
    """Pure-python brute-force oracle for cross validation."""
    res = []
    m, n = len(pat), len(txt)
    if m == 0 or m > n:
        return res
    start = 0
    while True:
        idx = txt.find(pat, start)
        if idx == -1:
            break
        res.append(idx)
        start = idx + 1
    return res


def rnd_string(rng, length, alphabet):
    return "".join(rng.choice(alphabet) for _ in range(length))


def build_inputs():
    rng = random.Random(987654321)
    cases = []  # list of (pat, txt)

    # ---------------- Deterministic edge cases ----------------
    edge = [
        # dataset examples
        ("abc", "ababcabcababc"),   # -> 2 5 10
        ("ll", "hello"),            # -> 2
        ("gh", "abcdef"),           # -> (empty)
        # min sizes
        ("a", "a"),                 # -> 0
        ("a", "b"),                 # -> (empty)
        ("a", "aaaaa"),             # -> 0 1 2 3 4 (overlapping)
        ("aa", "aaaa"),             # -> 0 1 2 (overlapping)
        ("aaa", "aaaaa"),           # -> 0 1 2
        ("ab", "abab"),             # -> 0 2
        ("aba", "ababa"),           # -> 0 2 (overlapping)
        # pattern longer than text -> empty
        ("abcdef", "abc"),
        # pattern equals text
        ("abcdef", "abcdef"),       # -> 0
        # pattern at the very end
        ("def", "abcdef"),          # -> 3
        # pattern at the very start
        ("abc", "abcdef"),          # -> 0
        # no overlap, repeated
        ("xy", "xyxyxy"),           # -> 0 2 4
        # single char text & pattern, no match
        ("z", "a"),
    ]
    cases.extend(edge)

    # max-length edges
    # 1) huge text of all 'a', pattern "a" -> every index matches
    cases.append(("a", "a" * MAX_LEN))
    # 2) huge text all 'a', pattern "aa" -> 0..MAX_LEN-2
    cases.append(("aa", "a" * MAX_LEN))
    # 3) huge text, pattern not present
    cases.append(("b", "a" * MAX_LEN))
    # 4) huge pattern == huge text -> single match at 0
    big = rnd_string(rng, MAX_LEN, ALPHABETS["lower"])
    cases.append((big, big))
    # 5) huge pattern longer than text -> empty
    cases.append((rnd_string(rng, MAX_LEN, ALPHABETS["small"]), rnd_string(rng, 1000, ALPHABETS["small"])))
    # 6) max text, max-ish pattern present at known position
    txt6 = rnd_string(rng, MAX_LEN, ALPHABETS["small"])
    p6start = rng.randint(0, MAX_LEN - 100)
    pat6 = txt6[p6start:p6start + 100]
    cases.append((pat6, txt6))

    # ---------------- Randomised cases ----------------
    while len(cases) < N_CASES:
        r = rng.random()
        alpha_name = rng.choices(
            ["binary", "tiny", "small", "lower"],
            weights=[0.30, 0.25, 0.25, 0.20],
        )[0]
        alphabet = ALPHABETS[alpha_name]

        if r < 0.35:
            # small sizes: dense coverage, lots of overlaps & matches
            tlen = rng.randint(1, 30)
            txt = rnd_string(rng, tlen, alphabet)
            mlen = rng.randint(1, max(1, tlen))
            if rng.random() < 0.6 and tlen >= mlen:
                # embed an actual substring of txt as the pattern (guaranteed match)
                s = rng.randint(0, tlen - mlen)
                pat = txt[s:s + mlen]
            else:
                pat = rnd_string(rng, mlen, alphabet)
        elif r < 0.6:
            # medium sizes
            tlen = rng.randint(30, 2000)
            txt = rnd_string(rng, tlen, alphabet)
            mlen = rng.randint(1, min(tlen, 50))
            if rng.random() < 0.5:
                s = rng.randint(0, tlen - mlen)
                pat = txt[s:s + mlen]
            else:
                pat = rnd_string(rng, mlen, alphabet)
        elif r < 0.8:
            # large sizes
            tlen = rng.randint(2000, MAX_LEN)
            txt = rnd_string(rng, tlen, alphabet)
            mlen = rng.randint(1, min(tlen, 200))
            if rng.random() < 0.5:
                s = rng.randint(0, tlen - mlen)
                pat = txt[s:s + mlen]
            else:
                pat = rnd_string(rng, mlen, alphabet)
        elif r < 0.9:
            # pattern possibly longer than text (tests the m>n -> empty branch)
            tlen = rng.randint(1, 50)
            mlen = rng.randint(1, 100)
            txt = rnd_string(rng, tlen, alphabet)
            pat = rnd_string(rng, mlen, alphabet)
        else:
            # highly repetitive text to stress overlapping matches
            base = rng.choice(["a", "ab", "abc", "aab", "aba"])
            reps = rng.randint(1, MAX_LEN // len(base))
            txt = (base * reps)[:MAX_LEN]
            mlen = rng.randint(1, min(len(txt), 6))
            if rng.random() < 0.7:
                s = rng.randint(0, len(txt) - mlen)
                pat = txt[s:s + mlen]
            else:
                pat = rnd_string(rng, mlen, "ab")

        # constraints: 1 <= len(pat), len(txt) <= MAX_LEN
        if not (1 <= len(pat) <= MAX_LEN):
            continue
        if not (1 <= len(txt) <= MAX_LEN):
            continue
        cases.append((pat, txt))

    return cases[:N_CASES]


def compile_reference(tmpdir):
    src = os.path.join(tmpdir, "ref.cpp")
    binp = os.path.join(tmpdir, "ref")
    with open(src, "w") as f:
        f.write(REFERENCE_CPP)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def run_reference(binp, cases):
    """Feed all cases as 'pat<TAB>txt' lines; collect one output line per case."""
    payload = "".join(p + "\t" + t + "\n" for (p, t) in cases)
    proc = subprocess.run(
        [binp], input=payload, capture_output=True, text=True, check=True
    )
    # keep ALL lines (including blank ones for empty results) but drop the final
    # trailing newline only.
    out = proc.stdout
    if out.endswith("\n"):
        out = out[:-1]
    out_lines = out.split("\n") if out != "" else []
    # If output is fully empty (all results empty), split gives [''] length 1;
    # handle the general alignment by re-deriving from count.
    if len(out_lines) != len(cases):
        # Reconstruct: the C++ prints exactly one line per input line, so the
        # number of '\n' equals number of cases. Recompute robustly.
        raw = proc.stdout
        out_lines = raw.split("\n")
        # last element after final '\n' is '' -> drop it
        if out_lines and out_lines[-1] == "":
            out_lines.pop()
    if len(out_lines) != len(cases):
        raise RuntimeError(
            f"reference produced {len(out_lines)} outputs for {len(cases)} cases"
        )
    return out_lines


def main():
    cases = build_inputs()

    with tempfile.TemporaryDirectory() as tmpdir:
        binp = compile_reference(tmpdir)

        # Self-test against dataset examples before trusting the oracle.
        sample = [("abc", "ababcabcababc"), ("ll", "hello"), ("gh", "abcdef")]
        expected_sample = ["2 5 10", "2", ""]
        got = run_reference(binp, sample)
        assert got == expected_sample, f"reference failed dataset examples: {got!r}"

        outputs = run_reference(binp, cases)

    # Cross-validate every case against the pure-python brute-force oracle.
    mismatches = 0
    with open(OUT_PATH, "w") as f:
        for (pat, txt), out in zip(cases, outputs):
            py_ans = py_reference(pat, txt)
            py_str = " ".join(str(x) for x in py_ans)
            if py_str != out:
                mismatches += 1
                if mismatches <= 5:
                    print(f"MISMATCH pat={pat!r} txt(len={len(txt)}) "
                          f"cpp={out!r} py={py_str!r}")
            # input keys are EXACTLY the signature param names, in order.
            obj = {"inputs": {"pat": pat, "txt": txt}, "expected": out}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    if mismatches:
        raise RuntimeError(f"{mismatches} oracle mismatches between C++ and python")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")
    print("All cases cross-validated (C++ ref == python brute force).")


if __name__ == "__main__":
    main()
