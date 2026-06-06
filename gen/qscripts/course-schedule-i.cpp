// Generator + static test set for "Course Schedule I"
// Reference: Kahn's algorithm (DAG check). Edge b->a for prerequisite [a,b].
// Output JSONL keys are the starterCpp param names: N, arr.
//
// Build:  clang++ -std=c++17 -O2 -w course-schedule-i.cpp -o /tmp/csgen/gen
// Run:    /tmp/csgen/gen > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/course-schedule-i.jsonl"

#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <random>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;

// ---- Reference oracle (same logic the judge will run) ----
bool canFinish(int N, vector<vector<int>> arr) {
    vector<int> indeg(N, 0);
    vector<vector<int>> adj(N);
    for (auto &it : arr) {
        indeg[it[0]]++;
        adj[it[1]].push_back(it[0]);
    }
    queue<int> q;
    for (int i = 0; i < N; i++) if (indeg[i] == 0) q.push(i);
    int cnt = 0;
    while (!q.empty()) {
        int node = q.front(); q.pop();
        cnt++;
        for (int v : adj[node]) {
            indeg[v]--;
            if (indeg[v] == 0) q.push(v);
        }
    }
    return cnt == N;
}

mt19937 rng(987654321u);
int randint(int lo, int hi) { return uniform_int_distribution<int>(lo, hi)(rng); }

string arrToStr(const vector<vector<int>>& arr) {
    // formatted like examples: [[1,0],[2,1]]
    string s = "[";
    for (size_t i = 0; i < arr.size(); i++) {
        if (i) s += ",";
        s += "[" + to_string(arr[i][0]) + "," + to_string(arr[i][1]) + "]";
    }
    s += "]";
    return s;
}

string jsonEscape(const string& in) {
    string out;
    for (char c : in) {
        if (c == '"' || c == '\\') { out += '\\'; out += c; }
        else out += c;
    }
    return out;
}

// Generate a random unique set of pairs given N and a target count.
// All pairs distinct, 0 <= a,b < N. Pairs may include self-loops (a==b) which
// constraints permit (0<=arr[i][0],arr[i][1]<N, no restriction a!=b); a self
// loop makes it impossible. We'll keep self-loops rare but allowed to exercise.
vector<vector<int>> genPairs(int N, int target, bool allowSelfLoop) {
    set<pair<int,int>> seen;
    vector<vector<int>> arr;
    long long maxPairs = (long long)N * N; // a,b each in [0,N) -> N*N possible incl self loops
    if (!allowSelfLoop) maxPairs = (long long)N * (N - 1);
    if (target > maxPairs) target = (int)maxPairs;
    int attempts = 0;
    int attemptCap = target * 50 + 1000;
    while ((int)arr.size() < target && attempts < attemptCap) {
        attempts++;
        int a = randint(0, N - 1);
        int b = randint(0, N - 1);
        if (!allowSelfLoop && a == b) continue;
        if (seen.count({a, b})) continue;
        seen.insert({a, b});
        arr.push_back({a, b});
    }
    return arr;
}

// Generate a guaranteed-acyclic set: pick a random permutation as topo order,
// only emit edges b->a (prereq [a,b]) where b comes before a in topo order,
// i.e. pos[b] < pos[a]. This guarantees a DAG (canFinish == true).
vector<vector<int>> genDAG(int N, int target) {
    vector<int> perm(N);
    for (int i = 0; i < N; i++) perm[i] = i;
    shuffle(perm.begin(), perm.end(), rng);
    vector<int> pos(N);
    for (int i = 0; i < N; i++) pos[perm[i]] = i; // pos in topo order
    set<pair<int,int>> seen;
    vector<vector<int>> arr;
    long long maxPairs = (long long)N * (N - 1) / 2;
    if (target > maxPairs) target = (int)maxPairs;
    int attempts = 0;
    int attemptCap = target * 50 + 1000;
    while ((int)arr.size() < target && attempts < attemptCap) {
        attempts++;
        int a = randint(0, N - 1);
        int b = randint(0, N - 1);
        if (a == b) continue;
        // prereq [a,b]: must take b before a => b earlier in topo order
        if (pos[b] >= pos[a]) swap(a, b); // ensure b earlier than a
        if (pos[b] >= pos[a]) continue; // both equal impossible since a!=b
        if (seen.count({a, b})) continue;
        seen.insert({a, b});
        arr.push_back({a, b});
    }
    return arr;
}

void emit(const vector<pair<int, vector<vector<int>>>>& cases) {
    for (auto &c : cases) {
        int N = c.first;
        const vector<vector<int>>& arr = c.second;
        bool res = canFinish(N, arr);
        string expected = res ? "True" : "False";
        // inputs: N (int), arr (2D array)
        string line = "{\"inputs\": {\"N\": \"" + to_string(N) +
                      "\", \"arr\": \"" + jsonEscape(arrToStr(arr)) +
                      "\"}, \"expected\": \"" + expected + "\"}";
        cout << line << "\n";
    }
}

int main() {
    vector<pair<int, vector<vector<int>>>> cases;

    // ---- Edge / fixed cases ----
    // Dataset examples (verify reproduction)
    cases.push_back({4, {{1,0},{2,1},{3,2}}});            // True
    cases.push_back({4, {{0,1},{3,2},{1,3},{3,0}}});      // False
    cases.push_back({2, {{1,0}}});                         // True
    // min N, no edges
    cases.push_back({1, {}});                              // True
    cases.push_back({2, {}});                              // True
    // self loop -> impossible
    cases.push_back({1, {{0,0}}});                         // False
    cases.push_back({3, {{0,0}}});                         // False
    // simple 2-cycle
    cases.push_back({2, {{0,1},{1,0}}});                   // False
    // chain (DAG)
    cases.push_back({5, {{1,0},{2,1},{3,2},{4,3}}});       // True
    // large N no edges
    cases.push_back({2000, {}});                           // True

    int produced = (int)cases.size();
    int TOTAL = 2000;

    // ---- Random DAG cases (expected True) ~ 35% ----
    int dagCount = (TOTAL - produced) * 35 / 100;
    for (int i = 0; i < dagCount; i++) {
        int N = randint(1, 2000);
        long long maxEdges = (long long)N * (N - 1) / 2;
        int target = (int)min<long long>(randint(0, 5000), maxEdges);
        cases.push_back({N, genDAG(N, target)});
    }

    // ---- Random general cases (mixed True/False) ----
    while ((int)cases.size() < TOTAL) {
        int N = randint(1, 2000);
        // edge count up to 5000 (and not exceeding possible distinct pairs)
        int target = randint(0, 5000);
        bool allowSelf = (randint(0, 9) == 0); // 10% allow self loops
        cases.push_back({N, genPairs(N, target, allowSelf)});
    }

    emit(cases);
    return 0;
}
