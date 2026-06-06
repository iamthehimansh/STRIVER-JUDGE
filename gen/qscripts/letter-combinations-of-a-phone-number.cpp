// Generator for "Letter Combinations of a Phone Number"
// Constraints: 1 <= digits.length <= 4, each digit in [2,9].
// Output line format: {"inputs": {"digits": "<str>"}, "expected": "<combos>"}
// expected is the list of combinations joined by spaces (judge compares leniently,
// ignoring brackets/commas/whitespace/quotes).
//
// Build:  clang++ -std=c++17 -O2 -w letter-combinations-of-a-phone-number.cpp -o gen
// Run:    ./gen > /path/to/letter-combinations-of-a-phone-number.jsonl
#include <iostream>
#include <vector>
#include <string>
#include <set>
#include <random>
using namespace std;

// ---- Reference solution (from strivers-a2z-ref) ----
void solve(int index, const string& digits, string& temp, vector<string>& ans, vector<string>& mp) {
    if (index == (int)digits.size()) {
        ans.push_back(temp);
        return;
    }
    int num = digits[index] - '0';
    for (int i = 0; i < (int)mp[num].size(); i++) {
        temp.push_back(mp[num][i]);
        solve(index + 1, digits, temp, ans, mp);
        temp.pop_back();
    }
}
vector<string> letterCombinations(string digits) {
    if (digits.empty()) return {};
    vector<string> mp{"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};
    string temp = "";
    vector<string> ans;
    solve(0, digits, temp, ans, mp);
    return ans;
}
// ----------------------------------------------------

int main(int argc, char** argv) {
    int N = 2000;
    if (argc > 1) N = atoi(argv[1]);

    mt19937 rng(987654321u);

    // Build complete set of edge / coverage cases first, then fill with random.
    set<string> seen;
    vector<string> inputs;

    auto addInput = [&](const string& d) {
        if (seen.insert(d).second) inputs.push_back(d);
    };

    // All single digits (min length, every mapping including 7 and 9 with 4 letters)
    for (char c = '2'; c <= '9'; ++c) addInput(string(1, c));

    // Some explicit examples
    addInput("34");
    addInput("3");
    addInput("23");

    // All length-2 combos (8*8 = 64) for thorough coverage
    for (char a = '2'; a <= '9'; ++a)
        for (char b = '2'; b <= '9'; ++b)
            addInput(string{a, b});

    // Extremes: max length all-min digit, all-max digit
    addInput("2222");
    addInput("9999");
    addInput("7777"); // largest output (4^4 = 256)
    addInput("7979");

    // Fill remainder with random valid strings of length 1..4
    uniform_int_distribution<int> lenDist(1, 4);
    uniform_int_distribution<int> digDist(2, 9);
    while ((int)inputs.size() < N) {
        int len = lenDist(rng);
        string d;
        for (int i = 0; i < len; ++i) d.push_back(char('0' + digDist(rng)));
        addInput(d);
    }
    // Trim to exactly N if we overshot via dedup logic (we won't, addInput is gated by size only on random).
    if ((int)inputs.size() > N) inputs.resize(N);

    for (const string& d : inputs) {
        vector<string> res = letterCombinations(d);
        // expected: combinations joined by single space
        string expected;
        for (size_t i = 0; i < res.size(); ++i) {
            if (i) expected.push_back(' ');
            expected += res[i];
        }
        // digits has no special JSON chars (only [2-9]); expected has no special chars either.
        cout << "{\"inputs\": {\"digits\": \"" << d << "\"}, \"expected\": \"" << expected << "\"}\n";
    }
    return 0;
}
