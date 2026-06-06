// Generator + reference for:
//   Shortest path in undirected graph with unit weights
// Signature: vector<int> shortestPath(vector<vector<int>>& edges, int N, int M)
// Source is fixed at vertex 0. Unreachable -> -1.
// Constraints: 1<=n,m<=10^4 ; 0<=edges[i][j]<=n-1
//
// Output jsonl line: {"inputs": {"edges":"[[..],..]","n":"<N>"}, "expected":"d0 d1 ..."}
// (M param dropped because it equals the number of edges; N is keyed as "n".)
//
// Build: clang++ -std=c++17 -O2 -w gen.cpp -o gen && ./gen
#include <vector>
#include <queue>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
using namespace std;

// ---- reference (BFS from src=0) ----
vector<int> shortestPath(vector<vector<int>>& edges, int N, int M){
    int src = 0;
    vector<vector<int>> adj(N);
    for(auto &e: edges){
        adj[e[0]].push_back(e[1]);
        adj[e[1]].push_back(e[0]);
    }
    vector<int> dis(N, -1);
    queue<int> q;
    q.push(src);
    dis[src] = 0;
    while(!q.empty()){
        int node = q.front(); q.pop();
        for(int v: adj[node]){
            if(dis[v] == -1){
                dis[v] = dis[node] + 1;
                q.push(v);
            }
        }
    }
    return dis;
}

static string edgesToStr(const vector<vector<int>>& edges){
    string s = "[";
    for(size_t i=0;i<edges.size();++i){
        if(i) s += ",";
        s += "[" + to_string(edges[i][0]) + "," + to_string(edges[i][1]) + "]";
    }
    s += "]";
    return s;
}

static string distToStr(const vector<int>& d){
    string s;
    for(size_t i=0;i<d.size();++i){
        if(i) s += " ";
        s += to_string(d[i]);
    }
    return s;
}

mt19937 rng(987654321);
int randint(int lo, int hi){ return uniform_int_distribution<int>(lo,hi)(rng); }

int main(){
    const int TOTAL = 2000;
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/shortest-path-in-undirected-graph-with-unit-weights.jsonl");

    auto emit = [&](vector<vector<int>> edges, int N){
        // M = number of edges (>=1 per constraints).
        int M = (int)edges.size();
        vector<int> d = shortestPath(edges, N, M);
        // Keys are EXACTLY the signature param names (edges, N, M) in order.
        // The judge binds case-insensitively, so lowercase n/m is fine.
        out << "{\"inputs\": {\"edges\": \"" << edgesToStr(edges)
            << "\", \"n\": \"" << N
            << "\", \"m\": \"" << M << "\"}, \"expected\": \""
            << distToStr(d) << "\"}\n";
    };

    int count = 0;

    // ---- explicit edge cases ----
    // dataset example 1
    emit({{0,1},{0,3},{3,4},{4,5},{5,6},{1,2},{2,6},{6,7},{7,8},{6,8}}, 9); count++;
    // dataset example 2
    emit({{1,0},{2,1},{0,3},{3,7},{3,4},{7,4},{7,6},{4,5},{4,6},{6,5}}, 8); count++;
    // dataset example 3 (n=3, single edge between 1-2, node0 isolated)
    emit({{1,2}}, 3); count++;
    // n=1, single self... must satisfy m>=1; smallest valid edge is a self loop 0-0
    emit({{0,0}}, 1); count++;
    // n=2, one edge
    emit({{0,1}}, 2); count++;
    // n=2, self loop on 0 (1 unreachable)
    emit({{0,0}}, 2); count++;
    // disconnected: edge not touching component of 0
    emit({{1,2},{3,4}}, 5); count++;
    // duplicate edges + self loop
    emit({{0,1},{0,1},{1,1},{1,2}}, 3); count++;
    // path graph 0-1-2-...-9
    {
        vector<vector<int>> e; for(int i=0;i+1<10;++i) e.push_back({i,i+1});
        emit(e, 10); count++;
    }
    // star centered at 0
    {
        vector<vector<int>> e; for(int i=1;i<8;++i) e.push_back({0,i});
        emit(e, 8); count++;
    }
    // all edges among far nodes, 0 isolated
    {
        vector<vector<int>> e; for(int i=1;i<6;++i) for(int j=i+1;j<6;++j) e.push_back({i,j});
        emit(e, 6); count++;
    }

    // ---- random cases ----
    while(count < TOTAL){
        // pick N within [1,10^4]; bias toward small but include large
        int N;
        int r = randint(0,99);
        if(r < 40) N = randint(1, 12);
        else if(r < 70) N = randint(1, 100);
        else if(r < 90) N = randint(1, 2000);
        else N = randint(1, 10000);

        // pick M within [1, 10^4]
        int M;
        int rm = randint(0,99);
        if(rm < 50) M = randint(1, max(1, min(N*2, 30)));
        else if(rm < 85) M = randint(1, min(10000, max(1, N*3)));
        else M = randint(1, 10000);

        vector<vector<int>> edges;
        edges.reserve(M);
        for(int i=0;i<M;++i){
            int a = randint(0, N-1);
            int b = randint(0, N-1);
            edges.push_back({a,b});
        }
        emit(edges, N);
        count++;
    }

    out.close();
    cerr << "wrote " << count << " cases\n";
    return 0;
}
