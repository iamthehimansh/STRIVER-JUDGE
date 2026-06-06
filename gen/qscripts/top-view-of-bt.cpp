// Generator for "Top View of BT" (slug: top-view-of-bt)
// Builds random valid binary trees within constraints, serializes them
// level-order LeetCode-style (null for missing child, trailing nulls trimmed),
// computes the top view with the reference algorithm, and writes JSONL:
//   {"inputs": {"root": "<level-order>"}, "expected": "[v, v, ...]"}
//
// Constraints: 1 <= nodes <= 1e4 ; -1e3 <= Node.val <= 1e3
//
// Build:  clang++ -std=c++17 -O2 -w top-view-of-bt.cpp -o /tmp/topview_work/gen
// Run:    /tmp/topview_work/gen > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/top-view-of-bt.jsonl"

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <queue>
#include <map>
#include <unordered_map>
#include <random>
#include <string>
#include <algorithm>
using namespace std;

struct Node {
    int data;
    Node* left;
    Node* right;
    Node(int v): data(v), left(nullptr), right(nullptr) {}
};

// ---- Reference top-view algorithm (BFS by horizontal distance) ----
vector<int> topView(Node* root) {
    if (!root) return {};
    map<int,int> mp;                 // hd -> value (first seen in BFS = topmost-leftmost)
    queue<pair<int,Node*>> q;
    q.push({0, root});
    while (!q.empty()) {
        auto [hd, cur] = q.front(); q.pop();
        if (mp.find(hd) == mp.end()) mp[hd] = cur->data;
        if (cur->left)  q.push({hd-1, cur->left});
        if (cur->right) q.push({hd+1, cur->right});
    }
    vector<int> ans;
    for (auto& kv : mp) ans.push_back(kv.second);
    return ans;
}

// ---- Serialize a tree level-order, LeetCode style, trailing nulls trimmed ----
string serializeTree(Node* root) {
    if (!root) return "";
    vector<string> out;
    queue<Node*> q;
    q.push(root);
    while (!q.empty()) {
        Node* cur = q.front(); q.pop();
        if (!cur) { out.push_back("null"); continue; }
        out.push_back(to_string(cur->data));
        q.push(cur->left);
        q.push(cur->right);
    }
    // trim trailing nulls
    while (!out.empty() && out.back() == "null") out.pop_back();
    string s;
    for (size_t i = 0; i < out.size(); ++i) {
        if (i) s += ' ';
        s += out[i];
    }
    return s;
}

string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// ---- Random tree builders ----
mt19937 rng(123456789u);

int randVal() { return (int)(rng() % 2001) - 1000; } // -1000..1000

// Build a random tree by inserting nodes one at a time into random open slots.
Node* buildRandomTree(int n, double leanLeft = -1.0) {
    if (n <= 0) return nullptr;
    Node* root = new Node(randVal());
    // open child slots
    vector<Node*> nodes;
    nodes.push_back(root);
    int created = 1;
    // frontier of (node, isLeft) available slots
    // We'll just pick a random existing node that has a free slot.
    while (created < n) {
        // pick a random node that has at least one free child
        // gather candidates lazily; for performance pick random and probe
        Node* parent = nullptr;
        for (int tries = 0; tries < 50; ++tries) {
            Node* cand = nodes[rng() % nodes.size()];
            if (!cand->left || !cand->right) { parent = cand; break; }
        }
        if (!parent) {
            // linear scan fallback
            for (Node* cand : nodes) {
                if (!cand->left || !cand->right) { parent = cand; break; }
            }
        }
        if (!parent) break; // tree full (shouldn't happen)
        Node* child = new Node(randVal());
        bool leftFree = !parent->left;
        bool rightFree = !parent->right;
        bool putLeft;
        if (leftFree && rightFree) {
            if (leanLeft >= 0.0) {
                double r = (double)(rng() % 1000) / 1000.0;
                putLeft = (r < leanLeft);
            } else {
                putLeft = (rng() & 1);
            }
        } else {
            putLeft = leftFree;
        }
        if (putLeft) parent->left = child; else parent->right = child;
        nodes.push_back(child);
        created++;
    }
    return root;
}

// Build a complete tree from a value array (perfect/complete level order).
Node* buildComplete(int n) {
    if (n <= 0) return nullptr;
    vector<Node*> v(n);
    for (int i = 0; i < n; ++i) v[i] = new Node(randVal());
    for (int i = 0; i < n; ++i) {
        int l = 2*i+1, r = 2*i+2;
        if (l < n) v[i]->left = v[l];
        if (r < n) v[i]->right = v[r];
    }
    return v[0];
}

// left skewed
Node* buildLeftSkew(int n) {
    if (n <= 0) return nullptr;
    Node* root = new Node(randVal());
    Node* cur = root;
    for (int i = 1; i < n; ++i) { cur->left = new Node(randVal()); cur = cur->left; }
    return root;
}
Node* buildRightSkew(int n) {
    if (n <= 0) return nullptr;
    Node* root = new Node(randVal());
    Node* cur = root;
    for (int i = 1; i < n; ++i) { cur->right = new Node(randVal()); cur = cur->right; }
    return root;
}
// zig-zag
Node* buildZigZag(int n) {
    if (n <= 0) return nullptr;
    Node* root = new Node(randVal());
    Node* cur = root;
    bool left = true;
    for (int i = 1; i < n; ++i) {
        Node* c = new Node(randVal());
        if (left) cur->left = c; else cur->right = c;
        cur = c; left = !left;
    }
    return root;
}

void emit(Node* root) {
    string in = serializeTree(root);
    vector<int> tv = topView(root);
    string out = vecToStr(tv);
    // JSON line. root string has no quotes/backslashes (just ints, spaces, "null").
    printf("{\"inputs\": {\"root\": \"%s\"}, \"expected\": \"%s\"}\n", in.c_str(), out.c_str());
}

int main() {
    int total = 2000;
    int emitted = 0;

    // ---- Edge cases first ----
    // single node
    { Node* r = new Node(7); emit(r); emitted++; }
    { Node* r = new Node(-1000); emit(r); emitted++; }
    { Node* r = new Node(1000); emit(r); emitted++; }
    { Node* r = new Node(0); emit(r); emitted++; }
    // example cases (exact from dataset)
    { Node* r = buildComplete(7);
      // override with example values [1..7]
      // rebuild explicitly
      delete r;
      vector<int> vals = {1,2,3,4,5,6,7};
      vector<Node*> v(7);
      for (int i=0;i<7;i++) v[i]=new Node(vals[i]);
      for (int i=0;i<7;i++){int l=2*i+1,rr=2*i+2; if(l<7)v[i]->left=v[l]; if(rr<7)v[i]->right=v[rr];}
      emit(v[0]); emitted++; }
    { vector<int> vals = {10,20,30,40,60,90,100};
      vector<Node*> v(7);
      for (int i=0;i<7;i++) v[i]=new Node(vals[i]);
      for (int i=0;i<7;i++){int l=2*i+1,rr=2*i+2; if(l<7)v[i]->left=v[l]; if(rr<7)v[i]->right=v[rr];}
      emit(v[0]); emitted++; }
    // skewed small
    { emit(buildLeftSkew(2)); emitted++; }
    { emit(buildRightSkew(2)); emitted++; }
    { emit(buildLeftSkew(50)); emitted++; }
    { emit(buildRightSkew(50)); emitted++; }
    { emit(buildZigZag(40)); emitted++; }
    // large complete
    { emit(buildComplete(9999)); emitted++; }
    { emit(buildComplete(10000)); emitted++; }
    // large left/right skew (caps at constraint)
    { emit(buildLeftSkew(10000)); emitted++; }
    { emit(buildRightSkew(10000)); emitted++; }

    // ---- Random small trees (cover sizes 1..30) ----
    for (int n = 1; n <= 30 && emitted < total; ++n) {
        for (int rep = 0; rep < 8 && emitted < total; ++rep) {
            emit(buildRandomTree(n));
            emitted++;
        }
    }

    // ---- Random medium/large trees ----
    while (emitted < total) {
        int pick = rng() % 100;
        Node* r = nullptr;
        if (pick < 50) {
            int n = 1 + (rng() % 200);
            r = buildRandomTree(n);
        } else if (pick < 70) {
            int n = 1 + (rng() % 2000);
            r = buildRandomTree(n);
        } else if (pick < 82) {
            int n = 1 + (rng() % 10000);
            r = buildRandomTree(n);
        } else if (pick < 90) {
            int n = 1 + (rng() % 500);
            // lean strongly left or right to stress horizontal distances
            double lean = (rng() & 1) ? 0.85 : 0.15;
            r = buildRandomTree(n, lean);
        } else if (pick < 96) {
            int n = 1 + (rng() % 4000);
            r = buildComplete(n);
        } else {
            int n = 1 + (rng() % 300);
            r = buildZigZag(n);
        }
        emit(r);
        emitted++;
    }

    return 0;
}
