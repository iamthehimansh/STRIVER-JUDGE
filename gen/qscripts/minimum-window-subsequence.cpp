#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <climits>
#include <random>
using namespace std;

string minWindow(string s, string t) {
    int n=s.size();
    string ans="";
    int l=0,r=0,r2=0,len=INT_MAX;
    while(r<n){
        if(s[r]==t[r2]) r2++;
        if(r2==(int)t.size()){
            l=r;
            r2--;
            while(l>=0 && r2>=0){
                if(s[l]==t[r2]) r2--;
                l--;
            }
            l++;
            if(r-l+1<len){
                len=r-l+1;
                ans=s.substr(l,r-l+1);
            }
            r2=0;
            r=l+1;
        }
        r++;
    }
    return ans;
}

mt19937 rng(987654321);
int ri(int lo,int hi){return uniform_int_distribution<int>(lo,hi)(rng);}

// JSON string escape for raw strings (lowercase letters only here, so minimal needed)
string jesc(const string&x){
    string o; for(char c:x){ if(c=='"'||c=='\\') o+='\\'; o+=c;} return o;
}

string randStr(int len, int alpha){
    string s; s.reserve(len);
    for(int i=0;i<len;i++) s+=(char)('a'+ri(0,alpha-1));
    return s;
}

int main(){
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/minimum-window-subsequence.jsonl");
    int total=2000;
    int count=0;

    auto emit=[&](const string&s1,const string&s2){
        string exp=minWindow(s1,s2);
        out << "{\"inputs\": {\"s1\": \"" << jesc(s1) << "\", \"s2\": \"" << jesc(s2)
            << "\"}, \"expected\": \"\\\"" << jesc(exp) << "\\\"\"}\n";
        count++;
    };

    // Edge / fixed cases
    emit("abcdebdde","bde");
    emit("jmeqsiwvaovvnbstl","u");
    emit("a","a");        // min sizes, match
    emit("a","b");        // min sizes, no match
    emit("aaaa","aa");    // repeats
    emit("ab","ba");      // order matters, no window
    emit("ababab","ab");
    emit("cnhczmccula","cm"); // arbitrary

    // s2 longer than s1 -> always "" (but constraints allow s2 up to 100)
    emit(randStr(5,3), randStr(20,3));

    while(count<total){
        int mode=ri(0,6);
        int n,m,alpha;
        if(mode==0){ // tiny strings, small alphabet (high match chance)
            n=ri(1,8); m=ri(1,4); alpha=2;
        } else if(mode==1){ // small alphabet medium
            n=ri(5,60); m=ri(1,8); alpha=2;
        } else if(mode==2){ // medium, alphabet 4
            n=ri(10,200); m=ri(1,15); alpha=4;
        } else if(mode==3){ // larger, full alphabet (often no window)
            n=ri(100,2000); m=ri(1,30); alpha=26;
        } else if(mode==4){ // big s1 near max-ish, small alphabet -> windows exist
            n=ri(1000,20000); m=ri(1,50); alpha=3;
        } else if(mode==5){ // s2 close to s1 length
            n=ri(5,100); m=ri(max(1,n-5),n+10); alpha=3; if(m>100)m=ri(1,100);
        } else { // s2 long up to constraint max
            n=ri(50,5000); m=ri(1,100); alpha=ri(2,6);
        }
        if(m>100) m=100;        // enforce s2 <= 100
        if(n>20000) n=20000;    // enforce s1 <= 2e4
        if(n<1) n=1; if(m<1) m=1;
        string s1=randStr(n,alpha);
        string s2=randStr(m,alpha);
        emit(s1,s2);
    }
    out.close();
    cerr<<"wrote "<<count<<" cases\n";
    return 0;
}
