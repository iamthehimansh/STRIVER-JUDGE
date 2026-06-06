// Generator for "network-delay-time".
// Produces 2000 random valid cases within constraints, computes expected via
// the reference Dijkstra solution, and writes JSONL to the generated-tests dir.
//
// Constraints:
//   1 <= k <= n <= 100
//   1 <= times.length <= 6000
//   1 <= ui, vi <= n, ui != vi
//   0 <= wi <= 100
//   Every ordered pair (ui,vi) appears at most once (no parallel edges).
//
// Output line format:
//   {"inputs": {"times": "[[...]]", "n": "N", "k": "K"}, "expected": "VAL"}
//
// Compile: clang++ -std=c++17 -O2 -w network-delay-time.cpp -o gen
// Run:     ./gen > /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/network-delay-time.jsonl

#include <vector>
#include <queue>
#include <random>
#include <algorithm>
#include <set>
#include <climits>
#include <cstdio>
#include <string>
#include <utility>
using namespace std;

// Reference (ground-truth oracle), identical logic to starterCpp signature.
int networkDelayTime(vector<vector<int>>& times, int n, int k) {
    vector<vector<pair<int,int>>> adj(n + 1);
    for (auto &t : times) adj[t[0]].push_back({t[1], t[2]});
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    vector<long long> dis(n + 1, (long long)1e18);
    dis[k] = 0;
    pq.push({0, k});
    while (!pq.empty()) {
        auto [uwt, u] = pq.top(); pq.pop();
        if (uwt > dis[u]) continue;
        for (auto [v, vwt] : adj[u]) {
            if (dis[v] > (long long)uwt + vwt) {
                dis[v] = (long long)uwt + vwt;
                pq.push({(int)dis[v], v});
            }
        }
    }
    long long ans = LLONG_MIN;
    for (int i = 1; i <= n; i++) {
        if (dis[i] >= (long long)1e18) return -1;
        ans = max(ans, dis[i]);
    }
    return (int)ans;
}

static string timesToStr(const vector<vector<int>>& times) {
    string s = "[";
    for (size_t i = 0; i < times.size(); i++) {
        if (i) s += ",";
        s += "[" + to_string(times[i][0]) + "," + to_string(times[i][1]) + "," + to_string(times[i][2]) + "]";
    }
    s += "]";
    return s;
}

int main() {
    std::mt19937 rng(123456789u);

    auto emit = [&](vector<vector<int>>& times, int n, int k) {
        int exp = networkDelayTime(times, n, k);
        printf("{\"inputs\": {\"times\": \"%s\", \"n\": \"%d\", \"k\": \"%d\"}, \"expected\": \"%d\"}\n",
               timesToStr(times).c_str(), n, k, exp);
    };

    int produced = 0;
    const int TARGET = 2000;

    // ----- Hand-crafted edge cases first -----
    {
        // Example 1
        vector<vector<int>> t = {{2,1,1},{2,3,1},{3,4,1}};
        emit(t, 4, 2); produced++;
        // Example 2
        vector<vector<int>> t2 = {{1,2,1}};
        emit(t2, 2, 1); produced++;
        // Example 3 (unreachable -> -1)
        vector<vector<int>> t3 = {{1,2,1},{1,3,4},{2,3,1},{3,4,1},{2,4,7}};
        emit(t3, 4, 1); produced++;
        // n=1: single node, no edges needed, but times.length>=1 required.
        // Use a self-irrelevant edge? ui!=vi so with n=1 we cannot make any edge.
        // times.length>=1 must hold, so n=1 is infeasible per constraints. Skip n=1.
        // Smallest: n=2, k=2, edge 2->1 weight 0
        vector<vector<int>> t4 = {{2,1,0}};
        emit(t4, 2, 2); produced++;
        // n=2, k=1, edge 1->2 weight 100 (max weight)
        vector<vector<int>> t5 = {{1,2,100}};
        emit(t5, 2, 1); produced++;
        // n=2, k=1, only edge 2->1 -> node2 unreachable from 1 -> -1
        vector<vector<int>> t6 = {{2,1,5}};
        emit(t6, 2, 1); produced++;
        // weight 0 chain
        vector<vector<int>> t7 = {{1,2,0},{2,3,0},{3,4,0},{4,5,0}};
        emit(t7, 5, 1); produced++;
        // complete-ish small graph
        vector<vector<int>> t8 = {{1,2,3},{1,3,1},{2,3,1},{3,2,1},{2,1,4},{3,1,2}};
        emit(t8, 3, 1); produced++;
    }

    // ----- Randomized cases -----
    while (produced < TARGET) {
        // pick n in [2,100]
        std::uniform_int_distribution<int> nDist(2, 100);
        int n = nDist(rng);
        std::uniform_int_distribution<int> kDist(1, n);
        int k = kDist(rng);

        // max possible distinct ordered pairs (ui!=vi) = n*(n-1)
        long long maxEdges = (long long)n * (n - 1);
        // choose number of edges in [1, min(maxEdges, 6000)]
        long long capE = maxEdges < 6000 ? maxEdges : 6000;
        std::uniform_int_distribution<long long> eDist(1, capE);
        long long m = eDist(rng);

        vector<vector<int>> times;
        times.reserve(m);
        std::uniform_int_distribution<int> wDist(0, 100);

        if (m * 4 >= maxEdges) {
            // dense: enumerate all ordered pairs, shuffle, take first m
            vector<pair<int,int>> pairs;
            pairs.reserve(maxEdges);
            for (int u = 1; u <= n; u++)
                for (int v = 1; v <= n; v++)
                    if (u != v) pairs.push_back({u, v});
            std::shuffle(pairs.begin(), pairs.end(), rng);
            for (long long i = 0; i < m; i++)
                times.push_back({pairs[i].first, pairs[i].second, wDist(rng)});
        } else {
            // sparse: sample distinct pairs via a set
            std::set<pair<int,int>> used;
            std::uniform_int_distribution<int> nodeDist(1, n);
            while ((long long)times.size() < m) {
                int u = nodeDist(rng), v = nodeDist(rng);
                if (u == v) continue;
                if (used.count({u, v})) continue;
                used.insert({u, v});
                times.push_back({u, v, wDist(rng)});
            }
        }

        emit(times, n, k);
        produced++;
    }

    return 0;
}
