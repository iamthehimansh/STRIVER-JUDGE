// Generator + reference for "KMP Algorithm or LPS array"
// Problem: vector<int> search(string pat, string txt)
//   Return all 0-based start indices where `pat` occurs in `txt`, ascending.
//   Empty list -> empty output line.
// Constraints: 1 <= text.length, pattern.length <= 5*10^4
//
// Output JSONL: one object per line:
//   {"inputs": {"pattern": "<pat>", "text": "<txt>"}, "expected": "<idx idx ...>"}
// Keys are in starterCpp signature order: (pat, txt) -> ("pattern","text").
//
// Build: clang++ -std=c++17 -O2 -w kmp-algorithm-or-lps-array.cpp -o gen
// Run:   ./gen > kmp-algorithm-or-lps-array.jsonl

#include <iostream>
#include <vector>
#include <string>
#include <random>
#include <cstdint>

using namespace std;

// LPS (longest proper prefix which is also suffix) array for s.
static vector<int> buildLPS(const string& s){
    int n = (int)s.size();
    vector<int> pi(n, 0);
    for(int i = 1; i < n; i++){
        int j = pi[i-1];
        while(j > 0 && s[j] != s[i]) j = pi[j-1];
        if(s[j] == s[i]) j++;
        pi[i] = j;
    }
    return pi;
}

// KMP search: all 0-based occurrences of pat in txt.
static vector<int> search(const string& pat, const string& txt){
    vector<int> res;
    int m = (int)pat.size(), n = (int)txt.size();
    if(m == 0 || m > n) return res;
    vector<int> lps = buildLPS(pat);
    int i = 0, j = 0;
    while(i < n){
        if(txt[i] == pat[j]){
            i++; j++;
            if(j == m){
                res.push_back(i - m);
                j = lps[j-1];
            }
        } else {
            if(j > 0) j = lps[j-1];
            else i++;
        }
    }
    return res;
}

// JSON-escape a raw string for embedding inside a JSON string literal.
static string jesc(const string& s){
    string o;
    o.reserve(s.size()+8);
    for(char c : s){
        switch(c){
            case '"':  o += "\\\""; break;
            case '\\': o += "\\\\"; break;
            case '\n': o += "\\n"; break;
            case '\r': o += "\\r"; break;
            case '\t': o += "\\t"; break;
            case '\b': o += "\\b"; break;
            case '\f': o += "\\f"; break;
            default:
                if((unsigned char)c < 0x20){
                    char buf[8];
                    snprintf(buf, sizeof(buf), "\\u%04x", (int)(unsigned char)c);
                    o += buf;
                } else {
                    o += c;
                }
        }
    }
    return o;
}

int main(int argc, char** argv){
    uint64_t seed = 0xC0FFEEu;
    if(argc > 1) seed = strtoull(argv[1], nullptr, 10);
    mt19937_64 rng(seed);

    int total = 2000;
    int produced = 0;

    auto emit = [&](const string& pat, const string& txt){
        vector<int> r = search(pat, txt);
        string exp;
        for(size_t k = 0; k < r.size(); k++){
            if(k) exp += ' ';
            exp += to_string(r[k]);
        }
        // {"inputs": {"pattern": "...", "text": "..."}, "expected": "..."}
        string line = "{\"inputs\": {\"pattern\": \"";
        line += jesc(pat);
        line += "\", \"text\": \"";
        line += jesc(txt);
        line += "\"}, \"expected\": \"";
        line += jesc(exp);
        line += "\"}";
        cout << line << "\n";
        produced++;
    };

    // ---- Deterministic edge cases first ----
    // 1) single-char text & pattern, match
    emit("a", "a");
    // 2) single-char, no match
    emit("a", "b");
    // 3) pattern longer than text -> no occurrence
    emit("abc", "a");
    // 4) pattern == text
    emit("hello", "hello");
    // 5) dataset examples
    emit("abra", "abracadabra");
    emit("abc", "abcabcabc");
    emit("aa", "daad"); // no match -> empty expected
    // 6) overlapping occurrences
    emit("aa", "aaaa");        // indices 0 1 2
    emit("aba", "ababababa");  // overlapping
    // 7) all-same long text
    emit("aaa", string(50, 'a'));
    // 8) pattern of length 1 over varied text
    emit("z", "zzzazzz");
    // 9) text with no occurrence at all of a char
    emit("xyz", string(40, 'a'));

    // ---- Random cases ----
    // Use small alphabets sometimes (to force overlaps/many matches),
    // larger alphabets other times. Keep lengths within constraints but
    // moderate so the file stays modest while still covering structure.
    auto randStr = [&](int len, int alphabet){
        string s;
        s.reserve(len);
        uniform_int_distribution<int> ch(0, alphabet-1);
        for(int i = 0; i < len; i++) s += char('a' + ch(rng));
        return s;
    };

    while(produced < total){
        int bucket = (int)(rng() % 10);
        int alpha;
        if(bucket < 4) alpha = 2;        // binary alphabet -> many overlaps
        else if(bucket < 7) alpha = 3;
        else if(bucket < 9) alpha = 6;
        else alpha = 26;

        // text length: mix of tiny, small, medium, and a few large.
        int tlen;
        int lb = (int)(rng() % 20);
        if(lb == 0) tlen = 1;
        else if(lb < 8) tlen = 1 + (int)(rng() % 12);        // tiny
        else if(lb < 16) tlen = 1 + (int)(rng() % 200);      // small
        else if(lb < 19) tlen = 1 + (int)(rng() % 3000);     // medium
        else tlen = 1 + (int)(rng() % 50000);                // up to 5*10^4

        // pattern length: usually <= tlen, occasionally longer (no match).
        int plen;
        int pb = (int)(rng() % 12);
        if(pb == 0) plen = 1;
        else if(pb == 1) plen = tlen + 1 + (int)(rng() % 3); // longer than text
        else {
            int maxp = tlen;
            plen = 1 + (int)(rng() % maxp);
            if(plen > tlen) plen = tlen;
        }
        if(plen < 1) plen = 1;
        if(plen > 50000) plen = 50000;

        string txt = randStr(tlen, alpha);
        string pat;

        // With some probability, build the pattern as a substring of txt so
        // we guarantee at least one occurrence and exercise the match path.
        int mode = (int)(rng() % 3);
        if(mode == 0 && plen <= tlen){
            int start = (int)(rng() % (tlen - plen + 1));
            pat = txt.substr(start, plen);
        } else {
            pat = randStr(plen, alpha);
        }
        emit(pat, txt);
    }

    return 0;
}
