#!/usr/bin/env python3
"""
Test-case generator for Striver problem: check-for-symmetrical-bts (Symmetric Binary Tree).

starterCpp signature:  bool isSymmetric(TreeNode* root)
=> single input param "root" (TreeNode*, level-order space-separated, "null" for missing child).

Constraints:
  1 <= Number of Nodes <= 10^4
  -100 <= Node.val <= 100

Strategy:
  - Build random binary trees. To get a healthy mix of symmetric / non-symmetric:
      * ~45% : build a random left subtree, mirror it to the right (guaranteed symmetric base),
               with matching root structure -> symmetric. Sometimes perturb one node to break it.
      * ~45% : fully random tree (usually non-symmetric, occasionally symmetric by luck).
      * ~10% : edge cases (single node, two nodes, perfect small symmetric trees, deep skewed, etc.)
  - Serialize tree to LeetCode-style level-order (null children of null nodes are NOT emitted),
    trimming trailing nulls -- exactly how the judge round-trips a TreeNode input.
  - Expected output computed by a compiled C++ oracle (same isMirror logic the judge runs).

Writes: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-for-symmetrical-bts.jsonl
"""
import json, os, random, subprocess, sys, tempfile
from collections import deque

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/check-for-symmetrical-bts.jsonl"
ORACLE_SRC = """
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <queue>
using namespace std;
struct TreeNode { int data; TreeNode *left,*right; TreeNode(int v):data(v),left(nullptr),right(nullptr){} };
TreeNode* build(const vector<string>& t){
    if(t.empty()||t[0]=="null") return nullptr;
    TreeNode* root=new TreeNode(stoi(t[0])); queue<TreeNode*> q; q.push(root); size_t i=1;
    while(!q.empty()&&i<t.size()){
        TreeNode* c=q.front(); q.pop();
        if(i<t.size()){ if(t[i]!="null"){c->left=new TreeNode(stoi(t[i])); q.push(c->left);} i++; }
        if(i<t.size()){ if(t[i]!="null"){c->right=new TreeNode(stoi(t[i])); q.push(c->right);} i++; }
    }
    return root;
}
bool isMirror(TreeNode* a,TreeNode* b){
    if(!a&&!b) return true; if(!a||!b) return false;
    return (a->data==b->data)&&isMirror(a->left,b->right)&&isMirror(a->right,b->left);
}
bool isSymmetric(TreeNode* r){ if(!r) return true; return isMirror(r->left,r->right); }
int main(){
    string line;
    while(getline(cin,line)){
        vector<string> toks; stringstream ss(line); string x;
        while(ss>>x) toks.push_back(x);
        if(toks.empty()){ cout<<"\\n"; continue; }
        cout<<(isSymmetric(build(toks))?"true":"false")<<"\\n";
    }
    return 0;
}
"""

class Node:
    __slots__ = ("v", "l", "r")
    def __init__(self, v):
        self.v = v; self.l = None; self.r = None

def rand_val():
    return random.randint(-100, 100)

def random_tree(max_nodes):
    """Build a random binary tree with up to max_nodes nodes (>=1)."""
    n = random.randint(1, max_nodes)
    root = Node(rand_val())
    frontier = [root]
    count = 1
    while count < n and frontier:
        # pick a random node in frontier to attach a child
        idx = random.randrange(len(frontier))
        node = frontier[idx]
        added = False
        # try to add left/right children
        if node.l is None and (random.random() < 0.7):
            node.l = Node(rand_val()); frontier.append(node.l); count += 1; added = True
        if count < n and node.r is None and (random.random() < 0.7):
            node.r = Node(rand_val()); frontier.append(node.r); count += 1; added = True
        # remove fully-expanded nodes occasionally to keep frontier moving
        if node.l is not None and node.r is not None:
            frontier.pop(idx)
        elif not added:
            # nudge: force-add a child so we make progress
            if node.l is None:
                node.l = Node(rand_val()); frontier.append(node.l); count += 1
            elif node.r is None:
                node.r = Node(rand_val()); frontier.append(node.r); count += 1
            if node.l is not None and node.r is not None:
                frontier.pop(idx)
    return root

def mirror_copy(node):
    if node is None:
        return None
    m = Node(node.v)
    m.l = mirror_copy(node.r)
    m.r = mirror_copy(node.l)
    return m

def random_symmetric_tree(max_half):
    """Root + a random left subtree mirrored to the right -> symmetric tree."""
    root = Node(rand_val())
    left = random_tree(max_half)
    root.l = left
    root.r = mirror_copy(left)
    return root

def all_nodes(root):
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is None: continue
        out.append(n)
        q.append(n.l); q.append(n.r)
    return out

def perturb_value(root):
    """Change one node's value to (likely) break symmetry."""
    nodes = all_nodes(root)
    if not nodes: return
    n = random.choice(nodes)
    n.v = max(-100, min(100, n.v + random.choice([-1, 1, 7, -13, 50, -50])))
    if n.v > 100: n.v = 100
    if n.v < -100: n.v = -100

def perturb_structure(root):
    """Remove a random child to (likely) break symmetry."""
    nodes = all_nodes(root)
    cand = [n for n in nodes if n.l is not None or n.r is not None]
    if not cand: return
    n = random.choice(cand)
    if n.l is not None and (n.r is None or random.random() < 0.5):
        n.l = None
    else:
        n.r = None

def serialize(root):
    """LeetCode-style level-order. null children of present nodes emitted as 'null';
    trailing nulls trimmed; null nodes do NOT enqueue children."""
    if root is None:
        return ""
    out = []
    q = deque([root])
    while q:
        n = q.popleft()
        if n is None:
            out.append("null")
            continue
        out.append(str(n.v))
        q.append(n.l)
        q.append(n.r)
    # trim trailing nulls
    while out and out[-1] == "null":
        out.pop()
    return " ".join(out)

def count_nodes(root):
    return len(all_nodes(root))

def main():
    seed = 20260606
    random.seed(seed)

    # compile oracle
    tmp = tempfile.mkdtemp(prefix="symtree_")
    src = os.path.join(tmp, "oracle.cpp")
    binp = os.path.join(tmp, "oracle")
    with open(src, "w") as f:
        f.write(ORACLE_SRC)
    r = subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("oracle compile failed:\n" + r.stderr + "\n")
        sys.exit(1)

    N = 2000
    serial_inputs = []   # serialized tree strings (the 'root' values)

    # ---- edge cases ----
    edge = [
        "1",                              # single node -> symmetric (no children)
        "0",
        "-100",
        "100",
        "1 1 1",                          # symmetric
        "1 2 3",                          # non-symmetric (matches nowYourTurn -> false)
        "1 2 2",                          # symmetric (values mirror)
        "1 2 2 3 4 4 3",                 # example 1 -> true
        "1 2 2 null 3 null 3",           # example 2 -> false
        "1 2 2 3 null null 3",           # symmetric
        "2 3 3 4 5 5 4",                 # symmetric
        "1 2 2 2 null 2",                # asym structure
        "5 4 1 null 1 null 4 2 null null 2",  # palindrome-ish
        "-100 -100 -100 100 100 100 100",
    ]
    serial_inputs.extend(edge)

    # ---- targeted symmetric trees (with optional perturbation) ----
    while len(serial_inputs) < N:
        roll = random.random()
        if roll < 0.45:
            # symmetric base
            root = random_symmetric_tree(random.choice([2, 3, 5, 8, 15, 30, 60, 150]))
            # cap total nodes at 10^4
            if count_nodes(root) > 10000:
                continue
            r2 = random.random()
            if r2 < 0.45:
                # break symmetry by value
                perturb_value(root)
            elif r2 < 0.65:
                # break symmetry by structure
                perturb_structure(root)
            # else keep symmetric
            serial_inputs.append(serialize(root))
        else:
            # fully random tree
            root = random_tree(random.choice([1, 2, 3, 5, 10, 20, 50, 120, 400]))
            if count_nodes(root) > 10000:
                continue
            serial_inputs.append(serialize(root))

    serial_inputs = serial_inputs[:N]

    # one big symmetric tree near max size as a stress edge (replace last edge slot region)
    # build a perfect-ish symmetric tree with ~5000 nodes
    big_half = random_tree(4900)
    bigroot = Node(rand_val())
    bigroot.l = big_half
    bigroot.r = mirror_copy(big_half)
    if count_nodes(bigroot) <= 10000:
        serial_inputs[-1] = serialize(bigroot)

    # ---- run oracle on all inputs (batch via stdin, one line each) ----
    # Guard: ensure no empty lines (single root always present since >=1 node)
    payload = "\n".join(serial_inputs) + "\n"
    proc = subprocess.run([binp], input=payload, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write("oracle run failed:\n" + proc.stderr + "\n")
        sys.exit(1)
    outs = proc.stdout.split("\n")
    # strip trailing empty
    while outs and outs[-1] == "":
        outs.pop()
    if len(outs) != len(serial_inputs):
        sys.stderr.write(f"mismatch: {len(outs)} outputs vs {len(serial_inputs)} inputs\n")
        sys.exit(1)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for inp, exp in zip(serial_inputs, outs):
            obj = {"inputs": {"root": inp}, "expected": exp}
            f.write(json.dumps(obj) + "\n")

    # quick stats
    t = sum(1 for o in outs if o == "true")
    fcnt = sum(1 for o in outs if o == "false")
    sys.stderr.write(f"wrote {len(serial_inputs)} cases -> {OUT}\n")
    sys.stderr.write(f"true={t} false={fcnt}\n")

if __name__ == "__main__":
    main()
