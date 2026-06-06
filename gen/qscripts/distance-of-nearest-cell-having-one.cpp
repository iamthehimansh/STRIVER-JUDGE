// Generator + reference for "Distance of nearest cell having one"
// Problem: given N x M binary grid (1<=N,M<=500, at least one 1),
// for each cell output Manhattan distance to nearest 1.
// Reference: multi-source BFS starting from all cells == 1.
//
// Emits /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/distance-of-nearest-cell-having-one.jsonl
// One JSON line per case: {"inputs":{"grid":"[[..],[..]]"},"expected":"<flattened ints>"}
//
// Compile: clang++ -std=c++17 -O2 -w gen.cpp -o gen
#include <vector>
#include <queue>
#include <string>
#include <random>
#include <fstream>
#include <iostream>
using namespace std;

// ---- Reference oracle: distance to nearest cell having value 1 ----
vector<vector<int>> nearest(const vector<vector<int>>& grid){
    int n = grid.size();
    int m = grid[0].size();
    vector<vector<int>> dist(n, vector<int>(m, -1));
    queue<pair<int,int>> q;
    for(int i=0;i<n;i++)
        for(int j=0;j<m;j++)
            if(grid[i][j]==1){ dist[i][j]=0; q.push({i,j}); }
    int dr[4]={-1,1,0,0};
    int dc[4]={0,0,-1,1};
    while(!q.empty()){
        auto [x,y]=q.front(); q.pop();
        for(int k=0;k<4;k++){
            int nx=x+dr[k], ny=y+dc[k];
            if(nx>=0&&nx<n&&ny>=0&&ny<m&&dist[nx][ny]==-1){
                dist[nx][ny]=dist[x][y]+1;
                q.push({nx,ny});
            }
        }
    }
    return dist;
}

string gridToStr(const vector<vector<int>>& g){
    string s="[";
    for(size_t i=0;i<g.size();i++){
        if(i) s+=", ";
        s+="[";
        for(size_t j=0;j<g[i].size();j++){
            if(j) s+=", ";
            s+=to_string(g[i][j]);
        }
        s+="]";
    }
    s+="]";
    return s;
}

// expected: flatten matrix to space-separated ints on one line
string expectedToStr(const vector<vector<int>>& g){
    string s;
    bool first=true;
    for(const auto& row:g)
        for(int v:row){
            if(!first) s+=" ";
            s+=to_string(v);
            first=false;
        }
    return s;
}

mt19937 rng(987654321u);
int randint(int lo,int hi){ return uniform_int_distribution<int>(lo,hi)(rng); }

// Generate a valid grid: at least one 1 guaranteed.
vector<vector<int>> genGrid(int n,int m,int onesPercent){
    vector<vector<int>> g(n, vector<int>(m,0));
    for(int i=0;i<n;i++)
        for(int j=0;j<m;j++)
            g[i][j] = (randint(1,100)<=onesPercent)?1:0;
    // ensure at least one 1
    bool hasOne=false;
    for(auto&r:g) for(int v:r) if(v==1){hasOne=true;break;}
    if(!hasOne){
        g[randint(0,n-1)][randint(0,m-1)]=1;
    }
    return g;
}

int main(){
    const string outPath="/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/distance-of-nearest-cell-having-one.jsonl";
    ofstream out(outPath);
    if(!out){ cerr<<"cannot open "<<outPath<<"\n"; return 1; }

    int total=2000;
    int count=0;

    auto emit=[&](const vector<vector<int>>& g){
        if(count>=total) return;
        auto exp=nearest(g);
        out<<"{\"inputs\": {\"grid\": \""<<gridToStr(g)
           <<"\"}, \"expected\": \""<<expectedToStr(exp)<<"\"}\n";
        count++;
    };

    // ---- Edge / fixed cases ----
    // 1x1 with single 1
    emit({{1}});
    // 1x1 -> but must have at least one 1, so {{1}} only valid for 1x1; cover.
    // example cases from statement
    emit({{0,1,1,0},{1,1,0,0},{0,0,1,1}});
    emit({{1,0,1},{1,1,0},{1,0,0}});
    emit({{0,1},{1,0}});
    // single row various
    emit({{0,0,0,0,1}});
    emit({{1,0,0,0,0}});
    emit({{0,0,1,0,0}});
    // single column
    emit({{0},{0},{1},{0}});
    // all ones small
    emit({{1,1},{1,1}});
    // sparse: one 1 in a large-ish corner
    {
        int n=500,m=500;
        vector<vector<int>> g(n, vector<int>(m,0));
        g[0][0]=1;
        emit(g);
    }
    // one 1 in center of 500x500
    {
        int n=500,m=500;
        vector<vector<int>> g(n, vector<int>(m,0));
        g[250][250]=1;
        emit(g);
    }
    // full 1x500 with single 1 at end
    {
        vector<vector<int>> g(1, vector<int>(500,0));
        g[0][499]=1;
        emit(g);
    }
    // 500x1 single 1
    {
        vector<vector<int>> g(500, vector<int>(1,0));
        g[0][0]=1;
        emit(g);
    }

    // ---- Random small cases (dense coverage) ----
    while(count<700){
        int n=randint(1,8);
        int m=randint(1,8);
        int p=randint(5,90);
        emit(genGrid(n,m,p));
    }
    // ---- Random medium cases ----
    while(count<1400){
        int n=randint(1,60);
        int m=randint(1,60);
        int p=randint(2,80);
        emit(genGrid(n,m,p));
    }
    // ---- Random larger cases (kept modest in width to keep file size sane) ----
    while(count<1900){
        int n=randint(1,120);
        int m=randint(1,40);
        int p=randint(1,50);
        emit(genGrid(n,m,p));
    }
    // ---- A few big-ish but capped to control file size ----
    while(count<total){
        int n=randint(100,250);
        int m=randint(1,15);
        int p=randint(1,30);
        emit(genGrid(n,m,p));
    }

    out.close();
    cerr<<"wrote "<<count<<" cases\n";
    return 0;
}
