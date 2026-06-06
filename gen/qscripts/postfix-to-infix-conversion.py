#!/usr/bin/env python3
"""
Generator for "Postfix to Infix Conversion" (slug: postfix-to-infix-conversion).

Produces /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postfix-to-infix-conversion.jsonl
One JSON object per line: {"inputs": {"postExp": "<raw string>"}, "expected": "\"<infix>\""}

A C++ reference (compiled to /tmp/p2i/ref) is used as the ground-truth oracle.
Run:  python3 postfix-to-infix-conversion.py
"""
import json, os, random, subprocess, sys, tempfile

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postfix-to-infix-conversion.jsonl"
N_CASES = 2000
MAXLEN = 16000          # constraint: 1 <= postExp.length <= 16000
OPS = "+-*/"
LETTERS = "abcdefghijklmnopqrstuvwxyz"

REF_SRC = r'''
#include <iostream>
#include <stack>
#include <string>
using namespace std;
bool isOperand(char ch){ return (ch>='a'&&ch<='z')||(ch>='A'&&ch<='Z')||(ch>='0'&&ch<='9'); }
string postToInfix(string exp){
    stack<string> st;
    for(char ch: exp){
        if(isOperand(ch)) st.push(string(1,ch));
        else { string a=st.top();st.pop(); string b=st.top();st.pop(); st.push("("+b+ch+a+")"); }
    }
    return st.top();
}
int main(){ string line; while(getline(cin,line)) cout<<postToInfix(line)<<"\n"; return 0; }
'''

def build_ref(tmp):
    src = os.path.join(tmp, "ref.cpp")
    exe = os.path.join(tmp, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", exe], check=True)
    return exe

def gen_postfix(num_operators):
    """
    Build a syntactically valid postfix expression with exactly `num_operators`
    binary operators (=> num_operands = num_operators+1, total length = 2*num_operators+1).
    Maintain a virtual stack depth; only emit an operator when depth >= 2.
    """
    out = []
    depth = 0
    operands_left = num_operators + 1
    operators_left = num_operators
    # always must start with an operand
    while operands_left > 0 or operators_left > 0:
        can_operand = operands_left > 0
        can_operator = operators_left > 0 and depth >= 2
        if can_operand and can_operator:
            # bias toward operands early; random choice keeps trees varied
            if random.random() < 0.55:
                out.append(random.choice(LETTERS)); depth += 1; operands_left -= 1
            else:
                out.append(random.choice(OPS)); depth -= 1; operators_left -= 1
        elif can_operand:
            out.append(random.choice(LETTERS)); depth += 1; operands_left -= 1
        elif can_operator:
            out.append(random.choice(OPS)); depth -= 1; operators_left -= 1
        else:
            break
    return "".join(out)

def main():
    random.seed(82420240606)
    cases = []

    # ---- edge cases ----
    cases.append("a")                 # min length 1, single operand
    cases.append("z")
    cases.append("ab+")               # example 1
    cases.append("abc*+")             # example 2
    cases.append("ab*c+")             # left-heavy
    cases.append("ab+c+")
    cases.append("ab-c-")
    cases.append("ab/c/")
    cases.append("abcd+++")           # right skewed
    cases.append("ab+cd+*")
    # a single operand (each distinct letter) -- a few
    for ch in "abcdz":
        cases.append(ch)
    # all-same operand small trees
    cases.append("aa+")
    cases.append("aaa**")
    # all four operators in one tree
    cases.append("ab+cd-*ef/+")
    # max length case: length must be odd (2k+1). 16000 is even, so use 15999.
    cases.append(gen_postfix((15999 - 1) // 2))     # length 15999
    cases.append(gen_postfix((15997 - 1) // 2))     # length 15997

    # ---- random cases across a spread of sizes ----
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.45:
            k = random.randint(0, 8)        # tiny
        elif r < 0.80:
            k = random.randint(0, 60)       # small/medium
        elif r < 0.95:
            k = random.randint(0, 1000)     # large
        else:
            k = random.randint(0, 7999)     # very large (len up to 15999)
        cases.append(gen_postfix(k))

    cases = cases[:N_CASES]

    # sanity: every case valid & within constraints
    for s in cases:
        assert 1 <= len(s) <= MAXLEN, ("len out of range", len(s))
        depth = 0
        for ch in s:
            if ch in OPS:
                assert depth >= 2, ("invalid postfix", s[:40])
                depth -= 1
            else:
                assert ch in LETTERS, ("bad char", ch)
                depth += 1
        assert depth == 1, ("not single result", s[:40])

    with tempfile.TemporaryDirectory() as tmp:
        exe = build_ref(tmp)
        stdin = "\n".join(cases) + "\n"
        res = subprocess.run([exe], input=stdin, capture_output=True, text=True, check=True)
        outs = res.stdout.split("\n")
        # last split element is empty due to trailing newline
        if outs and outs[-1] == "":
            outs.pop()
        assert len(outs) == len(cases), (len(outs), len(cases))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for inp, exp in zip(cases, outs):
            assert exp != "", "empty expected"
            obj = {"inputs": {"postExp": inp}, "expected": '"' + exp + '"'}
            f.write(json.dumps(obj) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")

if __name__ == "__main__":
    main()
