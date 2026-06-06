#!/usr/bin/env python3
"""Generator for Striver problem: number-of-provinces.

Signature: int numProvinces(vector<vector<int>> adj)
- adj is an n x n symmetric 0/1 matrix with adj[i][i] == 1.
- Output: number of connected components (provinces).

Reference oracle = connected-components count via union-find. This is the
canonical correct answer; it reproduces both dataset examples.

Output file lines: {"inputs": {"adj": "[[...],[...]]"}, "expected": "<int>"}
"""
import json
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/number-of-provinces.jsonl"
N_CASES = 2000
random.seed(20240606)


def num_provinces(adj):
    """Ground-truth oracle: count connected components in symmetric 0/1 matrix."""
    n = len(adj)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 1:
                ri, rj = find(i), find(j)
                if ri != rj:
                    parent[ri] = rj
    roots = {find(i) for i in range(n)}
    return len(roots)


def make_valid(n, edge_prob):
    """Build a valid adj: symmetric, diagonal 1, off-diagonal 0/1 by prob."""
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        adj[i][i] = 1
    for i in range(n):
        for j in range(i + 1, n):
            v = 1 if random.random() < edge_prob else 0
            adj[i][j] = v
            adj[j][i] = v
    return adj


def make_chain(n):
    """Single province: a path 0-1-2-...-(n-1)."""
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        adj[i][i] = 1
    for i in range(n - 1):
        adj[i][i + 1] = 1
        adj[i + 1][i] = 1
    return adj


def make_isolated(n):
    """n provinces: only diagonal set (no edges)."""
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        adj[i][i] = 1
    return adj


def make_full(n):
    """1 province: complete graph."""
    return [[1] * n for _ in range(n)]


def make_k_clusters(n, k):
    """Partition vertices into k groups, each an internal clique => k provinces."""
    adj = make_isolated(n)
    if k < 1:
        k = 1
    if k > n:
        k = n
    groups = [[] for _ in range(k)]
    for v in range(n):
        groups[v % k].append(v)
    # ensure each non-empty group is connected (clique)
    for g in groups:
        for a in range(len(g)):
            for b in range(a + 1, len(g)):
                adj[g[a]][g[b]] = 1
                adj[g[b]][g[a]] = 1
    return adj


def fmt(adj):
    return "[" + ",".join("[" + ", ".join(str(x) for x in row) + "]" for row in adj) + "]"


def validate(adj):
    n = len(adj)
    assert 1 <= n <= 300
    for i in range(n):
        assert len(adj[i]) == n
        assert adj[i][i] == 1
        for j in range(n):
            assert adj[i][j] in (0, 1)
            assert adj[i][j] == adj[j][i]


def main():
    cases = []

    # Mandatory edge cases
    cases.append(make_full(1))                 # n=1 -> 1
    cases.append(make_isolated(2))             # 2 isolated -> 2
    cases.append(make_full(2))                 # -> 1
    cases.append(make_isolated(300))           # max size, all isolated -> 300
    cases.append(make_full(300))               # max size, full -> 1
    cases.append(make_chain(300))              # max size, chain -> 1
    cases.append(make_chain(2))
    cases.append(make_k_clusters(300, 7))
    cases.append(make_k_clusters(50, 1))
    cases.append(make_k_clusters(50, 50))

    # dataset examples for sanity (will be checked)
    cases.append([[1,0,0,1],[0,1,1,0],[0,1,1,0],[1,0,0,1]])  # exp 2
    cases.append([[1,0,1],[0,1,0],[1,0,1]])                  # exp 2
    cases.append([[1,1],[1,1]])                              # exp 1

    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.55:
            n = random.randint(1, 60)
            p = random.choice([0.0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.7, 1.0])
            cases.append(make_valid(n, p))
        elif r < 0.70:
            n = random.randint(60, 300)
            p = random.choice([0.0, 0.005, 0.01, 0.03, 0.1, 0.5, 1.0])
            cases.append(make_valid(n, p))
        elif r < 0.82:
            n = random.randint(2, 200)
            k = random.randint(1, n)
            cases.append(make_k_clusters(n, k))
        elif r < 0.90:
            cases.append(make_chain(random.randint(1, 300)))
        elif r < 0.96:
            cases.append(make_isolated(random.randint(1, 300)))
        else:
            cases.append(make_full(random.randint(1, 300)))

    cases = cases[:N_CASES]

    with open(OUT, "w") as f:
        for adj in cases:
            validate(adj)
            exp = num_provinces(adj)
            f.write(json.dumps({"inputs": {"adj": fmt(adj)}, "expected": str(exp)}) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
