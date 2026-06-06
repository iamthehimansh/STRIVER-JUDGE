#!/usr/bin/env python3
"""
Test-case generator for Striver problem: search-in-bst
("Search in a Binary Search Tree").

Method signature (starterCpp):
    TreeNode* searchBST(TreeNode* root, int val)

Constraints:
    1 <= Number of Nodes <= 5000
    1 <= Node.val <= 10^7
    1 <= val      <= 10^7
    All node values in the BST are unique.

Semantics:
    Return the subtree rooted at the node whose value == val, or null if no
    such node exists.

Input / output serialization (must match the judge EXACTLY):
    * root (TreeNode*): level-order, space-separated, "null" for a missing
      child, LeetCode-style (null nodes get no children), trailing nulls
      trimmed. e.g. "4 2 7 1 3". Judge struct field is .data.
    * val (int): "2"
    * expected (TreeNode* output): the returned subtree serialized the SAME
      level-order way (trailing nulls trimmed). Empty string when null.

The "expected" values are produced by a C++ oracle that REUSES the judge's
exact rdTree (deserialize) and pr(TreeNode*) (serialize) routines plus the
canonical BST-search reference, so a correct submission reproduces them
token-for-token. This was confirmed against the live judge (passed == total).

jsonl line: {"inputs": {"root": "..", "val": ".."}, "expected": ".."}
Input key order matches starterCpp signature order: root, val.
"""
import json
import os
import random
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT_PATH = os.path.join(PROJECT, "generated-tests", "search-in-bst.jsonl")

ORACLE_DIR = "/tmp/searchbstgen"
ORACLE_SRC = os.path.join(ORACLE_DIR, "oracle.cpp")
ORACLE_BIN = os.path.join(ORACLE_DIR, "oracle")

MAX_NODES = 5000
MAX_VAL = 10**7
N_CASES = 2000

random.seed(20260606)

# ---------------------------------------------------------------------------
# Oracle: the EXACT judge TreeNode (.data) + rdTree + pr(TreeNode*) + the
# canonical BST search reference. Written/compiled here so the script is
# fully self-contained and re-runnable.
# ---------------------------------------------------------------------------
ORACLE_CPP = r'''
#include <iostream>
#include <sstream>
#include <vector>
#include <queue>
#include <string>
#include <cctype>
using namespace std;

struct TreeNode { int data; TreeNode *left,*right; TreeNode(int x):data(x),left(nullptr),right(nullptr){} };

static inline string trim(const string& s){size_t a=0,b=s.size();while(a<b&&isspace((unsigned char)s[a]))a++;while(b>a&&isspace((unsigned char)s[b-1]))b--;return s.substr(a,b-a);}
static inline string strip_brackets(const string& in){string s=trim(in);if(s.size()>=2){char c=s.front(),d=s.back();if((c=='['&&d==']')||(c=='{'&&d=='}')||(c=='('&&d==')'))return s.substr(1,s.size()-2);}return s;}
static vector<string> tokens(const string& in){vector<string> out;string cur;bool inq=false;char q=0;auto flush=[&](){if(!cur.empty()){out.push_back(cur);cur.clear();}};for(size_t i=0;i<in.size();++i){char ch=in[i];if(inq){if(ch==q){inq=false;out.push_back(cur);cur.clear();}else cur.push_back(ch);continue;}if(ch=='"'||ch=='\''){flush();inq=true;q=ch;cur.clear();continue;}if(ch=='['||ch=='{'||ch=='('||ch==']'||ch=='}'||ch==')'||ch==','||isspace((unsigned char)ch)){flush();continue;}cur.push_back(ch);}flush();return out;}
static long long toLL(const string& s){string t=trim(s);if(t.empty())return 0;try{return stoll(t);}catch(...){return 0;}}

static TreeNode* rdTree(const string& s){vector<string> toks=tokens(strip_brackets(s));if(toks.empty()||toks[0]=="null"||toks[0]=="N")return nullptr;TreeNode* root=new TreeNode((int)toLL(toks[0]));queue<TreeNode*> q;q.push(root);size_t i=1;while(!q.empty()&&i<toks.size()){TreeNode* node=q.front();q.pop();if(i<toks.size()){if(toks[i]!="null"&&toks[i]!="N"){node->left=new TreeNode((int)toLL(toks[i]));q.push(node->left);}i++;}if(i<toks.size()){if(toks[i]!="null"&&toks[i]!="N"){node->right=new TreeNode((int)toLL(toks[i]));q.push(node->right);}i++;}}return root;}

static string prTree(TreeNode* root){vector<string> out;queue<TreeNode*> q;if(root)q.push(root);while(!q.empty()){TreeNode* n=q.front();q.pop();if(n){out.push_back(to_string(n->data));q.push(n->left);q.push(n->right);}else out.push_back("null");}while(!out.empty()&&out.back()=="null")out.pop_back();string r;for(size_t i=0;i<out.size();++i){if(i)r+=' ';r+=out[i];}return r;}

TreeNode* searchBST(TreeNode* root, int val){
  if(root==nullptr) return nullptr;
  if(root->data==val) return root;
  if(root->data>val) return searchBST(root->left,val);
  return searchBST(root->right,val);
}

int main(){
  string line;
  while(getline(cin,line)){
    if(line.empty()){cout<<"\n";continue;}
    vector<string> f;string cur;for(char ch:line){if(ch=='\t'){f.push_back(cur);cur.clear();}else cur+=ch;}f.push_back(cur);
    while(f.size()<2)f.push_back("");
    TreeNode* root=rdTree(f[0]);
    int val=(int)toLL(f[1]);
    TreeNode* ans=searchBST(root,val);
    cout<<prTree(ans)<<"\n";
  }
  return 0;
}
'''


def ensure_oracle():
    os.makedirs(ORACLE_DIR, exist_ok=True)
    need_build = True
    if os.path.exists(ORACLE_SRC):
        with open(ORACLE_SRC) as f:
            if f.read() == ORACLE_CPP and os.path.exists(ORACLE_BIN):
                need_build = False
    if need_build:
        with open(ORACLE_SRC, "w") as f:
            f.write(ORACLE_CPP)
        r = subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", ORACLE_SRC, "-o", ORACLE_BIN],
            capture_output=True, text=True)
        if r.returncode != 0:
            print("ORACLE COMPILE FAILED:\n" + r.stderr, file=sys.stderr)
            sys.exit(1)


# ---------------------------------------------------------------------------
# BST construction / serialization
# ---------------------------------------------------------------------------
def build_bst(values):
    """Insert distinct values (in given order) into a BST. Return root value
    plus left/right child maps."""
    left, right = {}, {}
    root = values[0]
    for v in values[1:]:
        cur = root
        while True:
            if v < cur:
                if cur in left:
                    cur = left[cur]
                else:
                    left[cur] = v
                    break
            else:  # v > cur (all distinct)
                if cur in right:
                    cur = right[cur]
                else:
                    right[cur] = v
                    break
    return root, left, right


def serialize_levelorder(root, left, right):
    """LeetCode-style level-order; "null" for a missing child; trailing nulls
    trimmed — matches the judge's pr(TreeNode*)."""
    if root is None:
        return ""
    out, q = [], [root]
    while q:
        nxt = []
        for node in q:
            if node is None:
                out.append("null")
            else:
                out.append(str(node))
                nxt.append(left.get(node))
                nxt.append(right.get(node))
        q = nxt
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)


def make_random_bst(n):
    """n distinct values in [1, MAX_VAL], inserted in random order -> random
    shaped BST. Returns (serialization, list_of_values)."""
    vals = random.sample(range(1, MAX_VAL + 1), n)
    order = vals[:]
    random.shuffle(order)
    root, left, right = build_bst(order)
    return serialize_levelorder(root, left, right), vals


def make_skewed_bst(n, increasing=True):
    """Inserting sorted values -> a degenerate chain (height n)."""
    vals = sorted(random.sample(range(1, MAX_VAL + 1), n))
    order = vals if increasing else list(reversed(vals))
    root, left, right = build_bst(order)
    return serialize_levelorder(root, left, right), vals


def gen_case():
    """One (root_serialization, val) honoring all constraints."""
    r = random.random()
    if r < 0.06:
        # single node (minimum size)
        ser, vals = make_random_bst(1)
    elif r < 0.16:
        ser, vals = make_skewed_bst(random.randint(2, 40),
                                    increasing=random.random() < 0.5)
    elif r < 0.80:
        ser, vals = make_random_bst(random.randint(2, 25))
    else:
        ser, vals = make_random_bst(random.randint(26, 80))

    # ~60% present (val is an existing node), ~40% absent.
    if random.random() < 0.60:
        val = random.choice(vals)
    else:
        present = set(vals)
        for _ in range(40):
            cand = random.randint(1, MAX_VAL)
            if cand not in present:
                val = cand
                break
        else:
            val = random.choice(vals)  # fallback (vanishingly unlikely)
    return ser, val


def main():
    ensure_oracle()
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    cases = []  # list of (root_ser, val)

    # --- explicit edge cases ---
    # dataset examples (self-check)
    cases.append(("4 2 7 1 3", 2))          # -> "2 1 3"
    cases.append(("4 2 7 1 3", 5))          # -> "" (absent)
    cases.append(("6 4 7 null null null 10", 4))   # -> "4" (subtree at leaf 4)
    cases.append(("10 2 12 1 4 null null null null 3", 2))  # -> "2 1 4 null null 3"
    # single-node trees
    cases.append(("1", 1))                  # present
    cases.append(("1", 2))                  # absent
    cases.append((str(MAX_VAL), MAX_VAL))   # max value present
    cases.append((str(MAX_VAL), 1))         # absent at min
    cases.append(("5000000", 5000000))
    # two-node trees, both orientations
    cases.append(("2 1", 1))
    cases.append(("2 1", 2))
    cases.append(("1 null 2", 2))
    cases.append(("1 null 2", 1))
    cases.append(("2 1", 3))                # absent
    # extreme value endpoints present
    cases.append((f"5000000 1 {MAX_VAL}", 1))
    cases.append((f"5000000 1 {MAX_VAL}", MAX_VAL))
    cases.append((f"5000000 1 {MAX_VAL}", 5000000))
    # search for root value
    s, vals = make_random_bst(60)
    cases.append((s, int(s.split()[0])))
    # search for the maximum value (always a right-leaning leaf -> tiny output)
    s, vals = make_random_bst(50)
    cases.append((s, max(vals)))
    # search for the minimum value (left-leaning leaf)
    s, vals = make_random_bst(50)
    cases.append((s, min(vals)))
    # absent value smaller than everything / larger than everything
    s, vals = make_random_bst(30)
    cases.append((s, 1 if 1 not in set(vals) else min(vals)))
    s, vals = make_random_bst(30)
    mx = max(vals)
    cases.append((s, mx + 1 if mx < MAX_VAL else mx))

    # A few large trees up to the node-count cap. Search the MAX value (a leaf)
    # so the returned subtree is a single node -> tiny output, keeping the
    # batched judge stdout small while still exercising scale & the boundary.
    for nodes in (1000, 2500, 4000, MAX_NODES):
        s, vals = make_random_bst(nodes)
        cases.append((s, max(vals)))           # present leaf
        s2, vals2 = make_random_bst(nodes)
        present = set(vals2)
        cand = random.randint(1, MAX_VAL)
        while cand in present:
            cand = random.randint(1, MAX_VAL)
        cases.append((s2, cand))               # absent

    # --- random fill ---
    while len(cases) < N_CASES:
        cases.append(gen_case())
    cases = cases[:N_CASES]

    # --- compute expected via oracle (one tab-sep line per case) ---
    stdin = "\n".join(f"{ser}\t{val}" for ser, val in cases) + "\n"
    proc = subprocess.run([ORACLE_BIN], input=stdin, capture_output=True, text=True)
    if proc.returncode != 0:
        print("ORACLE RUN FAILED:\n" + proc.stderr, file=sys.stderr)
        sys.exit(1)
    expected = proc.stdout.split("\n")[:len(cases)]
    if len(expected) != len(cases):
        print(f"ERROR: oracle returned {len(expected)} lines for "
              f"{len(cases)} cases", file=sys.stderr)
        sys.exit(1)

    with open(OUT_PATH, "w") as f:
        for (ser, val), exp in zip(cases, expected):
            obj = {"inputs": {"root": ser, "val": str(val)}, "expected": exp}
            f.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
