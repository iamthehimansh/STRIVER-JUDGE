// Test-case generator for "number-of-operations-to-make-network-connected".
// Reference: Disjoint Set Union. ans = (#connected components - 1), or -1 if
// there are fewer than n-1 edges (then the network can never be connected).
//
// Build (macOS clang lacks <bits/stdc++.h>, so provide a shim include dir):
//   mkdir -p /tmp/ng/bits && cat > /tmp/ng/bits/stdc++.h <<'H'
//   #include <iostream>
//   #include <vector>
//   #include <functional>
//   #include <algorithm>
//   #include <fstream>
//   #include <string>
//   #include <random>
//   H
//   clang++ -std=c++17 -O2 -w -I /tmp/ng \
//     "gen/qscripts/number-of-operations-to-make-network-connected.cpp" -o /tmp/ng/gen
//   /tmp/ng/gen 2000      # writes generated-tests/<slug>.jsonl (2000 cases)
//
// On Linux just: g++ -std=c++17 -O2 -w <file> -o gen && ./gen 2000
#include <bits/stdc++.h>
using namespace std;

// ---- Reference (same logic as class Solution::solve) ----
int solve(int n, vector<vector<int>> &Edge){
    if ((long long)(n - 1) > (long long)Edge.size())
        return -1;
    vector<int> parent(n), sz(n, 1);
    for (int i = 0; i < n; i++) parent[i] = i;
    function<int(int)> find = [&](int x){
        while (parent[x] != x){ parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    };
    for (auto &c : Edge){
        int u = c[0], v = c[1];
        int pu = find(u), pv = find(v);
        if (pu == pv) continue;
        if (sz[pu] < sz[pv]) swap(pu, pv);
        parent[pv] = pu; sz[pu] += sz[pv];
    }
    int comp = 0;
    for (int i = 0; i < n; i++) if (find(i) == i) comp++;
    return comp - 1;
}

string edgesToStr(vector<vector<int>> &E){
    string s = "[";
    for (size_t i=0;i<E.size();i++){
        if(i) s += ",";
        s += "[" + to_string(E[i][0]) + "," + to_string(E[i][1]) + "]";
    }
    s += "]";
    return s;
}

mt19937 rng(123456789);
int randint(int lo, int hi){ return lo + (int)(rng() % (unsigned)(hi - lo + 1)); }

int main(int argc, char** argv){
    int N = 2000;
    if (argc > 1) N = atoi(argv[1]);
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-operations-to-make-network-connected.jsonl");

    // helper to emit one case given n and edges
    auto emit = [&](int n, vector<vector<int>> &E){
        // edges must be non-empty per constraint (1 <= Edge.length)
        if (E.empty()) return;
        int ans = solve(n, E);
        out << "{\"inputs\": {\"n\": \"" << n << "\", \"Edge\": \"" << edgesToStr(E) << "\"}, \"expected\": \"" << ans << "\"}\n";
    };

    int produced = 0;

    // ---- Edge cases ----
    {
        // n=1, single self edge [0,0] -> connected, 0 ops
        vector<vector<int>> E = {{0,0}}; emit(1,E); produced++;
    }
    {
        // n=2, edge [0,1] -> 0
        vector<vector<int>> E = {{0,1}}; emit(2,E); produced++;
    }
    {
        // n=4, [[0,1]] -> -1 (example 3)
        vector<vector<int>> E = {{0,1}}; emit(4,E); produced++;
    }
    {
        // example 1: n=4
        vector<vector<int>> E = {{0,1},{0,2},{1,2}}; emit(4,E); produced++;
    }
    {
        // example 2: n=9
        vector<vector<int>> E = {{0,1},{0,2},{0,3},{1,2},{2,3},{4,5},{5,6},{7,8}}; emit(9,E); produced++;
    }
    {
        // n=3 with self loops only -> 3 isolated comps but edges count 3 >= n-1=2 -> 2 ops
        vector<vector<int>> E = {{0,0},{1,1},{2,2}}; emit(3,E); produced++;
    }

    // ---- Random cases ----
    while (produced < N){
        // choose n: mix of small and larger up to 1e4
        int n;
        int r = randint(0,9);
        if (r < 3) n = randint(1, 6);
        else if (r < 6) n = randint(2, 50);
        else if (r < 8) n = randint(2, 1000);
        else n = randint(2, 10000);

        // number of edges: 1 .. 1e4
        int maxE = 10000;
        int m;
        int er = randint(0,9);
        if (er < 4) {
            // sometimes near n-1 to get connected / few comps
            int base = max(1, n-1);
            m = max(1, min(maxE, base + randint(-2, 3)));
        } else if (er < 7) {
            m = randint(1, min(maxE, max(1, 3*n)));
        } else {
            m = randint(1, maxE);
        }
        if (m < 1) m = 1;
        if (m > maxE) m = maxE;

        vector<vector<int>> E;
        E.reserve(m);
        for (int i=0;i<m;i++){
            int a = randint(0, n-1);
            int b = randint(0, n-1);
            E.push_back({a,b});
        }
        emit(n, E);
        produced++;
    }

    out.close();
    cerr << "produced " << produced << " cases\n";
    return 0;
}
