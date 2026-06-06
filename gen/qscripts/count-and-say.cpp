// Generator for Striver problem: count-and-say
// signature: string countAndSay(int n)
// constraint: 1 <= n <= 30
// Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-and-say.jsonl
//   one JSON object per line: {"inputs": {"n": "<int>"}, "expected": "<string>"}
//
// Compile: clang++ -std=c++17 -O2 -w count-and-say.cpp -o gen
// Run:     ./gen
#include <string>
#include <vector>
#include <fstream>
#include <random>
#include <iostream>
using namespace std;

// ----- reference oracle -----
string countAndSay(int n) {
    if (n == 1) return "1";
    string prev = countAndSay(n - 1);
    string ans = "";
    for (size_t i = 0; i < prev.size(); i++) {
        size_t j = i + 1;
        while (j < prev.size() && prev[j - 1] == prev[j]) j++;
        ans += to_string((int)(j - i)) + prev[i];
        i = j - 1;
    }
    return ans;
}

int main() {
    const int N_CASES = 2000;
    const char* OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-and-say.jsonl";

    vector<string> ans(31);
    for (int n = 1; n <= 30; n++) ans[n] = countAndSay(n);

    ofstream out(OUT);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    mt19937 rng(12345);
    uniform_int_distribution<int> dist(1, 30);

    // Ensure every distinct n in [1,30] (edge cases min=1, max=30) appears,
    // then fill the rest randomly.
    vector<int> cases;
    for (int n = 1; n <= 30; n++) cases.push_back(n);
    while ((int)cases.size() < N_CASES) cases.push_back(dist(rng));

    for (int n : cases) {
        out << "{\"inputs\": {\"n\": \"" << n << "\"}, \"expected\": \""
            << ans[n] << "\"}\n";
    }
    out.close();
    cerr << "wrote " << cases.size() << " cases\n";
    return 0;
}
