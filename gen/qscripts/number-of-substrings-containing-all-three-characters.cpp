// Generator + static test set for:
//   Number of Substrings Containing All Three Characters
//
// Reference (ground-truth oracle): sliding-window "last seen" technique.
// For each index i (treated as the right end of substrings), once all of
// 'a','b','c' have been seen, every substring ending at i whose left end is
// <= min(lastseen) is valid -> add (1 + min(lastseen)).
//
// Constraints:
//   1 <= s.length <= 5*10^4
//   s consists only of 'a','b','c'.
//
// Output: one JSON object per line:
//   {"inputs": {"s": "<string>"}, "expected": "<int>"}
//
// Build:  clang++ -std=c++17 -O2 -w gen.cpp -o gen
// Run:    ./gen > out.jsonl
//
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <set>
using namespace std;

// ---- Reference solution (oracle) ----
long long numberOfSubstrings(const string &s) {
    int n = (int)s.size();
    int lastseen[3] = {-1, -1, -1};
    long long ans = 0;
    for (int i = 0; i < n; i++) {
        lastseen[s[i] - 'a'] = i;
        if (lastseen[0] != -1 && lastseen[1] != -1 && lastseen[2] != -1) {
            ans += (long long)(1 + min(min(lastseen[0], lastseen[1]), lastseen[2]));
        }
    }
    return ans;
}

int main() {
    const int TOTAL = 2000;
    const int MAXLEN = 50000; // 5 * 10^4
    mt19937 rng(20240606u);

    ofstream out("/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-substrings-containing-all-three-characters.jsonl");

    auto emit = [&](const string &s) {
        long long e = numberOfSubstrings(s);
        out << "{\"inputs\": {\"s\": \"" << s << "\"}, \"expected\": \"" << e << "\"}\n";
    };

    set<string> seen;            // avoid duplicate small cases
    vector<string> cases;

    auto add = [&](const string &s) {
        if (s.empty()) return;
        if (s.size() <= 12 && seen.count(s)) return;
        if (s.size() <= 12) seen.insert(s);
        cases.push_back(s);
    };

    // ---- Edge cases ----
    add("a");                 // min length, no triple
    add("b");
    add("c");
    add("abc");               // smallest valid
    add("cba");
    add("aaa");               // no 'b','c' -> 0
    add("bbb");
    add("ccc");
    add("ab");                // missing one
    add("aabbcc");
    add("abcba");             // example 1 -> 5
    add("ccabcc");            // example 2 -> 8
    add("abccba");            // nowYourTurn -> 9
    add("abcccbab");          // dataset case 3
    add("abcabcabc");
    // all same char, large -> expected 0
    add(string(MAXLEN, 'a'));
    add(string(MAXLEN, 'b'));
    // only two distinct chars, large -> 0
    {
        string s; s.reserve(MAXLEN);
        for (int i = 0; i < MAXLEN; i++) s.push_back("ab"[i & 1]);
        add(s);
    }
    // perfectly cyclic abcabc... at MAXLEN
    {
        string s; s.reserve(MAXLEN);
        for (int i = 0; i < MAXLEN; i++) s.push_back("abc"[i % 3]);
        add(s);
    }
    // single 'c' at the very end of a long 'ab' prefix
    {
        string s(MAXLEN - 1, 'a');
        s[0] = 'b';
        s.push_back('c');
        add(s);
    }

    // ---- Random small cases (lengths 1..40), exhaust some short ones ----
    uniform_int_distribution<int> smallLen(1, 40);
    while ((int)cases.size() < 700) {
        int L = smallLen(rng);
        string s; s.reserve(L);
        uniform_int_distribution<int> ch(0, 2);
        for (int i = 0; i < L; i++) s.push_back('a' + ch(rng));
        add(s);
    }

    // ---- Random medium cases (lengths 41..2000) ----
    uniform_int_distribution<int> medLen(41, 2000);
    while ((int)cases.size() < 1300) {
        int L = medLen(rng);
        string s; s.reserve(L);
        uniform_int_distribution<int> ch(0, 2);
        for (int i = 0; i < L; i++) s.push_back('a' + ch(rng));
        add(s);
    }

    // ---- Random large cases (lengths up to MAXLEN), varied distributions ----
    uniform_int_distribution<int> bigLen(2001, MAXLEN);
    while ((int)cases.size() < TOTAL) {
        int L = bigLen(rng);
        string s; s.reserve(L);
        // pick a skew: sometimes one char dominates to stress edge handling
        int mode = rng() % 4;
        for (int i = 0; i < L; i++) {
            int r = rng() % 100;
            char c;
            if (mode == 0) {                 // uniform
                c = 'a' + (rng() % 3);
            } else if (mode == 1) {          // 'a' heavy
                c = (r < 80) ? 'a' : ('b' + (rng() % 2));
            } else if (mode == 2) {          // 'c' heavy
                c = (r < 80) ? 'c' : ('a' + (rng() % 2));
            } else {                         // mostly two chars, rare third
                c = (r < 49) ? 'a' : (r < 98 ? 'b' : 'c');
            }
            s.push_back(c);
        }
        add(s);
    }

    // Trim to exactly TOTAL (edge + random may overshoot)
    if ((int)cases.size() > TOTAL) cases.resize(TOTAL);

    for (auto &s : cases) emit(s);
    out.close();

    cerr << "wrote " << cases.size() << " cases\n";
    return 0;
}
