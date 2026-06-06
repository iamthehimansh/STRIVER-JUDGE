#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <set>
#include <fstream>
using namespace std;

class Solution {
public:
    vector<string> result;
    string num;
    long long target;

    void dfs(int idx, string expr, long long curVal, long long lastOperand) {
        if (idx == (int)num.size()) {
            if (curVal == target) result.push_back(expr);
            return;
        }
        for (int i = idx; i < (int)num.size(); i++) {
            if (i != idx && num[idx] == '0') break;
            string curStr = num.substr(idx, i - idx + 1);
            long long curNum = stoll(curStr);
            if (idx == 0) {
                dfs(i + 1, curStr, curNum, curNum);
            } else {
                dfs(i + 1, expr + "+" + curStr, curVal + curNum, curNum);
                dfs(i + 1, expr + "-" + curStr, curVal - curNum, -curNum);
                dfs(i + 1, expr + "*" + curStr, curVal - lastOperand + lastOperand * curNum, lastOperand * curNum);
            }
        }
    }

    vector<string> addOperators(string s, long long target_) {
        result.clear();
        num = s;
        target = target_;
        dfs(0, "", 0, 0);
        sort(result.begin(), result.end());
        return result;
    }
};

string esc(const string&s){ string o; for(char c:s){ if(c=='"'||c=='\\') o+='\\'; o+=c;} return o; }

int main(int argc, char**argv){
    string outpath = argv[1];
    int N = atoi(argv[2]);
    mt19937 rng(12345);

    ofstream out(outpath);
    set<pair<string,long long>> seen;
    Solution sol;

    auto emit = [&](const string& num, long long target){
        if(seen.count({num,target})) return false;
        seen.insert({num,target});
        auto res = sol.addOperators(num, target);
        // build expected: space separated expressions (lenient compare ignores brackets/quotes)
        string exp;
        for(size_t i=0;i<res.size();i++){ if(i) exp+=" "; exp+=res[i]; }
        out << "{\"inputs\": {\"s\": \"" << esc(num) << "\", \"target\": \"" << target << "\"}, \"expected\": \"" << esc(exp) << "\"}\n";
        return true;
    };

    int count = 0;

    // Edge cases first
    vector<pair<string,long long>> edges = {
        {"1",1},{"1",0},{"1",2},{"0",0},{"9",9},{"9",-1},
        {"123",6},{"0232",8},{"00",0},{"000",0},{"105",5},{"1234",10},
        {"1000000000",1000000000},
        {"2147483647", 2147483647LL},{"99",1},{"99",18},{"99",-1},
        {"10",10},{"10",1},{"05",5},{"05",0},{"3456237490",1},
        {"5",-2147483648LL},{"5",2147483647LL},{"123456789",45},
        {"111111",111111},{"0000000000",0},{"2147483647",-2147483648LL}
    };
    for(auto&e:edges){
        if((int)e.first.size()<1 || (int)e.first.size()>10) continue;
        if(e.second < -2147483648LL || e.second > 2147483647LL) continue; // enforce target constraint
        if(emit(e.first,e.second)) count++;
    }

    uniform_int_distribution<int> lenD(1,10);
    uniform_int_distribution<int> digD(0,9);

    auto randNum = [&]()->string{
        int L = lenD(rng);
        string s; for(int i=0;i<L;i++) s+=('0'+digD(rng));
        return s;
    };

    // helper: pick a target that is achievable by a random expression over num
    auto reachableTarget = [&](const string&num)->long long{
        // build a random expression and evaluate
        int n = num.size();
        if(n==1) return stoll(num);
        // split into operands at random positions, choose ops, ensure no leading-zero multi-digit
        // simple approach: random partition
        vector<string> ops_choices = {"+","-","*"};
        // generate partition
        vector<int> cuts;
        for(int i=1;i<n;i++){ if(rng()&1) cuts.push_back(i); }
        vector<string> operands;
        int prev=0;
        vector<int> bounds; bounds.push_back(0); for(int c:cuts) bounds.push_back(c); bounds.push_back(n);
        for(size_t i=0;i+1<bounds.size();i++){
            string seg = num.substr(bounds[i], bounds[i+1]-bounds[i]);
            // leading zero multi-digit not allowed -> if so, split into single digits for that seg
            if(seg.size()>1 && seg[0]=='0'){ for(char ch:seg) operands.push_back(string(1,ch)); }
            else operands.push_back(seg);
        }
        // evaluate with operator precedence
        // values and ops
        vector<long long> vals; vals.push_back(stoll(operands[0]));
        vector<char> ops;
        for(size_t i=1;i<operands.size();i++){
            string op = ops_choices[rng()%3];
            long long v = stoll(operands[i]);
            if(op=="*"){ vals.back()*=v; }
            else if(op=="+"){ vals.push_back(v); }
            else { vals.push_back(-v); }
        }
        long long s=0; for(long long v:vals) s+=v; return s;
    };

    uniform_int_distribution<long long> tgtD(-2147483648LL, 2147483647LL);

    while(count < N){
        string num = randNum();
        long long target;
        int mode = rng()%3;
        if(mode==0){ target = reachableTarget(num); }
        else if(mode==1){ target = reachableTarget(num) + (long long)(rng()%5) - 2; }
        else { target = tgtD(rng); }
        // clamp target to int range
        if(target < -2147483648LL) target = -2147483648LL;
        if(target > 2147483647LL) target = 2147483647LL;
        if(emit(num,target)) count++;
    }

    out.close();
    cerr << "wrote " << count << " cases\n";
    return 0;
}
