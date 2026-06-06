#!/usr/bin/env python3
"""
Test-case generator for Striver problem: task-scheduler

Problem: leastInterval(vector<char>& tasks, int n)
Constraints:
  - 1 <= tasks.length <= 10^4
  - tasks[i] is an uppercase English letter 'A'..'Z'
  - 0 <= n <= 100

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/task-scheduler.jsonl
  One JSON object per line:
    {"inputs": {"tasks": "[\"A\",\"B\"]", "n": "2"}, "expected": "<int>"}

Key names/order from starterCpp signature: tasks, n
(both kept; n is not an array length so it is NOT dropped)

Expected output is computed by a compiled C++ reference oracle.
"""
import json
import os
import random
import subprocess
import tempfile

SLUG = "task-scheduler"
OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/task-scheduler.jsonl"
N_CASES = 2000
LETTERS = [chr(ord('A') + i) for i in range(26)]

REF_SRC = r'''
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
using namespace std;

class Solution {
public:
    int leastInterval(vector<char>& tasks, int n) {
        vector<int> hash(26, 0);
        for (auto it : tasks) hash[it - 'A']++;
        sort(hash.begin(), hash.end(), greater<int>());
        int ideal = (hash[0] - 1) * n;
        for (int i = 1; i < (int)hash.size(); i++) {
            ideal = ideal - min(hash[0] - 1, hash[i]);
        }
        return (int)tasks.size() + max(0, ideal);
    }
};

int main() {
    int T;
    if (!(cin >> T)) return 0;
    while (T--) {
        int n, m;
        cin >> n >> m;
        vector<char> tasks(m);
        for (int i = 0; i < m; i++) {
            string s;
            cin >> s;
            tasks[i] = s[0];
        }
        Solution sol;
        cout << sol.leastInterval(tasks, n) << "\n";
    }
    return 0;
}
'''


def build_reference(workdir):
    src = os.path.join(workdir, "ref.cpp")
    binp = os.path.join(workdir, "ref")
    with open(src, "w") as f:
        f.write(REF_SRC)
    subprocess.run(
        ["clang++", "-std=c++17", "-O2", "-w", src, "-o", binp],
        check=True,
    )
    return binp


def fmt_tasks(tasks):
    # Same serialization as the examples: ["A","B","C"]
    return "[" + ",".join('"' + c + '"' for c in tasks) + "]"


def gen_case(idx):
    """Return a list of task chars and an int n, strictly within constraints."""
    # A spread of structural shapes so the oracle exercises many branches.
    r = random.random()
    if idx == 0:
        # min size edge case
        tasks = ["A"]
        n = 0
    elif idx == 1:
        # single task, max n
        tasks = ["Z"]
        n = 100
    elif idx == 2:
        # all identical, small
        tasks = ["A"] * random.randint(2, 8)
        n = random.randint(0, 100)
    elif idx == 3:
        # n = 0 means no cooldown -> answer == length
        m = random.randint(1, 200)
        tasks = [random.choice(LETTERS) for _ in range(m)]
        n = 0
    elif idx == 4:
        # all 26 letters present, heavy duplicates
        tasks = []
        for c in LETTERS:
            tasks.extend([c] * random.randint(1, 50))
        random.shuffle(tasks)
        n = random.randint(0, 100)
    elif r < 0.12:
        # large near-max size
        m = random.randint(9000, 10000)
        k = random.randint(1, 26)
        pool = LETTERS[:k]
        tasks = [random.choice(pool) for _ in range(m)]
        n = random.randint(0, 100)
    elif r < 0.30:
        # small arrays, few distinct letters (lots of cooldown / idle)
        m = random.randint(1, 20)
        k = random.randint(1, 4)
        pool = random.sample(LETTERS, k)
        tasks = [random.choice(pool) for _ in range(m)]
        n = random.randint(0, 100)
    elif r < 0.55:
        # medium arrays, moderate distinct letters
        m = random.randint(20, 500)
        k = random.randint(1, 26)
        pool = random.sample(LETTERS, k)
        tasks = [random.choice(pool) for _ in range(m)]
        n = random.randint(0, 100)
    elif r < 0.75:
        # one dominant high-frequency task + filler
        m = random.randint(10, 2000)
        dominant = random.choice(LETTERS)
        tasks = [dominant] * (m // 2)
        rest = m - len(tasks)
        others = [c for c in LETTERS if c != dominant]
        tasks.extend(random.choice(others) for _ in range(rest))
        random.shuffle(tasks)
        n = random.randint(0, 100)
    else:
        # general random
        m = random.randint(1, 3000)
        k = random.randint(1, 26)
        pool = random.sample(LETTERS, k)
        tasks = [random.choice(pool) for _ in range(m)]
        n = random.randint(0, 100)

    # Safety clamp to constraints
    if len(tasks) > 10000:
        tasks = tasks[:10000]
    if len(tasks) < 1:
        tasks = ["A"]
    n = max(0, min(100, n))
    return tasks, n


def main():
    random.seed(20260606)
    with tempfile.TemporaryDirectory() as workdir:
        binp = build_reference(workdir)

        cases = [gen_case(i) for i in range(N_CASES)]

        # Build a single batched stdin for the oracle.
        lines = [str(len(cases))]
        for tasks, n in cases:
            lines.append(f"{n} {len(tasks)}")
            lines.append(" ".join(tasks))
        stdin_data = "\n".join(lines) + "\n"

        proc = subprocess.run(
            [binp], input=stdin_data, capture_output=True, text=True, check=True
        )
        outputs = proc.stdout.split()
        assert len(outputs) == len(cases), (
            f"oracle produced {len(outputs)} outputs for {len(cases)} cases"
        )

        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        with open(OUT_PATH, "w") as f:
            for (tasks, n), exp in zip(cases, outputs):
                rec = {
                    "inputs": {"tasks": fmt_tasks(tasks), "n": str(n)},
                    "expected": str(exp),
                }
                f.write(json.dumps(rec) + "\n")

    print(f"wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
