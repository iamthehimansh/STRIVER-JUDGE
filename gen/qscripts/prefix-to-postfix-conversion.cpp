// Generator for "Prefix to Postfix Conversion" (Striver)
// Builds random VALID prefix expressions within constraints, computes the
// correct postfix using the reference algorithm (stack-based, reverse scan),
// and writes 2000 JSONL cases to generated-tests/prefix-to-postfix-conversion.jsonl
//
// Constraints honored:
//   1 <= expression.length <= 10^4
//   operands: a-z, 0-9 (single char)
//   binary operators: + - * / ^
//   expression is a guaranteed-valid prefix expression
//
// Compile: clang++ -std=c++17 -O2 -w prefix-to-postfix-conversion.cpp -o gen
// Run:     ./gen > out.jsonl
#include <iostream>
#include <string>
#include <vector>
#include <stack>
#include <random>
#include <cstdint>

using namespace std;

// ---- Reference oracle: prefix -> postfix ----
static bool isOperand(char ch) {
    return ('A' <= ch && ch <= 'Z') || ('a' <= ch && ch <= 'z') ||
           ('0' <= ch && ch <= '9');
}

string prefixToPostfix(const string& s) {
    stack<string> st;
    for (int i = (int)s.size() - 1; i >= 0; i--) {
        char ch = s[i];
        if (isOperand(ch)) {
            st.push(string(1, ch));
        } else {
            // operator: in a valid prefix expr there are always 2 operands on stack
            string a = st.top(); st.pop();
            string b = st.top(); st.pop();
            st.push(a + b + ch);
        }
    }
    return st.top();
}

// ---- Random valid prefix expression builder ----
// We build a binary expression tree iteratively, capping the operator count so
// the final string length stays within maxLen. A prefix expression with k
// binary operators has exactly k+1 operands, so length = 2k+1.
static const char OPS[] = {'+', '-', '*', '/', '^'};

string buildPrefix(mt19937_64& rng, int maxOps) {
    // operandChars pool
    static const string pool =
        "abcdefghijklmnopqrstuvwxyz0123456789";
    uniform_int_distribution<int> poolDist(0, (int)pool.size() - 1);
    uniform_int_distribution<int> opDist(0, 4);

    // Decide number of operators (0..maxOps). 0 operators => single operand.
    uniform_int_distribution<int> opsCountDist(0, maxOps);
    int numOps = opsCountDist(rng);

    if (numOps == 0) {
        return string(1, pool[poolDist(rng)]);
    }

    // Build a valid prefix string using the standard "needed operands" method:
    // Start needing 1 token. Emit tokens left-to-right. When we still can place
    // operators (budget remaining) and randomly decide to, emit an operator
    // (which increases the number of operands still needed by 1). Otherwise emit
    // an operand (decreases needed by 1). Stop when needed == 0.
    string result;
    result.reserve(2 * numOps + 1);
    int opsLeft = numOps;     // operators we still must place
    int needed = 1;           // tokens still required to complete a full subtree

    // Probability of choosing an operator when allowed.
    uniform_real_distribution<double> coin(0.0, 1.0);

    while (needed > 0) {
        // remaining slots that MUST still be filled after this token if it is an
        // operand = needed-1 ; we must ensure we can still place all opsLeft.
        // An operator can be placed only if opsLeft > 0. We also must guarantee
        // that we don't run out of room: each remaining operator needs to be
        // emitted before the tree closes. The "needed" accounting naturally
        // allows it because an operator keeps needed from reaching 0.
        bool canOp = (opsLeft > 0);
        // Force operator while opsLeft equals the number of "open slots" budget
        // we have not yet committed: if needed == 1 and opsLeft > 0 we MUST emit
        // an operator now, else the expression would close prematurely without
        // using remaining operators.
        bool mustOp = (needed == 1 && opsLeft > 0);

        bool emitOp;
        if (mustOp) emitOp = true;
        else if (!canOp) emitOp = false;
        else emitOp = (coin(rng) < 0.55); // bias toward operators to grow tree

        if (emitOp) {
            result.push_back(OPS[opDist(rng)]);
            opsLeft--;
            needed += 1; // operator consumes 1 needed but adds 2 -> net +1
        } else {
            result.push_back(pool[poolDist(rng)]);
            needed -= 1;
        }
    }
    return result;
}

// JSON string escaper (for the raw prefix string used as an input value)
string jsonEscape(const string& s) {
    string out;
    out.reserve(s.size() + 2);
    for (char c : s) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n"; break;
            case '\r': out += "\\r"; break;
            case '\t': out += "\\t"; break;
            default:   out += c;     break;
        }
    }
    return out;
}

int main(int argc, char** argv) {
    uint64_t seed = 0x9E3779B97F4A7C15ULL;
    int total = 2000;
    if (argc >= 2) total = atoi(argv[1]);
    if (argc >= 3) seed = strtoull(argv[2], nullptr, 10);

    mt19937_64 rng(seed);

    // Edge / special cases first (each must be a valid prefix expr).
    vector<string> fixed = {
        "a",            // min size 1, single operand
        "z",
        "0",
        "9",
        "+ab",          // example 1
        "*+ab-cd",      // example 2
        "^a*bc",        // nowYourTurn
        "+a*+bc^de",    // testcase 3
        "*-A/BC-/AKL",  // ref example (uppercase letters are valid operands a-z? no -> use lowercase variant too)
    };
    // Note: constraints say a-z (lowercase). The uppercase ref example is from a
    // different problem variant; the algorithm handles A-Z too but to stay within
    // stated constraints we drop the uppercase one and add a lowercase analog.
    fixed.pop_back();
    fixed.push_back("*-a/bc-/akl");

    // Add a maximal-length case (length up to ~10^4). Max ops chosen so
    // 2*ops+1 <= 10000  => ops <= 4999. Build one near that limit.
    // We'll construct a near-max deterministic valid prefix explicitly below.
    {
        // 4999 operators followed by 5000 operands -> a left-leaning chain.
        // Pattern: op op op ... op  operand operand ... operand is NOT valid in
        // general; build a valid right-recursive chain: + a + a + a ... a
        // That has k operators and k+1 operands -> length 2k+1.
        int k = 4999;
        string big;
        big.reserve(2 * k + 1);
        for (int i = 0; i < k; i++) {
            big.push_back(OPS[i % 5]);
            big.push_back('a' + (i % 26));
        }
        big.push_back('z'); // final operand
        fixed.push_back(big); // length = 2*4999+1 = 9999 <= 10000
    }

    vector<string> exprs = fixed;

    // Random cases: vary maxOps to cover small and large expressions.
    // maxOps up to 4999 keeps length <= 9999.
    int remaining = total - (int)exprs.size();
    if (remaining < 0) remaining = 0;
    uniform_int_distribution<int> sizeBucket(0, 99);
    for (int i = 0; i < remaining; i++) {
        int bucket = sizeBucket(rng);
        int maxOps;
        if (bucket < 50)      maxOps = 10;     // small
        else if (bucket < 80) maxOps = 100;    // medium
        else if (bucket < 95) maxOps = 1000;   // large
        else                  maxOps = 4999;   // near-max
        exprs.push_back(buildPrefix(rng, maxOps));
    }

    // Trim to exactly `total`
    if ((int)exprs.size() > total) exprs.resize(total);

    for (const string& e : exprs) {
        string post = prefixToPostfix(e);
        // input value: raw string (matches example formatting). expected: the
        // postfix wrapped in quotes the way example outputs show ("ab+").
        // The judge strips quotes/whitespace, but we match the dataset style.
        string expected = "\"" + post + "\"";
        cout << "{\"inputs\": {\"expression\": \""
             << jsonEscape(e) << "\"}, \"expected\": \""
             << jsonEscape(expected) << "\"}\n";
    }
    return 0;
}
