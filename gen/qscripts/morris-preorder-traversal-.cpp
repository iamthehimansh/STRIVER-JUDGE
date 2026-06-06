// Generator for "Morris Preorder Traversal of a Binary Tree"
// slug: morris-preorder-traversal-
//
// Builds random binary trees (level-order, LeetCode-style serialization),
// computes preorder via the Morris algorithm (the reference oracle),
// and emits JSONL: {"inputs":{"root":"<level-order>"},"expected":"[...]"}.
//
// Constraints:
//   1 <= Number of Nodes <= 100
//   -100 <= Node.val <= 100
//
// Build:  clang++ -std=c++17 -O2 -w -o /tmp/gen_morris morris-preorder-traversal-.cpp
// Run:    /tmp/gen_morris > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/morris-preorder-traversal-.jsonl"

#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <random>
#include <queue>
#include <sstream>

using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

// ---- Reference oracle: Morris preorder traversal ----
vector<int> preorder(TreeNode* root) {
    vector<int> ans;
    TreeNode* curr = root;
    while (curr) {
        if (!curr->left) {
            ans.push_back(curr->data);
            curr = curr->right;
        } else {
            TreeNode* rightmost = curr->left;
            while (rightmost->right && rightmost->right != curr)
                rightmost = rightmost->right;
            if (!rightmost->right) {
                ans.push_back(curr->data);
                rightmost->right = curr;
                curr = curr->left;
            } else {
                rightmost->right = nullptr;
                curr = curr->right;
            }
        }
    }
    return ans;
}

// Build a tree from a level-order token list (LeetCode-style: "null" = absent).
// Returns root; tokens given as vector of strings ("null" or integer).
TreeNode* buildTree(const vector<string>& toks) {
    if (toks.empty() || toks[0] == "null") return nullptr;
    TreeNode* root = new TreeNode(stoi(toks[0]));
    queue<TreeNode*> q;
    q.push(root);
    size_t i = 1;
    while (!q.empty() && i < toks.size()) {
        TreeNode* cur = q.front(); q.pop();
        if (i < toks.size()) {
            if (toks[i] != "null") {
                cur->left = new TreeNode(stoi(toks[i]));
                q.push(cur->left);
            }
            i++;
        }
        if (i < toks.size()) {
            if (toks[i] != "null") {
                cur->right = new TreeNode(stoi(toks[i]));
                q.push(cur->right);
            }
            i++;
        }
    }
    return root;
}

void freeTree(TreeNode* r) {
    if (!r) return;
    freeTree(r->left);
    freeTree(r->right);
    delete r;
}

mt19937 rng(987654321u);

int randVal() {
    // -100 <= val <= 100
    uniform_int_distribution<int> d(-100, 100);
    return d(rng);
}

// Generate a random tree with exactly `n` nodes, return its level-order
// token list (LeetCode-style: only real nodes' children listed; null markers
// only where a present node is missing a child). Trailing nulls trimmed.
vector<string> genTreeTokens(int n) {
    // Build a random binary tree structure with n nodes.
    // Strategy: start with root, keep a list of "open slots" (node + side),
    // attach new nodes to randomly chosen open slots.
    struct Slot { int parentIdx; int side; }; // side 0=left,1=right
    vector<int> vals(n);
    for (int i = 0; i < n; i++) vals[i] = randVal();

    // parent/child arrays
    vector<int> leftChild(n, -1), rightChild(n, -1);
    vector<Slot> openSlots;
    // node 0 is root
    openSlots.push_back({0, 0});
    openSlots.push_back({0, 1});
    int created = 1;
    while (created < n) {
        // pick a random open slot
        uniform_int_distribution<int> ds(0, (int)openSlots.size() - 1);
        int si = ds(rng);
        Slot s = openSlots[si];
        // remove it (swap-pop)
        openSlots[si] = openSlots.back();
        openSlots.pop_back();
        int newIdx = created++;
        if (s.side == 0) leftChild[s.parentIdx] = newIdx;
        else rightChild[s.parentIdx] = newIdx;
        openSlots.push_back({newIdx, 0});
        openSlots.push_back({newIdx, 1});
    }

    // Now serialize this tree (indices) in level-order, LeetCode-style.
    // Build actual TreeNode-like indexing via BFS.
    vector<string> toks;
    queue<int> q;
    q.push(0);
    toks.push_back(to_string(vals[0]));
    while (!q.empty()) {
        int idx = q.front(); q.pop();
        int l = leftChild[idx];
        int r = rightChild[idx];
        if (l != -1) { toks.push_back(to_string(vals[l])); q.push(l); }
        else toks.push_back("null");
        if (r != -1) { toks.push_back(to_string(vals[r])); q.push(r); }
        else toks.push_back("null");
    }
    // trim trailing nulls
    while (!toks.empty() && toks.back() == "null") toks.pop_back();
    return toks;
}

string joinSpace(const vector<string>& toks) {
    string out;
    for (size_t i = 0; i < toks.size(); i++) {
        if (i) out += " ";
        out += toks[i];
    }
    return out;
}

string vecToBracket(const vector<int>& v) {
    string out = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) out += ", ";
        out += to_string(v[i]);
    }
    out += "]";
    return out;
}

// JSON-escape a string (root tokens contain no quotes/backslashes, but be safe).
string jsonEscape(const string& s) {
    string out;
    for (char c : s) {
        if (c == '"' || c == '\\') { out += '\\'; out += c; }
        else out += c;
    }
    return out;
}

int main(int argc, char** argv) {
    int total = 2000;
    if (argc > 1) total = atoi(argv[1]);

    // IMPORTANT (judge constraint): the batched submit judge caps TOTAL captured
    // stdout at 256 KB (OUT_CAP). The judge's per-case stdout is the preorder
    // values space-separated (roughly n * ~3.4 bytes). To keep the full 2000-case
    // set under that cap, we bias tree sizes small while still covering the whole
    // valid range (1..100) and including the max-size edge cases.
    //
    // Collect node-size schedule: ensure edge cases included.
    vector<int> sizes;
    // Explicit edge cases first.
    sizes.push_back(1);
    sizes.push_back(1);
    sizes.push_back(2);
    sizes.push_back(2);
    sizes.push_back(3);
    sizes.push_back(100); // max constraint
    sizes.push_back(100);
    sizes.push_back(99);
    sizes.push_back(50);
    sizes.push_back(50);
    // A handful more large trees for coverage (kept few to respect the cap).
    for (int k = 0; k < 6; k++) sizes.push_back(80 + (int)(rng() % 21)); // 80..100
    for (int k = 0; k < 10; k++) sizes.push_back(40 + (int)(rng() % 21)); // 40..60

    // Fill the rest with small random sizes (1..12) so the cumulative output
    // stays comfortably under the judge's 256 KB stdout cap.
    uniform_int_distribution<int> dsz(1, 12);
    while ((int)sizes.size() < total) sizes.push_back(dsz(rng));

    long long approxStdout = 0; // running estimate of the judge's captured stdout bytes
    for (int t = 0; t < total; t++) {
        int n = sizes[t];
        vector<string> toks = genTreeTokens(n);
        TreeNode* root = buildTree(toks);
        vector<int> ans = preorder(root);
        // sanity: preorder size must equal node count n
        if ((int)ans.size() != n) {
            fprintf(stderr, "MISMATCH n=%d ans=%zu\n", n, ans.size());
        }
        freeTree(root);

        // Estimate the judge's per-case stdout: values space-separated + newline.
        for (int v : ans) approxStdout += (long long)to_string(v).size() + 1;

        string rootStr = joinSpace(toks);
        string expected = vecToBracket(ans);

        // Emit one JSON line.
        printf("{\"inputs\": {\"root\": \"%s\"}, \"expected\": \"%s\"}\n",
               jsonEscape(rootStr).c_str(), jsonEscape(expected).c_str());
    }
    // Report the estimated judge-side stdout size (must stay under 256 KB).
    fprintf(stderr, "approx judge stdout bytes = %lld (cap = %d)\n",
            approxStdout, 256 * 1024);
    return 0;
}
