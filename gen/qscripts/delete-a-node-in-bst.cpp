// Generator for "Delete a node in BST" (slug: delete-a-node-in-bst)
//
// Builds random BSTs (distinct values within constraints), picks a key (sometimes
// present in the tree, sometimes absent, sometimes an extreme), deletes it with the
// SAME deterministic algorithm the submitted reference uses (in-order predecessor:
// the max of the left subtree), and emits one JSON line per case.
//
// Input/output serialization MUST match the judge (lib/judge/harness.ts):
//   * TreeNode input/output  : level-order, space-separated, "null" for a missing
//                              child (LeetCode-style), trailing nulls trimmed; field .data.
//   * inputs keys            : "root" (TreeNode*), "key" (int) — in starterCpp order.
//
// Constraints (from the problem):
//   1 <= #nodes <= 1e4 ; -1e8 <= Node.val <= 1e8 ; all values unique ; -1e8 <= key <= 1e8.
//
// Build:  clang++ -std=c++17 -O2 -w delete-a-node-in-bst.cpp -o /tmp/delbst/gen
// Run:    /tmp/delbst/gen > /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/delete-a-node-in-bst.jsonl

#include <bits/stdc++.h>
using namespace std;

struct TreeNode {
    int data;
    TreeNode *left, *right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

// ----- BST construction (insertion keeps the BST property; values are distinct) -----
TreeNode* bstInsert(TreeNode* root, int val) {
    if (!root) return new TreeNode(val);
    if (val < root->data) root->left = bstInsert(root->left, val);
    else if (val > root->data) root->right = bstInsert(root->right, val);
    // equal: ignore (values are unique)
    return root;
}

// ----- Reference deletion: in-order predecessor (max of left subtree) -----
TreeNode* deleteNode(TreeNode* root, int key) {
    if (!root) return nullptr;
    if (key < root->data) {
        root->left = deleteNode(root->left, key);
    } else if (key > root->data) {
        root->right = deleteNode(root->right, key);
    } else {
        // found
        if (!root->left) return root->right;
        if (!root->right) return root->left;
        // two children: take max of left subtree (rightmost), copy, delete it there
        TreeNode* pred = root->left;
        while (pred->right) pred = pred->right;
        root->data = pred->data;
        root->left = deleteNode(root->left, pred->data);
    }
    return root;
}

// ----- Serialize TreeNode level-order, trim trailing nulls (matches judge pr()) -----
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
    return s; // empty string if tree is null
}

// collect all values currently in the tree (in-order)
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

// JSON-escape (values here have no quotes/backslashes, but be safe)
string jesc(const string& s) {
    string o;
    for (char c : s) {
        if (c == '"' || c == '\\') { o += '\\'; o += c; }
        else o += c;
    }
    return o;
}

mt19937 rng(0xC0FFEE ^ 12345u);

int randVal(int lo, int hi) {
    return uniform_int_distribution<int>(lo, hi)(rng);
}

// build a BST of exactly n distinct nodes; values drawn from [lo,hi]; insertion
// order randomized so tree shape varies (balanced-ish to skewed).
TreeNode* buildRandomBST(int n, int lo, int hi, vector<int>& valsOut) {
    set<int> used;
    // For small ranges relative to n, sample distinct deterministically.
    vector<int> vals;
    long long range = (long long)hi - lo + 1;
    if (range <= (long long)n * 3) {
        // dense: shuffle the whole range and take n
        vector<int> all;
        for (long long x = lo; x <= hi; ++x) all.push_back((int)x);
        shuffle(all.begin(), all.end(), rng);
        for (int i = 0; i < n && i < (int)all.size(); ++i) vals.push_back(all[i]);
    } else {
        while ((int)vals.size() < n) {
            int v = randVal(lo, hi);
            if (used.insert(v).second) vals.push_back(v);
        }
    }
    // randomize insertion order for varied shape
    vector<int> order = vals;
    shuffle(order.begin(), order.end(), rng);
    TreeNode* root = nullptr;
    for (int v : order) root = bstInsert(root, v);
    valsOut = vals;
    return root;
}

int main(int argc, char** argv) {
    const int TOTAL = 2000;
    const int VLO = -100000000, VHI = 100000000;

    // The live judge batches ALL cases in ONE process and caps that process's
    // TOTAL stdout at 256 KB (scripts/judge_exec.py: OUT_CAP = 256*1024). Each
    // case prints one output line (the serialized result tree), so the SUM of
    // all expected-output sizes must stay comfortably under 256 KB or later
    // cases get truncated and (correctly) fail. We budget ~210 KB and skip any
    // case whose expected serialization would blow the remaining budget.
    const size_t OUT_BUDGET = 240 * 1024;
    size_t outUsed = 0;

    // emit one case
    auto emit = [&](TreeNode* root, int key) {
        TreeNode* res = deleteNode(root, key); // mutates/rebuilds; root may change
        string rootStr; // we need the ORIGINAL input string -> serialize BEFORE delete
        // NOTE: handled by caller (serialize input first). See loop below.
        (void)rootStr; (void)res;
    };
    (void)emit;

    int count = 0;
    // returns false if emitting would exceed the output budget (caller should
    // shrink the tree and retry). The "+1" accounts for the per-case newline the
    // judge's batch driver appends to each output line.
    auto wouldFit = [&](const string& expected) {
        return outUsed + expected.size() + 1 <= OUT_BUDGET;
    };
    auto printCase = [&](const string& inRoot, int key, const string& expected) {
        printf("{\"inputs\": {\"root\": \"%s\", \"key\": \"%d\"}, \"expected\": \"%s\"}\n",
               jesc(inRoot).c_str(), key, jesc(expected).c_str());
        outUsed += expected.size() + 1;
        count++;
    };

    // -------- Hand-crafted edge cases first --------
    // 1) single node, delete it -> empty tree
    {
        TreeNode* r = new TreeNode(42);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 42);
        printCase(in, 42, serialize(out));
        freeTree(out);
    }
    // 2) single node, key absent -> unchanged
    {
        TreeNode* r = new TreeNode(-100000000);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 7);
        printCase(in, 7, serialize(out));
        freeTree(out);
    }
    // 3) the dataset example: [5,3,6,2,4,null,7], delete 3
    {
        // build exactly this BST via inserts: 5,3,6,2,4,7
        TreeNode* r = nullptr;
        for (int v : {5,3,6,2,4,7}) r = bstInsert(r, v);
        string in = serialize(r); // should be "5 3 6 2 4 null 7"
        TreeNode* out = deleteNode(r, 3);
        printCase(in, 3, serialize(out)); // expect "5 4 6 2 null null 7"
        freeTree(out);
    }
    // 4) same tree, key 0 absent -> unchanged
    {
        TreeNode* r = nullptr;
        for (int v : {5,3,6,2,4,7}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 0);
        printCase(in, 0, serialize(out));
        freeTree(out);
    }
    // 5) delete the root of a balanced tree (two children)
    {
        TreeNode* r = nullptr;
        for (int v : {50,30,70,20,40,60,80}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 50);
        printCase(in, 50, serialize(out));
        freeTree(out);
    }
    // 6) extremes for value/key bounds: min/max present
    {
        TreeNode* r = nullptr;
        for (int v : {0, VLO, VHI, -1, 1}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, VLO);
        printCase(in, VLO, serialize(out));
        freeTree(out);
    }
    {
        TreeNode* r = nullptr;
        for (int v : {0, VLO, VHI, -1, 1}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, VHI);
        printCase(in, VHI, serialize(out));
        freeTree(out);
    }
    // 7) skewed (right) chain, delete middle
    {
        TreeNode* r = nullptr;
        for (int v : {1,2,3,4,5,6,7,8}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 4);
        printCase(in, 4, serialize(out));
        freeTree(out);
    }
    // 8) skewed (left) chain, delete a leaf
    {
        TreeNode* r = nullptr;
        for (int v : {8,7,6,5,4,3,2,1}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 1);
        printCase(in, 1, serialize(out));
        freeTree(out);
    }
    // 9) key absent but within range (between two values)
    {
        TreeNode* r = nullptr;
        for (int v : {10,5,15,2,7,12,20}) r = bstInsert(r, v);
        string in = serialize(r);
        TreeNode* out = deleteNode(r, 8);
        printCase(in, 8, serialize(out));
        freeTree(out);
    }

    // -------- A FEW larger cases (within budget) to exercise big trees --------
    // The whole-set output budget is ~210 KB, so we can only afford a handful of
    // larger trees. One ~1500-node and a couple of few-hundred-node trees keep us
    // well under cap while still covering the "large BST" path. (The full 1e4-node
    // bound is not output-serializable under the judge's 256 KB cap for 2000 cases,
    // so we sample large-but-affordable sizes and rely on small cases for breadth.)
    {
        int bigSizes[] = {400, 250, 180, 130, 100, 80};
        for (int n : bigSizes) {
            vector<int> vals;
            TreeNode* root = buildRandomBST(n, VLO, VHI, vals);
            if ((int)vals.size() < n) { freeTree(root); continue; }
            int key = vals[randVal(0, (int)vals.size() - 1)]; // present key
            string inRoot = serialize(root);
            TreeNode* out = deleteNode(root, key);
            string expected = serialize(out);
            if (wouldFit(expected)) printCase(inRoot, key, expected);
            freeTree(out);
        }
    }

    // -------- Randomized small/medium cases (bulk) --------
    // Sizes kept modest so 2000 cases share the 256 KB output cap. We retry with a
    // smaller tree if a case would exceed the remaining budget.
    int safety = 0;
    while (count < TOTAL && safety < TOTAL * 60) {
        safety++;
        int n;
        int r = randVal(0, 99);
        if (r < 82)      n = randVal(1, 9);     // tiny (lots of edge shapes)
        else if (r < 96) n = randVal(10, 25);   // small
        else             n = randVal(26, 60);   // medium

        // value range: sometimes a narrow window (forces dense distinct), usually wide
        int lo, hi;
        int rr = randVal(0, 99);
        if (rr < 30) {
            int center = randVal(VLO + n, VHI - n);
            int half = max(n, randVal(n, n * 3 + 5));
            lo = max(VLO, center - half);
            hi = min(VHI, center + half);
            if (hi - lo + 1 < n) { lo = VLO; hi = VHI; }
        } else {
            lo = VLO; hi = VHI;
        }

        vector<int> vals;
        TreeNode* root = buildRandomBST(n, lo, hi, vals);
        if ((int)vals.size() < n) { freeTree(root); continue; } // couldn't fill (rare); retry
        set<int> sv(vals.begin(), vals.end());

        // choose key strategy
        int key;
        int ks = randVal(0, 99);
        if (ks < 60) {
            // present key
            key = vals[randVal(0, (int)vals.size() - 1)];
        } else if (ks < 82) {
            // absent key within value bounds
            int tries = 0;
            do { key = randVal(VLO, VHI); tries++; }
            while (sv.count(key) && tries < 200);
        } else {
            // extreme keys
            int e = randVal(0, 3);
            if (e == 0) key = VLO;
            else if (e == 1) key = VHI;
            else if (e == 2) key = *min_element(vals.begin(), vals.end());
            else key = *max_element(vals.begin(), vals.end());
        }

        string inRoot = serialize(root);
        TreeNode* out = deleteNode(root, key);
        string expected = serialize(out);
        if (!wouldFit(expected)) { freeTree(out); continue; } // skip; try a smaller tree
        printCase(inRoot, key, expected);
        freeTree(out);
    }

    fprintf(stderr, "generated %d cases\n", count);
    return 0;
}
