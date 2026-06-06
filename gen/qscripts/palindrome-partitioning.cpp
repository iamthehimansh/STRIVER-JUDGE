// Generator for "palindrome-partitioning"
// Builds an embedded reference solution (backtracking over palindrome
// partitions) and emits up to N JSONL test cases.
//
// Output line format (one JSON object per line):
//   {"inputs": {"s": "<string>"}, "expected": "<2D array of strings>"}
//
// The "expected" value is rendered in the same bracketed style the dataset
// examples use, e.g.  [ [ "a", "a" ] , [ "aa" ] ]
// The judge compares leniently (ignoring brackets/commas/whitespace/quotes),
// so this serialization matches the example outputs verbatim.
//
// Compile: clang++ -std=c++17 -O2 -w palindrome-partitioning.cpp -o gen
// Run:     ./gen [N] [seed]   (defaults: N=2000, seed=12345)
#include <string>
#include <vector>
#include <iostream>
#include <fstream>
#include <random>
#include <set>
#include <cstdint>
using namespace std;

// ---- reference solution ----------------------------------------------------
static bool isPalindrome(const string& p) {
    int i = 0, j = (int)p.size() - 1;
    while (i < j) {
        if (p[i] != p[j]) return false;
        ++i; --j;
    }
    return true;
}

static void solve(int i, const string& s, vector<string>& temp,
                  vector<vector<string>>& ans) {
    if (i >= (int)s.size()) { ans.push_back(temp); return; }
    for (int p = i; p < (int)s.size(); ++p) {
        string palin = s.substr(i, p - i + 1);
        if (isPalindrome(palin)) {
            temp.push_back(palin);
            solve(p + 1, s, temp, ans);
            temp.pop_back();
        }
    }
}

static vector<vector<string>> partition(const string& s) {
    vector<vector<string>> ans;
    vector<string> temp;
    solve(0, s, temp, ans);
    return ans;
}

// ---- serialization ---------------------------------------------------------
// Render as: [ [ "a", "a" ] , [ "aa" ] ]   (matches dataset example style)
static string serialize(const vector<vector<string>>& res) {
    string out = "[ ";
    for (size_t i = 0; i < res.size(); ++i) {
        if (i) out += " , ";
        out += "[ ";
        for (size_t j = 0; j < res[i].size(); ++j) {
            if (j) out += ", ";
            out += "\"";
            out += res[i][j];
            out += "\"";
        }
        out += " ]";
    }
    out += " ]";
    return out;
}

// JSON-escape (string here is only lowercase letters, but be safe).
static string jesc(const string& s) {
    string o;
    for (char c : s) {
        switch (c) {
            case '"': o += "\\\""; break;
            case '\\': o += "\\\\"; break;
            default: o += c;
        }
    }
    return o;
}

int main(int argc, char** argv) {
    long long N = (argc > 1) ? atoll(argv[1]) : 2000;
    uint64_t seed = (argc > 2) ? strtoull(argv[2], nullptr, 10) : 12345ULL;
    mt19937_64 rng(seed);

    const string outPath =
        "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/palindrome-partitioning.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open " << outPath << "\n"; return 1; }

    set<string> seen;
    long long written = 0;

    // ---- forced edge cases (within constraints: len 1..16, a-z) ----
    vector<string> edges = {
        "a",                 // min length
        "z",
        "ab",                // no merge palindromes
        "aa",                // single palindrome of len 2
        "aaa",
        "aabaa",             // dataset example 1
        "baa",               // dataset example 2
        "aaaaaaaaaaaaaaaa",  // 16 same chars (max partitions: 2^15)
        "abcdefghijklmnop",  // 16 distinct (only one partition)
        "racecar",
        "noonabbad",
        "abacaba",
        "aaaabbbb",
        "zzzzzzzzzzzzzzzz",
    };
    for (const string& e : edges) {
        if (written >= N) break;
        if ((int)e.size() < 1 || (int)e.size() > 16) continue;
        if (!seen.insert(e).second) continue;
        out << "{\"inputs\": {\"s\": \"" << jesc(e) << "\"}, \"expected\": \""
            << jesc(serialize(partition(e))) << "\"}\n";
        ++written;
    }

    // ---- random cases ----
    // Mix of small alphabets (more palindromes / interesting structure) and
    // larger alphabets. Length uniform in [1,16].
    auto genString = [&](int len, int alpha) {
        string s;
        uniform_int_distribution<int> cd(0, alpha - 1);
        for (int i = 0; i < len; ++i) s += char('a' + cd(rng));
        return s;
    };

    uniform_int_distribution<int> lenD(1, 16);
    // alphabet sizes weighted toward small to exercise many palindromes,
    // but capped so 2^(len-1) partitions stay manageable.
    int alphabets[] = {1, 2, 2, 2, 3, 3, 4, 5, 6, 8, 12, 26};
    uniform_int_distribution<int> aD(0, (int)(sizeof(alphabets)/sizeof(int)) - 1);

    long long attempts = 0;
    const long long maxAttempts = N * 200;
    while (written < N && attempts < maxAttempts) {
        ++attempts;
        int len = lenD(rng);
        int alpha = alphabets[aD(rng)];
        // For alphabet==1, cap length to avoid 2^15 explosion blowing file size
        // on every line; allow it occasionally but mostly shorter.
        if (alpha == 1 && len > 10) len = 1 + (int)(rng() % 10);
        string s = genString(len, alpha);
        if (!seen.insert(s).second) continue;
        out << "{\"inputs\": {\"s\": \"" << jesc(s) << "\"}, \"expected\": \""
            << jesc(serialize(partition(s))) << "\"}\n";
        ++written;
    }

    out.close();
    cerr << "wrote " << written << " cases to " << outPath << "\n";
    return 0;
}
