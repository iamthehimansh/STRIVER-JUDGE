// Generator for "m-coloring-problem"
// Builds random undirected simple graphs within constraints and computes
// expected output using an efficient correct M-colorability decision
// (bitmask backtracking with most-constrained-vertex ordering). This is
// algorithmically equivalent to the naive "try colors 1..M with backtracking"
// reference, but fast enough that even hard "false" instances on N=20 finish
// instantly.
//
// Constraints:
//   1 <= N <= 20
//   1 <= E <= N*(N-1)/2
//   1 <= M <= N
//
// starterCpp signature:
//   bool graphColoring(vector<vector<int> >& edges, int m, int n)
// Param order -> jsonl keys: edges, m, n
//
// Output line format:
//   {"inputs": {"edges": "[[0, 1], ...]", "m": "3", "n": "4"}, "expected": "true"}
//
// Build:  clang++ -std=c++17 -O2 -w m-coloring-problem.cpp -o gen
// Run:    ./gen > ../../generated-tests/m-coloring-problem.jsonl

#include <vector>
#include <set>
#include <random>
#include <iostream>
#include <sstream>
#include <algorithm>
using namespace std;

// ----- efficient reference (decides M-colorability; same answer as naive) ---
// Backtracking with (1) descending-degree vertex order and (2) color-symmetry
// breaking: vertex processed at step idx may use a color in [0, maxUsed+1].
// This is a complete, exact decision procedure (any valid m-coloring can be
// canonically relabeled to this form), and it collapses the permutation
// symmetry that makes complete graphs blow up under naive backtracking.
struct GC {
    int n, m;
    vector<int> adjmask;   // adjmask[v] = bitmask of neighbours
    vector<int> order;     // processing order (descending degree)
    vector<int> color;     // assigned color per vertex (-1 = none)

    bool dfs(int idx, int maxUsed) {
        if (idx == n) return true;
        int v = order[idx];
        int neighColorMask = 0;
        int nb = adjmask[v];
        while (nb) {
            int u = __builtin_ctz(nb);
            nb &= nb - 1;
            if (color[u] != -1) neighColorMask |= (1 << color[u]);
        }
        int limit = min(m - 1, maxUsed + 1);
        for (int c = 0; c <= limit; c++) {
            if (neighColorMask & (1 << c)) continue;
            color[v] = c;
            if (dfs(idx + 1, max(maxUsed, c))) return true;
            color[v] = -1;
        }
        return false;
    }
};

bool graphColoring(vector<vector<int>>& edges, int m, int n) {
    GC g;
    g.n = n; g.m = m;
    g.adjmask.assign(n, 0);
    for (auto& e : edges) {
        int u = e[0], v = e[1];
        if (u >= 0 && u < n && v >= 0 && v < n && u != v) {
            g.adjmask[u] |= (1 << v);
            g.adjmask[v] |= (1 << u);
        }
    }
    g.order.resize(n);
    for (int i = 0; i < n; i++) g.order[i] = i;
    sort(g.order.begin(), g.order.end(), [&](int a, int b){
        return __builtin_popcount(g.adjmask[a]) > __builtin_popcount(g.adjmask[b]);
    });
    g.color.assign(n, -1);
    return g.dfs(0, -1);
}
// ---------------------------------------------------------------------

mt19937 rng(987654321u);
int randint(int lo, int hi) { return uniform_int_distribution<int>(lo, hi)(rng); }

string edgesToStr(const vector<vector<int>>& edges) {
    string s = "[";
    for (size_t i = 0; i < edges.size(); i++) {
        s += "[" + to_string(edges[i][0]) + ", " + to_string(edges[i][1]) + "]";
        if (i + 1 < edges.size()) s += ", ";
    }
    s += "]";
    return s;
}

vector<vector<int>> makeGraph(int n, int e) {
    vector<pair<int,int>> pool;
    pool.reserve(n*(n-1)/2);
    for (int u = 0; u < n; u++)
        for (int v = u+1; v < n; v++)
            pool.push_back({u,v});
    shuffle(pool.begin(), pool.end(), rng);
    vector<vector<int>> edges;
    for (int i = 0; i < e && i < (int)pool.size(); i++)
        edges.push_back({pool[i].first, pool[i].second});
    return edges;
}

void emit(const vector<vector<int>>& edges, int m, int n) {
    vector<vector<int>> ed = edges;
    bool ans = graphColoring(ed, m, n);
    cout << "{\"inputs\": {\"edges\": \"" << edgesToStr(edges)
         << "\", \"m\": \"" << m << "\", \"n\": \"" << n
         << "\"}, \"expected\": \"" << (ans ? "true" : "false") << "\"}\n";
}

int main() {
    int total = 2000;
    int produced = 0;

    // ---- deterministic edge cases ----
    // N=2 single edge: M=1 -> false ; M=2 -> true
    { vector<vector<int>> e = {{0,1}}; emit(e,1,2); produced++; }
    { vector<vector<int>> e = {{0,1}}; emit(e,2,2); produced++; }

    // Complete graphs K_n: chromatic number = n.
    //   M=n   -> true   ;   M=n-1 -> false (the hard instance, fast with MRV)
    for (int n = 2; n <= 20 && produced < total; n++) {
        vector<vector<int>> e = makeGraph(n, n*(n-1)/2);
        emit(e, n, n); produced++;
        emit(e, max(1, n-1), n); produced++;
    }

    // Cycle graphs C_n: 2-colorable iff n even; always 3-colorable.
    for (int n = 3; n <= 20 && produced < total; n++) {
        vector<vector<int>> e;
        for (int i = 0; i < n; i++) e.push_back({i, (i+1)%n});
        emit(e, 2, n); produced++;   // true iff n even
        emit(e, 3, n); produced++;   // always true
    }

    // Star graphs: 2-colorable always (M=1 false for n>=2).
    for (int n = 2; n <= 20 && produced < total; n++) {
        vector<vector<int>> e;
        for (int i = 1; i < n; i++) e.push_back({0, i});
        emit(e, 1, n); produced++;   // false (has an edge)
        emit(e, 2, n); produced++;   // true
    }

    // ---- random body ----
    while (produced < total) {
        int n = randint(2, 20);          // need E>=1 so n>=2
        int maxE = n*(n-1)/2;            // >=1 for n>=2
        int e = randint(1, maxE);
        int m = randint(1, n);
        vector<vector<int>> edges = makeGraph(n, e);
        if (edges.empty()) continue;     // guarantee E>=1
        emit(edges, m, n);
        produced++;
    }
    return 0;
}
