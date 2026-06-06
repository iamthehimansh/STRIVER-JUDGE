// Generator for Striver problem "Pow(x, n)" (slug: pow(x,n))
// Method signature: double myPow(double x, int n)
// Constraints:
//   -100.0 <= x <= 100.0
//   -2^31 <= n <= 2^31 - 1
//   -10^4 <= x^n <= 10^4
//   Either x is not zero or n > 0  (i.e. x==0 only allowed when n>0)
// Output: x^n printed with exactly 4 digits after the decimal point.
//
// This program:
//   * builds a correct reference (binary exponentiation, INT_MIN-safe)
//   * generates ~2000 random+edge inputs strictly within constraints
//   * writes one JSON object per line to the .jsonl path.
//
// Keys are in starterCpp signature order: "x" then "n".
//
// Build: clang++ -std=c++17 -O2 -w -o gen "pow(x,n).cpp"
// Run:   ./gen > "pow(x,n).jsonl"

#include <cstdio>
#include <cstdint>
#include <cmath>
#include <string>
#include <vector>
#include <random>
#include <set>
#include <utility>

using namespace std;

// ----- Reference oracle (INT_MIN-safe) -----
// Computes x^n following the problem's semantics. n is read as the C++ int the
// judge would pass, but we widen to long long internally so abs(INT_MIN) works.
static double myPow(double x, int n_int) {
    long long n = (long long)n_int;
    bool neg = (n < 0);
    long long m = neg ? -n : n;        // safe even for INT_MIN
    double res = 1.0;
    double base = x;
    while (m > 0) {
        if (m & 1LL) res *= base;
        base *= base;
        m >>= 1;
    }
    if (neg) res = 1.0 / res;
    return res;
}

// Format a double with exactly 4 decimals; normalize "-0.0000" -> "0.0000".
static string fmt4(double v) {
    char buf[64];
    snprintf(buf, sizeof(buf), "%.4f", v);
    string s(buf);
    if (s == "-0.0000") s = "0.0000";
    return s;
}

// Format x for the "inputs" field. The dataset stores x like the examples
// (e.g. "2", "2.5"). We print a clean decimal: integers without a fractional
// part show as plain ints, otherwise trim trailing zeros (keep at least one dp).
static string fmtX(double x) {
    if (x == (long long)x) {
        return to_string((long long)x);
    }
    char buf[64];
    snprintf(buf, sizeof(buf), "%.6f", x);
    string s(buf);
    // trim trailing zeros but keep at least one digit after the dot
    size_t dot = s.find('.');
    size_t last = s.find_last_not_of('0');
    if (last > dot) s.erase(last + 1);
    else s.erase(dot + 2); // keep one zero
    return s;
}

int main() {
    mt19937_64 rng(12345);

    // Collect (x, n) pairs as a set to avoid duplicates.
    set<pair<long long, long long>> seen; // key: (x*1e6 rounded, n)
    vector<pair<double,int>> cases;

    auto in_xn_bounds = [](double x, int n) -> bool {
        double r = myPow(x, n);
        if (!isfinite(r)) return false;
        return r >= -10000.0 && r <= 10000.0;
    };

    auto valid = [&](double x, int n) -> bool {
        if (x < -100.0 || x > 100.0) return false;
        // either x != 0 or n > 0
        if (x == 0.0 && n <= 0) return false;
        return in_xn_bounds(x, n);
    };

    auto add = [&](double x, int n) -> bool {
        if (!valid(x, n)) return false;
        long long xk = (long long)llround(x * 1e6);
        pair<long long,long long> key{xk, (long long)n};
        if (seen.count(key)) return false;
        seen.insert(key);
        cases.push_back({x, n});
        return true;
    };

    // ---- Edge / hand-picked cases ----
    add(2.0, 10);     // 1024.0000  (example 1)
    add(2.0, -2);     // 0.2500     (example 2)
    add(2.5, 2);      // 6.2500     (nowYourTurn)
    add(1.0, 2147483647);   // 1.0000  (n = INT_MAX)
    add(1.0, -2147483647);  // 1.0000
    add(-1.0, 2147483647);  // -1.0000
    add(-1.0, -2147483647); // -1.0000
    add(0.0, 5);      // 0.0000 (x==0 allowed since n>0)
    add(0.0, 1);
    add(5.0, 0);      // 1.0000 (n==0)
    add(100.0, 0);
    add(-100.0, 0);
    add(100.0, 1);    // 100.0000
    add(100.0, 2);    // 10000.0000 (boundary x^n == 1e4)
    add(-100.0, 2);   // 10000.0000
    add(-10.0, 4);    // 10000.0000 boundary
    add(10.0, 4);     // 10000.0000 boundary
    add(0.5, -10);    // 1024.0000
    add(0.1, -4);     // 10000.0000 boundary
    add(7.0, -3);
    add(-2.0, 3);     // -8.0000
    add(-2.0, -3);    // -0.1250
    add(1.0, 0);
    add(-1.0, 0);
    add(3.0, 0);

    // n == INT_MIN is in range only for |x|<=1 essentially; x=1 / x=-1 give finite.
    add(1.0, (int)(-2147483647 - 1)); // INT_MIN -> 1.0000
    add(-1.0, (int)(-2147483647 - 1)); // INT_MIN (even) -> 1.0000

    // ---- Random generation ----
    // Distributions:
    //   group A: |x| > 1, choose small n so x^n stays within 1e4
    //   group B: |x| < 1 (including 0), choose n (possibly large negative) within bounds
    //   group C: x exactly == 1 or -1, allow huge |n|
    //   group D: integer x with small magnitude
    uniform_real_distribution<double> signPick(0.0, 1.0);

    auto rand_sign = [&]() -> double { return (signPick(rng) < 0.5) ? -1.0 : 1.0; };

    // Helper: given x, find the max |n| (call it cap) such that |x|^cap <= 1e4.
    auto maxAbsN = [](double x) -> long long {
        double ax = fabs(x);
        if (ax <= 1.0) return 2000000000LL; // |x|<=1 never explodes for positive n
        // ax^cap <= 1e4  -> cap <= log(1e4)/log(ax)
        double cap = log(10000.0) / log(ax);
        long long c = (long long)floor(cap);
        if (c < 0) c = 0;
        return c;
    };
    // For |x| < 1 and negative n: |x|^n = (1/|x|)^|n| can explode. Cap |n| there too.
    auto maxAbsNegN = [](double x) -> long long {
        double ax = fabs(x);
        if (ax >= 1.0) return 2000000000LL;
        if (ax == 0.0) return 0; // x==0, negative n not allowed anyway
        double inv = 1.0 / ax;
        if (inv <= 1.0) return 2000000000LL;
        double cap = log(10000.0) / log(inv);
        long long c = (long long)floor(cap);
        if (c < 0) c = 0;
        return c;
    };

    int target = 2000;
    int guard = 0;
    uniform_int_distribution<int> groupPick(0, 99);

    while ((int)cases.size() < target && guard < 20000000) {
        guard++;
        int g = groupPick(rng);
        double x;
        int n;

        if (g < 35) {
            // group A: |x| in (1, 100], small n
            uniform_real_distribution<double> mag(1.0001, 100.0);
            double ax = mag(rng);
            // round to a few decimals to keep values clean-ish
            uniform_int_distribution<int> dp(0, 4);
            int d = dp(rng);
            double scale = pow(10.0, d);
            ax = round(ax * scale) / scale;
            if (ax < 1.0001) ax = 1.0001;
            if (ax > 100.0) ax = 100.0;
            x = ax * rand_sign();
            long long capPos = maxAbsN(x);   // for positive n
            // negative n with |x|>1 always shrinks (fine), but result tiny -> still in bounds
            long long capNeg = 2000000000LL; // negative exponent with |x|>1 -> |result|<1
            // choose n in [-capNeg, capPos]
            if (capPos < 0) capPos = 0;
            long long lo = -capNeg, hi = capPos;
            // clamp to int range
            if (lo < -2147483648LL) lo = -2147483648LL;
            if (hi > 2147483647LL) hi = 2147483647LL;
            if (hi < lo) hi = lo;
            uniform_int_distribution<long long> nd(lo, hi);
            n = (int)nd(rng);
        } else if (g < 70) {
            // group B: |x| in [0,1), n can be large positive, negative limited
            uniform_real_distribution<double> mag(0.0, 0.9999);
            uniform_int_distribution<int> dp(1, 5);
            int d = dp(rng);
            double scale = pow(10.0, d);
            double ax = round(mag(rng) * scale) / scale;
            if (ax >= 1.0) ax = 0.9999;
            // allow exact zero sometimes
            uniform_int_distribution<int> zchance(0, 19);
            if (zchance(rng) == 0) ax = 0.0;
            x = (ax == 0.0) ? 0.0 : ax * rand_sign();
            long long capNeg = maxAbsNegN(x); // limit |negative n|
            long long capPos = 2000000000LL;  // positive n shrinks toward 0 -> fine
            long long lo = -capNeg, hi = capPos;
            if (x == 0.0) lo = 1; // x==0 requires n>0
            if (lo < -2147483648LL) lo = -2147483648LL;
            if (hi > 2147483647LL) hi = 2147483647LL;
            if (hi < lo) hi = lo;
            uniform_int_distribution<long long> nd(lo, hi);
            n = (int)nd(rng);
            if (x == 0.0 && n <= 0) n = 1;
        } else if (g < 80) {
            // group C: x == 1 or -1, huge |n|
            x = rand_sign(); // 1 or -1
            uniform_int_distribution<long long> nd(-2147483648LL, 2147483647LL);
            n = (int)nd(rng);
        } else {
            // group D: small integer x, small n
            uniform_int_distribution<int> xd(-12, 12);
            int xi = xd(rng);
            x = (double)xi;
            long long cap = maxAbsN(x);
            if (xi == 0) {
                uniform_int_distribution<int> nd(1, 30); // n>0 required
                n = nd(rng);
            } else {
                long long lo = -cap, hi = cap;
                if (abs(xi) == 1) { lo = -2147483648LL; hi = 2147483647LL; }
                if (lo < -2147483648LL) lo = -2147483648LL;
                if (hi > 2147483647LL) hi = 2147483647LL;
                if (hi < lo) hi = lo;
                uniform_int_distribution<long long> nd(lo, hi);
                n = (int)nd(rng);
            }
        }
        add(x, n);
    }

    // ---- Emit JSONL ----
    for (auto &c : cases) {
        double x = c.first;
        int n = c.second;
        double r = myPow(x, n);
        string xs = fmtX(x);
        string ns = to_string((long long)n);
        string es = fmt4(r);
        // JSON line: keys in signature order -> x then n
        printf("{\"inputs\": {\"x\": \"%s\", \"n\": \"%s\"}, \"expected\": \"%s\"}\n",
               xs.c_str(), ns.c_str(), es.c_str());
    }
    return 0;
}
