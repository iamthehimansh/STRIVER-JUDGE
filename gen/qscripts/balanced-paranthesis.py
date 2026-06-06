#!/usr/bin/env python3
"""
Test-case generator for Striver problem: Balanced Paranthesis (Valid Parentheses).

Problem: bool isValid(string str)
  Given a string `str` containing only the characters '(', ')', '{', '}', '[', ']',
  return true if the string is balanced, otherwise false.

Constraints:
  1 <= str.length <= 10^4
  str consists of parentheses only "()[]{}"

Output format (as in dataset examples): "True" / "False" (capitalized).

The single input key is `str` (the method signature only has `str`; the testcases'
leading `n` param is just the length and is dropped).

This script embeds a verified C++ reference (stack-based matcher), compiles it,
and uses it as the ground-truth oracle for every generated case.
"""

import os
import random
import subprocess
import tempfile
import json

SLUG = "balanced-paranthesis"
OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/balanced-paranthesis.jsonl"
N_CASES = 2000
MAX_LEN = 10000  # 10^4

OPEN = "([{"
CLOSE_OF = {"(": ")", "[": "]", "{": "}"}
ALL_CHARS = "()[]{}"

REFERENCE_CPP = r"""
#include <iostream>
#include <string>
#include <stack>
using namespace std;

class Solution {
public:
    bool isValid(string str) {
        stack<char> st;
        for (char c : str) {
            if (c == '(' || c == '[' || c == '{') {
                st.push(c);
            } else {
                if (st.empty()) return false;
                char open = st.top();
                if ((open == '(' && c == ')') ||
                    (open == '[' && c == ']') ||
                    (open == '{' && c == '}')) {
                    st.pop();
                } else {
                    return false;
                }
            }
        }
        return st.empty();
    }
};

int main() {
    // Read each input line literally as the string `str`.
    // Lines may be empty? No: constraint guarantees length >= 1, but we read
    // a length-prefixed protocol to be robust to any character content:
    //   first line: an integer L
    //   next L bytes: the string (no interpretation of newlines needed since
    //   the bracket alphabet has none).
    ios_base::sync_with_stdio(false);
    string token;
    Solution sol;
    // Protocol: read integer length, then read exactly that many chars.
    while (cin >> token) {
        int L = stoi(token);
        // consume the single space/newline after the integer
        string s;
        s.reserve(L);
        char ch;
        // read exactly L non-whitespace chars (the bracket alphabet)
        int got = 0;
        while (got < L && cin.get(ch)) {
            if (ch == '\n' || ch == '\r' || ch == ' ') continue;
            s.push_back(ch);
            got++;
        }
        bool ans = sol.isValid(s);
        cout << (ans ? "True" : "False") << "\n";
    }
    return 0;
}
"""


def py_reference(s: str) -> bool:
    """Pure-python oracle used for spot-check cross validation."""
    st = []
    for c in s:
        if c in OPEN:
            st.append(c)
        else:
            if not st:
                return False
            top = st[-1]
            if CLOSE_OF[top] == c:
                st.pop()
            else:
                return False
    return not st


def gen_balanced(rng, n_pairs):
    """Generate a guaranteed-balanced string with n_pairs pairs."""
    # build by random nesting/sequencing
    out = []
    stack = []
    remaining_open = n_pairs
    # We need to place n_pairs opens and n_pairs closes such that it's balanced.
    total = 2 * n_pairs
    opens_left = n_pairs
    closes_available = 0  # currently open and closeable
    for _ in range(total):
        can_open = opens_left > 0
        can_close = closes_available > 0
        if can_open and (not can_close or rng.random() < 0.5):
            b = rng.choice(OPEN)
            out.append(b)
            stack.append(b)
            opens_left -= 1
            closes_available += 1
        else:
            top = stack.pop()
            out.append(CLOSE_OF[top])
            closes_available -= 1
    return "".join(out)


def gen_random_brackets(rng, length):
    """Random string over the full bracket alphabet (likely unbalanced)."""
    return "".join(rng.choice(ALL_CHARS) for _ in range(length))


def gen_corrupt_balanced(rng, n_pairs):
    """Take a balanced string and corrupt it slightly so it's likely invalid."""
    s = list(gen_balanced(rng, n_pairs))
    if not s:
        return "".join(s)
    op = rng.randint(0, 3)
    if op == 0:
        # flip one char to a random bracket
        i = rng.randrange(len(s))
        s[i] = rng.choice(ALL_CHARS)
    elif op == 1:
        # remove one char
        i = rng.randrange(len(s))
        s.pop(i)
        if not s:
            s = ["("]
    elif op == 2:
        # swap two positions
        if len(s) >= 2:
            i, j = rng.sample(range(len(s)), 2)
            s[i], s[j] = s[j], s[i]
    else:
        # insert a stray closing bracket at front
        s.insert(0, rng.choice(")]}"))
    return "".join(s)


def build_inputs():
    rng = random.Random(12345)
    cases = []

    # ---- Edge cases (deterministic) ----
    edge = [
        "(",            # len 1, unbalanced
        ")",            # len 1, unbalanced
        "[",            # len 1
        "]",            # len 1
        "{",            # len 1
        "}",            # len 1
        "()",           # balanced
        "[]",
        "{}",
        "()[]{}",       # balanced sequence (like example)
        "()[{}()]",     # example 1 -> True
        "[()",          # example 2 -> False
        "{[()]}",       # nowYourTurn -> True
        "([)]",         # interleaved -> False
        "(]",           # mismatch
        "((((",         # all opens
        "))))",         # all closes
        "(((())))",     # deeply nested balanced
        "()()()()()()", # repeated
    ]
    # max-length all-open (unbalanced) and a max-length balanced
    edge.append("(" * MAX_LEN)                 # 10^4 opens, unbalanced
    edge.append(gen_balanced(rng, MAX_LEN // 2))  # 10^4 chars balanced
    edge.append(("()" * (MAX_LEN // 2)))       # 10^4 chars, balanced flat
    edge.append((")(" * (MAX_LEN // 2)))       # 10^4 chars, unbalanced
    edge.append("[]" * (MAX_LEN // 2))
    edge.append("{" * (MAX_LEN // 2) + "}" * (MAX_LEN // 2))  # balanced nested

    for s in edge:
        if 1 <= len(s) <= MAX_LEN:
            cases.append(s)

    # ---- Random generation ----
    while len(cases) < N_CASES:
        r = rng.random()
        if r < 0.30:
            # guaranteed balanced
            n_pairs = rng.randint(1, MAX_LEN // 2)
            s = gen_balanced(rng, n_pairs)
        elif r < 0.65:
            # fully random (any length) - usually invalid but sometimes valid
            length = rng.randint(1, MAX_LEN)
            s = gen_random_brackets(rng, length)
        elif r < 0.85:
            # corrupted balanced (usually invalid, near-miss)
            n_pairs = rng.randint(1, MAX_LEN // 2)
            s = gen_corrupt_balanced(rng, n_pairs)
        else:
            # small lengths to densely cover short strings
            length = rng.randint(1, 12)
            s = gen_random_brackets(rng, length)

        if not (1 <= len(s) <= MAX_LEN):
            # clamp / fix
            if len(s) == 0:
                s = "("
            else:
                s = s[:MAX_LEN]
        # final safety: only allowed chars
        assert all(ch in ALL_CHARS for ch in s)
        assert 1 <= len(s) <= MAX_LEN
        cases.append(s)

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
    """Feed all cases via length-prefixed protocol; collect outputs."""
    payload_parts = []
    for s in cases:
        payload_parts.append(str(len(s)) + "\n" + s + "\n")
    payload = "".join(payload_parts)
    proc = subprocess.run(
        [binp], input=payload, capture_output=True, text=True, check=True
    )
    out_lines = proc.stdout.strip("\n").split("\n")
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
        sample = ["()[{}()]", "[()", "{[()]}"]
        expected_sample = ["True", "False", "True"]
        got = run_reference(binp, sample)
        assert got == expected_sample, f"reference failed dataset examples: {got}"

        outputs = run_reference(binp, cases)

    # Cross-validate every case against the pure-python oracle.
    mismatches = 0
    with open(OUT_PATH, "w") as f:
        for s, out in zip(cases, outputs):
            py_ans = "True" if py_reference(s) else "False"
            if py_ans != out:
                mismatches += 1
            obj = {"inputs": {"str": s}, "expected": out}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    if mismatches:
        raise RuntimeError(f"{mismatches} oracle mismatches between C++ and python")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")
    print("All cases cross-validated (C++ ref == python ref).")


if __name__ == "__main__":
    main()
