// Generator for "Construct a BST from a preorder traversal"
// Builds a BST from a random valid preorder array, serializes the resulting
// tree level-order (LeetCode-style, trailing nulls trimmed) exactly as the
// judge does, and writes 2000 cases to the generated-tests jsonl.
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:     ./gen > out.jsonl
//
// Constraints:
//   1 <= preorder.length <= 100
//   1 <= preorder[i] <= 1000
//   All values unique. Array must be a valid preorder traversal of a BST
//   (any permutation works since BST is uniquely determined by insertion order,
//    and the values themselves are inserted in preorder order to form a BST).

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <climits>
#include <queue>
#include <algorithm>
#include <random>
#include <set>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

// Reference solution (adapted to use ->data to match judge struct).
TreeNode* solve(int& index, vector<int>& pre, int bound) {
    if (index >= (int)pre.size() || pre[index] > bound) return nullptr;
    TreeNode* root = new TreeNode(pre[index++]);
    root->left = solve(index, pre, root->data);
    root->right = solve(index, pre, bound);
    return root;
}
TreeNode* bstFromPreorder(vector<int>& preorder) {
    int i = 0;
    return solve(i, preorder, INT_MAX);
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
    // trim trailing nulls
    while (!tok.empty() && tok.back() == "null") tok.pop_back();
    string s;
    for (size_t i = 0; i < tok.size(); ++i) {
        if (i) s += ' ';
        s += tok[i];
    }
    return s;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

mt19937 rng(987654321u);

int main() {
    int N = 2000;
    // Edge cases first.
    vector<vector<int>> edge;
    edge.push_back({1});                       // min size
    edge.push_back({1000});                    // single max value
    edge.push_back({8,5,1,7,10,12});           // example 1
    edge.push_back({1,3});                     // example 2
    edge.push_back({5,3,2,4,6,7});             // nowYourTurn
    // increasing skew (all right) of size 100
    {
        vector<int> v;
        for (int i = 1; i <= 100; ++i) v.push_back(i);
        edge.push_back(v);
    }
    // decreasing skew (all left) of size 100
    {
        vector<int> v;
        for (int i = 100; i >= 1; --i) v.push_back(i);
        edge.push_back(v);
    }
    // max values 901..1000 increasing
    {
        vector<int> v;
        for (int i = 901; i <= 1000; ++i) v.push_back(i);
        edge.push_back(v);
    }

    // The judge batches ALL cases into ONE process whose total stdout is capped
    // at 256 KB (scripts/judge_exec.py OUT_CAP). A correct submission must
    // reproduce every line, so the SUM of all serialized tree outputs must stay
    // safely under that cap. We therefore keep most arrays small and sprinkle a
    // bounded number of large (up to length-100) cases for constraint coverage.
    // Budget: keep total expected bytes well under ~230 KB.
    //
    // Distribution of random lengths:
    //   - ~1.5% of cases use a large length (40..100) for big-tree coverage
    //   - the rest use small lengths (1..15) which serialize compactly
    for (int t = 0; t < N; ++t) {
        vector<int> pre;
        if (t < (int)edge.size()) {
            pre = edge[t];
        } else {
            int len;
            int roll = uniform_int_distribution<int>(0, 999)(rng);
            if (roll < 15) {
                // rare large case (constraint upper region)
                len = uniform_int_distribution<int>(40, 100)(rng);
            } else {
                // common small case
                len = uniform_int_distribution<int>(1, 15)(rng);
            }
            // pick `len` distinct values from [1,1000]
            set<int> used;
            vector<int> vals;
            while ((int)vals.size() < len) {
                int v = uniform_int_distribution<int>(1, 1000)(rng);
                if (used.insert(v).second) vals.push_back(v);
            }
            // A random permutation of distinct values is ALWAYS a valid preorder
            // of SOME BST (the BST built by the reference). So just shuffle.
            shuffle(vals.begin(), vals.end(), rng);
            pre = vals;
        }

        vector<int> copy = pre;
        TreeNode* root = bstFromPreorder(copy);
        string out = serialize(root);

        // JSON-escape not needed: tokens are digits/spaces/"null".
        printf("{\"inputs\": {\"preorder\": \"%s\"}, \"expected\": \"%s\"}\n",
               arrToStr(pre).c_str(), out.c_str());
    }
    return 0;
}
