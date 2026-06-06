#!/usr/bin/env python3
"""
Test-case generator for Striver problem: zig-zag-or-spiral-traversal.

Problem: Given the root of a binary tree, return the ZIGZAG level order traversal
of its nodes' values (left-to-right on level 0, then right-to-left, alternating).

Signature: vector<vector<int>> zigzagLevelOrder(TreeNode* root)
  -> single input param: root (TreeNode*)

Constraints:
  - 1 <= Number of Nodes <= 10^4
  - -1000 <= Node.val <= 1000

Serialization (must match the judge EXACTLY):
  - TreeNode* input: level-order, space-separated, "null" for missing child,
    LeetCode-style (null nodes get no children). Judge struct field is `data`.
  - vector<vector<int>> output: flattened to space-separated numbers on one line
    (judge compares leniently, ignoring brackets/commas/whitespace).

This script:
  1. Builds random valid binary trees in the level-order "null"-padded form.
  2. Runs the compiled C++ reference (which builds the tree exactly like the
     judge and emits the flattened zigzag level-order) to get expected output.
  3. Writes generated-tests/zig-zag-or-spiral-traversal.jsonl (one obj per line):
       {"inputs": {"root": "<level-order string>"}, "expected": "<flattened>"}
"""
import json
import os
import random
import subprocess
import tempfile
import shutil
from collections import deque

VAL_MIN, VAL_MAX = -1000, 1000   # -1000 <= Node.val <= 1000
MAX_NODES = 10000                # 1 <= Number of Nodes <= 10^4
N_CASES = 2000
SEED = 6062026

ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(ROOT, "generated-tests", "zig-zag-or-spiral-traversal.jsonl")

# C++ reference — same tree-build as the judge (LeetCode level-order, ".data"
# field, "null" tokens for missing children, null nodes get no children).
REF_SRC = r'''
#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;
struct TreeNode { int data; TreeNode *left,*right; TreeNode(int v):data(v),left(nullptr),right(nullptr){} };
TreeNode* build(const string& s){
    istringstream iss(s); vector<string> toks; string t;
    while(iss>>t) toks.push_back(t);
    if(toks.empty()||toks[0]=="null") return nullptr;
    TreeNode* root=new TreeNode(stoi(toks[0]));
    queue<TreeNode*> q; q.push(root); size_t i=1;
    while(!q.empty()&&i<toks.size()){
        TreeNode* cur=q.front();q.pop();
        if(i<toks.size()){ if(toks[i]!="null"){cur->left=new TreeNode(stoi(toks[i]));q.push(cur->left);} i++; }
        if(i<toks.size()){ if(toks[i]!="null"){cur->right=new TreeNode(stoi(toks[i]));q.push(cur->right);} i++; }
    }
    return root;
}
vector<vector<int>> zigzagLevelOrder(TreeNode* root){
    vector<vector<int>> ans; if(!root) return ans;
    queue<TreeNode*> q; q.push(root);
    bool ltor=true;
    while(!q.empty()){
        int n=q.size();
        vector<int> lvl(n);
        for(int i=0;i<n;i++){
            TreeNode* c=q.front();q.pop();
            int pos = ltor ? i : (n-1-i);
            lvl[pos] = c->data;
            if(c->left)  q.push(c->left);
            if(c->right) q.push(c->right);
        }
        ans.push_back(lvl);
        ltor = !ltor;
    }
    return ans;
}
int main(){
    string line;
    while(getline(cin,line)){
        TreeNode* root=build(line);
        auto res=zigzagLevelOrder(root);
        string out; bool first=true;
        for(auto& l:res) for(int v:l){ if(!first) out+=" "; out+=to_string(v); first=false; }
        cout<<out<<"\n";
    }
    return 0;
}
'''


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


def gen_tree_levelorder(n):
    """Random binary tree with exactly n nodes (n>=1) -> level-order string."""
    assert n >= 1
    # nodes[i] = [val, left_idx_or_None, right_idx_or_None]
    nodes = [[rand_val(), None, None]]
    open_slots = [(0, 1), (0, 2)]
    for _ in range(n - 1):
        si = random.randrange(len(open_slots))
        parent, side = open_slots.pop(si)
        idx = len(nodes)
        nodes.append([rand_val(), None, None])
        nodes[parent][side] = idx
        open_slots.append((idx, 1))
        open_slots.append((idx, 2))
    return serialize(nodes)


def serialize(nodes):
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


def gen_left_skewed(n):
    """All left children — tokens: v1 v2 null v3 null ... trailing nulls trimmed."""
    assert n >= 1
    if n == 1:
        return str(rand_val())
    out = [str(rand_val())]
    for i in range(1, n):
        out.append(str(rand_val()))
        if i < n - 1:
            out.append("null")
    return " ".join(out)


def gen_right_skewed(n):
    """All right children — root, then (null, val), (null, val), ..."""
    assert n >= 1
    if n == 1:
        return str(rand_val())
    out = [str(rand_val())]
    for _ in range(n - 1):
        out.append("null")
        out.append(str(rand_val()))
    return " ".join(out)


def gen_complete(n):
    """Array-style complete tree — first n positions filled L->R."""
    assert n >= 1
    return " ".join(str(rand_val()) for _ in range(n))


def build_inputs():
    random.seed(SEED)
    inputs = []

    # ---- Edge / boundary cases ----
    inputs.append("0")                       # single node value 0
    inputs.append(str(VAL_MIN))              # single node min val
    inputs.append(str(VAL_MAX))              # single node max val
    inputs.append(f"{VAL_MIN} {VAL_MAX}")    # two nodes extremes
    inputs.append("5 null 3")                # right-only child
    inputs.append("5 3 null")                # left-only child (note: trailing null normally trimmed; explicit form ok)
    inputs.append("5 3")                     # left-only child, trimmed form
    inputs.append("1 2 3 4 5 6 7")           # perfect tree depth 3
    inputs.append("1 2 3 null 4 8 5")        # example 1
    inputs.append("3 9 20 null null 15 7")   # example 2
    inputs.append("1 2 3 null null 4 5")     # example 3
    inputs.append("5 1 2 8 null 4 5 null 6") # nowYourTurn

    # Long skewed chains (output is small, single column)
    inputs.append(gen_left_skewed(200))
    inputs.append(gen_right_skewed(200))
    inputs.append(gen_left_skewed(500))
    inputs.append(gen_right_skewed(500))

    # Moderate complete trees
    inputs.append(gen_complete(31))
    inputs.append(gen_complete(63))
    inputs.append(gen_complete(127))
    inputs.append(gen_complete(255))

    # A couple of medium random trees
    inputs.append(gen_tree_levelorder(400))
    inputs.append(gen_tree_levelorder(600))

    # ---- small exhaustive-ish sizes ----
    for n in range(1, 13):
        for _ in range(8):
            inputs.append(gen_tree_levelorder(n))

    # ---- random varied sizes ----
    # CRITICAL: the judge's batched runner caps TOTAL stdout for the whole process
    # at 256 KB (262144 bytes); once exceeded, every later case's output line is
    # truncated and fails. Each node contributes ~3-5 chars to its case's output
    # line, so we keep the bulk of cases tiny. Constraint allows up to 10^4 nodes,
    # but we DON'T need to max it every time.
    while len(inputs) < N_CASES:
        r = random.random()
        if r < 0.85:
            n = random.randint(1, 12)      # vast majority: tiny trees
        elif r < 0.96:
            n = random.randint(1, 40)      # some small/medium trees
        elif r < 0.995:
            n = random.randint(1, 100)     # a few larger
        else:
            n = random.randint(1, 250)     # very few medium
        shape = random.random()
        if shape < 0.7:
            inputs.append(gen_tree_levelorder(n))
        elif shape < 0.85:
            inputs.append(gen_left_skewed(n))
        else:
            inputs.append(gen_right_skewed(n))

    return inputs[:N_CASES]


def main():
    tmp = tempfile.mkdtemp(prefix="zzref_")
    try:
        src = os.path.join(tmp, "ref.cpp")
        binp = os.path.join(tmp, "ref")
        with open(src, "w") as f:
            f.write(REF_SRC)
        subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
            check=True,
        )

        # Sanity: reproduce dataset example outputs.
        sample_inputs = [
            "1 2 3 null 4 8 5",
            "3 9 20 null null 15 7",
        ]
        stdin = "\n".join(sample_inputs) + "\n"
        proc = subprocess.run([binp], input=stdin, capture_output=True, text=True, check=True)
        sample_outs = proc.stdout.split("\n")
        if sample_outs and sample_outs[-1] == "":
            sample_outs = sample_outs[:-1]
        expected_flat = ["1 3 2 4 8 5", "3 20 9 15 7"]
        for got, exp in zip(sample_outs, expected_flat):
            assert got.split() == exp.split(), f"REFERENCE FAILED dataset example: got {got!r} expected {exp!r}"
        print(f"reference reproduces dataset examples OK: {sample_outs}")

        inputs = build_inputs()
        stdin_data = "\n".join(inputs) + "\n"
        proc = subprocess.run([binp], input=stdin_data,
                              capture_output=True, text=True, check=True)
        outs = proc.stdout.split("\n")
        if outs and outs[-1] == "":
            outs = outs[:-1]
        assert len(outs) == len(inputs), f"output count {len(outs)} != input count {len(inputs)}"

        # Total expected-output byte budget for the judge's 256KB cap
        total_bytes = sum(len(o) + 1 for o in outs)
        print(f"Total expected-output bytes: {total_bytes}")
        if total_bytes > 240_000:
            print("WARNING: total expected output is close to/over the 256KB cap")

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
