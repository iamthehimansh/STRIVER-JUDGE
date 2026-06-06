// Generator for "Floor and Ceil in a BST"
// Builds random valid BSTs, computes floor (greatest val <= key) and ceil
// (smallest val >= key), serializes tree level-order LeetCode-style.
// Output: generated-tests/floor-and-ceil-in-a-bst.jsonl
//
// Compile: clang++ -std=c++17 -O2 -w gen/qscripts/floor-and-ceil-in-a-bst.cpp -o /tmp/gen_floorceil
// Run:     /tmp/gen_floorceil
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <queue>
#include <string>
#include <algorithm>
#include <set>
#include <random>
using namespace std;

struct Node {
    int data;
    Node* left;
    Node* right;
    Node(int v) : data(v), left(nullptr), right(nullptr) {}
};

// Insert into BST (distinct values assumed)
Node* insertBST(Node* root, int v) {
    if (!root) return new Node(v);
    Node* cur = root;
    while (true) {
        if (v < cur->data) {
            if (cur->left) cur = cur->left; else { cur->left = new Node(v); break; }
        } else if (v > cur->data) {
            if (cur->right) cur = cur->right; else { cur->right = new Node(v); break; }
        } else {
            break; // duplicate, ignore
        }
    }
    return root;
}

// Level-order serialization, LeetCode-style (trim trailing nulls).
string serializeTree(Node* root) {
    if (!root) return "";
    vector<string> out;
    queue<Node*> q;
    q.push(root);
    while (!q.empty()) {
        Node* n = q.front(); q.pop();
        if (!n) { out.push_back("null"); continue; }
        out.push_back(to_string(n->data));
        q.push(n->left);
        q.push(n->right);
    }
    // trim trailing nulls
    while (!out.empty() && out.back() == "null") out.pop_back();
    string s;
    for (size_t i = 0; i < out.size(); ++i) {
        if (i) s += " ";
        s += out[i];
    }
    return s;
}

// Compute floor & ceil over the whole tree (robust; matches BST result).
void floorCeil(Node* root, int key, int& fl, int& ce) {
    fl = -1; ce = -1;
    bool ceSet = false;
    // iterative full traversal
    queue<Node*> q;
    if (root) q.push(root);
    while (!q.empty()) {
        Node* n = q.front(); q.pop();
        int v = n->data;
        if (v <= key) { if (v > fl) fl = v; }
        if (v >= key) { if (!ceSet || v < ce) { ce = v; ceSet = true; } }
        if (n->left) q.push(n->left);
        if (n->right) q.push(n->right);
    }
    if (!ceSet) ce = -1;
}

int main(int argc, char** argv) {
    long long N = 2000;
    unsigned seed = 12345;
    if (argc > 1) N = atoll(argv[1]);
    if (argc > 2) seed = (unsigned)atoll(argv[2]);
    mt19937 rng(seed);

    const int MAXV = 10000000; // 1e7
    FILE* f = fopen("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/floor-and-ceil-in-a-bst.jsonl", "w");
    if (!f) { fprintf(stderr, "cannot open output\n"); return 1; }

    for (long long t = 0; t < N; ++t) {
        // choose number of nodes: include edge cases
        int n;
        if (t == 0) n = 1;
        else if (t == 1) n = 1;
        else if (t == 2) n = 2;
        else if (t == 3) n = 5000; // max
        else if (t < 50) n = (int)(rng() % 10) + 1;     // small trees
        else if (t % 200 == 0) n = 5000;                // periodic max
        else n = (int)(rng() % 200) + 1;                // up to 200 nodes

        // pick value range. Sometimes wide, sometimes narrow to force collisions near key.
        int vmax;
        int mode = rng() % 3;
        if (mode == 0) vmax = MAXV;                 // full range
        else if (mode == 1) vmax = 50 + (rng() % 1000); // narrow
        else vmax = 1000 + (rng() % 100000);        // medium

        // generate n distinct values in [1, vmax]
        set<int> used;
        vector<int> vals;
        // if vmax < n, clamp vmax up
        if (vmax < n) vmax = n;
        if (vmax > MAXV) vmax = MAXV;
        // ensure we can get n distinct
        while ((int)vals.size() < n) {
            int v = 1 + (int)(rng() % (unsigned)vmax);
            if (used.insert(v).second) vals.push_back(v);
        }
        // shuffle insertion order so the BST is random shape
        shuffle(vals.begin(), vals.end(), rng);

        Node* root = nullptr;
        for (int v : vals) root = insertBST(root, v);

        // pick key in [1, 1e7]; sometimes equal to a node value, sometimes between,
        // sometimes below min / above max for floor/ceil = -1 edge cases.
        int key;
        int kmode = rng() % 5;
        if (kmode == 0) {
            key = vals[rng() % vals.size()];       // exact node
        } else if (kmode == 1) {
            // below everything (if possible)
            int mn = *min_element(vals.begin(), vals.end());
            key = (mn > 1) ? 1 + (rng() % (unsigned)mn) : 1; // <= mn region
            if (key > mn) key = mn; // safety
            if (mn == 1) key = 1;   // floor will be -1 only if key<mn; here use 1
        } else if (kmode == 2) {
            // above everything
            int mx = *max_element(vals.begin(), vals.end());
            if (mx < MAXV) key = mx + 1 + (rng() % (unsigned)(MAXV - mx)); else key = MAXV;
        } else {
            key = 1 + (int)(rng() % (unsigned)MAXV); // random anywhere
        }
        if (key < 1) key = 1;
        if (key > MAXV) key = MAXV;

        int fl, ce;
        floorCeil(root, key, fl, ce);
        string treeStr = serializeTree(root);

        // JSON line. Keys in signature order: root, key. Strings need escaping (none needed here).
        fprintf(f, "{\"inputs\": {\"root\": \"%s\", \"key\": \"%d\"}, \"expected\": \"[%d, %d]\"}\n",
                treeStr.c_str(), key, fl, ce);

        // free tree
        // (simple BFS delete)
        {
            queue<Node*> dq;
            if (root) dq.push(root);
            while (!dq.empty()) { Node* n = dq.front(); dq.pop(); if (n->left) dq.push(n->left); if (n->right) dq.push(n->right); delete n; }
        }
    }
    fclose(f);
    fprintf(stderr, "wrote %lld cases\n", N);
    return 0;
}
