#!/usr/bin/env python3
"""
Test-case generator for Striver problem: serialize-and-de-serialize-bt.

Problem: Design an algorithm to serialize and deserialize a binary tree.

Signature (judge picks the FIRST method in `class Solution`):
    string serialize(TreeNode* root)
The judge builds the TreeNode* from a level-order, "null"-padded token string
and compares the user's returned string to "expected" using the lenient
tokenizer (strips [ ] { } ( ) , " ' and whitespace). So the only way to pass
is for `serialize` to return the LEVEL-ORDER representation with "null" for
missing children of present nodes, trailing "null"s trimmed.

Constraints:
  - 1 <= Number of Nodes <= 10^4
  - 0 <= Node.val <= 10^4

This script:
  1. Builds random valid binary trees in the level-order "null"-padded form.
  2. Runs the compiled C++ reference (level-order serialize matching the judge)
     to compute the expected output for each input.
  3. Writes generated-tests/serialize-and-de-serialize-bt.jsonl (one obj/line):
       {"inputs": {"root": "<level-order string>"}, "expected": "<level-order>"}

NOTE: because the user-visible "expected" is essentially the same level-order
string as the input (just normalized — trailing nulls trimmed, single spaces),
the reference is straightforward and the inputs we feed are already canonical.
"""
import json
import os
import random
import subprocess
import tempfile
import shutil
from collections import deque

VAL_MIN, VAL_MAX = 0, 10000   # 0 <= Node.val <= 10^4
MAX_NODES = 10000             # 1 <= Number of Nodes <= 10^4
N_CASES = 2000
SEED = 20260606

ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(ROOT, "generated-tests", "serialize-and-de-serialize-bt.jsonl")

# Reference: build TreeNode from level-order string EXACTLY like the judge's
# rdTree (LeetCode-style: only present nodes contribute children slots), then
# serialize back via level-order with "null" for missing children of present
# nodes, with trailing "null"s trimmed. This is what the judge expects.
REF_SRC = r'''
#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <sstream>
using namespace std;
struct TreeNode { int data; TreeNode *left,*right; TreeNode(int v):data(v),left(nullptr),right(nullptr){} };

static TreeNode* build(const string& s){
    // Tokenize on any whitespace/comma/brackets/quotes (mirror judge tokens()).
    vector<string> toks; string cur;
    auto flush=[&](){ if(!cur.empty()){ toks.push_back(cur); cur.clear(); } };
    for(char c : s){
        if(c==' '||c=='\t'||c=='\n'||c=='\r'||c==','||c=='['||c==']'||c=='{'||c=='}'||c=='('||c==')'||c=='"'||c=='\''){ flush(); }
        else cur.push_back(c);
    }
    flush();
    if(toks.empty()||toks[0]=="null"||toks[0]=="N") return nullptr;
    TreeNode* root=new TreeNode(stoi(toks[0]));
    queue<TreeNode*> q; q.push(root); size_t i=1;
    while(!q.empty()&&i<toks.size()){
        TreeNode* cur2=q.front(); q.pop();
        if(i<toks.size()){ if(toks[i]!="null"&&toks[i]!="N"){ cur2->left=new TreeNode(stoi(toks[i])); q.push(cur2->left); } i++; }
        if(i<toks.size()){ if(toks[i]!="null"&&toks[i]!="N"){ cur2->right=new TreeNode(stoi(toks[i])); q.push(cur2->right); } i++; }
    }
    return root;
}

// Level-order serialize with "null" for missing children of present nodes;
// trailing "null"s trimmed. Matches the judge's expected output format.
static string serialize_tree(TreeNode* root){
    if(!root) return "";
    vector<string> out;
    queue<TreeNode*> q; q.push(root);
    while(!q.empty()){
        TreeNode* n=q.front(); q.pop();
        if(n){
            out.push_back(to_string(n->data));
            q.push(n->left);
            q.push(n->right);
        } else {
            out.push_back("null");
        }
    }
    while(!out.empty() && out.back()=="null") out.pop_back();
    string res;
    for(size_t i=0;i<out.size();++i){ if(i) res+=' '; res+=out[i]; }
    return res;
}

int main(){
    string line;
    while(getline(cin,line)){
        TreeNode* root=build(line);
        cout<<serialize_tree(root)<<"\n";
    }
    return 0;
}
'''


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


def gen_tree_tokens(n):
    """
    Generate a random binary tree with exactly n nodes (n >= 1) and return its
    level-order "null"-padded token string (LeetCode style: null nodes get
    no children). Trailing "null"s are trimmed.
    """
    assert n >= 1
    # nodes[i] = [val, left_idx_or_None, right_idx_or_None]
    nodes = [[rand_val(), None, None]]
    open_slots = [(0, 1), (0, 2)]   # (parent_idx, side: 1=left,2=right)
    for _ in range(n - 1):
        si = random.randrange(len(open_slots))
        parent, side = open_slots.pop(si)
        idx = len(nodes)
        nodes.append([rand_val(), None, None])
        nodes[parent][side] = idx
        open_slots.append((idx, 1))
        open_slots.append((idx, 2))
    return serialize_nodes(nodes)


def serialize_nodes(nodes):
    """BFS serialize, LeetCode-style, trailing nulls trimmed."""
    toks = []
    q = deque([0])
    while q:
        cur = q.popleft()
        if cur is None:
            toks.append("null")
            continue
        toks.append(str(nodes[cur][0]))
        q.append(nodes[cur][1])
        q.append(nodes[cur][2])
    while toks and toks[-1] == "null":
        toks.pop()
    return " ".join(toks)


def left_chain(n):
    """Each of n nodes has only a LEFT child (last is leaf)."""
    assert n >= 1
    out = [str(rand_val())]
    for i in range(n - 1):
        # current's right is null; current's left is next node
        out.append(str(rand_val()))   # left child of current
        out.append("null")            # right child of current
    # The trailing pattern: ... lastVal null (last's left), then trailing nulls trimmed
    # The above appends val,null pairs for each of the n-1 child positions:
    # produces: r v1 null v2 null ... v_{n-1} null
    # Last "null" trimmed.
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def right_chain(n):
    """Each of n nodes has only a RIGHT child."""
    assert n >= 1
    out = [str(rand_val())]
    for i in range(n - 1):
        out.append("null")             # left child of current is missing
        out.append(str(rand_val()))    # right child of current
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def perfect_tree(depth):
    """A perfect binary tree with 2^depth - 1 nodes (depth >= 1 = single node)."""
    n = (1 << depth) - 1
    toks = [str(rand_val()) for _ in range(n)]
    return " ".join(toks)


def build_inputs():
    random.seed(SEED)
    inputs = []

    # ---- Edge / boundary cases ----
    inputs.append("0")                      # single node, value 0
    inputs.append(str(VAL_MAX))             # single node, max value
    inputs.append(str(rand_val()))          # single random node
    inputs.append(f"{rand_val()} {rand_val()}")        # 2 nodes (root + left)
    inputs.append(f"{rand_val()} null {rand_val()}")   # 2 nodes (root + right)
    inputs.append("5 3 7")                  # 3 nodes complete
    inputs.append("1 2 3 4 5 6 7")          # perfect depth 3
    inputs.append("10 20 30 40 50 60")      # the "nowYourTurn" example
    inputs.append("7 3 15 null null 9 20")  # dataset example 2 shape

    # Chains (kept modest — these blow up output as null padding)
    inputs.append(left_chain(15))
    inputs.append(right_chain(15))
    inputs.append(left_chain(30))
    inputs.append(right_chain(30))

    # Perfect trees
    for depth in range(1, 7):  # 1..6 -> 1..63 nodes
        inputs.append(perfect_tree(depth))

    # ---- small exhaustive-ish sizes ----
    for n in range(1, 13):
        for _ in range(8):
            inputs.append(gen_tree_tokens(n))

    # ---- a handful of LARGER trees (well below the boundary) ----
    # CRITICAL: the judge's batched-process stdout is capped at 256 KB. Each
    # node contributes up to ~6 chars (number + space, with null padding) to
    # its case's single output line. To fit 2000 cases comfortably under that
    # cap, the budget per case averages ~120 bytes, i.e. ~20 nodes/case avg.
    # We include a few mediums for coverage and keep the rest tiny.
    for sz in [300, 250, 200, 180, 160, 140, 120, 100, 90, 80, 60, 50, 40, 30]:
        inputs.append(gen_tree_tokens(sz))

    # ---- bulk: tiny random trees (keeps the total well under 256 KB) ----
    while len(inputs) < N_CASES:
        r = random.random()
        if r < 0.92:
            n = random.randint(1, 12)
        elif r < 0.99:
            n = random.randint(1, 30)
        else:
            n = random.randint(1, 60)
        inputs.append(gen_tree_tokens(n))

    return inputs[:N_CASES]


def main():
    tmp = tempfile.mkdtemp(prefix="sd_ref_")
    try:
        src = os.path.join(tmp, "ref.cpp")
        binp = os.path.join(tmp, "ref")
        with open(src, "w") as f:
            f.write(REF_SRC)
        subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
            check=True,
        )

        inputs = build_inputs()
        stdin_data = "\n".join(inputs) + "\n"
        proc = subprocess.run([binp], input=stdin_data,
                              capture_output=True, text=True, check=True)
        outs = proc.stdout.split("\n")
        if outs and outs[-1] == "":
            outs = outs[:-1]
        assert len(outs) == len(inputs), \
            f"output count {len(outs)} != input count {len(inputs)}"

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w") as f:
            for root_str, expected in zip(inputs, outs):
                obj = {"inputs": {"root": root_str}, "expected": expected}
                f.write(json.dumps(obj) + "\n")
        print(f"Wrote {len(inputs)} cases to {OUT_PATH}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
