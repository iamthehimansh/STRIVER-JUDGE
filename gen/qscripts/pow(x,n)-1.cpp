// Generator for Striver problem "Pow(x,n)" (slug: pow(x,n)-1)
//
// Method signature: double myPow(double x, int n)
// Param order: x (double), n (int)
//
// Constraints (from problem):
//   -100.0 <= x <= 100.0
//   -2^31 <= n <= 2^31 - 1   (n is an int)
//   -10^4 <= x^n <= 10^4     (the RESULT must lie in this range)
//   Either x != 0 or n > 0.
//   n is an integer.
//
// Output: value of x^n printed with EXACTLY 4 digits after the decimal point.
//
// Reference oracle: binary exponentiation done in long double, computed in a
// way that is overflow-safe for n = INT_MIN (we never call abs(INT_MIN)).
//
// Output file: one JSON object per line:
//   {"inputs": {"x": "<x>", "n": "<n>"}, "expected": "<x^n with 4 decimals>"}
//
// NOTE: keys are exactly the starterCpp parameter names in signature order: x, n.

#include <cstdio>
#include <cstdint>
#include <cstdlib>
#include <cmath>
#include <string>
#include <vector>
#include <random>
#include <algorithm>

using namespace std;

// Overflow-safe fast power in long double.
// Handles n == INT_MIN without calling abs on it.
static long double fastPow(long double x, long long n) {
    bool neg = (n < 0);
    unsigned long long m = neg ? (unsigned long long)(-(n + 1)) + 1ULL : (unsigned long long)n;
    long double res = 1.0L;
    long double base = x;
    while (m > 0) {
        if (m & 1ULL) res *= base;
        base *= base;
        m >>= 1;
    }
    if (neg) res = 1.0L / res;
    return res;
}

// Format a double exactly like printf("%.4f") would for a `double` result.
// We compute the reference in long double but cast to double first so that the
// magnitude/precision matches what a user's double-returning myPow yields.
static string fmt4(long double valLD) {
    double val = (double)valLD;
    // Normalize -0.0000 to 0.0000 to match typical printf("%.4f") which prints "-0.0000".
    // Judge is lenient on whitespace/brackets but NOT sign; printf prints -0.0000 for
    // tiny negatives. To stay safe we mirror printf behaviour directly.
    char buf[64];
    snprintf(buf, sizeof(buf), "%.4f", val);
    // Avoid "-0.0000": map it to "0.0000"
    if (string(buf) == "-0.0000") return string("0.0000");
    return string(buf);
}

// Format x for the "inputs" field. The examples show x as e.g. "2" (Case shows
// inputs x:"2"). The judge passes this string to the user's program. We emit x
// using up to a few decimals, trimming trailing zeros, but keeping it a valid
// double literal. Integers are emitted without a decimal point (like "2").
static string fmtX(double x) {
    // print with enough precision then trim
    char buf[64];
    snprintf(buf, sizeof(buf), "%.6f", x);
    string s(buf);
    // trim trailing zeros
    size_t dot = s.find('.');
    if (dot != string::npos) {
        size_t last = s.find_last_not_of('0');
        if (last == dot) last = dot - 1; // drop the dot too -> integer
        s.erase(last + 1);
    }
    if (s == "-0") s = "0";
    return s;
}

int main(int argc, char** argv) {
    long long N = 2000;
    if (argc >= 2) N = atoll(argv[1]);
    unsigned int seed = 12345u;
    if (argc >= 3) seed = (unsigned int)atoll(argv[2]);

    mt19937_64 rng(seed);

    struct Case { double x; long long n; };
    vector<Case> cases;

    auto addIfValid = [&](double x, long long n) -> bool {
        // enforce: -100 <= x <= 100
        if (x < -100.0 || x > 100.0) return false;
        // enforce n in int range
        if (n < INT32_MIN || n > INT32_MAX) return false;
        // enforce: either x != 0 or n > 0
        if (x == 0.0 && n <= 0) return false;
        // 0^0 also disallowed by above (x==0 && n==0)
        // compute result, must lie in [-1e4, 1e4]
        long double r = fastPow((long double)x, n);
        if (!isfinite((double)r)) return false;
        if (r < -10000.0L || r > 10000.0L) return false;
        cases.push_back({x, n});
        return true;
    };

    // ---- Edge / fixed cases ----
    addIfValid(2.0, 10);      // example 1 -> 1024.0000
    addIfValid(2.0, -2);      // example 2 -> 0.2500
    addIfValid(2.5, 2);       // nowYourTurn -> 6.2500
    addIfValid(1.0, INT32_MAX);   // 1
    addIfValid(1.0, INT32_MIN);   // 1
    addIfValid(-1.0, INT32_MAX);  // -1
    addIfValid(-1.0, INT32_MIN);  // 1
    addIfValid(0.0, 5);           // 0
    addIfValid(0.0, INT32_MAX);   // 0
    addIfValid(100.0, 1);         // 100
    addIfValid(100.0, 2);         // 10000  (boundary)
    addIfValid(-100.0, 2);        // 10000
    addIfValid(-100.0, 1);        // -100
    addIfValid(100.0, -2);        // 0.0001
    addIfValid(0.1, -4);          // 10000
    addIfValid(0.1, 4);           // 0.0001
    addIfValid(10.0, 4);          // 10000
    addIfValid(10.0, -4);         // 0.0001
    addIfValid(3.0, 0);           // 1
    addIfValid(-3.0, 0);          // 1
    addIfValid(5.0, 5);           // 3125
    addIfValid(2.0, 13);          // 8192
    addIfValid(2.0, -13);         // ~0.0001220703
    addIfValid(1.5, 10);          // ~57.665
    addIfValid(99.0, 1);          // 99
    addIfValid(0.0001, 1);        // small x
    addIfValid(-0.0001, 1);
    addIfValid(7.0, 4);           // 2401
    addIfValid(0.5, -13);         // 8192
    addIfValid(0.5, 13);          // ~0.000122

    // ---- Random cases ----
    // Strategy: pick a random integer exponent n (mostly small magnitude so that
    // x^n stays within [-1e4, 1e4]), and a random x; reject if out of range.
    // We bias toward producing diverse, valid samples.

    uniform_int_distribution<int> categoryD(0, 99);

    auto randXContinuous = [&](double lo, double hi) -> double {
        uniform_real_distribution<double> d(lo, hi);
        double v = d(rng);
        // round to 4 decimals so input strings are clean & reproducible
        v = round(v * 10000.0) / 10000.0;
        return v;
    };

    long long target = N;
    int guard = 0;
    while ((long long)cases.size() < target && guard < 200000000) {
        guard++;
        int cat = categoryD(rng);
        double x;
        long long n;

        if (cat < 25) {
            // small |x| around [1,3], moderate exponent so result bounded
            // choose sign of x
            double mag = randXContinuous(1.0001, 3.0);
            if ((rng() & 1ULL)) mag = -mag;
            x = mag;
            // pick exponent: x^n in [-1e4,1e4] => |n| <= log(1e4)/log(|x|)
            double maxExp = log(10000.0) / log(fabs(x));
            int lim = (int)floor(maxExp);
            if (lim < 0) lim = 0;
            uniform_int_distribution<int> nd(-lim, lim);
            n = nd(rng);
        } else if (cat < 50) {
            // |x| in [3,100], small exponent
            double mag = randXContinuous(3.0, 100.0);
            if ((rng() & 1ULL)) mag = -mag;
            x = mag;
            double maxExp = log(10000.0) / log(fabs(x));
            int lim = (int)floor(maxExp);
            if (lim < 1) lim = 1;
            uniform_int_distribution<int> nd(-lim, lim);
            n = nd(rng);
        } else if (cat < 70) {
            // |x| in (0,1) fractional, negative exponents allowed (grow toward 1e4)
            double mag = randXContinuous(0.01, 0.9999);
            if ((rng() & 1ULL)) mag = -mag;
            x = mag;
            // x^n with |x|<1: large positive n -> tiny; negative n -> grows.
            // bound: |x|^n in [-1e4,1e4]. For negative n: |x|^n = (1/|x|)^{|n|}.
            double maxExpNeg = log(10000.0) / log(1.0 / fabs(x)); // upper bound on |n| for n<0
            int limNeg = (int)floor(maxExpNeg);
            if (limNeg < 1) limNeg = 1;
            // positive n can be large (result tiny -> still within range, but value
            // underflows to ~0 quickly). Keep positive exponent modest for variety.
            uniform_int_distribution<int> nd(-limNeg, 60);
            n = nd(rng);
        } else if (cat < 80) {
            // |x| exactly near 1 -> any exponent valid, exercise huge n
            double base = randXContinuous(0.99, 1.01);
            if ((rng() & 1ULL)) base = -base;
            x = base;
            // very large |n| but result stays bounded only if |x| close enough to 1.
            // Just pick large n and rely on rejection.
            uniform_int_distribution<int> pick(0, 2);
            int p = pick(rng);
            if (p == 0) { uniform_int_distribution<int> nd(-2000000000, 2000000000); n = nd(rng); }
            else if (p == 1) { uniform_int_distribution<int> nd(-1000, 1000); n = nd(rng); }
            else { n = (rng() & 1ULL) ? INT32_MAX : INT32_MIN; }
        } else if (cat < 90) {
            // integer x values for clean outputs
            int ax = (int)(rng() % 99) + 1; // 1..99
            x = (double)ax;
            if ((rng() & 1ULL)) x = -x;
            double maxExp = log(10000.0) / log(fabs(x) < 1.0 ? 1.0001 : fabs(x));
            int lim = (int)floor(maxExp);
            if (lim < 1) lim = 1;
            uniform_int_distribution<int> nd(-lim, lim);
            n = nd(rng);
        } else {
            // x = 1 or -1 with extreme exponents
            x = (rng() & 1ULL) ? 1.0 : -1.0;
            int p = (int)(rng() % 3);
            if (p == 0) n = INT32_MAX;
            else if (p == 1) n = INT32_MIN;
            else { uniform_int_distribution<int> nd(INT32_MIN, INT32_MAX); n = nd(rng); }
        }

        // n==0 with x==0 is invalid; addIfValid handles all constraint checks.
        addIfValid(x, n);
    }

    // Trim to exactly target (edge cases first ensures determinism of those)
    if ((long long)cases.size() > target) cases.resize(target);

    // ---- Write JSONL ----
    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/pow(x,n)-1.jsonl";
    FILE* f = fopen(outPath.c_str(), "w");
    if (!f) { fprintf(stderr, "cannot open output\n"); return 1; }

    for (auto& c : cases) {
        string xs = fmtX(c.x);
        string ns = to_string(c.n);
        string exp = fmt4(fastPow((long double)c.x, c.n));
        // JSON line
        fprintf(f, "{\"inputs\": {\"x\": \"%s\", \"n\": \"%s\"}, \"expected\": \"%s\"}\n",
                xs.c_str(), ns.c_str(), exp.c_str());
    }
    fclose(f);
    fprintf(stderr, "wrote %zu cases to %s\n", cases.size(), outPath.c_str());
    return 0;
}
