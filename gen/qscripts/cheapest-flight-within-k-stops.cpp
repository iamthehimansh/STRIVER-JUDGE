// Generator + reference oracle for "Cheapest flight within K stops"
// Writes 2000 JSONL cases to generated-tests/cheapest-flight-within-k-stops.jsonl
// Each line: {"inputs":{"n":"..","flights":"[[..]]","src":"..","dst":"..","K":".."},"expected":".."}
//
// Build:  clang++ -std=c++17 -O2 -w cheapest-flight-within-k-stops.cpp -o gen
// Run:    ./gen > out.jsonl
#include <bits/stdc++.h>
using namespace std;

// Reference oracle (BFS, at most k stops) — same logic as strivers reference.
int CheapestFlight(int n, vector<vector<int>> &flights, int src, int dst, int K) {
    vector<vector<pair<int,int>>> adj(n);
    for (auto &f : flights) adj[f[0]].push_back({f[1], f[2]});
    queue<pair<int,int>> q;
    q.push({src, 0});
    vector<int> dis(n, 1e9);
    dis[src] = 0;
    int stops = 0;
    while (!q.empty() && stops <= K) {
        int sz = q.size();
        while (sz--) {
            auto [u, uwt] = q.front(); q.pop();
            for (auto &pr : adj[u]) {
                int v = pr.first, vwt = pr.second;
                if (vwt + uwt < dis[v]) {
                    dis[v] = uwt + vwt;
                    q.push({v, dis[v]});
                }
            }
        }
        stops++;
    }
    if (dis[dst] == (int)1e9) return -1;
    return dis[dst];
}

mt19937 rng(123456789u);
int ri(int lo, int hi){ return lo + (int)(rng() % (unsigned)(hi - lo + 1)); }

string flightsToStr(const vector<vector<int>>& f){
    string s = "[";
    for (size_t i=0;i<f.size();++i){
        s += "[" + to_string(f[i][0]) + "," + to_string(f[i][1]) + "," + to_string(f[i][2]) + "]";
        if (i+1<f.size()) s += ",";
    }
    s += "]";
    return s;
}

// Generate one random valid instance.
void genCase(int n, vector<vector<int>>& flights, int& src, int& dst, int& K){
    // n given. Build set of valid directed edges (no self-loop, no duplicate directed pair).
    int maxEdges = n*(n-1)/2; // constraint: flights.length <= n*(n-1)/2
    // collect candidate ordered pairs (u != v)
    vector<pair<int,int>> cand;
    for (int u=0;u<n;++u) for (int v=0;v<n;++v) if (u!=v) cand.push_back({u,v});
    shuffle(cand.begin(), cand.end(), rng);
    int wantEdges = (maxEdges==0)?0:ri(0, maxEdges);
    // "no multiple flights between two cities" -> avoid both (u,v) and (v,u)? The constraint says
    // no multiple flights between the two cities; we ensure no duplicate of the SAME directed pair,
    // and to be safe treat undirected uniqueness so at most one edge per unordered pair.
    set<pair<int,int>> usedUnordered;
    flights.clear();
    for (auto &p : cand){
        if ((int)flights.size() >= wantEdges) break;
        int a = min(p.first,p.second), b = max(p.first,p.second);
        if (usedUnordered.count({a,b})) continue;
        usedUnordered.insert({a,b});
        flights.push_back({p.first, p.second, ri(1,10000)});
    }
    src = ri(0,n-1);
    dst = ri(0,n-1);
    K = ri(0,n-1);
}

int main(){
    vector<string> lines;
    auto emit = [&](int n, vector<vector<int>>& flights, int src, int dst, int K){
        int ans = CheapestFlight(n, flights, src, dst, K);
        string line = "{\"inputs\":{\"n\":\"" + to_string(n) + "\",\"flights\":\""
            + flightsToStr(flights) + "\",\"src\":\"" + to_string(src)
            + "\",\"dst\":\"" + to_string(dst) + "\",\"K\":\"" + to_string(K)
            + "\"},\"expected\":\"" + to_string(ans) + "\"}";
        lines.push_back(line);
    };

    // ---- Edge / fixed cases ----
    // Example 1
    { vector<vector<int>> f={{0,1,100},{1,2,100},{2,0,100},{1,3,600},{2,3,200}}; emit(4,f,0,3,1); }
    // Example 2
    { vector<vector<int>> f={{0,1,100},{1,2,100},{0,2,500}}; emit(3,f,0,2,1); }
    // Example 3 (k=0, no direct -> -1)
    { vector<vector<int>> f={{0,1,100},{1,2,100},{0,2,500}}; emit(3,f,0,2,0); }
    // n=1, no flights, src==dst -> 0
    { vector<vector<int>> f={}; emit(1,f,0,0,0); }
    // n=2, no flights -> -1
    { vector<vector<int>> f={}; emit(2,f,0,1,0); }
    // n=2 direct
    { vector<vector<int>> f={{0,1,5}}; emit(2,f,0,1,0); }
    // src==dst with flights -> 0
    { vector<vector<int>> f={{0,1,100},{1,2,100}}; emit(3,f,2,2,1); }
    // unreachable dst
    { vector<vector<int>> f={{0,1,100}}; emit(3,f,0,2,2); }
    // max price edges
    { vector<vector<int>> f={{0,1,10000},{1,2,10000}}; emit(3,f,0,2,1); }

    // ---- Random small n (1..5) heavy coverage ----
    for (int t=0;t<800;++t){
        int n = ri(1,5);
        vector<vector<int>> f; int s,d,K;
        genCase(n,f,s,d,K);
        emit(n,f,s,d,K);
    }
    // ---- Random medium n (6..30) ----
    for (int t=0;t<700;++t){
        int n = ri(6,30);
        vector<vector<int>> f; int s,d,K;
        genCase(n,f,s,d,K);
        emit(n,f,s,d,K);
    }
    // ---- Random large n (31..100) ----
    while ((int)lines.size() < 2000){
        int n = ri(31,100);
        vector<vector<int>> f; int s,d,K;
        genCase(n,f,s,d,K);
        emit(n,f,s,d,K);
    }

    // exactly 2000
    if ((int)lines.size() > 2000) lines.resize(2000);
    for (auto &l : lines) printf("%s\n", l.c_str());
    return 0;
}
