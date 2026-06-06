// Generator + reference for:
//   "Find the city with the smallest number of neighbors"
//
// Signature (starterCpp):
//   int findCity(int n, int m, vector<vector<int>>& edges, int distanceThreshold)
// The output keys (per dataset testcases) are: N, distanceThreshold, edges.
// "m" just equals edges.size() (an array-length param) so it is dropped.
//
// Constraints:
//   1 <= n <= 100
//   1 <= m <= n*(n-1)/2
//   length(edges[i]) == 3
//   0 <= from_i < to_i < n
//   1 <= weight_i, distanceThreshold <= 10^4
//   All pairs (from_i, to_i) are distinct
//
// Reference: Floyd-Warshall all-pairs shortest paths, then for each city count
//   reachable cities within distanceThreshold; pick city with smallest count,
//   ties broken by GREATEST city index.
//
// Build:  clang++ -std=c++17 -O2 -w gen.cpp -o gen && ./gen
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-the-city-with-the-smallest-number-of-neighbors.jsonl

#include <cstdio>
#include <cstdint>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <set>
#include <utility>
#include <limits>
#include <fstream>

using namespace std;

static const long long INF = (long long)4e18;

// ----- Reference solution (Floyd-Warshall) -----
int findCity(int n, int /*m*/, vector<vector<int>>& edges, int distanceThreshold) {
    vector<vector<long long>> dist(n, vector<long long>(n, INF));
    for (int i = 0; i < n; ++i) dist[i][i] = 0;
    for (auto& e : edges) {
        int u = e[0], v = e[1], w = e[2];
        if ((long long)w < dist[u][v]) { dist[u][v] = w; dist[v][u] = w; }
    }
    for (int k = 0; k < n; ++k)
        for (int i = 0; i < n; ++i) {
            if (dist[i][k] == INF) continue;
            for (int j = 0; j < n; ++j) {
                if (dist[k][j] == INF) continue;
                long long nd = dist[i][k] + dist[k][j];
                if (nd < dist[i][j]) dist[i][j] = nd;
            }
        }
    int bestCount = numeric_limits<int>::max();
    int ans = 0;
    for (int i = 0; i < n; ++i) {
        int cnt = 0;
        for (int j = 0; j < n; ++j)
            if (i != j && dist[i][j] <= distanceThreshold) ++cnt;
        if (cnt < bestCount) { bestCount = cnt; ans = i; }
        else if (cnt == bestCount) ans = max(ans, i); // tie -> greatest city
    }
    return ans;
}

// ----- Serialization helpers -----
string edgesToStr(const vector<vector<int>>& edges) {
    string s = "[";
    for (size_t i = 0; i < edges.size(); ++i) {
        if (i) s += ",";
        s += "[" + to_string(edges[i][0]) + "," + to_string(edges[i][1]) + "," + to_string(edges[i][2]) + "]";
    }
    s += "]";
    return s;
}

int main() {
    mt19937_64 rng(123456789ULL);
    auto randint = [&](int lo, int hi) {
        return (int)(rng() % (uint64_t)(hi - lo + 1)) + lo;
    };

    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/find-the-city-with-the-smallest-number-of-neighbors.jsonl";
    ofstream out(outPath);
    if (!out) { fprintf(stderr, "cannot open output\n"); return 1; }

    const int TOTAL = 2000;

    // A small set of explicit/edge cases first.
    struct Case { int n; vector<vector<int>> edges; int dt; };
    vector<Case> seeds;
    // dataset examples
    seeds.push_back({4, {{0,1,3},{1,2,1},{1,3,4},{2,3,1}}, 4}); // -> 3
    seeds.push_back({3, {{0,1,1},{0,2,3}}, 2});                  // -> 2
    seeds.push_back({3, {{0,1,2},{1,2,1},{0,2,4}}, 2});          // nowYourTurn -> 1
    // n=1 (no edges possible since m>=1 needs a pair, but n=1 has 0 possible pairs)
    // Constraint says m>=1; with n=1 there are zero possible edges. To stay valid
    // we require n>=2 whenever we must add an edge. We'll still test n=2 minimal.
    seeds.push_back({2, {{0,1,1}}, 1});      // both reachable -> tie -> city 1
    seeds.push_back({2, {{0,1,5}}, 4});      // not reachable within dt -> both count 0 -> city 1
    seeds.push_back({2, {{0,1,10000}}, 10000}); // extreme weight, reachable -> 1
    seeds.push_back({3, {{0,1,1},{0,2,1},{1,2,1}}, 1}); // triangle, all count 2 -> 2

    for (auto& c : seeds) {
        vector<vector<int>> e = c.edges;
        int a = findCity(c.n, (int)e.size(), e, c.dt);
        out << "{\"inputs\": {\"N\": \"" << c.n
            << "\", \"distanceThreshold\": \"" << c.dt
            << "\", \"edges\": \"" << edgesToStr(e)
            << "\"}, \"expected\": \"" << a << "\"}\n";
    }

    int produced = (int)seeds.size();

    while (produced < TOTAL) {
        // choose n
        int n;
        int r = randint(1, 100);
        if (r <= 8) n = 2;                 // many small
        else if (r <= 15) n = 3;
        else if (r <= 20) n = randint(2, 5);
        else if (r >= 99) n = 100;         // a few max
        else n = randint(2, 60);

        // maximum possible distinct undirected pairs
        long long maxPairs = (long long)n * (n - 1) / 2;
        if (maxPairs < 1) continue; // shouldn't happen since n>=2

        // choose m in [1, maxPairs]; bias toward sparse-ish but include dense
        int m;
        {
            long long cap = maxPairs;
            // for large n, cap edges to keep input modest but still valid & varied
            long long upper = min<long long>(cap, 300);
            int rr = randint(1, 100);
            if (rr <= 25) m = (int)max<long long>(1, n - 1);                 // tree-ish density
            else if (rr <= 60) m = (int)randint(1, (int)min<long long>(upper, max<long long>(1, 2LL*n)));
            else if (rr <= 90) m = (int)randint(1, (int)upper);
            else m = (int)cap; // fully dense (only feasible for small n)
            if (m < 1) m = 1;
            if (m > cap) m = (int)cap;
            // hard guard so very dense large-n cases stay reasonable in size
            if (m > 400) m = 400;
        }

        // Build a list of all possible pairs (only feasible for small/medium n).
        // For large n we sample pairs without enumerating all.
        vector<vector<int>> edges;
        edges.reserve(m);
        set<pair<int,int>> used;

        if (maxPairs <= 5000) {
            vector<pair<int,int>> all;
            all.reserve((size_t)maxPairs);
            for (int u = 0; u < n; ++u)
                for (int v = u + 1; v < n; ++v)
                    all.push_back({u, v});
            shuffle(all.begin(), all.end(), rng);
            for (int i = 0; i < m && i < (int)all.size(); ++i) {
                int w = randint(1, 10000);
                edges.push_back({all[i].first, all[i].second, w});
            }
        } else {
            // sample distinct pairs by rejection
            int guard = 0;
            while ((int)edges.size() < m && guard < m * 40) {
                ++guard;
                int u = randint(0, n - 1), v = randint(0, n - 1);
                if (u == v) continue;
                if (u > v) swap(u, v);
                if (used.count({u, v})) continue;
                used.insert({u, v});
                int w = randint(1, 10000);
                edges.push_back({u, v, w});
            }
            if (edges.empty()) continue;
        }

        if (edges.empty()) continue;

        int dt = randint(1, 10000);

        int a = findCity(n, (int)edges.size(), edges, dt);
        out << "{\"inputs\": {\"N\": \"" << n
            << "\", \"distanceThreshold\": \"" << dt
            << "\", \"edges\": \"" << edgesToStr(edges)
            << "\"}, \"expected\": \"" << a << "\"}\n";
        ++produced;
    }

    out.close();
    fprintf(stderr, "wrote %d cases\n", produced);
    return 0;
}
