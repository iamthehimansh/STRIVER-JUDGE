#include <iostream>
#include <string>
#include <fstream>
#include <random>
#include <vector>
using namespace std;

string removeOuterParentheses(string s) {
    int n=s.size();
    string ans="";
    int cnt=0;
    for(int i=0;i<n;i++){
        if(s[i]==')') cnt--;
        if(cnt!=0) ans+=s[i];
        if(s[i]=='(') cnt++;
    }
    return ans;
}

// Generate a random valid parentheses string of exactly 2*pairs chars
string genValid(int pairs, mt19937 &rng) {
    string res;
    int open=0, close=0;
    for(int i=0;i<2*pairs;i++){
        // we can add '(' if open<pairs; can add ')' if close<open
        bool canOpen = open<pairs;
        bool canClose = close<open;
        if(canOpen && canClose){
            // bias: choose randomly
            if(rng()&1){ res+='('; open++; } else { res+=')'; close++; }
        } else if(canOpen){ res+='('; open++; }
        else { res+=')'; close++; }
    }
    return res;
}

int main(int argc, char** argv){
    long long n = 2000;
    if(argc>1) n = atoll(argv[1]);
    string outpath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/remove-outermost-parentheses.jsonl";
    if(argc>2) outpath = argv[2];
    ofstream out(outpath);
    mt19937 rng(12345);

    auto emit = [&](const string &s){
        string exp = removeOuterParentheses(s);
        // JSON: inputs.s raw string, expected raw string (quoted in dataset style)
        out << "{\"inputs\": {\"s\": \"" << s << "\"}, \"expected\": \"" << exp << "\"}\n";
    };

    // Edge cases first
    vector<string> edges = {
        "()",            // min size, single primitive -> ""
        "(())",
        "((()))",
        "()(()())(())",
        "(()(()))(()())",
        "()()()",
        "((((()))))"
    };
    long long produced=0;
    for(auto &e: edges){ emit(e); produced++; if(produced>=n) { out.close(); return 0; } }

    // Random valid strings across size ranges
    // length must be 1<=len<=1e5 and even (valid). pairs from 1..50000
    uniform_int_distribution<int> smallPairs(1, 50);
    uniform_int_distribution<int> medPairs(1, 2000);
    uniform_int_distribution<int> bigPairs(1, 50000);

    while(produced < n){
        int bucket = produced % 10;
        int pairs;
        if(bucket < 5) pairs = smallPairs(rng);       // many small for variety
        else if(bucket < 9) pairs = medPairs(rng);    // medium
        else pairs = bigPairs(rng);                   // large stress
        if(pairs<1) pairs=1;
        string s = genValid(pairs, rng);
        emit(s);
        produced++;
    }
    out.close();
    return 0;
}
