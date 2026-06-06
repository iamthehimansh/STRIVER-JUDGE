// Generator + reference for "Serialize and De-serialize BT".
//
// IMPORTANT — how the judge handles this problem:
//   The auto-judge parses the FIRST method inside `class Solution`, which here is
//   `string serialize(TreeNode* root)`. It builds `root` from the input string
//   (level-order, LeetCode-style, "null" for a missing child) via its rdTree(),
//   calls serialize(root), and prints the returned string VERBATIM. It does NOT
//   perform the round trip. The serialize format is therefore implementation
//   defined, so the only self-consistent "expected" is the exact string THIS
//   reference's serialize() produces (compared leniently — brackets/commas/
//   whitespace are stripped before token compare).
//
// This program:
//   1. Generates random valid binary trees within constraints
//        1 <= #nodes <= 1e4 (we cap small for a modest file), 0 <= val <= 1e4.
//   2. Emits the tree as the judge's level-order input string (matches rdTree()).
//   3. Computes expected = serialize(root) using the SAME preorder "v,"/"N," form
//      the submitted class Solution uses.
//   4. Writes one JSON object per line to the .jsonl.
//
// Build & run (from a temp dir):
//   clang++ -std=c++17 -O2 -w serialize-and-de-serialize-bt.cpp -o gen && ./gen
// The output path is fixed below.

#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int x) : data(x), left(nullptr), right(nullptr) {}
};

// ---- reference serialize (preorder, "v," / "N,"), identical to /tmp/myref.cpp ----
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
// (level-order, "null" for missing child, trailing nulls trimmed). This is the
// exact string the judge would build a tree from, so feeding it back through the
// judge's rdTree() reconstructs the same tree.
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

// ---- random tree builder: grow `n` nodes one at a time onto random open slots ----
mt19937 rng(0xC0FFEE);
int randint(int lo, int hi) { return lo + (int)(rng() % (unsigned)(hi - lo + 1)); }
int randVal() { return randint(0, 10000); } // 0 <= val <= 1e4

TreeNode* buildRandomTree(int n) {
    if (n <= 0) return nullptr;
    TreeNode* root = new TreeNode(randVal());
    // pool of nodes that still have a free child slot
    vector<TreeNode*> slots = { root };
    for (int added = 1; added < n; ++added) {
        // pick a random node that has at least one free slot
        // (slots vector may contain nodes already full; skip those)
        TreeNode* parent = nullptr;
        while (!slots.empty()) {
            int idx = randint(0, (int)slots.size() - 1);
            TreeNode* cand = slots[idx];
            if (cand->left && cand->right) {
                // full -> remove from pool
                swap(slots[idx], slots.back());
                slots.pop_back();
                continue;
            }
            parent = cand;
            break;
        }
        if (!parent) break; // shouldn't happen
        TreeNode* child = new TreeNode(randVal());
        bool leftFree = (parent->left == nullptr);
        bool rightFree = (parent->right == nullptr);
        bool putLeft;
        if (leftFree && rightFree) putLeft = (randint(0, 1) == 0);
        else putLeft = leftFree;
        if (putLeft) parent->left = child; else parent->right = child;
        slots.push_back(child);
    }
    return root;
}

// JSON-escape (input strings contain only digits/spaces/"null"; serialize string
// contains digits, commas, 'N' — none need escaping, but be safe).
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
    long long totalExpBytes = 0; // sum of serialize() output bytes (judge stdout budget)

    auto emit = [&](TreeNode* root) {
        string inp = levelOrder(root);   // judge input format
        string exp = serialize(root);    // exact string the judge prints for serialize()
        totalExpBytes += (long long)exp.size() + 1; // +1 for the newline the batch driver adds
        out << "{\"inputs\": {\"root\": \"" << jesc(inp) << "\"}, \"expected\": \""
            << jesc(exp) << "\"}\n";
        ++count;
    };

    // ---- deterministic edge cases first ----
    // single node, value 0 (min val) and max val
    { TreeNode* r = new TreeNode(0); emit(r); }
    { TreeNode* r = new TreeNode(10000); emit(r); }
    { TreeNode* r = new TreeNode(7); emit(r); }
    // the dataset's own example trees
    { // [2,1,3]
        TreeNode* r = new TreeNode(2); r->left = new TreeNode(1); r->right = new TreeNode(3); emit(r);
    }
    { // [7,3,15,null,null,9,20]
        TreeNode* r = new TreeNode(7);
        r->left = new TreeNode(3);
        r->right = new TreeNode(15);
        r->right->left = new TreeNode(9);
        r->right->right = new TreeNode(20);
        emit(r);
    }
    // left-only chain (skewed)
    { TreeNode* r = new TreeNode(randVal()); TreeNode* c = r;
      for (int i = 1; i < 50; ++i) { c->left = new TreeNode(randVal()); c = c->left; } emit(r); }
    // right-only chain (skewed)
    { TreeNode* r = new TreeNode(randVal()); TreeNode* c = r;
      for (int i = 1; i < 50; ++i) { c->right = new TreeNode(randVal()); c = c->right; } emit(r); }
    // perfect-ish small trees
    for (int n = 2; n <= 15 && count < TOTAL; ++n) emit(buildRandomTree(n));

    // ---- random trees of varied sizes ----
    // NOTE on the size cap: the judge's runner captures only the first 1 MiB of
    // a process's stdout (lib/judge/runner.ts: cap = 1024*1024), and the batch
    // submit prints serialize(root) for ALL cases into one process. serialize
    // emits ~8 bytes/node ("v," per node + "N," per null leaf). To keep the
    // total batched output comfortably < ~850 KiB across 2000 cases we bias to
    // small trees (avg ~30 nodes) with a modest tail. All sizes stay well within
    // the problem's 1 <= #nodes <= 1e4 constraint.
    while (count < TOTAL) {
        int bucket = randint(0, 99);
        int n;
        if (bucket < 45)      n = randint(1, 15);     // tiny
        else if (bucket < 80) n = randint(16, 60);    // small
        else if (bucket < 96) n = randint(61, 150);   // medium
        else                  n = randint(151, 350);  // larger tail
        emit(buildRandomTree(n));
    }

    out.close();
    fprintf(stderr, "wrote %d cases (%lld output bytes) to %s\n",
            count, (long long)totalExpBytes, outPath.c_str());
    return 0;
}
