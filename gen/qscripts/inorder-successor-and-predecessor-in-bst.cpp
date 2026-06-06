// Generator for "Inorder Successor/Predecessor in BST"
// (slug: inorder-successor-and-predecessor-in-bst)
//
// Given a BST root and an integer key (key is ALWAYS present in the BST), return
// the inorder predecessor and successor of that key as vector<int> {pred, succ}.
// If a predecessor or successor is missing, that slot is -1.
//
// Method signature (starterCpp):
//   vector<int> succPredBST(TreeNode* root, int key)
//   -> inputs keys in order: "root" (TreeNode*), "key" (int)
//
// Output format: the example shows "[7, 12]" i.e. [predecessor, successor].
//   Example 1: key=10 -> pred=7, succ=12 -> "[7, 12]"
//   Example 2: key=12 -> pred=10, succ=-1 -> "[10, -1]"
// The judge compares leniently (ignores brackets/commas/whitespace), but we emit
// the bracketed form to match the example exactly.
//
// Serialization MUST match the judge (lib/judge/harness.ts):
//   * TreeNode input : level-order, space-separated, "null" for missing child
//                      (LeetCode-style), trailing nulls trimmed; struct field .data.
//
// Constraints (from the problem):
//   1 <= #nodes <= 1e4 ; 1 <= Node.val <= 1e5 ; all values unique ;
//   key is ALWAYS one of the node values.
//
// Build:  clang++ -std=c++17 -O2 -w inorder-successor-and-predecessor-in-bst.cpp -o /tmp/insp/gen
// Run:    /tmp/insp/gen > /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/inorder-successor-and-predecessor-in-bst.jsonl

#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

TreeNode* bstInsert(TreeNode* root, int val) {
    if (!root) return new TreeNode(val);
    if (val < root->data) root->left = bstInsert(root->left, val);
    else if (val > root->data) root->right = bstInsert(root->right, val);
    return root;
}

// ----- Reference: inorder predecessor & successor of `key` in a BST -----
// Standard O(height) BST walk. key is guaranteed present.
vector<int> succPredBST(TreeNode* root, int key) {
    int pred = -1, succ = -1;
    // successor: smallest value > key
    TreeNode* cur = root;
    while (cur) {
        if (cur->data > key) { succ = cur->data; cur = cur->left; }
        else cur = cur->right;
    }
    // predecessor: largest value < key
    cur = root;
    while (cur) {
        if (cur->data < key) { pred = cur->data; cur = cur->right; }
        else cur = cur->left;
    }
    return {pred, succ};
}

// ----- Serialize TreeNode level-order, trim trailing nulls (matches judge) -----
string serialize(TreeNode* root) {
    vector<string> out;
    queue<TreeNode*> q;
    if (root) q.push(root);
    while (!q.empty()) {
        TreeNode* n = q.front(); q.pop();
        if (n) { out.push_back(to_string(n->data)); q.push(n->left); q.push(n->right); }
        else out.push_back("null");
    }
    while (!out.empty() && out.back() == "null") out.pop_back();
    string s;
    for (size_t i = 0; i < out.size(); ++i) { if (i) s += ' '; s += out[i]; }
    return s;
}

void collect(TreeNode* root, vector<int>& v) {
    if (!root) return;
    collect(root->left, v);
    v.push_back(root->data);
    collect(root->right, v);
}

void freeTree(TreeNode* root) {
    if (!root) return;
    freeTree(root->left); freeTree(root->right);
    delete root;
}

string jesc(const string& s) {
    string o;
    for (char c : s) {
        if (c == '"' || c == '\\') { o += '\\'; o += c; }
        else o += c;
    }
    return o;
}

mt19937 rng(0xBADF00D ^ 271828u);

int randVal(int lo, int hi) {
    return uniform_int_distribution<int>(lo, hi)(rng);
}

// Build a BST of exactly n distinct nodes, values drawn from [lo,hi],
// insertion order randomized so the shape varies (balanced-ish to skewed).
TreeNode* buildRandomBST(int n, int lo, int hi, vector<int>& valsOut) {
    vector<int> vals;
    long long range = (long long)hi - lo + 1;
    if (range <= (long long)n * 3) {
        vector<int> all;
        for (long long x = lo; x <= hi; ++x) all.push_back((int)x);
        shuffle(all.begin(), all.end(), rng);
        for (int i = 0; i < n && i < (int)all.size(); ++i) vals.push_back(all[i]);
    } else {
        set<int> used;
        while ((int)vals.size() < n) {
            int v = randVal(lo, hi);
            if (used.insert(v).second) vals.push_back(v);
        }
    }
    vector<int> order = vals;
    shuffle(order.begin(), order.end(), rng);
    TreeNode* root = nullptr;
    for (int v : order) root = bstInsert(root, v);
    valsOut = vals;
    return root;
}

int main() {
    const int TOTAL = 2000;
    const int VLO = 1, VHI = 100000; // 1 <= Node.val <= 1e5

    // The live judge batches ALL cases in one process with a stdout cap. Each
    // case prints one line; the input tree serialization dominates size. Keep
    // the per-case tree small enough that 2000 lines stay well under the cap.
    const size_t OUT_BUDGET = 240 * 1024;
    size_t outUsed = 0;
    int count = 0;

    auto printCase = [&](const string& inRoot, int key, const string& expected) {
        string line = string("{\"inputs\": {\"root\": \"") + jesc(inRoot)
                    + "\", \"key\": \"" + to_string(key) + "\"}, \"expected\": \""
                    + jesc(expected) + "\"}\n";
        fputs(line.c_str(), stdout);
        outUsed += line.size();
        count++;
    };

    auto expectedStr = [](const vector<int>& pr) {
        return "[" + to_string(pr[0]) + ", " + to_string(pr[1]) + "]";
    };

    // ---------------- Hand-crafted edge cases ----------------
    // E1: dataset example, key=10 -> [7, 12]
    {
        TreeNode* r = nullptr;
        for (int v : {5,2,10,1,4,7,12}) r = bstInsert(r, v);
        string in = serialize(r); // "5 2 10 1 4 7 12"
        printCase(in, 10, expectedStr(succPredBST(r, 10)));
        freeTree(r);
    }
    // E2: dataset example, key=12 -> [10, -1]
    {
        TreeNode* r = nullptr;
        for (int v : {5,2,10,1,4,7,12}) r = bstInsert(r, v);
        string in = serialize(r);
        printCase(in, 12, expectedStr(succPredBST(r, 12)));
        freeTree(r);
    }
    // E3: single node -> both pred and succ missing -> [-1, -1]
    {
        TreeNode* r = new TreeNode(50000);
        string in = serialize(r); // "50000"
        printCase(in, 50000, expectedStr(succPredBST(r, 50000)));
        freeTree(r);
    }
    // E4: smallest key in tree -> pred = -1
    {
        TreeNode* r = nullptr;
        for (int v : {5,2,10,1,4,7,12}) r = bstInsert(r, v);
        string in = serialize(r);
        printCase(in, 1, expectedStr(succPredBST(r, 1))); // pred=-1, succ=2
        freeTree(r);
    }
    // E5: value=1 (min allowed) as smallest, value=1e5 (max) as largest
    {
        TreeNode* r = nullptr;
        for (int v : {500, 1, 100000, 250, 750}) r = bstInsert(r, v);
        string in = serialize(r);
        printCase(in, 100000, expectedStr(succPredBST(r, 100000))); // succ=-1
        printCase(in, 1, expectedStr(succPredBST(r, 1)));           // pred=-1
        printCase(in, 500, expectedStr(succPredBST(r, 500)));       // [250, 750]
        freeTree(r);
    }
    // E6: left-skewed chain (descending insert) and right-skewed chain
    {
        TreeNode* r = nullptr;
        for (int v : {10,9,8,7,6,5,4,3,2,1}) r = bstInsert(r, v); // left-skewed
        string in = serialize(r);
        printCase(in, 5, expectedStr(succPredBST(r, 5))); // [4, 6]
        printCase(in, 1, expectedStr(succPredBST(r, 1))); // [-1, 2]
        printCase(in, 10, expectedStr(succPredBST(r, 10))); // [9, -1]
        freeTree(r);
    }
    {
        TreeNode* r = nullptr;
        for (int v : {1,2,3,4,5,6,7,8,9,10}) r = bstInsert(r, v); // right-skewed
        string in = serialize(r);
        printCase(in, 5, expectedStr(succPredBST(r, 5)));
        printCase(in, 1, expectedStr(succPredBST(r, 1)));
        printCase(in, 10, expectedStr(succPredBST(r, 10)));
        freeTree(r);
    }

    // ---------------- Random cases ----------------
    // Mix of sizes; bias toward small/medium so the batched output fits the cap.
    auto sizeForIdx = [&](int i) -> int {
        int r = i % 100;
        if (r < 50) return 1 + randVal(1, 12);     // tiny: 2..13
        if (r < 85) return randVal(14, 60);        // small/medium
        if (r < 97) return randVal(61, 200);       // medium
        return randVal(201, 400);                  // larger
    };

    while (count < TOTAL) {
        int n = sizeForIdx(count);
        if (n < 1) n = 1;
        vector<int> vals;
        TreeNode* root = buildRandomBST(n, VLO, VHI, vals);
        if (vals.empty()) { freeTree(root); continue; }
        string in = serialize(root);

        // Pre-check output budget: input tree string is the bulk of the line.
        if (outUsed + in.size() + 64 > OUT_BUDGET) {
            // Too big to fit the remaining budget; shrink by using a tiny tree.
            freeTree(root);
            int small = 1 + randVal(1, 8);
            root = buildRandomBST(small, VLO, VHI, vals);
            in = serialize(root);
            if (vals.empty()) { freeTree(root); continue; }
        }

        // key is ALWAYS present: pick a random existing value.
        int key = vals[randVal(0, (int)vals.size() - 1)];
        printCase(in, key, expectedStr(succPredBST(root, key)));
        freeTree(root);
    }

    return 0;
}
