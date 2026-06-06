// Generator + static test set for "Longest Repeating Character Replacement"
// Signature: int characterReplacement(string s, int k)
// Constraints: 1 <= s.length <= 1e5 ; 0 <= k <= s.length ; s only uppercase A-Z.
//
// Build:  clang++ -std=c++17 -O2 -w -o /tmp/lrcr_build/gen longest-repeating-character-replacement.cpp
// Run:    /tmp/lrcr_build/gen > "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/longest-repeating-character-replacement.jsonl"
//
// Emits 2000 JSONL lines: {"inputs":{"s":"...","k":"N"},"expected":"M"}
// (keys in starterCpp signature order: s, then k.)

#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <iostream>
#include <cstdio>
using namespace std;

// ---- reference (ground-truth oracle), from ref2 sliding-window solution ----
int characterReplacement(string s, int k) {
    int n = s.size();
    int l = 0, r = 0, maxf = 0, maxi = 0;
    int hash_[26] = {0};
    while (r < n) {
        hash_[s[r] - 'A']++;
        maxf = max(maxf, hash_[s[r] - 'A']);
        if ((r - l + 1) - maxf > k) {
            hash_[s[l] - 'A']--;
            l++;
        }
        if ((r - l + 1) - maxf <= k) maxi = max(maxi, r - l + 1);
        r++;
    }
    return maxi;
}

int main() {
    std::mt19937 rng(1234567u);

    struct Case { string s; int k; };
    vector<Case> cases;

    // ---- deterministic edge cases ----
    cases.push_back({"BAABAABBBAAA", 2}); // example 1 -> 6
    cases.push_back({"AABABBA", 1});      // example 2 -> 4
    cases.push_back({"ABAFEABBRADA", 3}); // dataset case 3
    cases.push_back({"A", 0});            // min length, k=0
    cases.push_back({"A", 1});            // k == length
    cases.push_back({"Z", 0});
    cases.push_back({"AB", 0});
    cases.push_back({"AB", 1});
    cases.push_back({"AB", 2});           // k == length
    cases.push_back({"AAAA", 0});         // all same
    cases.push_back({"AAAA", 4});
    cases.push_back({"ABCDEF", 1});       // nowYourTurn -> 2
    cases.push_back({"ABABAB", 0});
    cases.push_back({"AABBCC", 2});
    cases.push_back({string(100000, 'A'), 0});          // max length all same
    cases.push_back({string(100000, 'A'), 100000});     // k == length, all same
    {
        // alternating max-length string
        string big; big.reserve(100000);
        for (int i = 0; i < 100000; i++) big.push_back('A' + (i % 26));
        cases.push_back({big, 5});
        cases.push_back({big, 0});
        cases.push_back({big, 100000});
    }

    int target = 2000;

    // helper alphabet-size distributions to create varied structure
    auto makeRandom = [&](int n, int alpha) -> string {
        string s; s.reserve(n);
        std::uniform_int_distribution<int> letter(0, alpha - 1);
        for (int i = 0; i < n; i++) s.push_back('A' + letter(rng));
        return s;
    };

    while ((int)cases.size() < target) {
        // pick a length: bias toward small but include large.
        int n;
        int bucket = rng() % 10;
        if (bucket == 0)      n = 1 + (int)(rng() % 5);          // tiny
        else if (bucket == 1) n = 1 + (int)(rng() % 50);         // small
        else if (bucket <= 5) n = 1 + (int)(rng() % 2000);       // medium
        else if (bucket <= 8) n = 1 + (int)(rng() % 50000);      // large
        else                  n = 90000 + (int)(rng() % 10001);  // near-max (90000..100000)

        // alphabet size 1..26 controls repetition structure
        int alpha = 1 + (int)(rng() % 26);
        string s = makeRandom(n, alpha);

        // k in [0, n]  (constraint: 0 <= k <= s.length)
        int k;
        int kb = rng() % 6;
        if (kb == 0) k = 0;
        else if (kb == 1) k = n;                 // k == length
        else if (kb == 2) k = (int)(rng() % 4);  // small k
        else k = (int)(rng() % (n + 1));         // any valid k
        if (k > n) k = n;                        // enforce constraint 0 <= k <= s.length
        cases.push_back({std::move(s), k});
    }

    // JSON string escaper for s (s only contains A-Z so no escaping needed,
    // but keep it safe in case of edge inputs).
    auto esc = [](const string& s) -> string {
        string out; out.reserve(s.size() + 2);
        for (char c : s) {
            if (c == '"' || c == '\\') { out.push_back('\\'); out.push_back(c); }
            else out.push_back(c);
        }
        return out;
    };

    string outbuf;
    outbuf.reserve(1 << 20);
    char numbuf[32];
    for (auto& c : cases) {
        int ans = characterReplacement(c.s, c.k);
        outbuf += "{\"inputs\":{\"s\":\"";
        outbuf += esc(c.s);
        outbuf += "\",\"k\":\"";
        snprintf(numbuf, sizeof(numbuf), "%d", c.k);
        outbuf += numbuf;
        outbuf += "\"},\"expected\":\"";
        snprintf(numbuf, sizeof(numbuf), "%d", ans);
        outbuf += numbuf;
        outbuf += "\"}\n";
    }
    fputs(outbuf.c_str(), stdout);
    return 0;
}
