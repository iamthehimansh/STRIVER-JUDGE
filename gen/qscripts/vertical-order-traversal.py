#!/usr/bin/env python3
"""
Generator + static test set for Striver problem "Vertical Order Traversal" (slug: vertical-order-traversal).

Constraints:
  - 1 <= Number of Nodes <= 10^4
  - -10^3 <= Node.val <= 10^3

Input format (root): level-order, space-separated, "null" for a missing child,
LeetCode-style (null nodes get no children). Field name in judge struct is `data`.

Output: vector<vector<int>> serialized by the judge as rows separated by '\n',
values within a row space-separated. The judge compares leniently
(ignoring brackets/commas/quotes/whitespace), but we still produce the same
format the judge's pr() emits to stay self-consistent.

Expected outputs are computed by an external C++ oracle (compiled from
/tmp/vot/oracle.cpp, same logic as the judge reference).
"""
import os
import random
import subprocess
import json
import collections

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/vertical-order-traversal.jsonl"
ORACLE_DIR = "/tmp/vot"
ORACLE_SRC = "/tmp/vot/oracle.cpp"
ORACLE_BIN = "/tmp/vot/oracle"

VAL_MIN, VAL_MAX = -1000, 1000
N_CASES = 2000
MAX_NODES = 10000

ORACLE_CPP = r"""
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <queue>
#include <tuple>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int x) : data(x), left(nullptr), right(nullptr) {}
};

static long long toLL(const string& s) { return stoll(s); }

static TreeNode* rdTree(const string& s) {
    stringstream ss(s);
    vector<string> toks;
    string t;
    while (ss >> t) toks.push_back(t);
    if (toks.empty() || toks[0] == "null" || toks[0] == "N") return nullptr;
    TreeNode* root = new TreeNode((int)toLL(toks[0]));
    queue<TreeNode*> q; q.push(root);
    size_t i = 1;
    while (!q.empty() && i < toks.size()) {
        TreeNode* node = q.front(); q.pop();
        if (i < toks.size()) {
            if (toks[i] != "null" && toks[i] != "N") {
                node->left = new TreeNode((int)toLL(toks[i]));
                q.push(node->left);
            }
            i++;
        }
        if (i < toks.size()) {
            if (toks[i] != "null" && toks[i] != "N") {
                node->right = new TreeNode((int)toLL(toks[i]));
                q.push(node->right);
            }
            i++;
        }
    }
    return root;
}

class Solution {
public:
    vector<vector<int>> verticalTraversal(TreeNode* root) {
        map<int, map<int, multiset<int>>> mpp;
        queue<tuple<TreeNode*, int, int>> q;
        q.push({root, 0, 0});
        while (!q.empty()) {
            auto [node, x, y] = q.front(); q.pop();
            mpp[x][y].insert(node->data);
            if (node->left)  q.push({node->left,  x - 1, y + 1});
            if (node->right) q.push({node->right, x + 1, y + 1});
        }
        vector<vector<int>> ans;
        for (auto& [col, rowMap] : mpp) {
            vector<int> v;
            for (auto& [row, ms] : rowMap)
                for (int x : ms) v.push_back(x);
            ans.push_back(v);
        }
        return ans;
    }
};

int main() {
    string line;
    if (!getline(cin, line)) return 0;
    TreeNode* root = rdTree(line);
    Solution s;
    auto out = s.verticalTraversal(root);
    for (size_t i = 0; i < out.size(); ++i) {
        if (i) cout << '\n';
        for (size_t j = 0; j < out[i].size(); ++j) {
            if (j) cout << ' ';
            cout << out[i][j];
        }
    }
    return 0;
}
"""

def ensure_oracle():
    os.makedirs(ORACLE_DIR, exist_ok=True)
    need_write = (not os.path.exists(ORACLE_SRC)) or open(ORACLE_SRC).read() != ORACLE_CPP
    if need_write:
        with open(ORACLE_SRC, "w") as f:
            f.write(ORACLE_CPP)
    if (not os.path.exists(ORACLE_BIN)) or os.path.getmtime(ORACLE_SRC) > os.path.getmtime(ORACLE_BIN):
        subprocess.run(
            ["clang++", "-std=c++17", "-O2", "-w", ORACLE_SRC, "-o", ORACLE_BIN],
            check=True,
        )

def rv():
    return random.randint(VAL_MIN, VAL_MAX)

def serialize_levelorder(values, left, right):
    n = len(values)
    if n == 0:
        return ["null"]
    toks = []
    q = collections.deque([0])
    while q:
        node = q.popleft()
        if node == -1:
            toks.append("null")
            continue
        toks.append(str(values[node]))
        q.append(left[node])
        q.append(right[node])
    while toks and toks[-1] == "null":
        toks.pop()
    return toks

def build_random_tree(n):
    values = [rv() for _ in range(n)]
    left = [-1] * n
    right = [-1] * n
    open_slots = [(0, 'L'), (0, 'R')]
    next_node = 1
    while next_node < n and open_slots:
        idx = random.randrange(len(open_slots))
        node_i, side = open_slots.pop(idx)
        child = next_node
        next_node += 1
        if side == 'L':
            left[node_i] = child
        else:
            right[node_i] = child
        open_slots.append((child, 'L'))
        open_slots.append((child, 'R'))
    return serialize_levelorder(values, left, right)

def left_chain(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n-1):
        left[i] = i+1
    return serialize_levelorder(values, left, right)

def right_chain(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n-1):
        right[i] = i+1
    return serialize_levelorder(values, left, right)

def zigzag(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n-1):
        if i % 2 == 0:
            left[i] = i+1
        else:
            right[i] = i+1
    return serialize_levelorder(values, left, right)

def complete_tree(n):
    values = [rv() for _ in range(n)]
    left = [-1]*n; right = [-1]*n
    for i in range(n):
        l = 2*i+1; r = 2*i+2
        if l < n: left[i] = l
        if r < n: right[i] = r
    return serialize_levelorder(values, left, right)

def same_values_complete_tree(n, v):
    """Useful for stressing the multiset tie-break."""
    values = [v] * n
    left = [-1]*n; right = [-1]*n
    for i in range(n):
        l = 2*i+1; r = 2*i+2
        if l < n: left[i] = l
        if r < n: right[i] = r
    return serialize_levelorder(values, left, right)

def run_oracle(token_line):
    p = subprocess.run([ORACLE_BIN], input=token_line + "\n",
                       capture_output=True, text=True, check=True)
    return p.stdout  # don't strip trailing/leading - empty rows shouldn't happen

def main():
    random.seed(12506)
    ensure_oracle()
    cases = []

    # Dataset examples
    cases.append("3 9 20 null null 15 7".split())
    cases.append("1 2 3 4 5 6 7".split())
    cases.append("5 1 2 8 null 4 5 null 6".split())
    cases.append("1 2 3 null 4 null 5".split())

    # Edge cases
    cases.append([str(rv())])                                    # single node random
    cases.append([str(VAL_MIN)])                                  # single node min val
    cases.append([str(VAL_MAX)])                                  # single node max val
    cases.append(["0"])                                           # single node zero
    cases.append(left_chain(50))                                  # pure left chain
    cases.append(right_chain(50))                                 # pure right chain
    cases.append(zigzag(30))                                      # zigzag
    cases.append(complete_tree(15))                               # complete tree 15
    cases.append(complete_tree(31))                               # full 5 levels
    cases.append(complete_tree(127))                              # full 7 levels
    # A handful of larger stress cases. Bounded so aggregate output across all
    # 2000 cases stays under the judge's 256KB captured-stdout cap. (We still
    # cover the algorithmic edges: pure chains, complete tree, ties on value.)
    cases.append(left_chain(100))                                 # left chain stress
    cases.append(right_chain(100))                                # right chain stress
    cases.append(complete_tree(200))                              # complete tree stress
    cases.append(same_values_complete_tree(63, 0))                # ties on value
    cases.append(same_values_complete_tree(127, VAL_MAX))         # large ties
    cases.append(same_values_complete_tree(127, VAL_MIN))         # large ties

    # Random trees with varying sizes. Keep the AGGREGATE output across all
    # cases under the judge's 256KB captured-stdout cap. Each output value is
    # up to ~5 chars wide, so we keep average node-count small and reserve a
    # handful of larger stress cases for tail coverage.
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.75:
            n = random.randint(1, 15)
        elif r < 0.95:
            n = random.randint(15, 40)
        elif r < 0.99:
            n = random.randint(40, 80)
        else:
            n = random.randint(80, 150)
        toks = build_random_tree(n)
        cases.append(toks)

    cases = cases[:N_CASES]

    written = 0
    with open(OUT_PATH, "w") as f:
        for toks in cases:
            line = " ".join(toks)
            expected = run_oracle(line)
            obj = {"inputs": {"root": line}, "expected": expected}
            f.write(json.dumps(obj) + "\n")
            written += 1
            if written % 200 == 0:
                print(f"  {written}/{N_CASES}")
    print(f"Wrote {written} cases to {OUT_PATH}")

if __name__ == "__main__":
    main()
