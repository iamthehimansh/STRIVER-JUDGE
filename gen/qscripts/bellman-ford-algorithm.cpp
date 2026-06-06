#include <iostream>
#include <vector>
#include <random>
#include <set>
#include <fstream>
#include <sstream>
#include <algorithm>
using namespace std;

const long long UNREACH = 1000000000LL; // 10^9 per problem statement

// Reference Bellman-Ford. Returns distances (UNREACH for unreachable),
// or {-1} if a negative cycle affecting reachable nodes exists.
vector<long long> bellman_ford(int V, vector<vector<int>>& edges, int S) {
    vector<long long> dis(V, UNREACH);
    dis[S] = 0;
    for (int i = 0; i < V - 1; i++) {
        bool changed = false;
        for (auto &e : edges) {
            int u = e[0], v = e[1]; long long w = e[2];
            if (dis[u] != UNREACH && dis[u] + w < dis[v]) {
                dis[v] = dis[u] + w;
                changed = true;
            }
        }
        if (!changed) break;
    }
    // detect negative cycle (reachable)
    for (auto &e : edges) {
        int u = e[0], v = e[1]; long long w = e[2];
        if (dis[u] != UNREACH && dis[u] + w < dis[v]) {
            return vector<long long>{-1};
        }
    }
    return dis;
}

mt19937 rng(12345);
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
    string outpath = argv[2];
    ofstream out(outpath);

    // Build deterministic list of edge cases first, then random.
    vector<int> cases_done(0);
    int produced = 0;

    auto emit = [&](int V, vector<vector<int>> edges, int S){
        vector<long long> exp = bellman_ford(V, edges, S);
        string line = "{\"inputs\": {\"V\": \"" + to_string(V) + "\", \"Edges\": \"" +
            jsonEscape(fmtEdges(edges)) + "\", \"S\": \"" + to_string(S) + "\"}, \"expected\": \"" +
            jsonEscape(fmtExpected(exp)) + "\"}";
        out << line << "\n";
        produced++;
    };

    // ---- Fixed edge cases ----
    // Example 1
    {
        vector<vector<int>> e = {{3,2,6},{5,3,1},{0,1,5},{1,5,-3},{1,2,-2},{3,4,-2},{2,4,3}};
        emit(6, e, 0);
    }
    // Example 2
    {
        vector<vector<int>> e = {{0,1,9}};
        emit(2, e, 0);
    }
    // V=2 minimum valid graph (E range is [1, V*(V-1)] = [1,2])
    {
        vector<vector<int>> e = {{0,1,7}};
        emit(2, e, 0);
    }
    // V=2 two edges, both directions, source on far node
    {
        vector<vector<int>> e = {{0,1,3},{1,0,4}};
        emit(2, e, 1);
    }
    // Negative cycle case (from problem "now your turn": 2->0->1->...? Actually that one has neg cycle)
    {
        vector<vector<int>> e = {{0,1,5},{1,0,3},{1,2,-1},{2,0,1}};
        emit(3, e, 2);
    }
    // unreachable node: V=3, only edge 0->1, S=0 ; node 2 unreachable -> 10^9
    {
        vector<vector<int>> e = {{0,1,4}};
        emit(3, e, 0);
    }
    // all max weights
    {
        vector<vector<int>> e = {{0,1,1000},{1,2,1000}};
        emit(3, e, 0);
    }
    // negative weights chain (no cycle since directed forward)
    {
        vector<vector<int>> e = {{0,1,-1000},{1,2,-1000},{2,3,-1000}};
        emit(4, e, 0);
    }

    // ---- Random cases ----
    set<long long> usedEdge; // to dedupe directed edges within a graph
    while (produced < N) {
        usedEdge.clear();
        // Constraint: 1 <= E <= V*(V-1). For V=1 this range is empty, so use V>=2.
        // NOTE: the submit-mode judge truncates per-case stdout at ~115 bytes. Since an
        // unreachable distance prints as 1000000000 (10 chars), V must stay small enough
        // that the worst-case output line (all 10-char numbers) fits. Cap V at 9
        // (9 * 11 = 99 bytes worst case <= 115) so a correct submission is never truncated.
        int V = randint(2, 9);
        // max edges = V*(V-1) for simple directed graph (no self loops, no parallel).
        long long maxE = (long long)V * (V - 1);
        int S = randint(0, V - 1);
        vector<vector<int>> edges;

        int E = randint(1, (int)min(maxE, (long long)400));
        // Choose graph "mode" to balance the dataset:
        //  0: DAG (edges only forward in a random permutation) -> never has a cycle,
        //     weights in [-1000,1000] -> valid finite shortest paths.
        //  1: all-nonnegative weights -> never negative cycle.
        //  2: fully random weights (often produces negative cycles -> expected "-1").
        int mode = randint(0, 2);
        // random permutation order for DAG mode
        vector<int> perm(V);
        for (int i=0;i<V;i++) perm[i]=i;
        shuffle(perm.begin(), perm.end(), rng);
        vector<int> pos(V);
        for (int i=0;i<V;i++) pos[perm[i]]=i;

        int attempts = 0;
        while ((int)edges.size() < E && attempts < E*30) {
            attempts++;
            int a = randint(0, V-1);
            int b = randint(0, V-1);
            if (a == b) continue; // no self loops
            if (mode == 0 && pos[a] >= pos[b]) continue; // enforce DAG by topo order
            long long key = (long long)a * 1000 + b;
            if (usedEdge.count(key)) continue;
            usedEdge.insert(key);
            int w;
            if (mode == 1) w = randint(0, 1000);
            else w = randint(-1000, 1000);
            edges.push_back({a,b,w});
        }
        if (edges.empty()) {
            // fallback ensure at least 1 edge
            int a = 0, b = (V>1?1:0);
            edges.push_back({a,b,randint(-1000,1000)});
        }
        emit(V, edges, S);
    }

    out.close();
    cerr << "produced " << produced << " cases\n";
    return 0;
}
