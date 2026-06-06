#include <vector>
#include <string>
#include <iostream>
#include <fstream>
#include <random>
#include <cstdint>
using namespace std;

// ---- Reference (matches starterCpp signature) ----
struct Solution {
    int maxi(vector<vector<int>>& mat, int m, int col){
        int best=-1; int ind=-1;
        for(int i=0;i<m;i++){ if(mat[i][col]>best){ best=mat[i][col]; ind=i; } }
        return ind;
    }
    vector<int> findPeakGrid(vector<vector<int>>& mat) {
        int m=mat.size(), n=mat[0].size();
        int low=0, high=n-1;
        while(low<=high){
            int mid=low+(high-low)/2;
            int row=maxi(mat,m,mid);
            int left = mid-1>=0 ? mat[row][mid-1] : -1;
            int right= mid+1<n ? mat[row][mid+1] : -1;
            if(mat[row][mid]>left && mat[row][mid]>right) return {row,mid};
            else if(mat[row][mid]<left) high=mid-1;
            else low=mid+1;
        }
        return {-1,-1};
    }
};

// independent verifier: is (i,j) a peak (strictly > all 4 neighbours, border=-1)
bool isPeak(const vector<vector<int>>& mat, int i, int j){
    int n=mat.size(), m=mat[0].size();
    int v=mat[i][j];
    int up    = i-1>=0 ? mat[i-1][j] : -1;
    int down  = i+1<n  ? mat[i+1][j] : -1;
    int left  = j-1>=0 ? mat[i][j-1] : -1;
    int right = j+1<m  ? mat[i][j+1] : -1;
    return v>up && v>down && v>left && v>right;
}

mt19937 rng(987654321u);
int randint(int lo,int hi){ return uniform_int_distribution<int>(lo,hi)(rng); }

// Generate a matrix with no two adjacent (4-neighbour) cells equal, values in [1,1e5].
vector<vector<int>> genMatrix(int n,int m,int maxV){
    vector<vector<int>> mat(n, vector<int>(m,0));
    for(int i=0;i<n;i++){
        for(int j=0;j<m;j++){
            int v;
            int tries=0;
            do{
                v = randint(1,maxV);
                tries++;
                bool ok=true;
                if(j>0 && mat[i][j-1]==v) ok=false;
                if(i>0 && mat[i-1][j]==v) ok=false;
                if(ok) break;
            }while(tries<100);
            // fallback guarantee: pick a value differing from both neighbours
            if((j>0 && mat[i][j-1]==v) || (i>0 && mat[i-1][j]==v)){
                int a = j>0?mat[i][j-1]:0;
                int b = i>0?mat[i-1][j]:0;
                for(int cand=1;cand<=maxV;cand++){ if(cand!=a && cand!=b){ v=cand; break; } }
            }
            mat[i][j]=v;
        }
    }
    return mat;
}

string matToStr(const vector<vector<int>>& mat){
    string s="[";
    for(size_t i=0;i<mat.size();i++){
        if(i) s+=", ";
        s+="[";
        for(size_t j=0;j<mat[i].size();j++){
            if(j) s+=", ";
            s+=to_string(mat[i][j]);
        }
        s+="]";
    }
    s+="]";
    return s;
}

int main(int argc,char**argv){
    int N = argc>1 ? atoi(argv[1]) : 2000;
    string outpath = argc>2 ? argv[2] : "out.jsonl";
    ofstream out(outpath);
    Solution sol;

    int produced=0;
    // explicit edge cases first
    vector<pair<int,int>> edges = {
        {1,1},{1,2},{2,1},{1,3},{3,1},{2,2},{1,5},{5,1},{2,3},{3,2},
        {500,1},{1,500},{500,500},{2,2},{1,1}
    };
    int edgeIdx=0;

    while(produced<N){
        int n,m,maxV;
        if(edgeIdx<(int)edges.size()){
            n=edges[edgeIdx].first; m=edges[edgeIdx].second;
            // for the giant ones keep value range bounded to ensure adjacency-distinct feasibility
            maxV = 100000;
            edgeIdx++;
        } else {
            // distribution of sizes; keep mostly small/medium for modest file size
            int r=randint(0,99);
            if(r<70){ n=randint(1,8); m=randint(1,8); }
            else if(r<90){ n=randint(1,20); m=randint(1,20); }
            else if(r<98){ n=randint(1,50); m=randint(1,50); }
            else { n=randint(1,120); m=randint(1,120); }
            // value range: mix small (forces lots of adjacency conflicts -> tests gen) and large
            int vr=randint(0,3);
            if(vr==0) maxV=randint(3,10);     // small range (must have >=3 to allow adjacency-distinct in 2D... actually >=2 enough for line, but 2D needs >=3 for safety on corners; we guard with fallback)
            else if(vr==1) maxV=randint(10,100);
            else if(vr==2) maxV=randint(100,5000);
            else maxV=100000;
        }
        // ensure feasibility of adjacency-distinct: need at least 3 distinct values when both n>1 and m>1
        if(n>1 && m>1 && maxV<3) maxV=3;
        if((n>1||m>1) && maxV<2) maxV=2;

        vector<vector<int>> mat = genMatrix(n,m,maxV);
        // verify adjacency-distinct property (should always hold)
        bool valid=true;
        for(int i=0;i<n && valid;i++) for(int j=0;j<m && valid;j++){
            if(j+1<m && mat[i][j]==mat[i][j+1]) valid=false;
            if(i+1<n && mat[i][j]==mat[i+1][j]) valid=false;
        }
        if(!valid) continue;

        vector<int> ans = sol.findPeakGrid(mat);
        // self-check: returned index must be a real peak
        if(ans[0]<0 || ans[1]<0 || !isPeak(mat,ans[0],ans[1])){
            // skip pathological (shouldn't happen)
            continue;
        }

        out << "{\"inputs\": {\"mat\": \"" << matToStr(mat) << "\"}, "
            << "\"expected\": \"[" << ans[0] << ", " << ans[1] << "]\"}\n";
        produced++;
    }
    out.close();
    cerr << "produced " << produced << " cases\n";
    return 0;
}
