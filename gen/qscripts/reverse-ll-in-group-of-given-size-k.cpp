// Generator for "Reverse LL in group of given size K"
// Builds random linked lists within constraints, runs the reference reverseKGroup,
// and writes generated-tests/reverse-ll-in-group-of-given-size-k.jsonl
//
// Constraints:
//   1 <= k <= number of nodes <= 1e5
//   -1e4 <= ListNode.val <= 1e4
//
// Input keys (matching dataset testcases): "nums" (list values as "[a, b, ...]"), "k" (int).
// Expected: reversed list values, space-separated (judge serializes ListNode output that way,
//           and compares leniently ignoring brackets/commas/whitespace).
//
// Build: clang++ -std=c++17 -O2 -w reverse-ll-in-group-of-given-size-k.cpp -o gen
// Run:   ./gen > output.jsonl

#include <cstdio>
#include <cstdlib>
#include <vector>
#include <string>
#include <random>
#include <set>
#include <iostream>
using namespace std;

struct ListNode {
    int val;
    ListNode *next;
    ListNode() { val = 0; next = NULL; }
    ListNode(int data1) { val = data1; next = NULL; }
    ListNode(int data1, ListNode *next1) { val = data1; next = next1; }
};

// ---- Reference solution (from striver-a2z ref) ----
ListNode* reverseKGroup(ListNode* head, int k) {
    ListNode* ptr = head;
    for (int i = 0; i < k; i++) {
        if (!ptr) return head; // less than k nodes remaining
        ptr = ptr->next;
    }
    int count = k;
    ListNode* prev = NULL;
    ListNode* curr = head;
    ListNode* frwd = NULL;
    while (count && curr) {
        frwd = curr->next;
        curr->next = prev;
        prev = curr;
        curr = frwd;
        count--;
    }
    if (frwd)
        head->next = reverseKGroup(frwd, k);
    return prev;
}
// ---------------------------------------------------

ListNode* build(const vector<int>& vals) {
    ListNode* head = NULL; ListNode* tail = NULL;
    for (int v : vals) {
        ListNode* node = new ListNode(v);
        if (!head) { head = tail = node; }
        else { tail->next = node; tail = node; }
    }
    return head;
}

void freeList(ListNode* head) {
    while (head) { ListNode* nx = head->next; delete head; head = nx; }
}

string vecToInputStr(const vector<int>& v) {
    // "[a, b, c]"
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

string listToExpected(ListNode* head) {
    // space-separated values
    string s;
    bool first = true;
    while (head) {
        if (!first) s += " ";
        s += to_string(head->val);
        first = false;
        head = head->next;
    }
    return s;
}

mt19937 rng(123456789u);
int randInt(int lo, int hi) {
    return uniform_int_distribution<int>(lo, hi)(rng);
}

void emitCase(const vector<int>& vals, int k) {
    ListNode* head = build(vals);
    ListNode* res = reverseKGroup(head, k);
    string expected = listToExpected(res);
    freeList(res);
    // JSON line. Values are simple ints; no escaping needed.
    printf("{\"inputs\": {\"nums\": \"%s\", \"k\": \"%d\"}, \"expected\": \"%s\"}\n",
           vecToInputStr(vals).c_str(), k, expected.c_str());
}

vector<int> randVals(int n) {
    vector<int> v(n);
    for (int i = 0; i < n; i++) v[i] = randInt(-10000, 10000);
    return v;
}

int main() {
    int total = 0;
    const int TARGET = 2000;

    // ---- Edge cases ----
    // single node, k=1
    emitCase({5}, 1); total++;
    emitCase({-10000}, 1); total++;
    emitCase({10000}, 1); total++;
    // k == n (full reverse)
    emitCase({1,2,3,4,5}, 5); total++;
    emitCase({1,2}, 2); total++;
    // k == 1 (no change)
    emitCase({3,1,4,1,5,9,2,6}, 1); total++;
    // dataset examples
    emitCase({1,2,3,4,5}, 2); total++;
    emitCase({1,2,3,4,5}, 3); total++;
    emitCase({6,1,2,3,4,7}, 4); total++;
    // remainder cases
    emitCase({1,2,3,4,5,6,7}, 3); total++;   // remainder 1
    emitCase({1,2,3,4,5,6,7,8}, 3); total++; // remainder 2
    // two nodes k=1
    emitCase({7,8}, 1); total++;
    // extremes
    emitCase({-10000,10000,-10000,10000}, 2); total++;
    emitCase({0,0,0,0}, 4); total++;

    // NOTE on sizes: the constraint allows up to 1e5 nodes, but the live judge
    // runs ALL cases in ONE batched process and caps the TOTAL captured stdout
    // at 256 KB (judge_exec.py OUT_CAP). With 2000 cases that is ~120 bytes/line
    // budget. We therefore keep list sizes small (<= MAXN) so the full output of
    // every case is captured and compared. MAXN is well within the stated
    // constraint range; the algorithm's correctness is independent of length and
    // is exercised thoroughly by every (n,k) grouping/remainder combination here.
    const int MAXN = 30; // <= 30 numbers * ~6 bytes < 180 bytes/line, total well under 256 KB

    // small exhaustive: all n in [1..30], every k in [1..n]  (465 cases)
    for (int n = 1; n <= MAXN && total < TARGET; n++) {
        for (int k = 1; k <= n && total < TARGET; k++) {
            vector<int> v = randVals(n);
            emitCase(v, k);
            total++;
        }
    }

    // fill the rest with random small cases (n in [1..MAXN]) covering many value
    // patterns; bias k toward boundary values (1, n, n/2) plus random.
    while (total < TARGET) {
        int n = randInt(1, MAXN);
        int kchoice = randInt(0, 3);
        int k;
        if (kchoice == 0) k = 1;
        else if (kchoice == 1) k = n;
        else if (kchoice == 2) k = (n + 1) / 2;
        else k = randInt(1, n);
        vector<int> v = randVals(n);
        emitCase(v, k);
        total++;
    }

    return 0;
}
