// Self-contained: explicit headers (macOS clang has no <bits/stdc++.h>).
// Compile: clang++ -std=c++17 -O2 -w infix-to-prefix-conversion.cpp -o gen
// Run:     ./gen 2000   (writes the .jsonl to the generated-tests dir)
#include <algorithm>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <stack>
#include <random>
#include <cctype>
#include <cstdlib>
using namespace std;

// ---- AST oracle (provably correct, left-associative) ----
struct P { const string& s; size_t i=0; P(const string& str):s(str){}
    char peek(){ return i<s.size()? s[i] : '\0'; }
    string expr(); string term(); string factor();
};
string P::factor(){ char c=peek(); if(c=='('){ i++; string e=expr(); i++; return e;} i++; return string(1,c);}
string P::term(){ string l=factor(); while(peek()=='*'||peek()=='/'){char op=peek();i++;string r=factor();l=string(1,op)+l+r;} return l;}
string P::expr(){ string l=term(); while(peek()=='+'||peek()=='-'){char op=peek();i++;string r=term();l=string(1,op)+l+r;} return l;}
string ast_prefix(const string& s){ P p(s); return p.expr(); }

// ---- stack oracle with strictly-greater rule (must agree with AST) ----
int prec(char c){ if(c=='*'||c=='/')return 2; if(c=='+'||c=='-')return 1; return 0;}
string stack_prefix(const string& s){
    string ans=""; stack<char> st;
    for(int i=(int)s.size()-1;i>=0;i--){ char c=s[i];
        if(islower((unsigned char)c)) ans.push_back(c);
        else if(c==')') st.push(c);
        else if(c=='('){ while(!st.empty()&&st.top()!=')'){ans.push_back(st.top());st.pop();} if(!st.empty())st.pop();}
        else { while(!st.empty()&&st.top()!=')'&&prec(st.top())>prec(c)){ans.push_back(st.top());st.pop();} st.push(c);} }
    while(!st.empty()){ans.push_back(st.top());st.pop();}
    reverse(ans.begin(),ans.end()); return ans;
}

// ---- random valid infix expression generator (recursive, depth/length controlled) ----
mt19937 rng(12345);
int randint(int lo,int hi){ return lo + (int)(rng()%(hi-lo+1)); }
char randop(){ const char ops[]={'+','-','*','/'}; return ops[randint(0,3)]; }
char randoperand(){ return (char)('a'+randint(0,25)); }

// build an expression with up to `maxleaves` operands, controlling parenthesization
string buildExpr(int maxleaves, int maxlen, int curlen);
string buildExpr(int maxleaves, int maxlen, int curlen){
    // base: single operand
    if(maxleaves<=1 || curlen>maxlen) return string(1,randoperand());
    // decide to make a binary node
    int split = randint(1, maxleaves-1);
    string left = buildExpr(split, maxlen, curlen);
    char op = randop();
    string right = buildExpr(maxleaves-split, maxlen, curlen+(int)left.size());
    // randomly parenthesize subexpressions
    string l = left, r = right;
    if(left.size()>1 && randint(0,2)==0) l = "("+left+")";
    if(right.size()>1 && randint(0,2)==0) r = "("+right+")";
    string res = l + string(1,op) + r;
    return res;
}

int main(int argc, char** argv){
    int N = argc>1? atoi(argv[1]) : 2000;
    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/infix-to-prefix-conversion.jsonl");

    auto emit=[&](const string& infix){
        string a = ast_prefix(infix);
        string b = stack_prefix(infix);
        if(a!=b){ return false; } // skip ambiguous (shouldn't happen with our generator using both checks)
        out << "{\"inputs\": {\"expression\": \"" << infix << "\"}, \"expected\": \"" << a << "\"}\n";
        return true;
    };

    int count=0;
    // ---- edge cases first ----
    vector<string> edges = {
        "a",                       // min length 1, single operand
        "a+b","a-b","a*b","a/b",
        "(a)","((a))",
        "(a+b)*c","a+b*c",
        "((a-(b/c))*((a/k)-l))",
        "a-b-c","a-b+c","a/b/c","a*b*c","a+b+c",
        "a-b-c-d-e","a/b/c/d","a*b/c*d",
        "(a+b)*(c+d)","((a))+((b))",
        "a+b*c-d/e",
        "z","(z)"
    };
    for(auto& e: edges){ if(emit(e)) count++; }

    // ---- a big chain of same-precedence operators to stress left-assoc (length up to ~1000) ----
    {
        string chain; chain.push_back(randoperand());
        while((int)chain.size() < 990){ chain.push_back('-'); chain.push_back(randoperand()); }
        if(emit(chain)) count++;
        string chain2; chain2.push_back(randoperand());
        while((int)chain2.size() < 990){ chain2.push_back('/'); chain2.push_back(randoperand()); }
        if(emit(chain2)) count++;
    }

    // ---- random expressions of varying sizes ----
    int guard=0;
    while(count<N && guard<N*50){
        guard++;
        int leaves = randint(1, 80);     // number of operands
        int maxlen = randint(5, 400);
        string e = buildExpr(leaves, maxlen, 0);
        if((int)e.size() < 1 || (int)e.size() > 1000) continue;
        if(emit(e)) count++;
    }

    out.close();
    cerr << "Generated " << count << " cases\n";
    return 0;
}
