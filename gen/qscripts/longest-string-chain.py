#!/usr/bin/env python3
"""
Generator for Striver problem: Longest String Chain (slug: longest-string-chain)

Method signature (starterCpp):
    int longestStringChain(vector<string>& words)

Param order: [words]  -> JSONL key: "words"
Output: int length of longest chain.

Constraints:
    1 <= words.length <= 1000
    1 <= words[i].length <= 20
    words[i] only lowercase English letters.

Strategy:
  - Build random inputs strictly within constraints, biased toward producing
    real chains (so answers vary), plus pure-random and edge cases.
  - Use a compiled C++ reference oracle (same algorithm as expected solution)
    to compute ground-truth answers. Examples verified before generation.

Writes:
  /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/longest-string-chain.jsonl
"""
import json, os, random, subprocess, tempfile, sys

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT = os.path.join(PROJECT, "generated-tests", "longest-string-chain.jsonl")
N_CASES = 2000
SEED = 20260606

LETTERS = "abcdefghijklmnopqrstuvwxyz"

REF_SRC = r'''
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_map>
using namespace std;
class Solution {
public:
    int longestStringChain(vector<string>& words) {
        sort(words.begin(), words.end(), [](const string& x, const string& y){
            return x.size() < y.size();
        });
        unordered_map<string,int> dp;
        int ans = 1;
        for (auto& w : words) {
            int best = 1;
            for (int k = 0; k < (int)w.size(); k++) {
                string prev = w.substr(0,k) + w.substr(k+1);
                auto it = dp.find(prev);
                if (it != dp.end()) best = max(best, it->second + 1);
            }
            auto it = dp.find(w);
            if (it == dp.end() || best > it->second) dp[w] = best;
            ans = max(ans, dp[w]);
        }
        return ans;
    }
};
int main(){
    int T;
    if(!(cin>>T)) return 0;
    while(T--){
        int n; cin>>n;
        vector<string> words(n);
        for(int i=0;i<n;i++) cin>>words[i];
        Solution s;
        cout << s.longestStringChain(words) << "\n";
    }
    return 0;
}
'''

def compile_ref(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp], check=True)
    return binp

def rand_word(minlen=1, maxlen=20, alphabet=LETTERS):
    L = random.randint(minlen, maxlen)
    return "".join(random.choice(alphabet) for _ in range(L))

def build_chain(start_len, steps, alphabet=LETTERS):
    """Build a list of words forming a predecessor chain by repeated single-char insertions."""
    w = "".join(random.choice(alphabet) for _ in range(start_len))
    chain = [w]
    cur = w
    for _ in range(steps):
        if len(cur) >= 20:
            break
        pos = random.randint(0, len(cur))
        c = random.choice(alphabet)
        cur = cur[:pos] + c + cur[pos:]
        chain.append(cur)
    return chain

def gen_case(idx):
    """Return list of words (each len 1..20, lowercase), 1..1000 words."""
    # Edge cases first
    if idx == 0:
        return ["a"]                                  # min size
    if idx == 1:
        return ["a", "ab", "abc", "abcd", "abcde"]    # example 1
    if idx == 2:
        return ["dog", "dogs", "dots", "dot", "d", "do"]  # example 2
    if idx == 3:
        return [LETTERS[i % 26] for i in range(1000)]  # max words, all len 1 (many dups)
    if idx == 4:
        # single long chain spanning lengths 1..20 -> answer 20
        return build_chain(1, 19)
    if idx == 5:
        return ["x" * 20]                              # single max-length word
    if idx == 6:
        # all identical words
        return ["abc"] * random.randint(1, 50)
    if idx == 7:
        # two-letter alphabet, many words -> dense chains
        words = []
        for _ in range(200):
            words.append(rand_word(1, 8, "ab"))
        return words

    r = random.random()
    if r < 0.45:
        # Chain-rich: several chains + noise
        words = []
        nchains = random.randint(1, 8)
        for _ in range(nchains):
            sl = random.randint(1, 5)
            steps = random.randint(0, 19 - sl + 1)
            words.extend(build_chain(sl, steps))
        # noise
        for _ in range(random.randint(0, 60)):
            words.append(rand_word(1, 20))
        random.shuffle(words)
        # cap at 1000
        return words[:1000] if len(words) > 1000 else words
    elif r < 0.7:
        # Small random alphabet -> incidental chains
        ab = "".join(random.sample(LETTERS, random.randint(2, 5)))
        n = random.randint(1, 300)
        return [rand_word(1, random.randint(1, 12), ab) for _ in range(n)]
    elif r < 0.9:
        # Pure random
        n = random.randint(1, random.choice([10, 50, 200, 1000]))
        return [rand_word(1, 20) for _ in range(n)]
    else:
        # Many short words (length 1..3) with full alphabet
        n = random.randint(1, 1000)
        return [rand_word(1, 3) for _ in range(n)]

def validate(words):
    assert 1 <= len(words) <= 1000, f"bad count {len(words)}"
    for w in words:
        assert 1 <= len(w) <= 20, f"bad word len {len(w)}: {w!r}"
        assert all(c in LETTERS for c in w), f"bad char in {w!r}"

def fmt_array(words):
    # int array of strings -> like example: ["a", "ab", ...]
    return "[" + ", ".join('"' + w + '"' for w in words) + "]"

def main():
    random.seed(SEED)
    work = tempfile.mkdtemp(prefix="lsc_")
    binp = compile_ref(work)

    cases = [gen_case(i) for i in range(N_CASES)]
    for c in cases:
        validate(c)

    # Build batched stdin for the oracle
    lines = [str(len(cases))]
    for c in cases:
        lines.append(str(len(c)))
        lines.append(" ".join(c))
    stdin = "\n".join(lines) + "\n"

    proc = subprocess.run([binp], input=stdin, capture_output=True, text=True, check=True)
    outs = proc.stdout.split()
    assert len(outs) == len(cases), f"oracle produced {len(outs)} outputs for {len(cases)} cases"

    with open(OUT, "w") as f:
        for c, ans in zip(cases, outs):
            obj = {"inputs": {"words": fmt_array(c)}, "expected": ans}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT}")
    # quick stats
    from collections import Counter
    cnt = Counter(int(x) for x in outs)
    print("answer distribution (top):", dict(sorted(cnt.items())[:25]))

if __name__ == "__main__":
    main()
