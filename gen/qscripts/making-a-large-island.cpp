// Generator for "making-a-large-island"
// Generates random n x n binary grids (1 <= n <= 500) and computes the
// reference answer for largestIsland. Writes 2000 JSONL lines:
//   {"inputs": {"grid": "[[...],[...]]"}, "expected": "<int>"}
//
// Compile (macOS clang lacks <bits/stdc++.h>):
//   clang++ -std=c++17 -O2 -w -o /tmp/mli/gen \
//     "/Users/iamthehimansh/Downloads/stiver'sdata/gen/qscripts/making-a-large-island.cpp"
// Run:
//   /tmp/mli/gen > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/making-a-large-island.jsonl"

#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <random>
#include <climits>
#include <unordered_set>
#include <algorithm>
using namespace std;

// ----- Reference solution (ground-truth oracle) -----
struct DSU {
    vector<int> parent, sz;
    DSU(int n) { parent.resize(n); sz.assign(n, 1); for (int i=0;i<n;i++) parent[i]=i; }
    int find(int x){ return parent[x]==x ? x : parent[x]=find(parent[x]); }
    void uni(int u,int v){ int a=find(u),b=find(v); if(a==b) return; if(sz[a]>sz[b]){parent[b]=a;sz[a]+=sz[b];} else {parent[a]=b;sz[b]+=sz[a];} }
};

static bool isLand(int i,int j,const vector<vector<int>>& g){
    int n=g.size();
    return (i>=0 && i<n && j>=0 && j<n && g[i][j]==1);
}

int largestIsland(vector<vector<int>>& grid){
    int n=grid.size();
    int dr[4]={1,-1,0,0}, dc[4]={0,0,1,-1};
    DSU djs(n*n);
    for(int i=0;i<n;i++) for(int j=0;j<n;j++){
        if(grid[i][j]==1){
            int id=i*n+j;
            for(int d=0;d<4;d++){
                int ni=i+dr[d], nj=j+dc[d];
                if(isLand(ni,nj,grid)){ int nid=ni*n+nj; if(djs.find(id)!=djs.find(nid)) djs.uni(id,nid); }
            }
        }
    }
    long long ans=LLONG_MIN;
    for(int i=0;i<n;i++) for(int j=0;j<n;j++){
        if(grid[i][j]==0){
            unordered_set<int> st;
            for(int d=0;d<4;d++){
                int ni=i+dr[d], nj=j+dc[d];
                if(isLand(ni,nj,grid)){ int nid=ni*n+nj; st.insert(djs.find(nid)); }
            }
            int siz=0; for(int u:st) siz+=djs.sz[u];
            ans=max(ans,(long long)siz+1);
        }
    }
    for(int c=0;c<n*n;c++) ans=max(ans,(long long)djs.sz[djs.find(c)]);
    return (int)ans;
}

// ----- Serialization -----
string gridToStr(const vector<vector<int>>& g){
    string s="[";
    for(size_t i=0;i<g.size();i++){
        if(i) s+=", ";
        s+="[";
        for(size_t j=0;j<g[i].size();j++){ if(j) s+=", "; s+=to_string(g[i][j]); }
        s+="]";
    }
    s+="]";
    return s;
}

int main(){
    std::mt19937 rng(987654321u);
    const int TOTAL=2000;
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/making-a-large-island.jsonl");

    auto emit=[&](vector<vector<int>> grid){
        int exp=largestIsland(grid);
        out << "{\"inputs\": {\"grid\": \"" << gridToStr(grid)
            << "\"}, \"expected\": \"" << exp << "\"}\n";
    };

    int count=0;

    // ---- Hand-crafted edge cases first ----
    vector<vector<vector<int>>> edges = {
        {{0}},                       // n=1, all 0 -> 1
        {{1}},                       // n=1, all 1 -> 1
        {{1,0},{0,1}},               // example 1 -> 3
        {{1,1},{1,1}},               // example 2 -> 4
        {{1,1},{1,0}},               // nowYourTurn -> 4
        {{0,0},{0,0}},               // 2x2 all 0 -> 1
        {{1,0,1},{0,0,0},{1,0,1}},   // checkerboard-ish corners
        {{1,1,1},{1,1,1},{1,1,1}},   // all 1 -> 9
        {{0,0,0},{0,0,0},{0,0,0}},   // all 0 -> 1
    };
    for(auto& g : edges){ emit(g); count++; }

    // helper to make an n x n grid with given probability of 1
    auto randGrid=[&](int n, double p)->vector<vector<int>>{
        std::bernoulli_distribution b(p);
        vector<vector<int>> g(n, vector<int>(n,0));
        for(int i=0;i<n;i++) for(int j=0;j<n;j++) g[i][j]= b(rng)?1:0;
        return g;
    };

    // ---- Small grids (n from 1..8) with varied densities ----
    while(count < 800){
        int n = 1 + (rng()%8);            // 1..8
        double p = (rng()%100)/100.0;     // 0.00 .. 0.99
        emit(randGrid(n,p));
        count++;
    }

    // ---- Medium grids (n 9..40) ----
    while(count < 1500){
        int n = 9 + (rng()%32);           // 9..40
        double p;
        int r = rng()%5;
        if(r==0) p=0.0;                   // all zero
        else if(r==1) p=1.0;              // all one
        else p=0.2 + (rng()%60)/100.0;    // 0.2..0.79
        emit(randGrid(n,p));
        count++;
    }

    // ---- Large grids near the upper bound (n 41..500) ----
    // Keep these less frequent (heavier compute) but include extremes.
    {
        // explicit large extremes
        emit(randGrid(500, 0.0));  count++;  // 500x500 all 0 -> 1
        emit(randGrid(500, 1.0));  count++;  // 500x500 all 1 -> 250000
        emit(randGrid(500, 0.5));  count++;
        emit(randGrid(500, 0.6));  count++;
        emit(randGrid(500, 0.7));  count++;
    }
    while(count < TOTAL){
        int n = 41 + (rng()%200);          // 41..240 (keep file/compute modest)
        double p;
        int r = rng()%4;
        if(r==0) p=0.0;
        else if(r==1) p=1.0;
        else p=0.3 + (rng()%50)/100.0;     // 0.3..0.79
        emit(randGrid(n,p));
        count++;
    }

    out.close();
    cerr << "Wrote " << count << " cases.\n";
    return 0;
}
