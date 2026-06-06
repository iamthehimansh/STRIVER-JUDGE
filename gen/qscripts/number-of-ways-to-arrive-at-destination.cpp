// Generator + reference oracle for "Number of ways to arrive at destination".
// Builds random connected graphs within constraints and computes expected
// output via Dijkstra (counting shortest paths, mod 1e9+7).
//
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-ways-to-arrive-at-destination.jsonl
// Each line: {"inputs": {"n": "7", "roads": "[[...],...]"}, "expected": "<int>"}
//
// Constraints:
//   1 <= n <= 200
//   n-1 <= roads.length <= n*(n-1)/2
//   roads[i].length == 3, 0 <= u,v <= n-1, 1 <= time <= 1e9, u != v
//   connected, at most one road between any pair.

#include <vector>
#include <queue>
#include <string>
#include <random>
#include <set>
#include <fstream>
#include <iostream>
#include <algorithm>
using namespace std;

// ---- reference (matches the required class Solution signature) ----
int countPaths(int n, vector<vector<int>>& roads) {
    vector<vector<pair<int,int>>> adj(n);
    for (auto &road : roads) {
        adj[road[0]].push_back({road[1], road[2]});
        adj[road[1]].push_back({road[0], road[2]});
    }
    const long long MOD = 1e9 + 7;
    priority_queue<pair<long long,long long>, vector<pair<long long,long long>>,
                   greater<pair<long long,long long>>> pq;
    vector<long long> dis(n, (long long)4e18);
    vector<long long> ways(n, 0);
    dis[0] = 0; ways[0] = 1;
    pq.push({0, 0});
    while (!pq.empty()) {
        auto [uwt, u] = pq.top(); pq.pop();
        if (uwt > dis[u]) continue;
        for (auto [v, vwt] : adj[u]) {
            if (dis[v] > uwt + vwt) {
                ways[v] = ways[u];
                dis[v] = uwt + vwt;
                pq.push({dis[v], v});
            } else if (dis[v] == uwt + vwt) {
                ways[v] = (ways[v] + ways[u]) % MOD;
            }
        }
    }
    return (int)(ways[n-1] % MOD);
}

static std::mt19937_64 rng(987654321ULL);
long long randRange(long long lo, long long hi) {
    std::uniform_int_distribution<long long> d(lo, hi);
    return d(rng);
}

string roadsToStr(const vector<vector<int>>& roads) {
    string s = "[";
    for (size_t i = 0; i < roads.size(); ++i) {
        if (i) s += ",";
        s += "[" + to_string(roads[i][0]) + "," + to_string(roads[i][1]) + "," + to_string(roads[i][2]) + "]";
    }
    s += "]";
    return s;
}

// Build a random connected graph on n nodes with m edges, weights in [wlo,whi].
vector<vector<int>> buildGraph(int n, int m, long long wlo, long long whi) {
    set<pair<int,int>> used;
    vector<vector<int>> roads;
    auto edgeKey = [](int a, int b){ return a < b ? make_pair(a,b) : make_pair(b,a); };
    // spanning tree first (guarantees connectivity)
    if (n >= 2) {
        vector<int> perm(n);
        for (int i = 0; i < n; ++i) perm[i] = i;
        shuffle(perm.begin(), perm.end(), rng);
        for (int i = 1; i < n; ++i) {
            int a = perm[i];
            int b = perm[randRange(0, i-1)];
            used.insert(edgeKey(a,b));
            roads.push_back({a, b, (int)randRange(wlo, whi)});
        }
    }
    // add extra edges up to m
    long long maxEdges = (long long)n * (n-1) / 2;
    m = (int)min((long long)m, maxEdges);
    int guard = 0;
    while ((int)roads.size() < m && guard < 50 * m + 1000) {
        guard++;
        int a = (int)randRange(0, n-1);
        int b = (int)randRange(0, n-1);
        if (a == b) continue;
        auto k = edgeKey(a,b);
        if (used.count(k)) continue;
        used.insert(k);
        roads.push_back({a, b, (int)randRange(wlo, whi)});
    }
    shuffle(roads.begin(), roads.end(), rng);
    return roads;
}

int main() {
    const string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-ways-to-arrive-at-destination.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    vector<pair<int,vector<vector<int>>>> cases;

    // ---- explicit edge / example cases ----
    cases.push_back({1, {}});                                 // n=1, no roads (0 reachable trivially -> 1 way)
    cases.push_back({2, {{0,1,1}}});                          // min n with edge
    cases.push_back({2, {{0,1,1000000000}}});                // max weight, min graph
    cases.push_back({7, {{0,6,7},{0,1,2},{1,2,3},{1,3,3},{6,3,3},{3,5,1},{6,5,1},{2,5,1},{0,4,5},{4,6,2}}}); // example 1 -> 4
    cases.push_back({6, {{0,5,8},{0,2,2},{0,1,1},{1,3,3},{1,2,3},{2,5,6},{3,4,2},{4,5,2}}});                 // example 2 -> 3
    cases.push_back({4, {{0,1,10},{1,2,7},{2,3,4},{0,3,3}}}); // nowYourTurn -> 1
    // a graph with all equal weights to force many shortest paths
    {
        vector<vector<int>> r;
        for (int i=0;i<3;i++) for(int j=i+1;j<4;j++) r.push_back({i,j,1});
        cases.push_back({4, r});
    }

    // ---- random cases ----
    int target = 2000;
    while ((int)cases.size() < target) {
        int bucket = (int)randRange(0, 9);
        int n;
        if (bucket == 0) n = (int)randRange(1, 3);          // tiny
        else if (bucket == 1) n = (int)randRange(2, 6);     // small
        else if (bucket <= 4) n = (int)randRange(2, 30);    // medium
        else if (bucket <= 7) n = (int)randRange(2, 80);    // large
        else n = (int)randRange(150, 200);                  // max-ish

        long long maxEdges = (long long)n * (n-1) / 2;
        long long minEdges = (n >= 1) ? (long long)n - 1 : 0;
        int m = (int)randRange(minEdges, maxEdges);

        // weight ranges: mix small (more ties / multiple shortest paths) and large
        long long whi;
        int wb = (int)randRange(0, 3);
        if (wb == 0) whi = randRange(1, 1);                 // all weight 1
        else if (wb == 1) whi = randRange(1, 3);            // small -> many ties
        else if (wb == 2) whi = randRange(1, 100);
        else whi = 1000000000LL;                            // full range
        long long wlo = 1;

        vector<vector<int>> roads = buildGraph(n, m, wlo, whi);
        // n==1 has no roads; roads.length==0 which is fine (n-1==0)
        if (n == 1) roads.clear();
        cases.push_back({n, roads});
    }

    int written = 0;
    for (auto &c : cases) {
        int n = c.first;
        vector<vector<int>> roads = c.second;
        int ans = countPaths(n, roads);
        out << "{\"inputs\": {\"n\": \"" << n << "\", \"roads\": \""
            << roadsToStr(roads) << "\"}, \"expected\": \"" << ans << "\"}\n";
        written++;
    }
    out.close();
    cerr << "wrote " << written << " cases to " << outPath << "\n";
    return 0;
}
