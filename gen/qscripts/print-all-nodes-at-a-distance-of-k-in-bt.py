#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Print all nodes at a distance of K in BT".

Signature: vector<int> distanceK(TreeNode* root, TreeNode* target, int k)

Constraints:
  - 1 <= Number of Nodes <= 10^3
  - -10^4 <= Node.val <= 10^4
  - All Node.val are unique
  - target is the value of one of the nodes in the tree
  - 0 <= k <= 10^3

Input/output serialization MUST match the judge (lib/judge/harness.ts):
  - root: TreeNode* given level-order, space-separated, "null" for missing child,
    LeetCode-style (null nodes get no children). struct field is `data`.
  - target: the signature type is TreeNode*, but the dataset passes a bare value
    (e.g. "5"); the judge builds a single-node tree whose .data == that value.
    So we emit target as the plain integer string of the chosen node value.
  - k: plain integer string.
  - expected: vector<int> printed space-separated. The answer may be returned in
    ANY order, so the reference SORTS it ascending and the submitted solution must
    do the same to be deterministic.

The expected output is computed by a compiled C++ oracle (oracle.cpp) that builds
the tree exactly like the judge and runs the reference distanceK.
"""
import json, os, random, subprocess, tempfile, sys

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/print-all-nodes-at-a-distance-of-k-in-bt.jsonl"
N_CASES = 2000
VMIN, VMAX = -10000, 10000
MAX_NODES = 1000

ORACLE_SRC = r'''
#include <bits/stdc++.h>
using namespace std;
struct TreeNode{int data;TreeNode*left,*right;TreeNode(int x):data(x),left(nullptr),right(nullptr){}};
static inline string trim(const string& s){size_t a=0,b=s.size();while(a<b&&isspace((unsigned char)s[a]))a++;while(b>a&&isspace((unsigned char)s[b-1]))b--;return s.substr(a,b-a);}
static inline string strip_brackets(const string& in){string s=trim(in);if(s.size()>=2){char c=s.front(),d=s.back();if((c=='['&&d==']')||(c=='{'&&d=='}')||(c=='('&&d==')'))return s.substr(1,s.size()-2);}return s;}
static vector<string> tokens(const string& in){vector<string> out;string cur;bool inq=false;char q=0;auto flush=[&](){if(!cur.empty()){out.push_back(cur);cur.clear();}};for(size_t i=0;i<in.size();++i){char ch=in[i];if(inq){if(ch==q){inq=false;out.push_back(cur);cur.clear();}else cur.push_back(ch);continue;}if(ch=='"'||ch=='\''){flush();inq=true;q=ch;cur.clear();continue;}if(ch=='['||ch=='{'||ch=='('||ch==']'||ch=='}'||ch==')'||ch==','||isspace((unsigned char)ch)){flush();continue;}cur.push_back(ch);}flush();return out;}
static long long toLL(const string& s){string t=trim(s);if(t.empty())return 0;try{return stoll(t);}catch(...){return 0;}}
static TreeNode* rdTree(const string& s){vector<string> toks=tokens(strip_brackets(s));if(toks.empty()||toks[0]=="null"||toks[0]=="N")return nullptr;TreeNode* root=new TreeNode((int)toLL(toks[0]));queue<TreeNode*> q;q.push(root);size_t i=1;while(!q.empty()&&i<toks.size()){TreeNode* node=q.front();q.pop();if(i<toks.size()){if(toks[i]!="null"&&toks[i]!="N"){node->left=new TreeNode((int)toLL(toks[i]));q.push(node->left);}i++;}if(i<toks.size()){if(toks[i]!="null"&&toks[i]!="N"){node->right=new TreeNode((int)toLL(toks[i]));q.push(node->right);}i++;}}return root;}
vector<int> distanceK(TreeNode* root,int tgtVal,int k){TreeNode* target=nullptr;unordered_map<int,TreeNode*> parent;queue<TreeNode*> q;q.push(root);while(!q.empty()){auto top=q.front();q.pop();if(top->data==tgtVal)target=top;if(top->left){parent[top->left->data]=top;q.push(top->left);}if(top->right){parent[top->right->data]=top;q.push(top->right);}}vector<int> ans;if(!target)return ans;unordered_map<int,int> visited;queue<TreeNode*> bq;bq.push(target);int kk=k;while(kk-->0&&!bq.empty()){int size=bq.size();for(int i=0;i<size;i++){auto top=bq.front();bq.pop();visited[top->data]=1;if(top->left&&!visited[top->left->data])bq.push(top->left);if(top->right&&!visited[top->right->data])bq.push(top->right);if(parent.count(top->data)&&parent[top->data]&&!visited[parent[top->data]->data])bq.push(parent[top->data]);}}while(!bq.empty()){ans.push_back(bq.front()->data);bq.pop();}sort(ans.begin(),ans.end());return ans;}
int main(){string line;while(getline(cin,line)){if(line.empty()){cout<<"\n";continue;}vector<string> f;string c;for(char ch:line){if(ch=='\t'){f.push_back(c);c.clear();}else c+=ch;}f.push_back(c);if(f.size()<3){cout<<"\n";continue;}TreeNode* root=rdTree(f[0]);int tgt=(int)toLL(f[1]);int k=(int)toLL(f[2]);vector<int> ans=distanceK(root,tgt,k);string out;for(size_t i=0;i<ans.size();++i){if(i)out+=' ';out+=to_string(ans[i]);}cout<<out<<"\n";}return 0;}
'''

BITS_SHIM = """#pragma once
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <queue>
#include <cctype>
"""

def compile_oracle(tmp):
    inc = os.path.join(tmp, "inc", "bits")
    os.makedirs(inc, exist_ok=True)
    with open(os.path.join(inc, "stdc++.h"), "w") as f:
        f.write(BITS_SHIM)
    src = os.path.join(tmp, "oracle.cpp")
    with open(src, "w") as f:
        f.write(ORACLE_SRC)
    binp = os.path.join(tmp, "oracle")
    r = subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", "-I" + os.path.join(tmp, "inc"), src, "-o", binp],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit("oracle compile failed")
    return binp


def gen_tree(n):
    """Build a random binary tree with n nodes and unique values; return
    (level_order_tokens, list_of_node_values). Uses random insertion of children
    into available slots so structure is varied (not just complete)."""
    vals = random.sample(range(VMIN, VMAX + 1), n)
    # Represent tree as nodes with optional children indices.
    # Build by attaching each new node to a random open child slot of an existing node.
    # children[i] = [leftIdx or None, rightIdx or None]
    children = [[None, None]]  # node 0 = root
    open_slots = [(0, 0), (0, 1)]  # (parentIdx, side)
    for idx in range(1, n):
        random.shuffle(open_slots)
        p, side = open_slots.pop()
        children[p][side] = idx
        children.append([None, None])
        open_slots.append((idx, 0))
        open_slots.append((idx, 1))
    # Now produce LeetCode level-order tokens with "null" for missing children.
    # BFS; only enqueue real children; emit null for missing child of a present node.
    toks = []
    from collections import deque
    q = deque([0])
    while q:
        cur = q.popleft()
        toks.append(str(vals[cur]))
        for side in (0, 1):
            ch = children[cur][side]
            if ch is None:
                toks.append("null")
            else:
                q.append(ch)
    # trim trailing nulls (judge handles either way, but keep it clean)
    while toks and toks[-1] == "null":
        toks.pop()
    return toks, vals


def make_case(force=None):
    if force == "single":
        n = 1
    elif force == "small":
        n = random.randint(1, 5)
    else:
        # weight toward smaller-to-medium for variety; occasional large
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 40)
        elif r < 0.85:
            n = random.randint(40, 200)
        else:
            n = random.randint(200, MAX_NODES)
    toks, vals = gen_tree(n)
    target = random.choice(vals)  # must be a value in the tree
    # k range 0..10^3. The max useful distance from any node is < n. To keep most
    # outputs non-trivial while still covering empty-result edges, bias k small.
    bound = max(1, min(n - 1, 1000))
    r = random.random()
    if r < 0.10:
        k = random.randint(0, 1000)            # extreme: usually empty result
    elif r < 0.20:
        k = random.randint(0, min(n + 2, 1000))  # near/just past the edge
    else:
        k = random.randint(0, bound)            # likely to hit real nodes
    return toks, target, k


def main():
    random.seed(20260606)
    tmp = tempfile.mkdtemp(prefix="distk_")
    binp = compile_oracle(tmp)

    cases = []
    # deterministic edge cases first
    # single node, k=0 -> [target]; k>0 -> []
    cases.append((["7"], 7, 0))
    cases.append((["7"], 7, 5))
    cases.append((["-10000"], -10000, 1000))
    cases.append((["10000"], 10000, 0))
    # dataset examples
    ex_tree = "3 5 1 6 2 0 8 N N 7 4".replace("N", "null").split()
    cases.append((list(ex_tree), 5, 2))
    cases.append((list(ex_tree), 5, 3))
    cases.append((["1", "2", "3", "4", "null", "5", "6"], 6, 2))
    # a few forced small
    for _ in range(20):
        cases.append(make_case("single"))
    for _ in range(40):
        cases.append(make_case("small"))
    while len(cases) < N_CASES:
        cases.append(make_case())
    cases = cases[:N_CASES]

    # build oracle input
    lines = []
    for toks, tgt, k in cases:
        lines.append("{}\t{}\t{}".format(" ".join(toks), tgt, k))
    inp = "\n".join(lines) + "\n"
    r = subprocess.run([binp], input=inp, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        raise SystemExit("oracle run failed")
    outs = r.stdout.split("\n")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    written = 0
    with open(OUT, "w") as f:
        for i, (toks, tgt, k) in enumerate(cases):
            expected = outs[i].strip() if i < len(outs) else ""
            obj = {
                "inputs": {
                    "root": " ".join(toks),
                    "target": str(tgt),
                    "k": str(k),
                },
                "expected": expected,
            }
            f.write(json.dumps(obj) + "\n")
            written += 1
    print("wrote {} cases to {}".format(written, OUT))


if __name__ == "__main__":
    main()
