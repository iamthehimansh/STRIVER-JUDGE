// Generator for "Preorder, Inorder, and Postorder Traversal in one Traversal"
// slug: pre,-post,-inorder-in-one-traversal-1
//
// Builds random binary trees within constraints:
//   1 <= number of nodes <= 1e5  (we cap generated sizes much smaller for a modest file,
//                                  but include a few large edge cases)
//   0 <= Node.val <= 1e5
//
// The tree is serialized in LeetCode-style level-order (null children of a present node are
// emitted as "null"; null nodes themselves spawn no children) -- this matches the judge's
// TreeNode* deserializer exactly. We then build the SAME tree from that serialization and
// compute in/pre/post-order, so the expected output is self-consistent with the judge.
//
// Output: generated-tests/pre,-post,-inorder-in-one-traversal-1.jsonl
//   {"inputs": {"root": "<level-order string>"}, "expected": "[ [in...] , [pre...] , [post...] ]"}

#include <iostream>
#include <vector>
#include <string>
#include <queue>
#include <random>
#include <sstream>
#include <fstream>
#include <cstdint>
using namespace std;

struct Node {
    int data;
    Node* left;
    Node* right;
    Node(int v): data(v), left(nullptr), right(nullptr) {}
};

mt19937 rng(987654321u);

// Build a random tree with exactly `n` nodes (n >= 1).
// Strategy: grow tree by repeatedly attaching a new node to a random existing free slot.
Node* buildRandomTree(int n, int maxVal) {
    uniform_int_distribution<int> valDist(0, maxVal);
    Node* root = new Node(valDist(rng));
    // list of nodes that still have a free child slot
    // store pointers to slots: pair<Node*, which> -> we model as vector of (node, side)
    struct Slot { Node* parent; int side; }; // side 0=left,1=right
    vector<Slot> slots;
    slots.push_back({root, 0});
    slots.push_back({root, 1});
    int created = 1;
    while (created < n && !slots.empty()) {
        // pick a random free slot
        uniform_int_distribution<size_t> sd(0, slots.size() - 1);
        size_t idx = sd(rng);
        Slot s = slots[idx];
        // remove by swap-pop
        slots[idx] = slots.back();
        slots.pop_back();
        Node* nw = new Node(valDist(rng));
        if (s.side == 0) s.parent->left = nw; else s.parent->right = nw;
        created++;
        slots.push_back({nw, 0});
        slots.push_back({nw, 1});
    }
    return root;
}

// Serialize tree LeetCode-style: BFS, present node -> its value; for each present node enqueue
// both children (which may be null -> emitted as "null", but a null does NOT enqueue children).
// Trim trailing nulls.
string serializeTree(Node* root) {
    vector<string> tokens;
    queue<Node*> q;
    q.push(root);
    while (!q.empty()) {
        Node* cur = q.front(); q.pop();
        if (cur == nullptr) {
            tokens.push_back("null");
        } else {
            tokens.push_back(to_string(cur->data));
            q.push(cur->left);
            q.push(cur->right);
        }
    }
    // trim trailing nulls
    while (!tokens.empty() && tokens.back() == "null") tokens.pop_back();
    string out;
    for (size_t i = 0; i < tokens.size(); ++i) {
        if (i) out += ' ';
        out += tokens[i];
    }
    return out;
}

void inorder(Node* r, vector<int>& v){ if(!r) return; inorder(r->left,v); v.push_back(r->data); inorder(r->right,v); }
void preorder(Node* r, vector<int>& v){ if(!r) return; v.push_back(r->data); preorder(r->left,v); preorder(r->right,v); }
void postorder(Node* r, vector<int>& v){ if(!r) return; postorder(r->left,v); postorder(r->right,v); v.push_back(r->data); }

// Iterative versions to avoid stack overflow on large/degenerate trees.
void inorderIt(Node* root, vector<int>& v){
    vector<Node*> st; Node* cur=root;
    while(cur||!st.empty()){
        while(cur){ st.push_back(cur); cur=cur->left; }
        cur=st.back(); st.pop_back();
        v.push_back(cur->data);
        cur=cur->right;
    }
}
void preorderIt(Node* root, vector<int>& v){
    if(!root) return;
    vector<Node*> st; st.push_back(root);
    while(!st.empty()){
        Node* c=st.back(); st.pop_back();
        v.push_back(c->data);
        if(c->right) st.push_back(c->right);
        if(c->left) st.push_back(c->left);
    }
}
void postorderIt(Node* root, vector<int>& v){
    if(!root) return;
    vector<Node*> st1, st2;
    st1.push_back(root);
    while(!st1.empty()){
        Node* c=st1.back(); st1.pop_back();
        st2.push_back(c);
        if(c->left) st1.push_back(c->left);
        if(c->right) st1.push_back(c->right);
    }
    while(!st2.empty()){ v.push_back(st2.back()->data); st2.pop_back(); }
}

string vecToStr(const vector<int>& v){
    string s = "[";
    for(size_t i=0;i<v.size();++i){ if(i) s += ", "; s += to_string(v[i]); }
    s += "]";
    return s;
}

string expectedStr(Node* root){
    vector<int> in, pre, post;
    inorderIt(root, in);
    preorderIt(root, pre);
    postorderIt(root, post);
    // [ [in] , [pre] , [post] ]
    string s = "[ " + vecToStr(in) + " , " + vecToStr(pre) + " , " + vecToStr(post) + " ]";
    return s;
}

void freeTree(Node* r){
    if(!r) return;
    // iterative free
    vector<Node*> st; st.push_back(r);
    while(!st.empty()){
        Node* c=st.back(); st.pop_back();
        if(c->left) st.push_back(c->left);
        if(c->right) st.push_back(c->right);
        delete c;
    }
}

// JSON string escaping (root string contains only digits, spaces, "null" -> no special chars,
// but escape defensively).
string jsonEscape(const string& s){
    string o; o.reserve(s.size()+2);
    for(char c: s){
        switch(c){
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

int main(){
    const string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/pre,-post,-inorder-in-one-traversal-1.jsonl";
    ofstream fout(outPath);
    if(!fout){ cerr << "cannot open output\n"; return 1; }

    const int TOTAL = 2000;
    const int MAXVAL = 100000;
    // Cap on node count for generated cases. The problem allows up to 1e5 nodes, but the live
    // judge runs ALL 2000 cases in ONE batched process and caps the COMBINED captured stdout at
    // 1 MB (lib/judge/runner.ts: cap = 1024*1024). Each node contributes 3 output numbers
    // (in/pre/post) ~ up to ~21 bytes. So the SUM of (3 * nodes * ~7 bytes) across all 2000 cases
    // must stay well under 1 MB or later cases get truncated and misaligned. We therefore bound
    // per-case size AND enforce a global output-byte budget below.
    const int MAXNODES = 120;                 // hard per-case cap on node count
    // The live judge (scripts/judge_exec.py) caps the COMBINED captured stdout at OUT_CAP = 256 KB.
    // Empirically, total batched stdout crossing ~256 KB truncates later cases mid-line. Keep the
    // total comfortably under that.
    const long long OUT_BUDGET = 200000;      // total output-bytes budget (< 256 KB cap, with margin)

    // Estimate the output bytes a case will contribute to the batched stdout: 3 traversals,
    // each prints `n` numbers space-separated; rows are joined by a space when flattened, plus a
    // trailing newline. ~= total_digits + separators + 1.
    auto outBytesFor = [&](Node* root)->long long{
        vector<int> in; inorderIt(root, in);
        long long nums = (long long)in.size() * 3;          // total numbers across 3 traversals
        long long digits = 0;
        for(int x : in){ digits += (x==0?1:(long long)to_string(x).size()); }
        digits *= 3;                                         // same multiset printed 3 times
        return digits + nums /*separators*/ + 1 /*newline*/;
    };

    long long usedOut = 0;

    auto emit = [&](Node* root){
        string ser = serializeTree(root);
        string exp = expectedStr(root);
        fout << "{\"inputs\": {\"root\": \"" << jsonEscape(ser) << "\"}, \"expected\": \""
             << jsonEscape(exp) << "\"}\n";
        usedOut += outBytesFor(root);
    };

    int count = 0;

    // ---- Edge cases first ----
    // single node, val 0
    { Node* r = new Node(0); emit(r); freeTree(r); count++; }
    // single node, val max
    { Node* r = new Node(MAXVAL); emit(r); freeTree(r); count++; }
    // single node, val 1
    { Node* r = new Node(1); emit(r); freeTree(r); count++; }
    // two nodes (left child)
    { Node* r=new Node(5); r->left=new Node(3); emit(r); freeTree(r); count++; }
    // two nodes (right child)
    { Node* r=new Node(5); r->right=new Node(7); emit(r); freeTree(r); count++; }
    // the dataset example 1: [1,3,4,5,2,7,6]
    {
        Node* n1=new Node(1), *n3=new Node(3), *n4=new Node(4),
             *n5=new Node(5), *n2=new Node(2), *n7=new Node(7), *n6=new Node(6);
        n1->left=n3; n1->right=n4; n3->left=n5; n3->right=n2; n4->left=n7; n4->right=n6;
        emit(n1); freeTree(n1); count++;
    }
    // dataset example 2: [1,2,3,null,null,null,6]
    {
        Node* n1=new Node(1), *n2=new Node(2), *n3=new Node(3), *n6=new Node(6);
        n1->left=n2; n1->right=n3; n3->right=n6;
        emit(n1); freeTree(n1); count++;
    }
    // left-skewed chain (degenerate) at MAXNODES
    {
        Node* r=new Node(0); Node* cur=r;
        for(int i=1;i<MAXNODES;i++){ cur->left=new Node(i%(MAXVAL+1)); cur=cur->left; }
        emit(r); freeTree(r); count++;
    }
    // right-skewed chain (degenerate) at MAXNODES
    {
        Node* r=new Node(0); Node* cur=r;
        for(int i=1;i<MAXNODES;i++){ cur->right=new Node(i%(MAXVAL+1)); cur=cur->right; }
        emit(r); freeTree(r); count++;
    }
    // a near-MAXNODES random tree (largest random structure we emit)
    {
        Node* r = buildRandomTree(MAXNODES, MAXVAL);
        emit(r); freeTree(r); count++;
    }

    // ---- Random cases ----
    // Heavily weighted toward small trees so the COMBINED batched stdout stays under the judge's
    // 1 MB capture cap. We also enforce a running output-byte budget: once we approach the budget,
    // we shrink generated sizes so all 2000 cases fit. (Final cases may be size 1-3 — still valid.)
    while(count < TOTAL){
        long long remainingCases = TOTAL - count;
        long long remainingBudget = OUT_BUDGET - usedOut;
        // average output bytes still affordable per remaining case
        long long avgBudget = remainingCases > 0 ? remainingBudget / remainingCases : 0;
        // each node ~ 21 output bytes (3 traversals * ~7 bytes). derive a soft node cap.
        int softCap = (int)(avgBudget / 21);
        if(softCap < 1) softCap = 1;
        if(softCap > MAXNODES) softCap = MAXNODES;

        int n;
        int bucket = rng() % 100;
        if(bucket < 70){
            n = 1 + rng() % 12;                  // tiny trees (cheap, lots of variety)
        } else if(bucket < 95){
            n = 1 + rng() % 40;                  // small
        } else {
            n = 1 + rng() % MAXNODES;            // occasionally larger
        }
        if(n > softCap) n = 1 + rng() % softCap; // clamp to budget
        if(n < 1) n = 1;

        Node* r = buildRandomTree(n, MAXVAL);
        emit(r);
        freeTree(r);
        count++;
    }

    fout.close();
    cerr << "Wrote " << count << " cases to " << outPath << "\n";
    return 0;
}
