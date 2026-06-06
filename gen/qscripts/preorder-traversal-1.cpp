// Generator + reference for Striver problem "preorder-traversal-1"
// (Iterative Preorder Traversal of Binary Tree).
//
// Signature judged: vector<int> preorder(TreeNode* root)
// Constraints: 1 <= Number of Nodes <= 100 ; -100 <= Node.val <= 100
//
// Output: generated-tests/preorder-traversal-1.jsonl
//   one JSON object per line: {"inputs": {"root": "<level-order tree>"}, "expected": "[...]"}
//
// The TreeNode (de)serialization matches the judge's harness EXACTLY:
//   - input: level-order, space-separated tokens, "null" for missing child,
//     LeetCode-style (null nodes get no children).
//   - the reference's vector<int> output is printed space-separated; we wrap it
//     in brackets to mirror the dataset examples (the judge compares leniently).
//
// Build:  clang++ -std=c++17 -O2 -w -o /tmp/preordergen/gen preorder-traversal-1.cpp
// Run:    /tmp/preordergen/gen 2000 > generated-tests/preorder-traversal-1.jsonl

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <stack>
#include <random>
#include <sstream>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int x) : data(x), left(nullptr), right(nullptr) {}
};

// ---- Reference solution (iterative preorder), identical logic to /tmp/myref.cpp ----
vector<int> preorder(TreeNode* root) {
    vector<int> res;
    if (!root) return res;
    stack<TreeNode*> st;
    st.push(root);
    while (!st.empty()) {
        TreeNode* node = st.top();
        st.pop();
        res.push_back(node->data);
        if (node->right) st.push(node->right);
        if (node->left) st.push(node->left);
    }
    return res;
}

// ---- Build a random valid binary tree as a level-order token list ----
// We build node-by-node: node count n in [1, maxNodes]. Maintain a pool of
// "open child slots". For each new node we attach it to a random open slot.
// Then we emit the tree in LeetCode level-order to match the judge's rdTree.
struct Node { int val; int left = -1, right = -1; };

mt19937 rng;

string buildRandomTreeLevelOrder(int n, int valLo, int valHi) {
    uniform_int_distribution<int> valDist(valLo, valHi);
    vector<Node> nodes;
    nodes.reserve(n);
    // root
    nodes.push_back({valDist(rng)});
    // open slots: pairs (nodeIndex, isLeft)
    // represented as parent index *2 + (0 left/1 right)
    vector<long long> slots;
    slots.push_back(0LL * 2 + 0);
    slots.push_back(0LL * 2 + 1);
    for (int i = 1; i < n; i++) {
        // pick a random open slot
        uniform_int_distribution<size_t> sd(0, slots.size() - 1);
        size_t pick = sd(rng);
        long long slot = slots[pick];
        slots[pick] = slots.back();
        slots.pop_back();
        int parent = (int)(slot / 2);
        bool isLeft = (slot % 2) == 0;
        int idx = (int)nodes.size();
        nodes.push_back({valDist(rng)});
        if (isLeft) nodes[parent].left = idx;
        else nodes[parent].right = idx;
        // new node opens two slots
        slots.push_back((long long)idx * 2 + 0);
        slots.push_back((long long)idx * 2 + 1);
    }

    // Emit LeetCode-style level order. We need indices into `nodes`, where a
    // missing child is "null" and null nodes have no children.
    vector<string> out;
    queue<int> q;
    q.push(0);
    while (!q.empty()) {
        int cur = q.front(); q.pop();
        out.push_back(to_string(nodes[cur].val));
        int l = nodes[cur].left, r = nodes[cur].right;
        if (l != -1) q.push(l); else out.push_back("null");
        if (r != -1) q.push(r); else out.push_back("null");
        // Reconstruct: but the above interleaves incorrectly because we push
        // "null" inline. Need to handle ordering carefully — do it differently.
        (void)0;
    }
    // The simple inline approach above is wrong (nulls and real nodes mixed in
    // wrong order). Rebuild properly using a queue of indices including -1.
    out.clear();
    {
        queue<int> qq;
        qq.push(0);
        while (!qq.empty()) {
            int cur = qq.front(); qq.pop();
            if (cur == -1) { out.push_back("null"); continue; }
            out.push_back(to_string(nodes[cur].val));
            qq.push(nodes[cur].left);
            qq.push(nodes[cur].right);
        }
        // trim trailing nulls
        while (!out.empty() && out.back() == "null") out.pop_back();
    }

    string s;
    for (size_t i = 0; i < out.size(); i++) {
        if (i) s += ' ';
        s += out[i];
    }
    return s;
}

// Parse a level-order token string back into a TreeNode* EXACTLY like the judge.
TreeNode* parseTree(const string& s) {
    vector<string> toks;
    {
        string cur;
        for (char ch : s) {
            if (ch == ' ' || ch == ',' || ch == '[' || ch == ']') {
                if (!cur.empty()) { toks.push_back(cur); cur.clear(); }
            } else cur += ch;
        }
        if (!cur.empty()) toks.push_back(cur);
    }
    if (toks.empty() || toks[0] == "null" || toks[0] == "N") return nullptr;
    TreeNode* root = new TreeNode(stoi(toks[0]));
    queue<TreeNode*> q; q.push(root);
    size_t i = 1;
    while (!q.empty() && i < toks.size()) {
        TreeNode* node = q.front(); q.pop();
        if (i < toks.size()) { if (toks[i] != "null" && toks[i] != "N") { node->left = new TreeNode(stoi(toks[i])); q.push(node->left); } i++; }
        if (i < toks.size()) { if (toks[i] != "null" && toks[i] != "N") { node->right = new TreeNode(stoi(toks[i])); q.push(node->right); } i++; }
    }
    return root;
}

string jsonEscape(const string& s) {
    string o;
    for (char c : s) {
        if (c == '"' || c == '\\') { o += '\\'; o += c; }
        else o += c;
    }
    return o;
}

int main(int argc, char** argv) {
    int N = (argc > 1) ? atoi(argv[1]) : 2000;
    unsigned seed = (argc > 2) ? (unsigned)atoi(argv[2]) : 12345u;
    rng.seed(seed);

    const int VLO = -100, VHI = 100, MAXN = 100;

    // Deterministic edge cases first.
    vector<string> edge;
    edge.push_back("1");                          // single node (example 2)
    edge.push_back("1 4 null 4 2");               // example 1
    edge.push_back("-100");                       // min value, single
    edge.push_back("100");                        // max value, single
    edge.push_back("0");                          // zero
    edge.push_back("5 1 2 8 null 4 5 null 6");    // nowYourTurn tree
    // left-skewed chain of 100 nodes
    {
        string s = "1";
        for (int i = 0; i < 99; i++) s += " " + to_string((i % 201) - 100) + " null";
        // trailing handling: the above keeps a real left child each time plus a null right.
        edge.push_back(s);
    }
    // right-skewed chain of 100 nodes
    {
        string s = "1";
        for (int i = 0; i < 99; i++) s += " null " + to_string((i % 201) - 100);
        edge.push_back(s);
    }

    vector<string> trees;
    for (auto& e : edge) trees.push_back(e);

    // The live judge caps the batched stdout at 256 KB total. To keep a correct
    // solution at 100% pass, we keep the CUMULATIVE preorder output small while
    // still covering the constraint space (1..100 nodes, all sizes represented).
    // We therefore bias heavily toward small trees and include only a few
    // full-size (100-node) trees as extremes.
    uniform_int_distribution<int> smallPick(1, 20);
    uniform_int_distribution<int> midPick(1, 40);
    while ((int)trees.size() < N) {
        int n;
        int r = (int)(rng() % 100);
        if (r < 35) n = 1 + (int)(rng() % 6);           // tiny trees (1..6)
        else if (r < 80) n = smallPick(rng);            // small (1..20)
        else if (r < 96) n = midPick(rng);              // medium (1..40)
        else if (r < 99) {                              // larger (41..80)
            uniform_int_distribution<int> lp(41, 80);
            n = lp(rng);
        } else n = MAXN;                                // a few full-size (100)
        trees.push_back(buildRandomTreeLevelOrder(n, VLO, VHI));
    }
    trees.resize(N);

    for (auto& t : trees) {
        TreeNode* root = parseTree(t);
        vector<int> res = preorder(root);
        // format expected like the examples: [a, b, c]
        string exp = "[";
        for (size_t i = 0; i < res.size(); i++) {
            if (i) exp += ", ";
            exp += to_string(res[i]);
        }
        exp += "]";
        cout << "{\"inputs\": {\"root\": \"" << jsonEscape(t) << "\"}, \"expected\": \""
             << jsonEscape(exp) << "\"}\n";
    }
    return 0;
}
