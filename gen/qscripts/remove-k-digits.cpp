#include <iostream>
#include <string>
#include <stack>
#include <algorithm>
#include <vector>
#include <random>
#include <fstream>
using namespace std;

class Solution {
public:
    string removeKdigits(string nums, int k) {
        int n = nums.size();
        stack<char> st;
        for (int i = 0; i < n; i++) {
            while (!st.empty() && k > 0 && st.top() > nums[i]) {
                st.pop();
                k--;
            }
            st.push(nums[i]);
        }
        while (k > 0) { st.pop(); k--; }
        if (st.empty()) return "0";
        string ans = "";
        while (!st.empty()) { ans += st.top(); st.pop(); }
        while (!ans.empty() && ans.back() == '0') ans.pop_back();
        if (ans.empty()) return "0";
        reverse(ans.begin(), ans.end());
        return ans;
    }
};

mt19937 rng(987654321u);

// Build a valid nums string of length L: digits only, no leading zeros
// (except the single "0"). 1 <= L.
string makeNums(int L) {
    uniform_int_distribution<int> d09(0, 9);
    if (L == 1) {
        // can be "0".."9"
        return string(1, char('0' + d09(rng)));
    }
    string s;
    uniform_int_distribution<int> d19(1, 9);
    s += char('0' + d19(rng)); // first digit non-zero
    for (int i = 1; i < L; i++) s += char('0' + d09(rng));
    return s;
}

int main(int argc, char** argv) {
    int target = 2000;
    if (argc > 1) target = atoi(argv[1]);

    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/remove-k-digits.jsonl";
    if (argc > 2) outPath = argv[2];

    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    Solution sol;

    vector<pair<string,int>> cases; // (nums, k)

    // ---- Edge cases ----
    // length 1, k=1 (must become "0")
    for (int d = 0; d <= 9; d++) cases.push_back({string(1, char('0'+d)), 1});
    // example cases
    cases.push_back({"541892", 2});
    cases.push_back({"1002991", 3});
    cases.push_back({"10", 2});
    cases.push_back({"1432219", 3});
    // k == nums.length for various sizes -> always "0"
    cases.push_back({"9", 1});
    cases.push_back({"10", 2});
    cases.push_back({"100", 3});
    cases.push_back({"12345", 5});
    cases.push_back({"98765", 5});
    // all same digits
    cases.push_back({"1111111111", 4});
    cases.push_back({"9999999999", 3});
    // strictly increasing -> remove from the end
    cases.push_back({"123456789", 4});
    // strictly decreasing -> remove from the front
    cases.push_back({"987654321", 4});
    // leading-zero producing
    cases.push_back({"100200", 1});
    cases.push_back({"10001", 1});
    cases.push_back({"200", 1});
    // large all-nine string, large k (small but within bounds)
    {
        string big(10000, '9');
        cases.push_back({big, 9999});
        cases.push_back({big, 5000});
        cases.push_back({big, 1});
    }
    // large with leading non-zero, rest zeros -> becomes 0
    {
        string s = "1"; s += string(9999, '0');
        cases.push_back({s, 1});      // remove the 1 -> "0"
        cases.push_back({s, 10000});  // remove everything -> "0"
    }

    // ---- Random cases (small lengths, exhaustive variety) ----
    // small lengths 1..6 with all valid k
    for (int L = 1; L <= 6; L++) {
        for (int rep = 0; rep < 40; rep++) {
            string s = makeNums(L);
            uniform_int_distribution<int> dk(1, L);
            int k = dk(rng);
            cases.push_back({s, k});
        }
    }

    // ---- Random cases: medium lengths ----
    {
        uniform_int_distribution<int> dL(7, 50);
        while ((int)cases.size() < 700) {
            int L = dL(rng);
            string s = makeNums(L);
            uniform_int_distribution<int> dk(1, L);
            int k = dk(rng);
            cases.push_back({s, k});
        }
    }

    // ---- Random cases: larger lengths ----
    {
        uniform_int_distribution<int> dL(50, 1000);
        while ((int)cases.size() < 1500) {
            int L = dL(rng);
            string s = makeNums(L);
            uniform_int_distribution<int> dk(1, L);
            int k = dk(rng);
            cases.push_back({s, k});
        }
    }

    // ---- Random cases: very large lengths up to 10^4 ----
    {
        uniform_int_distribution<int> dL(1000, 10000);
        while ((int)cases.size() < target) {
            int L = dL(rng);
            string s = makeNums(L);
            uniform_int_distribution<int> dk(1, L);
            int k = dk(rng);
            cases.push_back({s, k});
        }
    }

    // Trim to exactly target if we overshot
    if ((int)cases.size() > target) cases.resize(target);

    for (auto& c : cases) {
        string nums = c.first;
        int k = c.second;
        // Safety assert constraints: 1 <= k <= nums.length <= 1e4, digits only, no leading zeros (except "0")
        // (kept implicit; generation guarantees it)
        string expected = sol.removeKdigits(nums, k);
        // JSON line. nums is raw string per examples; expected raw string.
        out << "{\"inputs\": {\"nums\": \"" << nums << "\", \"k\": \"" << k
            << "\"}, \"expected\": \"" << expected << "\"}\n";
    }

    out.close();
    cerr << "wrote " << cases.size() << " cases to " << outPath << "\n";
    return 0;
}
