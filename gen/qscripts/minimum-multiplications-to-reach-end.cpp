// Generator + reference for "Minimum multiplications to reach end" (Striver / GFG)
// BFS over states 0..99999. From node, edges to (node*arr[i])%100000.
// Find min steps from start to end, else -1.
//
// Constraints:
//   1 <= n <= 1e4
//   1 <= arr[i] <= 1e4
//   1 <= start, end < 1e5
//
// Writes 2000 JSONL lines:
//   {"inputs":{"arr":"[...]","start":"S","end":"E"},"expected":"V"}
//
// Build: clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:   ./gen > out.jsonl

#include <vector>
#include <queue>
#include <string>
#include <random>
#include <iostream>
#include <fstream>
#include <set>
using namespace std;

const int MOD = 100000;

// Reference solution: BFS shortest path in steps.
int minimumMultiplications(vector<int> &arr, int start, int end) {
    if (start == end) return 0;
    vector<int> dist(MOD, -1);
    queue<int> q;
    dist[start] = 0;
    q.push(start);
    while (!q.empty()) {
        int node = q.front(); q.pop();
        int steps = dist[node];
        for (int x : arr) {
            int nxt = (int)(((long long)node * x) % MOD);
            if (dist[nxt] == -1) {
                dist[nxt] = steps + 1;
                if (nxt == end) return steps + 1;
                q.push(nxt);
            }
        }
    }
    return -1;
}

string arrToStr(const vector<int>& a) {
    string s = "[";
    for (size_t i = 0; i < a.size(); ++i) {
        if (i) s += ", ";
        s += to_string(a[i]);
    }
    s += "]";
    return s;
}

int main() {
    mt19937 rng(987654321u);
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-multiplications-to-reach-end.jsonl");

    auto emit = [&](vector<int> arr, int start, int end) {
        int exp = minimumMultiplications(arr, start, end);
        out << "{\"inputs\": {\"arr\": \"" << arrToStr(arr)
            << "\", \"start\": \"" << start
            << "\", \"end\": \"" << end
            << "\"}, \"expected\": \"" << exp << "\"}\n";
    };

    int total = 2000;
    int count = 0;

    // ---- Deterministic edge / known cases first ----
    emit({2, 5, 7}, 3, 30);           // expected 2 (example)
    emit({3, 4, 65}, 7, 66175);       // expected 4 (example)
    emit({3, 4, 65}, 7, 21);          // expected -1 (example, unreachable)
    count += 3;

    // start == end variants
    emit({1}, 5, 5);                  // 0
    emit({2, 3}, 99999, 99999);       // 0
    count += 2;

    // arr with 1 only: can only stay (start*1=start). reachable only if start==end
    emit({1}, 7, 8);                  // -1
    emit({1}, 1, 1);                  // 0
    count += 2;

    // min/extreme bounds
    emit({10000}, 1, 1);              // 0 (start==end)
    emit({10000}, 1, 99999);         // some value or -1
    emit({2}, 1, 99998);            // reachable? BFS
    emit({1, 1, 1}, 99999, 1);       // -1
    count += 4;

    // ---- Random cases ----
    uniform_int_distribution<int> valDist(1, 10000);     // arr[i]
    uniform_int_distribution<int> seDist(1, 99999);      // start,end in [1,1e5)

    while (count < total) {
        // mix of small and larger arrays. Keep arrays modest in size so the
        // jsonl file stays small, but occasionally go larger.
        int n;
        int r = rng() % 100;
        if (r < 60) n = 1 + rng() % 8;          // small arrays mostly
        else if (r < 90) n = 1 + rng() % 40;    // medium
        else n = 1 + rng() % 200;               // larger (still well within 1e4)

        vector<int> arr(n);
        for (int i = 0; i < n; ++i) arr[i] = valDist(rng);

        int start = seDist(rng);
        int end = seDist(rng);

        // Occasionally force start==end to produce 0 answers.
        if (count % 37 == 0) end = start;

        emit(arr, start, end);
        ++count;
    }

    out.close();
    cerr << "Wrote " << count << " cases\n";
    return 0;
}
