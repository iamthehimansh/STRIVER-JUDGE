#!/usr/bin/env python3
"""
Test-case generator for Striver problem: level-order-traversal.

Problem: Given the root of a binary tree, return the level order traversal of
its nodes' values (level by level, left to right).

Signature: vector<vector<int>> levelOrder(TreeNode* root)
  -> single input param: root (TreeNode*)

Constraints:
  - 0 <= Number of Nodes <= 2000
  - -1000 <= Node.val <= 2000

Serialization (must match the judge EXACTLY):
  - TreeNode* input: level-order, space-separated, "null" for missing child,
    LeetCode-style (null nodes get no children). Judge struct field is `data`.
  - vector<vector<int>> output: flattened to space-separated numbers on one line
    (judge compares leniently, ignoring brackets/commas/whitespace).

This script:
  1. Builds random valid binary trees in the level-order "null"-padded form.
  2. Runs the compiled C++ reference (which builds the tree exactly like the
     judge and emits the flattened level-order) to get expected output.
  3. Writes generated-tests/level-order-traversal.jsonl (one JSON object/line):
       {"inputs": {"root": "<level-order string>"}, "expected": "<flattened>"}
"""
import json
import os
import random
import subprocess
import tempfile
import shutil

VAL_MIN, VAL_MAX = -1000, 2000   # -1000 <= Node.val <= 2000
MAX_NODES = 2000                 # 0 <= Number of Nodes <= 2000
N_CASES = 2000
SEED = 1234

ROOT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(ROOT, "generated-tests", "level-order-traversal.jsonl")

REF_SRC = r'''
#include <iostream>
#include <vector>
#include <queue>
#include <string>
#include <sstream>
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
vector<vector<int>> levelOrder(TreeNode* root){
    vector<vector<int>> ans; if(!root) return ans;
    queue<TreeNode*> q; q.push(root);
    while(!q.empty()){ int n=q.size(); vector<int> lvl;
        for(int i=0;i<n;i++){ TreeNode* c=q.front();q.pop(); lvl.push_back(c->data);
            if(c->left)q.push(c->left); if(c->right)q.push(c->right);} ans.push_back(lvl); }
    return ans;
}
int main(){
    string line;
    while(getline(cin,line)){
        TreeNode* root=build(line);
        auto res=levelOrder(root);
        string out; bool first=true;
        for(auto& l:res) for(int v:l){ if(!first) out+=" "; out+=to_string(v); first=false; }
        cout<<out<<"\n";
    }
    return 0;
}
'''


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


def gen_tree(n):
    """
    Generate a random binary tree with exactly n nodes and return its
    level-order "null"-padded token string (LeetCode style: null nodes get
    no children).

    Strategy: grow the tree node-by-node. Keep a list of available "slots"
    (left/right of existing nodes). Attach each new node to a random slot.
    Then serialize via BFS, emitting "null" for missing children of present
    nodes only (trailing nulls trimmed -> the standard form).
    """
    if n == 0:
        # Empty tree. The judge's batch driver SKIPS empty stdin lines, which
        # would misalign every later case, so represent the empty tree as the
        # token "null" (rdTree("null") -> nullptr) — a non-empty line.
        return "null"
    # nodes[i] = [val, left_idx_or_None, right_idx_or_None]
    nodes = [[rand_val(), None, None]]
    # open slots: list of (parent_idx, side) where side in (1,2)
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
    from collections import deque
    q = deque([0])  # store node index, or None for null child of a real node
    while q:
        cur = q.popleft()
        if cur is None:
            toks.append("null")
            continue
        toks.append(str(nodes[cur][0]))
        # only enqueue children placeholders for real nodes
        q.append(nodes[cur][1])  # left idx or None
        q.append(nodes[cur][2])  # right idx or None
    # trim trailing "null"
    while toks and toks[-1] == "null":
        toks.pop()
    return " ".join(toks)


def build_inputs():
    random.seed(SEED)
    inputs = []

    # ---- Edge / boundary cases ----
    inputs.append("null")                  # empty tree (0 nodes) -> rdTree gives nullptr
    inputs.append("0")                     # single node value 0
    inputs.append(str(VAL_MIN))            # single node min val
    inputs.append(str(VAL_MAX))            # single node max val
    inputs.append(f"{VAL_MIN} {VAL_MAX}")  # two nodes extremes
    inputs.append("5 null 3")              # right-only child
    inputs.append("5 3 null")              # left-only child
    inputs.append("1 2 3 4 5 6 7")         # perfect tree depth 3
    # right-skewed chain of 50
    # Left-skewed chain of 60 nodes: each node has only a LEFT child.
    # Level-order tokens: v1 v2 null  (v2's children) v3 null ... trailing nulls trimmed.
    left_chain = []
    for i in range(60):
        left_chain.append(str(rand_val()))   # the node value
        if i < 59:
            left_chain.append("null")         # its right child is missing
    inputs.append(" ".join(left_chain))

    # Right-skewed chain of 60 nodes: each node has only a RIGHT child.
    right_chain = []
    for i in range(60):
        if i < 59:
            right_chain.append("null")        # left child missing
        right_chain.append(str(rand_val()))   # the node value (placed as right child)
    # First token must be the root value, so reorder: root, then (null, val) pairs.
    rc = [str(rand_val())]
    for _ in range(59):
        rc.append("null")
        rc.append(str(rand_val()))
    inputs.append(" ".join(rc))

    # max-size tree (boundary: 2000 nodes)
    inputs.append(gen_tree(MAX_NODES))

    # ---- small exhaustive-ish sizes ----
    for n in range(0, 12):
        for _ in range(8):
            inputs.append(gen_tree(n))

    # A FEW large trees for coverage of big inputs. CRITICAL: the judge's batched
    # runner caps TOTAL stdout for the whole process at 256 KB (262144 bytes);
    # once exceeded, every later case's output line is truncated and fails. Each
    # tree node contributes up to ~5 chars to its case's single output line, so
    # large cases are kept very rare and the bulk of cases are tiny. We budget the
    # whole file's expected output to stay well under 256 KB (~180-200 KB).
    large_sizes = [2000, 1500, 1000, 600, 400, 300, 250, 200, 150, 120]
    for ls in large_sizes:
        inputs.append(gen_tree(ls))

    # ---- random varied sizes: keep the bulk TINY to stay under the 256 KB cap ----
    while len(inputs) < N_CASES:
        r = random.random()
        if r < 0.88:
            n = random.randint(1, 12)      # vast majority: tiny trees
        elif r < 0.98:
            n = random.randint(1, 40)      # some small/medium trees
        else:
            n = random.randint(1, 100)     # a few larger trees
        inputs.append(gen_tree(n))

    return inputs[:N_CASES]


def main():
    tmp = tempfile.mkdtemp(prefix="loref_")
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
        # Feed every input line to the reference; '' (empty tree) is a valid line.
        stdin_data = "\n".join(inputs) + "\n"
        proc = subprocess.run([binp], input=stdin_data,
                              capture_output=True, text=True, check=True)
        outs = proc.stdout.split("\n")
        # outs has trailing empty element from final newline; align with inputs
        if outs and outs[-1] == "":
            outs = outs[:-1]
        assert len(outs) == len(inputs), f"output count {len(outs)} != input count {len(inputs)}"

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
