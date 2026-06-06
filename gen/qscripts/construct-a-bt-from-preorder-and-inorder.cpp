// Generator for "Construct a BT from Preorder and Inorder"
// Strategy:
//   - Build a random binary tree with unique values in [-10^4, 10^4].
//   - Derive its preorder & inorder arrays (these are the INPUTS).
//   - Run the SAME reference algorithm the judge will run to rebuild the tree,
//     then serialize it level-order (LeetCode style, trailing nulls trimmed)
//     as the EXPECTED output.
// Output: one JSON object per line to the .jsonl path.
//
// Constraints enforced:
//   1 <= #nodes <= 10^4 ; -10^4 <= val <= 10^4 ; all values unique;
//   inputs are valid preorder/inorder of the same tree.
//
// Build: clang++ -std=c++17 -O2 -w this.cpp -o gen && ./gen > out.jsonl

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <random>
#include <set>
#include <unordered_map>
#include <queue>
#include <iostream>
#include <sstream>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v): data(v), left(nullptr), right(nullptr) {}
};

// ---- random tree builder (random shape) ----
mt19937 rng(987654321u);

// Build a random tree of exactly n nodes with given distinct values (vals shuffled).
// We assign values via in-order-ish random shape; shape random by splitting count.
TreeNode* buildRandomShape(int n, vector<int>& vals, int& idx) {
    // vals consumed in preorder order to give each node a value.
    if (n == 0) return nullptr;
    // randomly pick left subtree size in [0, n-1]
    uniform_int_distribution<int> d(0, n - 1);
    int leftCount = d(rng);
    int rightCount = n - 1 - leftCount;
    int myVal = vals[idx++];
    TreeNode* root = new TreeNode(myVal);
    root->left = buildRandomShape(leftCount, vals, idx);
    root->right = buildRandomShape(rightCount, vals, idx);
    return root;
}

void preorderCollect(TreeNode* r, vector<int>& out) {
    if (!r) return;
    out.push_back(r->data);
    preorderCollect(r->left, out);
    preorderCollect(r->right, out);
}
void inorderCollect(TreeNode* r, vector<int>& out) {
    if (!r) return;
    inorderCollect(r->left, out);
    out.push_back(r->data);
    inorderCollect(r->right, out);
}

// ---- REFERENCE: rebuild tree from preorder/inorder (this is what the judge runs) ----
unordered_map<int,int> inPos;
TreeNode* solve(int pre_s, int pre_e, int in_s, int in_e, vector<int>& preorder) {
    if (pre_s > pre_e || in_s > in_e) return nullptr;
    int rootVal = preorder[pre_s];
    TreeNode* root = new TreeNode(rootVal);
    int loc = inPos[rootVal];
    int leftCount = loc - in_s;
    root->left = solve(pre_s + 1, pre_s + leftCount, in_s, loc - 1, preorder);
    root->right = solve(pre_s + leftCount + 1, pre_e, loc + 1, in_e, preorder);
    return root;
}
TreeNode* buildTree(vector<int>& preorder, vector<int>& inorder) {
    inPos.clear();
    for (int i = 0; i < (int)inorder.size(); i++) inPos[inorder[i]] = i;
    return solve(0, (int)preorder.size() - 1, 0, (int)inorder.size() - 1, preorder);
}

// ---- serialize tree level-order, LeetCode style, trim trailing nulls ----
string serializeTree(TreeNode* root) {
    if (!root) return "[]";
    vector<string> toks;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* cur = q.front(); q.pop();
        if (!cur) { toks.push_back("null"); continue; }
        toks.push_back(to_string(cur->data));
        q.push(cur->left);
        q.push(cur->right);
    }
    // trim trailing nulls
    while (!toks.empty() && toks.back() == "null") toks.pop_back();
    string s = "[";
    for (size_t i = 0; i < toks.size(); i++) {
        if (i) s += ", ";
        s += toks[i];
    }
    s += "]";
    return s;
}

string arrToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// produce distinct values of size n in range [-10000, 10000]
vector<int> distinctVals(int n) {
    // range size 20001 >= 10^4 max nodes
    vector<int> vals;
    set<int> used;
    uniform_int_distribution<int> dv(-10000, 10000);
    while ((int)vals.size() < n) {
        int x = dv(rng);
        if (used.insert(x).second) vals.push_back(x);
    }
    // shuffle to randomize value->shape assignment
    shuffle(vals.begin(), vals.end(), rng);
    return vals;
}

int main(int argc, char** argv) {
    int TOTAL = 2000;
    if (argc > 1) TOTAL = atoi(argv[1]);

    // Size distribution kept SMALL on purpose.
    // The judge runs all 2000 cases in ONE process; each prints one line and the
    // LOCAL runner caps TOTAL captured stdout at 256 KiB (scripts/judge_exec.py
    // OUT_CAP). Level-order output of an unbalanced tree also balloons with
    // interior nulls. So we bound node counts to keep the WHOLE file's output
    // well under 256 KiB (we target ~150 KiB). Correctness coverage does not
    // need 10^4-node trees; small/medium random shapes exercise every branch.
    for (int t = 0; t < TOTAL; t++) {
        int n;
        if (t == 0) n = 1;                       // min size
        else if (t == 1) n = 1;                  // another single
        else if (t == 2) n = 2;
        else if (t == 3) n = 3;
        else if (t == 4) n = 4;
        else if (t < 60) {
            uniform_int_distribution<int> d(1, 8);    // many tiny edge shapes
            n = d(rng);
        } else if (t < 1900) {
            uniform_int_distribution<int> d(1, 18);   // bulk: small trees
            n = d(rng);
        } else if (t < 1980) {
            uniform_int_distribution<int> d(18, 35);  // medium
            n = d(rng);
        } else {
            uniform_int_distribution<int> d(35, 55);  // a few larger (still bounded)
            n = d(rng);
        }

        vector<int> vals = distinctVals(n);
        int idx = 0;
        TreeNode* tree = buildRandomShape(n, vals, idx);

        vector<int> pre, ino;
        preorderCollect(tree, pre);
        inorderCollect(tree, ino);

        // run reference to rebuild and serialize
        TreeNode* rebuilt = buildTree(pre, ino);
        string expected = serializeTree(rebuilt);

        // emit JSON line. keys in signature order: preorder, inorder
        // values are array strings.
        string line = "{\"inputs\": {\"preorder\": \"";
        line += arrToStr(pre);
        line += "\", \"inorder\": \"";
        line += arrToStr(ino);
        line += "\"}, \"expected\": \"";
        line += expected;
        line += "\"}";
        printf("%s\n", line.c_str());
    }
    return 0;
}
