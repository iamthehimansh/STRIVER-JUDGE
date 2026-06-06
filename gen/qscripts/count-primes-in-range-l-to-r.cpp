// Generator for "Count primes in range L to R"
// Signature: vector<int> primesInRange(vector<vector<int>>& queries)
// Constraints: 1 <= n <= 1e5 ; 1 <= queries[i][0] <= queries[i][1] <= 1e5
//
// Builds a sieve up to 1e5 with a prefix count of primes, then for each query
// [L,R] returns (count primes <= R) - (count primes <= L-1).
//
// Writes generated-tests/count-primes-in-range-l-to-r.jsonl
// Each line: {"inputs": {"queries": "[[L,R],...]"}, "expected": "[c1,c2,...]"}

#include <iostream>
#include <vector>
#include <random>
#include <string>
#include <fstream>
using namespace std;

const int MAXV = 100000; // 1e5

vector<int> prefixPrimes; // prefixPrimes[x] = number of primes in [2..x]

void buildSieve() {
    vector<char> isPrime(MAXV + 1, 1);
    isPrime[0] = isPrime[1] = 0;
    for (long long i = 2; i <= MAXV; i++) {
        if (isPrime[i]) {
            for (long long j = i * i; j <= MAXV; j += i) isPrime[j] = 0;
        }
    }
    prefixPrimes.assign(MAXV + 1, 0);
    for (int x = 1; x <= MAXV; x++)
        prefixPrimes[x] = prefixPrimes[x - 1] + (isPrime[x] ? 1 : 0);
}

// Reference solution
vector<int> primesInRange(vector<vector<int>>& queries) {
    vector<int> res;
    res.reserve(queries.size());
    for (auto& q : queries) {
        int L = q[0], R = q[1];
        res.push_back(prefixPrimes[R] - prefixPrimes[L - 1]);
    }
    return res;
}

string queriesToStr(const vector<vector<int>>& qs) {
    string s = "[";
    for (size_t i = 0; i < qs.size(); i++) {
        if (i) s += ", ";
        s += "[" + to_string(qs[i][0]) + ", " + to_string(qs[i][1]) + "]";
    }
    s += "]";
    return s;
}

string vecToStr(const vector<int>& v) {
    string s = "[";
    for (size_t i = 0; i < v.size(); i++) {
        if (i) s += ", ";
        s += to_string(v[i]);
    }
    s += "]";
    return s;
}

int main(int argc, char** argv) {
    buildSieve();

    // self-test on dataset examples
    {
        vector<vector<int>> q1 = {{2,5},{4,7}};
        vector<vector<int>> q2 = {{1,7},{3,7}};
        vector<vector<int>> q3 = {{1,10},{10,20}};
        vector<int> a1 = primesInRange(q1);
        vector<int> a2 = primesInRange(q2);
        vector<int> a3 = primesInRange(q3);
        if (vecToStr(a1) != "[3, 2]" || vecToStr(a2) != "[4, 3]") {
            cerr << "SELFTEST FAILED: " << vecToStr(a1) << " " << vecToStr(a2) << "\n";
            return 1;
        }
        // a3 should be [4, 4] (primes 1..10: 2,3,5,7 ; 10..20: 11,13,17,19)
        cerr << "selftest ok; nowYourTurn [1,10],[10,20] -> " << vecToStr(a3) << "\n";
    }

    int N = 2000;
    if (argc > 1) N = atoi(argv[1]);

    string outPath = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/count-primes-in-range-l-to-r.jsonl";
    ofstream out(outPath);
    if (!out) { cerr << "cannot open output\n"; return 1; }

    mt19937 rng(20240606);

    auto emit = [&](vector<vector<int>>& qs) {
        vector<int> ans = primesInRange(qs);
        out << "{\"inputs\": {\"queries\": \"" << queriesToStr(qs)
            << "\"}, \"expected\": \"" << vecToStr(ans) << "\"}\n";
    };

    int produced = 0;

    // --- deterministic edge cases first ---
    {
        // single query, minimal range [1,1] -> 0 primes
        vector<vector<int>> q = {{1,1}}; emit(q); produced++;
        // [2,2] -> 1
        q = {{2,2}}; emit(q); produced++;
        // [1, MAXV] full range
        q = {{1, MAXV}}; emit(q); produced++;
        // [MAXV, MAXV]
        q = {{MAXV, MAXV}}; emit(q); produced++;
        // dataset examples
        q = {{2,5},{4,7}}; emit(q); produced++;
        q = {{1,7},{3,7}}; emit(q); produced++;
        q = {{1,10},{10,20}}; emit(q); produced++;
        q = {{2,10},{3,10},{4,10}}; emit(q); produced++;
        // many tiny ranges
        q.clear();
        for (int i = 1; i <= 50; i++) q.push_back({i, i});
        emit(q); produced++;
        // ranges hugging MAXV
        q = {{MAXV-100, MAXV},{MAXV-1, MAXV},{99990, 100000}}; emit(q); produced++;
    }

    // --- random cases ---
    uniform_int_distribution<int> nDist(1, 50);        // number of queries per test (keep modest)
    uniform_int_distribution<int> valDist(1, MAXV);

    // occasionally larger n
    uniform_int_distribution<int> bigN(50, 1000);
    uniform_int_distribution<int> coin(0, 9);

    while (produced < N) {
        int n;
        if (coin(rng) == 0) n = bigN(rng); else n = nDist(rng);
        vector<vector<int>> qs;
        qs.reserve(n);
        for (int i = 0; i < n; i++) {
            int a = valDist(rng);
            int b = valDist(rng);
            if (a > b) swap(a, b);
            qs.push_back({a, b});
        }
        emit(qs);
        produced++;
    }

    out.close();
    cerr << "wrote " << produced << " cases to " << outPath << "\n";
    return 0;
}
