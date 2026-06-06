// Generator + static test set for Striver problem: longest-common-prefix
// Param name from starterCpp: vector<string>& str  -> input key = "str"
// Output: expected is the LCP string, formatted quoted like the examples ("fl", "").
//
// Constraints:
//   1 <= str.length (number of strings) <= 200
//   1 <= str[i].length <= 200
//   str[i] contains only lowercase English letters.
//
// Build:  clang++ -std=c++17 -O2 -w longest-common-prefix.cpp -o gen
// Run:    ./gen > longest-common-prefix.jsonl

#include <vector>
#include <string>
#include <algorithm>
#include <random>
#include <cstdio>
#include <iostream>
using namespace std;

// ---- Reference oracle (from strivers-a2z-ref, sort + compare first/last) ----
string longestCommonPrefix(vector<string> strs) {
    if (strs.empty()) return "";
    sort(strs.begin(), strs.end());
    const string& a = strs.front();
    const string& b = strs.back();
    int n = (int)min(a.size(), b.size());
    int len = 0;
    while (len < n && a[len] == b[len]) len++;
    return a.substr(0, len);
}

// ---- JSON helpers ----
// All strings are lowercase letters only, so no escaping needed beyond quotes.
static string jsonArray(const vector<string>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); ++i) {
        if (i) s += ", ";
        s += "\"" + v[i] + "\"";
    }
    s += "]";
    return s;
}

int main() {
    std::mt19937 rng(123456789u);
    auto randint = [&](int lo, int hi) {
        return std::uniform_int_distribution<int>(lo, hi)(rng);
    };
    auto randLetter = [&]() -> char { return char('a' + randint(0, 25)); };
    auto randStr = [&](int len) {
        string s; s.reserve(len);
        for (int i = 0; i < len; ++i) s += randLetter();
        return s;
    };

    const int TARGET = 2000;
    vector<vector<string>> cases;

    // ---- Edge cases ----
    cases.push_back({"a"});                                  // single 1-char
    cases.push_back({"z"});                                  // single 1-char
    cases.push_back({"a", "a"});                             // identical 1-char
    cases.push_back({"a", "b"});                             // no common prefix
    cases.push_back({"ab", "ab"});                           // identical
    cases.push_back({"abc", "ab"});                          // one is prefix of other
    cases.push_back({"ab", "abc"});
    cases.push_back({"flowers", "flow", "fly", "flight"});   // example 1 -> "fl"
    cases.push_back({"dog", "cat", "animal", "monkey"});     // example 2 -> ""
    cases.push_back({"car", "cars", "case", "capsicum"});    // dataset case 3 -> "ca"
    cases.push_back({"lady", "lazy"});                       // nowYourTurn -> "la"
    {
        // max length identical strings (length 200), 200 of them
        string big(200, 'q');
        vector<string> v(200, big);
        cases.push_back(v);
    }
    {
        // 200 strings, all length 200, sharing a 100-char prefix then diverging
        string pref(100, 'm');
        vector<string> v;
        for (int i = 0; i < 200; ++i) {
            string s = pref + randStr(100);
            v.push_back(s);
        }
        cases.push_back(v);
    }
    {
        // 200 distinct single chars cycling -> common prefix "" unless all same
        vector<string> v;
        for (int i = 0; i < 200; ++i) v.push_back(string(1, char('a' + (i % 26))));
        cases.push_back(v);
    }
    {
        // all same except first char differs in one -> ""
        vector<string> v;
        for (int i = 0; i < 50; ++i) v.push_back("hello");
        v.push_back("world");
        cases.push_back(v);
    }

    // ---- Random cases ----
    while ((int)cases.size() < TARGET) {
        int mode = randint(0, 4);
        int n = randint(1, 200);
        vector<string> v;

        if (mode == 0) {
            // Fully random strings (likely short or empty common prefix)
            for (int i = 0; i < n; ++i) v.push_back(randStr(randint(1, 200)));
        } else if (mode == 1) {
            // Shared random prefix, then random tails
            int plen = randint(0, 50);
            string pref = randStr(plen);
            for (int i = 0; i < n; ++i) {
                int tail = randint(0, 50);
                string s = pref + randStr(tail);
                if (s.empty()) s = randStr(1); // enforce length >= 1
                v.push_back(s);
            }
        } else if (mode == 2) {
            // Small alphabet to make collisions / longer common prefixes likely
            int plen = randint(0, 10);
            string pref;
            for (int i = 0; i < plen; ++i) pref += char('a' + randint(0, 2));
            for (int i = 0; i < n; ++i) {
                int tail = randint(0, 10);
                string s = pref;
                for (int k = 0; k < tail; ++k) s += char('a' + randint(0, 2));
                if (s.empty()) s = string(1, char('a' + randint(0, 2)));
                v.push_back(s);
            }
        } else if (mode == 3) {
            // Many identical strings + a few random
            string base = randStr(randint(1, 30));
            for (int i = 0; i < n; ++i) {
                if (randint(0, 4) == 0) v.push_back(randStr(randint(1, 30)));
                else v.push_back(base);
            }
        } else {
            // Short strings, length 1..5
            for (int i = 0; i < n; ++i) v.push_back(randStr(randint(1, 5)));
        }

        // Safety: enforce all constraints (1..200 length each, 1..200 count)
        bool ok = !v.empty() && v.size() <= 200;
        for (auto& s : v) if (s.empty() || s.size() > 200) ok = false;
        if (!ok) continue;
        cases.push_back(v);
    }

    // ---- Emit JSONL ----
    string out;
    out.reserve(1 << 20);
    for (auto& v : cases) {
        string lcp = longestCommonPrefix(v);
        // expected formatted as a quoted string, matching the example outputs.
        out += "{\"inputs\": {\"str\": ";
        out += jsonArray(v);
        out += "}, \"expected\": \"\\\"";
        out += lcp;
        out += "\\\"\"}\n";
    }
    fwrite(out.data(), 1, out.size(), stdout);
    return 0;
}
