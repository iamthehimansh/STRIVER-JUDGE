#!/usr/bin/env python3
"""
Test-case generator for Striver problem
"Find Pairs with Given Sum in Doubly Linked List"
(slug: find-pairs-with-given-sum-in-doubly-linked-list).

Signature:  vector<vector<int>> findPairsWithGivenSum(ListNode* head, int target)

Constraints:
  0 <= number of nodes <= 10^5
  1 <= Node.val <= 10^5
  1 <= target <= 10^5
  The linked list is sorted in STRICTLY increasing order (distinct positive values).

IMPORTANT about the judge:
  The judge's ListNode struct has ONLY {int val; ListNode* next;} -- there is NO
  `prev` pointer (the problem's starter comments out a ListNode with prev, but the
  judge replaces it with a forward-only node). So the reference oracle here does
  NOT use ->prev: it collects values from the forward list into a vector and runs
  the standard two-pointer scan over indices. This matches exactly what a correct
  submitted `class Solution` must do.

Input format:
  head   -> the node values as an array, e.g. "[1, 2, 4, 5]"  (judge rdList)
  target -> int, e.g. "7"

Output format:
  vector<vector<int>> printed like the dataset examples: "[[1, 6], [2, 5]]".
  Empty result is "[]". The judge compares leniently (ignores brackets/commas/
  whitespace) and flattens the 2D output to space-separated tokens, so this
  canonical form matches a correct submission.
"""
import json
import os
import random
import subprocess
import tempfile

PROJECT = "/Users/iamthehimansh/Downloads/stiver'sdata"
OUT_PATH = os.path.join(PROJECT, "generated-tests",
                        "find-pairs-with-given-sum-in-doubly-linked-list.jsonl")
N_CASES = 2000
SEED = 20260606

# Reference oracle. Mirrors the judge's forward-only ListNode (val, next).
# Reads many cases from stdin: each line is "<head-array>\t<target>".
CPP_REF = r'''
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

struct ListNode {
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {}
};

class Solution {
public:
    vector<vector<int>> findPairsWithGivenSum(ListNode* head, int target) {
        // forward-only: gather values (list is sorted ascending, distinct)
        vector<int> a;
        for (ListNode* c = head; c; c = c->next) a.push_back(c->val);
        vector<vector<int>> ans;
        int i = 0, j = (int)a.size() - 1;
        while (i < j) {
            int sum = a[i] + a[j];
            if (sum == target) {
                ans.push_back({a[i], a[j]});
                i++; j--;
            } else if (sum < target) {
                i++;
            } else {
                j--;
            }
        }
        return ans;
    }
};

static ListNode* buildList(const string& s) {
    // s is a (possibly bracketed) list of ints
    ListNode dummy(0); ListNode* cur = &dummy;
    string num; bool inNum = false; bool neg = false;
    auto flush = [&]() {
        if (inNum) {
            int v = stoi(num);
            if (neg) v = -v;
            cur->next = new ListNode(v); cur = cur->next;
            num.clear(); inNum = false; neg = false;
        }
    };
    for (char c : s) {
        if (c == '-') { neg = true; }
        else if (c >= '0' && c <= '9') { num += c; inNum = true; }
        else flush();
    }
    flush();
    return dummy.next;
}

int main() {
    string line;
    while (getline(cin, line)) {
        if (line.empty()) continue;
        // split on tab: field0 = head array, field1 = target
        size_t tab = line.find('\t');
        string headStr = (tab == string::npos) ? line : line.substr(0, tab);
        string tgtStr  = (tab == string::npos) ? "0"  : line.substr(tab + 1);
        ListNode* head = buildList(headStr);
        int target = stoi(tgtStr);
        Solution sol;
        vector<vector<int>> res = sol.findPairsWithGivenSum(head, target);
        string out = "[";
        for (size_t a = 0; a < res.size(); a++) {
            if (a) out += ", ";
            out += "[";
            for (size_t b = 0; b < res[a].size(); b++) {
                if (b) out += ", ";
                out += to_string(res[a][b]);
            }
            out += "]";
        }
        out += "]";
        cout << out << "\n";
    }
    return 0;
}
'''

VMIN, VMAX = 1, 100000      # Node.val range
TMIN, TMAX = 1, 100000      # target range
NMAX = 100000               # max nodes


def build_ref(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(CPP_REF)
    subprocess.run(["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
                   check=True)
    return binp


def fmt_list(vals):
    return "[" + ", ".join(str(x) for x in vals) + "]"


def run_ref_batch(binp, cases):
    """cases: list of (vals, target) -> list of expected strings."""
    lines = []
    for vals, tgt in cases:
        lines.append(fmt_list(vals) + "\t" + str(tgt))
    p = subprocess.run([binp], input="\n".join(lines) + "\n",
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("ref failed: " + p.stderr)
    out = p.stdout.splitlines()
    if len(out) != len(cases):
        raise RuntimeError(f"expected {len(cases)} outputs, got {len(out)}")
    return [o.strip() for o in out]


def sorted_distinct(vals):
    """Return a strictly increasing distinct list within [VMIN, VMAX]."""
    s = sorted(set(v for v in vals if VMIN <= v <= VMAX))
    return s


# The judge runs ALL cases in a single batch process and caps that process's
# TOTAL stdout at 256 KB (scripts/judge_exec.py OUT_CAP). With 2000 cases that
# leaves a small budget per case, so a case emitting thousands of pairs would
# blow the cumulative cap and cause later cases to be truncated/miscompared.
# Cap the number of result pairs per case to keep total output well under 256 KB
# while still exercising the full constraint ranges (large lists, big values).
MAX_PAIRS = 12


def count_pairs(vals, t):
    """How many pairs (a,b), a<b, a+b==t exist in the sorted distinct list."""
    i, j = 0, len(vals) - 1
    cnt = 0
    while i < j:
        s = vals[i] + vals[j]
        if s == t:
            cnt += 1
            i += 1
            j -= 1
        elif s < t:
            i += 1
        else:
            j -= 1
    return cnt


def sample_distinct(n, lo, hi, rng):
    """Sample n distinct ints in [lo, hi], sorted ascending."""
    hi = min(hi, VMAX)
    lo = max(lo, VMIN)
    span = hi - lo + 1
    n = min(n, span)
    if n <= 0:
        return []
    if n >= span:
        return list(range(lo, lo + n))
    vals = rng.sample(range(lo, hi + 1), n)
    vals.sort()
    return vals


def gen_case(rng):
    """Generate (vals_sorted_distinct, target) strictly within constraints."""
    mode = rng.random()

    if mode < 0.06:
        # empty / tiny lists (edge: 0 or 1 node)
        n = rng.randint(0, 2)
        vals = sample_distinct(n, 1, 50, rng)
    elif mode < 0.35:
        # small list, small value range -> guarantees pairs are likely
        n = rng.randint(2, 30)
        hi = rng.choice([20, 50, 100, 500])
        vals = sample_distinct(n, 1, hi, rng)
    elif mode < 0.55:
        # medium list, medium range
        n = rng.randint(10, 300)
        hi = rng.choice([200, 1000, 5000, 20000])
        vals = sample_distinct(n, 1, hi, rng)
    elif mode < 0.70:
        # full value range, modest size (pairs rarer)
        n = rng.randint(2, 200)
        vals = sample_distinct(n, 1, VMAX, rng)
    elif mode < 0.82:
        # constructed: ensure several valid pairs for a chosen target
        target_hi = rng.randint(4, VMAX)
        npairs = rng.randint(1, 8)
        vals = set()
        for _ in range(npairs):
            a = rng.randint(1, target_hi - 1)
            b = target_hi - a
            if 1 <= a <= VMAX and 1 <= b <= VMAX and a != b:
                vals.add(a); vals.add(b)
        # add noise
        for _ in range(rng.randint(0, 30)):
            vals.add(rng.randint(1, VMAX))
        vals = sorted(vals)
        return vals, target_hi
    elif mode < 0.90:
        # contiguous run (max density of pairs)
        n = rng.randint(2, 1000)
        start = rng.randint(1, max(1, VMAX - n))
        vals = list(range(start, start + n))
    else:
        # large stress lists within bounds
        n = rng.choice([2000, 5000, 20000, 50000, 100000])
        n = min(n, VMAX)
        if rng.random() < 0.5:
            vals = list(range(1, n + 1))          # 1..n contiguous
        else:
            vals = sample_distinct(n, 1, VMAX, rng)

    vals = sorted_distinct(vals)
    # choose a target in valid range; bias toward sums that can occur
    if vals and rng.random() < 0.75 and len(vals) >= 2:
        # pick target equal to sum of two existing values sometimes
        if rng.random() < 0.6:
            i = rng.randrange(len(vals))
            j = rng.randrange(len(vals))
            s = vals[i] + vals[j]
            if i != j and TMIN <= s <= TMAX:
                return vals, s
        # else a random valid target
    target = rng.randint(TMIN, TMAX)
    return vals, target


def main():
    rng = random.Random(SEED)
    with tempfile.TemporaryDirectory() as workdir:
        binp = build_ref(workdir)

        # sanity: reproduce dataset examples
        ex = run_ref_batch(binp, [
            ([1, 2, 4, 5, 6, 8, 9], 7),
            ([1, 5, 6], 6),
            ([1, 2, 3, 4], 10),
        ])
        assert ex[0] == "[[1, 6], [2, 5]]", f"example1 mismatch: {ex[0]}"
        assert ex[1] == "[[1, 5]]",          f"example2 mismatch: {ex[1]}"
        assert ex[2] == "[]",                f"example3 mismatch: {ex[2]}"

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

        cases = []

        # explicit edge cases first
        edge = [
            ([], 1),
            ([], 100000),
            ([1], 1),
            ([1], 2),
            ([100000], 100000),
            ([1, 2], 3),
            ([1, 2], 4),
            ([1, 100000], 100001),     # target out of range cannot happen; use valid
            ([1, 2, 3], 4),
            ([1, 2, 3], 5),
            ([1, 2, 3], 6),
            ([1, 99999], 100000),
            ([50000, 50001], 100001),  # > TMAX target invalid; replaced below
            (list(range(1, 11)), 11),
            (list(range(1, 11)), 5),
            ([1, 2, 4, 5, 6, 8, 9], 7),
            ([1, 5, 6], 6),
            ([1, 2, 3, 4], 10),
        ]
        # sanitize edge targets into [TMIN, TMAX]; drop pairs that can't satisfy
        clean_edge = []
        for vals, t in edge:
            vals = sorted_distinct(vals)
            t = max(TMIN, min(TMAX, t))
            clean_edge.append((vals, t))
        cases.extend(clean_edge)

        while len(cases) < N_CASES:
            vals, t = gen_case(rng)
            # enforce all constraints strictly
            vals = sorted_distinct(vals)          # strictly increasing distinct, in-range
            if len(vals) > NMAX:
                vals = vals[:NMAX]
            t = max(TMIN, min(TMAX, int(t)))
            # skip cases that would produce a gigantic output (judge truncates
            # very large stdout). Inputs are still fully within constraints; we
            # just avoid pathological pair-counts. For large lists, retarget so
            # the output stays small.
            if count_pairs(vals, t) > MAX_PAIRS:
                if len(vals) > 5000:
                    # pick a target that yields very few pairs on a big list:
                    # an odd-ish sum near the extremes
                    t = max(TMIN, min(TMAX, vals[0] + vals[-1]))
                    if count_pairs(vals, t) > MAX_PAIRS:
                        continue
                else:
                    continue
            cases.append((vals, t))

        cases = cases[:N_CASES]

        # compute expected outputs in batch
        expected = run_ref_batch(binp, cases)

        with open(OUT_PATH, "w") as f:
            for (vals, t), exp in zip(cases, expected):
                obj = {
                    "inputs": {"head": fmt_list(vals), "target": str(t)},
                    "expected": exp,
                }
                f.write(json.dumps(obj) + "\n")

    print(f"wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
