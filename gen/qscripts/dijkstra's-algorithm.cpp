// Generator for "Djisktra's Algorithm" (slug: dijkstra's-algorithm)
// Method signature: vector<int> dijkstra(int V, vector<vector<int>> edges, int S)
// Graph is WEIGHTED, UNDIRECTED. Edges: [u, v, weight].
// Constraints:
//   1 <= V <= 10000
//   0 <= edges[i][j] <= 10000   (weights non-negative)
//   1 <= edges.size() <= V*(V-1)/2   (=> V >= 2 for a valid edge to exist)
//   0 <= S < V
// Unreachable node distance = 10^9.
//
// NOTE on V cap: the submit-mode judge truncates per-case stdout (~115 bytes).
// An unreachable distance prints as 1000000000 (10 chars). To never truncate a
// correct submission we keep the worst-case output line small; cap V at 9
// (9 numbers, up to 10 chars + 8 spaces = 98 bytes <= 115).
#include <iostream>
#include <vector>
#include <random>
#include <set>
#include <queue>
#include <fstream>
#include <string>
#include <algorithm>
using namespace std;

const long long UNREACH = 1000000000LL; // 10^9

// Reference Dijkstra on undirected graph with non-negative weights.
vector<long long> dijkstra(int V, vector<vector<int>>& edges, int S) {
    vector<vector<pair<int,int>>> adj(V);
    for (auto &e : edges) {
        int u = e[0], v = e[1], w = e[2];
        adj[u].push_back({v, w});
        adj[v].push_back({u, w});
    }
    vector<long long> dis(V, UNREACH);
    priority_queue<pair<long long,int>, vector<pair<long long,int>>, greater<>> pq;
    dis[S] = 0;
    pq.push({0, S});
    while (!pq.empty()) {
        auto [d, node] = pq.top();
        pq.pop();
        if (d > dis[node]) continue;
        for (auto &[nb, w] : adj[node]) {
            if (d + w < dis[nb]) {
                dis[nb] = d + w;
                pq.push({dis[nb], nb});
            }
        }
    }
    return dis;
}

mt19937 rng(987654321u);
int randint(int lo, int hi){ return uniform_int_distribution<int>(lo,hi)(rng); }

string fmtEdges(vector<vector<int>>& edges){
    string s = "[";
    for (size_t i=0;i<edges.size();i++){
        s += "[" + to_string(edges[i][0]) + "," + to_string(edges[i][1]) + "," + to_string(edges[i][2]) + "]";
        if (i+1<edges.size()) s += ",";
    }
    s += "]";
    return s;
}

string fmtExpected(vector<long long>& d){
    string s;
    for (size_t i=0;i<d.size();i++){
        if(i) s += " ";
        s += to_string(d[i]);
    }
    return s;
}

string jsonEscape(const string& in){
    string o;
    for(char c: in){
        if(c=='"'||c=='\\') { o+='\\'; o+=c; }
        else o+=c;
    }
    return o;
}

int main(int argc, char** argv){
    int N = 2000;
    if (argc > 1) N = atoi(argv[1]);
    string outpath = (argc > 2) ? argv[2]
        : "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/dijkstra's-algorithm.jsonl";
    ofstream out(outpath);

    int produced = 0;
    auto emit = [&](int V, vector<vector<int>> edges, int S){
        vector<long long> exp = dijkstra(V, edges, S);
        string line = "{\"inputs\": {\"V\": \"" + to_string(V) + "\", \"edges\": \"" +
            jsonEscape(fmtEdges(edges)) + "\", \"S\": \"" + to_string(S) + "\"}, \"expected\": \"" +
            jsonEscape(fmtExpected(exp)) + "\"}";
        out << line << "\n";
        produced++;
    };

    // ---- Fixed / edge cases ----
    emit(2, {{0,1,9}}, 0);                                   // Example 1 -> 0 9
    emit(3, {{0,1,1},{0,2,6},{1,2,3}}, 2);                   // Example 2 -> 4 3 0
    emit(4, {{0,1,1},{0,3,2},{1,2,4},{2,3,3}}, 0);           // nowYourTurn -> 0 1 5 2
    emit(2, {{0,1,0}}, 0);                                   // weight 0 (min weight)
    emit(2, {{0,1,10000}}, 1);                               // max weight, source on node 1
    emit(3, {{0,1,5}}, 0);                                   // node 2 unreachable -> 10^9
    emit(3, {{0,1,5}}, 2);                                   // source isolated-ish, nodes 0,1 unreachable
    emit(5, {{0,1,4},{0,2,1},{2,1,2},{1,3,1},{3,4,3}}, 0);   // classic dijkstra path
    emit(4, {{0,1,1},{1,2,1},{2,3,1},{3,0,1}}, 0);           // cycle/ring
    emit(2, {{0,1,7}}, 0);                                   // V=2 min

    // ---- Random cases ----
    set<long long> usedEdge; // dedupe undirected pairs within a graph
    while (produced < N) {
        usedEdge.clear();
        int V = randint(2, 9);                  // cap for judge stdout safety
        long long maxE = (long long)V * (V - 1) / 2; // undirected simple graph
        int S = randint(0, V - 1);
        vector<vector<int>> edges;

        // 1 <= E <= maxE
        int E = randint(1, (int)maxE);

        // mode: control connectivity flavor
        //  0: fully random edges (may leave nodes unreachable -> 10^9)
        //  1: build a random spanning tree first (guarantees connected), then add extra
        int mode = randint(0, 1);

        if (mode == 1 && V >= 2) {
            // random spanning tree to guarantee connectivity
            vector<int> perm(V);
            for (int i=0;i<V;i++) perm[i]=i;
            shuffle(perm.begin(), perm.end(), rng);
            for (int i=1;i<V && (int)edges.size()<E;i++){
                int a = perm[i];
                int b = perm[randint(0,i-1)];
                int u = min(a,b), v = max(a,b);
                long long key = (long long)u * 100000 + v;
                if (usedEdge.count(key)) continue;
                usedEdge.insert(key);
                edges.push_back({u, v, randint(0,10000)});
            }
        }

        int attempts = 0;
        while ((int)edges.size() < E && attempts < E*40 + 50) {
            attempts++;
            int a = randint(0, V-1);
            int b = randint(0, V-1);
            if (a == b) continue;                       // no self loops
            int u = min(a,b), v = max(a,b);
            long long key = (long long)u * 100000 + v;  // undirected pair, no parallel edges
            if (usedEdge.count(key)) continue;
            usedEdge.insert(key);
            edges.push_back({u, v, randint(0,10000)});
        }
        if (edges.empty()) {
            edges.push_back({0, 1, randint(0,10000)});
        }
        emit(V, edges, S);
    }

    out.close();
    cerr << "produced " << produced << " cases\n";
    return 0;
}
