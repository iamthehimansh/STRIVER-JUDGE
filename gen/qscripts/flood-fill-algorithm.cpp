// Generator + reference oracle for "flood-fill-algorithm"
// Builds 2000 test cases as JSONL.
//
// starterCpp signature:
//   vector<vector<int>> floodFill(vector<vector<int>> &image, int sr, int sc, int newColor)
// Param order (keys): image, sr, sc, newColor   (no trailing size/count params)
//
// Constraints:
//   1 <= n (rows), m (cols) <= 50
//   0 <= image[i][j], newColor < 2^16  (i.e. 0..65535)
//   0 <= sr < n ; 0 <= sc < m
//
// Output: vector<vector<int>> flattened to space-separated numbers on one line
// (judge compares leniently ignoring brackets/commas/whitespace).
//
// IMPORTANT — judge batch stdout buffer is 256 KiB (262144 bytes) for the WHOLE
// run. A correct submission whose total stdout across all 2000 cases exceeds
// that gets truncated mid-case -> false "wrong_answer". So this generator keeps
// the SUM of all "expected" outputs comfortably under ~200 KiB by sizing grids
// small. We still cover edge cases (incl. a few 50x50 grids with single-digit
// values whose flattened output is bounded).
//
// Build: clang++ -std=c++17 -O2 -w flood-fill-algorithm.cpp -o gen
// Run:   ./gen > flood-fill-algorithm.jsonl

#include <vector>
#include <queue>
#include <string>
#include <cstdio>
#include <random>
#include <utility>
using namespace std;

// ---- Reference (BFS flood fill) ----
vector<vector<int>> floodFill(vector<vector<int>>& image, int sr, int sc, int color) {
    vector<vector<int>> ans = image;
    int m = (int)image.size(), n = (int)image[0].size();
    int s = ans[sr][sc];
    if (s == color) return ans;
    queue<pair<int,int>> q;
    q.push({sr, sc});
    ans[sr][sc] = color;
    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};
    while (!q.empty()) {
        auto p = q.front(); q.pop();
        int x = p.first, y = p.second;
        for (int i = 0; i < 4; i++) {
            int nx = x + dr[i], ny = y + dc[i];
            if (nx >= 0 && nx < m && ny >= 0 && ny < n && ans[nx][ny] == s && ans[nx][ny] != color) {
                ans[nx][ny] = color;
                q.push({nx, ny});
            }
        }
    }
    return ans;
}

mt19937 rng(123456789u);
int randint(int lo, int hi) { return uniform_int_distribution<int>(lo, hi)(rng); }

string grid2str(const vector<vector<int>>& g) {
    string s = "[";
    for (size_t i = 0; i < g.size(); i++) {
        if (i) s += ", ";
        s += "[";
        for (size_t j = 0; j < g[i].size(); j++) {
            if (j) s += ", ";
            s += to_string(g[i][j]);
        }
        s += "]";
    }
    s += "]";
    return s;
}

string flat2str(const vector<vector<int>>& g) {
    string s;
    for (size_t i = 0; i < g.size(); i++)
        for (size_t j = 0; j < g[i].size(); j++) {
            if (!s.empty()) s += " ";
            s += to_string(g[i][j]);
        }
    return s;
}

// We buffer lines and track total expected-output bytes to stay < OUTPUT_BUDGET.
struct Line { string text; size_t expLen; };
vector<Line> lines;
size_t totalExp = 0;
const size_t OUTPUT_BUDGET = 200000; // < 262144 (256 KiB judge cap), with margin

void emit(const vector<vector<int>>& img, int sr, int sc, int newColor) {
    vector<vector<int>> in = img;
    vector<vector<int>> out = floodFill(in, sr, sc, newColor);
    string exp = flat2str(out);
    string line = "{\"inputs\": {\"image\": \"" + grid2str(img) +
                  "\", \"sr\": \"" + to_string(sr) +
                  "\", \"sc\": \"" + to_string(sc) +
                  "\", \"newColor\": \"" + to_string(newColor) +
                  "\"}, \"expected\": \"" + exp + "\"}";
    lines.push_back({line, exp.size()});
    totalExp += exp.size() + 1; // +1 newline
}

int main() {
    const int MAXV = (1 << 16) - 1; // 65535
    const int TARGET = 2000;

    // ---- Edge cases (kept small in OUTPUT size) ----
    emit({{0}}, 0, 0, 5);
    emit({{7}}, 0, 0, 7);
    emit({{MAXV}}, 0, 0, 0);              // max value, 1x1
    emit({{1,1,1,1,1}}, 0, 2, 9);         // single row fully filled
    emit({{2},{2},{2},{2}}, 3, 0, 8);     // single column
    emit({{1,1,1},{1,1,0},{1,0,1}}, 1, 1, 2);   // dataset example 1
    emit({{0,1,0},{1,1,0},{0,0,1}}, 2, 2, 3);   // dataset example 2
    emit({{1,1,1},{1,1,0},{1,0,1}}, 1, 1, 0);   // newColor==start -> no change
    emit({{4,4},{4,4}}, 0, 0, 4);               // no-op
    // a few MAX-SIZE 50x50 grids using single-digit values so output stays bounded
    {
        vector<vector<int>> g(50, vector<int>(50, 3));
        emit(g, 25, 25, 7);               // uniform 50x50, single-digit fill
        vector<vector<int>> c(50, vector<int>(50));
        for (int i = 0; i < 50; i++) for (int j = 0; j < 50; j++) c[i][j] = (i + j) & 1;
        emit(c, 49, 49, 5);               // checkerboard, single-digit fill, max coords
        vector<vector<int>> d(50, vector<int>(50, 0));
        emit(d, 0, 0, 9);                 // all zeros -> all nines
    }
    // 1x50 and 50x1 extremes
    {
        vector<vector<int>> r1(1, vector<int>(50, 2));
        emit(r1, 0, 49, 8);
        vector<vector<int>> c1(50, vector<int>(1, 4));
        emit(c1, 49, 0, 1);
    }

    // ---- Random cases, budget-controlled ----
    // Reserve budget for remaining cases so the SUM stays < OUTPUT_BUDGET.
    while ((int)lines.size() < TARGET) {
        int remaining = TARGET - (int)lines.size();
        // Per-case output byte budget (avg) for what's left.
        size_t budgetLeft = (totalExp < OUTPUT_BUDGET) ? (OUTPUT_BUDGET - totalExp) : 0;
        size_t perCaseBytes = budgetLeft / (size_t)remaining; // target avg bytes
        if (perCaseBytes < 6) perCaseBytes = 6;               // floor

        // Decide whether this case uses big (5-digit) or small (1-digit) values.
        // Big values cost ~6 bytes/cell; small cost ~2 bytes/cell.
        bool useBig = (randint(0, 9) == 0) && perCaseBytes > 120;
        int bytesPerCell = useBig ? 6 : 2;
        int maxCells = (int)(perCaseBytes / bytesPerCell);
        if (maxCells < 1) maxCells = 1;
        if (maxCells > 2500) maxCells = 2500; // 50x50 cap

        // Choose n,m with n*m <= maxCells and both in [1,50].
        int n, m;
        for (int attempt = 0; ; attempt++) {
            n = randint(1, 50);
            int maxM = maxCells / n;
            if (maxM < 1) { continue; }
            if (maxM > 50) maxM = 50;
            m = randint(1, maxM);
            break;
        }

        int palette;
        int mode = randint(0, 3);
        if (mode == 0) palette = 2;
        else if (mode == 1) palette = 3;
        else if (mode == 2) palette = 5;
        else palette = randint(2, 8);

        vector<int> vals;
        for (int k = 0; k < palette; k++)
            vals.push_back(useBig ? randint(0, MAXV) : randint(0, palette - 1));

        vector<vector<int>> g(n, vector<int>(m));
        for (int i = 0; i < n; i++)
            for (int j = 0; j < m; j++)
                g[i][j] = vals[randint(0, palette - 1)];

        int sr = randint(0, n - 1);
        int sc = randint(0, m - 1);
        int newColor;
        if (useBig) newColor = randint(0, MAXV);
        else newColor = randint(0, palette + 1); // sometimes equals existing color

        emit(g, sr, sc, newColor);
    }

    // ---- Write out ----
    for (auto& L : lines) {
        fputs(L.text.c_str(), stdout);
        fputc('\n', stdout);
    }
    // (debug to stderr)
    fprintf(stderr, "lines=%zu totalExpBytes=%zu (budget %zu, judge cap 262144)\n",
            lines.size(), totalExp, OUTPUT_BUDGET);
    return 0;
}
