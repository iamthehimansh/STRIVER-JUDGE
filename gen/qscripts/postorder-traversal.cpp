// Generator for "postorder-traversal".
// Builds random valid binary trees within constraints:
//   1 <= number of nodes <= 100,  -100 <= Node.val <= 100
// Input serialization: LeetCode-style level-order, space-separated, "null" for
// missing children (null nodes get no children). This matches the judge's
// TreeNode build (struct field is `data`).
// Output: postorder traversal (left, right, root) as "[a, b, c]".
//
// Writes: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postorder-traversal.jsonl
// One JSON object per line: {"inputs": {"root": "<level-order>"}, "expected": "[...]"}

#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <random>
#include <queue>
#include <set>

using namespace std;

struct TreeNode {
    int data;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int v) : data(v), left(nullptr), right(nullptr) {}
};

// Build a random tree with exactly nNodes nodes; return root.
// Uses the standard "attach to a random available slot" growth so any tree
// shape is reachable. Values in [-100, 100].
TreeNode* buildRandomTree(int nNodes, mt19937& rng) {
    uniform_int_distribution<int> valDist(-100, 100);
    TreeNode* root = new TreeNode(valDist(rng));
    // available slots: pairs (parent, side) where side 0=left,1=right
    vector<pair<TreeNode*, int>> slots;
    slots.push_back({root, 0});
    slots.push_back({root, 1});
    int created = 1;
    while (created < nNodes && !slots.empty()) {
        uniform_int_distribution<int> idx(0, (int)slots.size() - 1);
        int i = idx(rng);
        auto slot = slots[i];
        slots[i] = slots.back();
        slots.pop_back();
        TreeNode* node = new TreeNode(valDist(rng));
        if (slot.second == 0) slot.first->left = node;
        else slot.first->right = node;
        slots.push_back({node, 0});
        slots.push_back({node, 1});
        created++;
    }
    return root;
}

// Serialize tree to LeetCode-style level-order with "null" for missing children;
// null nodes do not enqueue children. Trailing nulls trimmed.
string serializeLevelOrder(TreeNode* root) {
    vector<string> out;
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* cur = q.front();
        q.pop();
        if (cur == nullptr) {
            out.push_back("null");
        } else {
            out.push_back(to_string(cur->data));
            q.push(cur->left);
            q.push(cur->right);
        }
    }
    // trim trailing nulls
    while (!out.empty() && out.back() == "null") out.pop_back();
    string s;
    for (size_t i = 0; i < out.size(); i++) {
        if (i) s += " ";
        s += out[i];
    }
    return s;
}

void postorder(TreeNode* root, vector<int>& ans) {
    if (!root) return;
    postorder(root->left, ans);
    postorder(root->right, ans);
    ans.push_back(root->data);
}

void freeTree(TreeNode* root) {
    if (!root) return;
    freeTree(root->left);
    freeTree(root->right);
    delete root;
}

string formatVec(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

// JSON-escape (only quotes/backslashes matter here since strings are simple)
string jesc(const string& s) {
    string o;
    for (char c : s) {
        if (c == '"' || c == '\\') o += '\\';
        o += c;
    }
    return o;
}

int main(int argc, char** argv) {
    const int TOTAL = 2000;
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/postorder-traversal.jsonl";
    if (argc > 1) outPath = argv[1];

    mt19937 rng(123456789u);
    ofstream fout(outPath);
    if (!fout) {
        cerr << "cannot open output" << endl;
        return 1;
    }

    set<string> seen;
    int written = 0;

    // The judge captures the batched program's TOTAL stdout with a hard cap of
    // 256*1024 bytes (judge_exec.py OUT_CAP). The driver prints, per case, the
    // postorder values space-separated plus one '\n'. We must keep the SUM of
    // those judge-output bytes under the cap (with margin) or later cases get
    // truncated mid-line and fail. Track and enforce a conservative budget.
    const long long OUT_BUDGET = 245000; // < 262144, leaves safety margin
    long long judgeOutBytes = 0;

    // bytes the judge will print for this answer: value list (space-separated) + '\n'
    auto judgeBytesFor = [](const vector<int>& v) -> long long {
        long long b = 1; // trailing '\n'
        for (size_t i = 0; i < v.size(); i++) {
            if (i) b += 1; // space separator
            b += (long long)to_string(v[i]).size();
        }
        return b;
    };

    auto emit = [&](TreeNode* root) {
        string in = serializeLevelOrder(root);
        if (seen.count(in)) return false;
        vector<int> ans;
        postorder(root, ans);
        long long need = judgeBytesFor(ans);
        if (judgeOutBytes + need > OUT_BUDGET) return false; // would exceed judge cap
        seen.insert(in);
        judgeOutBytes += need;
        fout << "{\"inputs\": {\"root\": \"" << jesc(in)
             << "\"}, \"expected\": \"" << jesc(formatVec(ans)) << "\"}\n";
        written++;
        return true;
    };

    // Edge cases first.
    {
        // single node, min/extreme values
        for (int v : {-100, 100, 0, 1, -1, 50}) {
            TreeNode* r = new TreeNode(v);
            emit(r);
            freeTree(r);
        }
        // left-skewed chain of 100
        {
            TreeNode* r = new TreeNode(-100);
            TreeNode* cur = r;
            for (int i = 1; i < 100; i++) { cur->left = new TreeNode(-100 + i); cur = cur->left; }
            emit(r);
            freeTree(r);
        }
        // right-skewed chain of 100
        {
            TreeNode* r = new TreeNode(100);
            TreeNode* cur = r;
            for (int i = 1; i < 100; i++) { cur->right = new TreeNode(100 - i); cur = cur->right; }
            emit(r);
            freeTree(r);
        }
        // perfect-ish full tree of 100 nodes
        {
            TreeNode* r = buildRandomTree(100, rng); // approx; just a 100-node tree
            emit(r);
            freeTree(r);
        }
    }

    // Random trees, sizes biased small so we can fit ~2000 cases under the
    // judge's total-stdout cap while still covering the full size range.
    // ~70% tiny (1..12), ~25% small (1..30), ~5% larger (1..100).
    uniform_int_distribution<int> bucket(0, 99);
    uniform_int_distribution<int> tiny(1, 12);
    uniform_int_distribution<int> small(1, 30);
    uniform_int_distribution<int> large(1, 100);
    int guard = 0;
    while (written < TOTAL && guard < TOTAL * 200) {
        guard++;
        int b = bucket(rng);
        int n;
        if (b < 70) n = tiny(rng);
        else if (b < 95) n = small(rng);
        else n = large(rng);
        TreeNode* r = buildRandomTree(n, rng);
        emit(r);
        freeTree(r);
    }

    fout.close();
    cerr << "written=" << written << endl;
    return 0;
}
