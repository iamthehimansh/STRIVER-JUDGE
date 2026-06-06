// Generator + reference for "Serialize and De-serialize BT".
//
// IMPORTANT — how the judge handles this problem:
//   The auto-judge parses the FIRST method inside `class Solution`, which for a
//   correct submission must be `string serialize(TreeNode* root)`. The judge
//   builds `root` from the input string (level-order, LeetCode-style, "null" for
//   a missing child) via its rdTree(), calls serialize(root), and prints the
//   returned string VERBATIM. It does NOT perform the round trip. The serialize
//   format is therefore implementation defined, so the only self-consistent
//   "expected" is the exact string THIS reference's serialize() produces. The
//   reference serialize here is preorder "v," / "N," — identical (token-for-
//   token) to the iterative preorder used in the submitted class Solution.
//   Comparison is lenient (brackets/commas/whitespace stripped before compare).
//
// OUTPUT-SIZE CAP: the running judge captures only the first 256 KiB of a
// process's stdout, and the batch submit prints serialize(root) for ALL 2000
// cases into ONE process. serialize emits ~8 bytes/node. We therefore bias hard
// to tiny trees so the TOTAL batched output stays well under 256 KiB. All sizes
// remain within the constraint 1 <= #nodes <= 1e4, 0 <= val <= 1e4.
//
// This program:
//   1. Generates random valid binary trees within constraints.
//   2. Emits the tree as the judge's level-order input string (matches rdTree()).
//   3. Computes expected = serialize(root) (preorder "v,"/"N,").
//   4. Writes one JSON object per line to the .jsonl.
//
// Build & run (from a temp dir, macOS clang needs a bits/stdc++.h shim):
//   clang++ -std=c++17 -O2 -w -I<shimdir> serialize-and-de-serialize-bt.cpp -o gen && ./gen

#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int x) : data(x), left(nullptr), right(nullptr) {}
};

// ---- reference serialize (recursive preorder, "v," / "N,") ----
// Token-for-token identical to the iterative preorder the submitted Solution uses.
void ser(TreeNode* root, string& s) {
    if (!root) { s += "N,"; return; }
    s += to_string(root->data) + ",";
    ser(root->left, s);
    ser(root->right, s);
}
string serialize(TreeNode* root) {
    string s;
    ser(root, s);
    return s;
}

// ---- level-order serialization identical to the judge's pr(TreeNode*) ----
// (level-order, "null" for a missing child, trailing nulls trimmed). This is the
// exact string the judge builds a tree from via rdTree(), so feeding it back
// reconstructs the same tree.
string levelOrder(TreeNode* root) {
    vector<string> out;
    queue<TreeNode*> q;
    if (root) q.push(root);
    while (!q.empty()) {
        TreeNode* n = q.front(); q.pop();
        if (n) { out.push_back(to_string(n->data)); q.push(n->left); q.push(n->right); }
        else out.push_back("null");
    }
    while (!out.empty() && out.back() == "null") out.pop_back();
    string res;
    for (size_t i = 0; i < out.size(); ++i) { if (i) res += ' '; res += out[i]; }
    return res;
}

// ---- random tree builder: grow `n` nodes onto random open child slots ----
mt19937 rng(0xC0FFEE);
int randint(int lo, int hi) { return lo + (int)(rng() % (unsigned)(hi - lo + 1)); }
int randVal() { return randint(0, 10000); } // 0 <= val <= 1e4

TreeNode* buildRandomTree(int n) {
    if (n <= 0) return nullptr;
    TreeNode* root = new TreeNode(randVal());
    vector<TreeNode*> slots = { root }; // nodes that may still have a free child slot
    for (int added = 1; added < n; ++added) {
        TreeNode* parent = nullptr;
        while (!slots.empty()) {
            int idx = randint(0, (int)slots.size() - 1);
            TreeNode* cand = slots[idx];
            if (cand->left && cand->right) { swap(slots[idx], slots.back()); slots.pop_back(); continue; }
            parent = cand; break;
        }
        if (!parent) break;
        TreeNode* child = new TreeNode(randVal());
        bool leftFree = (parent->left == nullptr);
        bool rightFree = (parent->right == nullptr);
        bool putLeft = (leftFree && rightFree) ? (randint(0, 1) == 0) : leftFree;
        if (putLeft) parent->left = child; else parent->right = child;
        slots.push_back(child);
    }
    return root;
}

string jesc(const string& s) {
    string o;
    for (char c : s) {
        switch (c) {
            case '"': o += "\\\""; break;
            case '\\': o += "\\\\"; break;
            case '\n': o += "\\n"; break;
            case '\t': o += "\\t"; break;
            case '\r': o += "\\r"; break;
            default: o += c;
        }
    }
    return o;
}

int main() {
    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/serialize-and-de-serialize-bt.jsonl";
    ofstream out(outPath);
    if (!out) { fprintf(stderr, "cannot open %s\n", outPath.c_str()); return 1; }

    const int TOTAL = 2000;
    int count = 0;
    long long totalExpBytes = 0; // sum of serialize() output bytes (judge 256 KiB budget)

    auto emit = [&](TreeNode* root) {
        string inp = levelOrder(root);   // judge input format
        string exp = serialize(root);    // exact string the judge prints for serialize()
        totalExpBytes += (long long)exp.size() + 1; // +1 for the newline the batch driver adds
        out << "{\"inputs\": {\"root\": \"" << jesc(inp) << "\"}, \"expected\": \""
            << jesc(exp) << "\"}\n";
        ++count;
    };

    // ---- deterministic edge cases first ----
    { TreeNode* r = new TreeNode(0); emit(r); }       // min value, single node
    { TreeNode* r = new TreeNode(10000); emit(r); }   // max value, single node
    { TreeNode* r = new TreeNode(7); emit(r); }
    { // dataset example [2,1,3]
        TreeNode* r = new TreeNode(2); r->left = new TreeNode(1); r->right = new TreeNode(3); emit(r);
    }
    { // dataset example [7,3,15,null,null,9,20]
        TreeNode* r = new TreeNode(7);
        r->left = new TreeNode(3); r->right = new TreeNode(15);
        r->right->left = new TreeNode(9); r->right->right = new TreeNode(20);
        emit(r);
    }
    // skewed chains (kept short to respect the output budget)
    { TreeNode* r = new TreeNode(randVal()); TreeNode* c = r;
      for (int i = 1; i < 30; ++i) { c->left = new TreeNode(randVal()); c = c->left; } emit(r); }
    { TreeNode* r = new TreeNode(randVal()); TreeNode* c = r;
      for (int i = 1; i < 30; ++i) { c->right = new TreeNode(randVal()); c = c->right; } emit(r); }
    // every small size 2..15 at least once
    for (int n = 2; n <= 15 && count < TOTAL; ++n) emit(buildRandomTree(n));

    // ---- random trees, biased to tiny so total output << 256 KiB ----
    while (count < TOTAL) {
        int bucket = randint(0, 99);
        int n;
        if (bucket < 60)      n = randint(1, 10);    // tiny (majority)
        else if (bucket < 88) n = randint(11, 25);   // small
        else if (bucket < 98) n = randint(26, 60);   // medium
        else                  n = randint(61, 120);  // larger tail
        emit(buildRandomTree(n));
    }

    out.close();
    fprintf(stderr, "wrote %d cases (%lld output bytes, cap 262144) to %s\n",
            count, (long long)totalExpBytes, outPath.c_str());
    return 0;
}
