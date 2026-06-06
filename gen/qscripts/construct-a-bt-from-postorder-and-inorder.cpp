// Generator for "Construct the Binary Tree from Postorder and Inorder Traversal"
//
// Strategy: build a RANDOM binary tree with distinct node values in [-10^4,10^4]
// and 1..3000 nodes. Derive its inorder + postorder traversals (these are by
// construction a valid, consistent pair). Feed (inorder, postorder) to the
// reference buildTree which reconstructs the tree, then serialize the result
// level-order (LeetCode-style, trailing nulls trimmed) exactly as the judge does.
//
// Signature: TreeNode* buildTree(vector<int>& inorder, vector<int>& postorder)
//   => inputs keys (signature order): "inorder", "postorder"
//   => expected: TreeNode* serialized level-order.
//
// Constraints:
//   1 <= Number of Nodes <= 3000
//   -10^4 <= Node.val <= 10^4
//   All values unique.
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:     ./gen > out.jsonl

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <climits>
#include <queue>
#include <algorithm>
#include <random>
#include <set>
#include <unordered_map>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

// ---------- Reference solution (adapted to ->data to match judge struct) ----------
unordered_map<int,int> idx;
TreeNode* solveRef(vector<int>& post, int& pi, int ins, int ine, vector<int>& inorder) {
    if (ins > ine || pi < 0) return nullptr;
    int val = post[pi--];
    TreeNode* root = new TreeNode(val);
    int loc = idx[val];
    root->right = solveRef(post, pi, loc + 1, ine, inorder);
    root->left  = solveRef(post, pi, ins, loc - 1, inorder);
    return root;
}
TreeNode* buildTree(vector<int>& inorder, vector<int>& postorder) {
    idx.clear();
    for (int i = 0; i < (int)inorder.size(); ++i) idx[inorder[i]] = i;
    int n = (int)postorder.size();
    int pi = n - 1;
    return solveRef(postorder, pi, 0, n - 1, inorder);
}

// ---------- Tree building / traversals ----------
void inorderTrav(TreeNode* r, vector<int>& out) {
    if (!r) return;
    inorderTrav(r->left, out);
    out.push_back(r->data);
    inorderTrav(r->right, out);
}
void postorderTrav(TreeNode* r, vector<int>& out) {
    if (!r) return;
    postorderTrav(r->left, out);
    postorderTrav(r->right, out);
    out.push_back(r->data);
}

// Build a random binary tree with `n` nodes using the given distinct values.
// Each new node is attached to a random free slot among existing nodes,
// producing arbitrary (unbalanced/balanced) shapes.
TreeNode* randomTree(const vector<int>& vals, mt19937& rng) {
    if (vals.empty()) return nullptr;
    int n = (int)vals.size();
    TreeNode* root = new TreeNode(vals[0]);
    // pool of (node, which-child) open slots
    vector<pair<TreeNode*,int>> slots; // 0=left,1=right
    slots.push_back({root, 0});
    slots.push_back({root, 1});
    for (int i = 1; i < n; ++i) {
        int s = uniform_int_distribution<int>(0, (int)slots.size() - 1)(rng);
        auto [node, side] = slots[s];
        slots[s] = slots.back(); slots.pop_back();
        TreeNode* nn = new TreeNode(vals[i]);
        if (side == 0) node->left = nn; else node->right = nn;
        slots.push_back({nn, 0});
        slots.push_back({nn, 1});
    }
    return root;
}

// Serialize tree level-order, LeetCode-style: null nodes get no children,
// trailing nulls trimmed. Output space-separated tokens.
string serialize(TreeNode* root) {
    if (!root) return "";
    vector<string> tok;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* n = q.front(); q.pop();
        if (!n) { tok.push_back("null"); continue; }
        tok.push_back(to_string(n->data));
        q.push(n->left);
        q.push(n->right);
    }
    while (!tok.empty() && tok.back() == "null") tok.pop_back();
    string s;
    for (size_t i = 0; i < tok.size(); ++i) { if (i) s += ' '; s += tok[i]; }
    return s;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) { if (i) s += ", "; s += to_string(a[i]); }
    s += "]";
    return s;
}

mt19937 rng(20240606u);

// pick `len` distinct values from [-10000, 10000]
vector<int> distinctVals(int len, mt19937& rng) {
    set<int> used; vector<int> vals;
    uniform_int_distribution<int> d(-10000, 10000);
    while ((int)vals.size() < len) {
        int v = d(rng);
        if (used.insert(v).second) vals.push_back(v);
    }
    return vals;
}

int main() {
    int N = 2000;

    // Emit a single case from an explicit tree (given as level-order template
    // built from distinct vals); used for the dataset examples.
    auto emitFromTree = [&](TreeNode* root) {
        vector<int> in, post;
        inorderTrav(root, in);
        postorderTrav(root, post);
        vector<int> inC = in, postC = post;
        TreeNode* rebuilt = buildTree(inC, postC);
        string out = serialize(rebuilt);
        printf("{\"inputs\": {\"inorder\": \"%s\", \"postorder\": \"%s\"}, \"expected\": \"%s\"}\n",
               arrToStr(in).c_str(), arrToStr(post).c_str(), out.c_str());
    };

    int produced = 0;

    // ---- Edge / example cases first ----
    // Example 1: tree [3,9,20,null,null,15,7]
    {
        TreeNode* r = new TreeNode(3);
        r->left = new TreeNode(9);
        r->right = new TreeNode(20);
        r->right->left = new TreeNode(15);
        r->right->right = new TreeNode(7);
        emitFromTree(r); produced++;
    }
    // Example 2: tree [3,4,2,5,6,null,9]
    {
        TreeNode* r = new TreeNode(3);
        r->left = new TreeNode(4);
        r->right = new TreeNode(2);
        r->left->left = new TreeNode(5);
        r->left->right = new TreeNode(6);
        r->right->right = new TreeNode(9);
        emitFromTree(r); produced++;
    }
    // single node, min value, max value
    { TreeNode* r = new TreeNode(0); emitFromTree(r); produced++; }
    { TreeNode* r = new TreeNode(-10000); emitFromTree(r); produced++; }
    { TreeNode* r = new TreeNode(10000); emitFromTree(r); produced++; }

    // left-skewed and right-skewed of size 40
    {
        vector<int> v = distinctVals(40, rng);
        TreeNode* r = new TreeNode(v[0]); TreeNode* cur = r;
        for (int i = 1; i < 40; ++i) { cur->left = new TreeNode(v[i]); cur = cur->left; }
        emitFromTree(r); produced++;
    }
    {
        vector<int> v = distinctVals(40, rng);
        TreeNode* r = new TreeNode(v[0]); TreeNode* cur = r;
        for (int i = 1; i < 40; ++i) { cur->right = new TreeNode(v[i]); cur = cur->right; }
        emitFromTree(r); produced++;
    }
    // ONE max-size tree (3000 nodes) for upper-constraint coverage. This alone
    // serializes to ~30 KB, so we keep it to a single case (see budget note below).
    {
        vector<int> v = distinctVals(3000, rng);
        TreeNode* r = randomTree(v, rng);
        emitFromTree(r); produced++;
    }
    // a 1500-node tree too, for a second large data point under the cap
    {
        vector<int> v = distinctVals(1500, rng);
        TreeNode* r = randomTree(v, rng);
        emitFromTree(r); produced++;
    }

    // ---- Random cases ----
    // BUDGET NOTE: the judge batches ALL cases into ONE process whose combined
    // stdout is capped at 256 KB (scripts/judge_exec.py OUT_CAP). Every line's
    // serialized tree output counts toward that cap, so total expected bytes must
    // stay well under ~200 KB. We therefore keep the vast majority of trees tiny
    // (1..15 nodes, ~60 bytes each) and only rarely emit a medium tree, plus the
    // single max tree above. ~2000 * ~60B ~= 120 KB, safely under the cap.
    for (; produced < N; ++produced) {
        int len;
        int roll = uniform_int_distribution<int>(0, 999)(rng);
        if (roll < 5)        len = uniform_int_distribution<int>(60, 150)(rng);  // rare medium
        else if (roll < 45)  len = uniform_int_distribution<int>(16, 50)(rng);   // small-medium
        else                 len = uniform_int_distribution<int>(1, 15)(rng);    // common tiny
        vector<int> v = distinctVals(len, rng);
        TreeNode* r = randomTree(v, rng);
        emitFromTree(r);
    }
    return 0;
}
