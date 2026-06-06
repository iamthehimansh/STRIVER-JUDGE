#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
  "Segregate odd and even nodes in Linked List"  (slug: segregate-odd-and-even-nodes-in-ll)

Method signature (starterCpp):
    ListNode* oddEvenList(ListNode* &head)

Semantics: group all nodes with ODD indices (1-indexed) followed by all nodes
with EVEN indices, preserving relative order within each group. This is the
classic LeetCode "Odd Even Linked List".

Constraints:
    0 <= number of nodes <= 1e5
    0 <= ListNode.val <= 1e4

Output:
    generated-tests/segregate-odd-and-even-nodes-in-ll.jsonl
    one JSON object per line: {"inputs": {"head": "[..]"}, "expected": "[..]"}

The judge:
  * builds the ListNode* from the input array (struct field is .val),
  * serializes the returned ListNode* as space-separated values,
  * compares leniently (ignores brackets / commas / whitespace / quotes).
So we format inputs/outputs as bracketed arrays like the dataset examples.

IMPORTANT — judge output cap:
  Submit mode runs ALL 2000 cases in ONE batched process whose stdout is capped
  at 1 MiB (lib/judge/runner.ts: cap = 1024*1024). Output beyond the cap is
  silently dropped, which would make every later case "fail". So even though the
  problem allows up to 1e5 nodes, we keep the TOTAL serialized output across all
  cases comfortably under ~850 KB so a correct submission reproduces 100%.
"""

import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/segregate-odd-and-even-nodes-in-ll.jsonl"
N_CASES = 2000
MAX_VAL = 10**4            # 0 <= val <= 1e4
MAX_NODES = 10**5         # 0 <= nodes <= 1e5 (problem bound)

# Batched-submit stdout cap is 1 MiB; keep total output safely below it.
OUTPUT_BUDGET_BYTES = 850_000
# Per-output-line cost ~= (digits+1) per value; ~6 bytes is a safe upper bound.
BYTES_PER_NODE = 6
# Largest single list we emit (well within MAX_NODES, but bounded so a few big
# cases don't blow the whole-batch 1 MiB output budget).
BIG_CAP = 3000

random.seed(20260606)


def odd_even_list(arr):
    """Reference oracle: odd-indexed (1-based) nodes first, then even-indexed."""
    odd = arr[0::2]   # indices 1,3,5,... (0-based positions 0,2,4,...)
    even = arr[1::2]  # indices 2,4,6,... (0-based positions 1,3,5,...)
    return odd + even


def fmt(arr):
    return "[" + ", ".join(str(x) for x in arr) + "]"


def rand_list(n):
    return [random.randint(0, MAX_VAL) for _ in range(n)]


def gen_cases():
    cases = []

    # ---- explicit edge cases ----
    edge = [
        [],                       # empty list (0 nodes allowed)
        [0],                      # single node, min value
        [MAX_VAL],                # single node, max value
        [1, 2],                   # two nodes
        [1, 2, 3],                # three nodes (odd length)
        [1, 2, 3, 4],             # four nodes (even length)
        [1, 2, 3, 4, 5],          # dataset example 1
        [4, 3, 2, 1],             # dataset example 2
        [0, 0, 0, 0, 0],          # all equal / all min
        [MAX_VAL] * 6,            # all max
        list(range(0, 10)),       # ascending small
        list(range(9, -1, -1)),   # descending small
    ]
    for e in edge:
        cases.append(e)

    # A few larger lists (bounded by BIG_CAP so the whole-batch 1 MiB stdout
    # budget is respected; still exercises the loop on long inputs).
    cases.append(rand_list(BIG_CAP))
    cases.append(rand_list(BIG_CAP - 1))
    cases.append(rand_list(1500))

    # running byte budget for the remaining (random) cases
    used = sum((len(c) * BYTES_PER_NODE + 2) for c in cases)

    # ---- random cases across a spread of sizes, honoring the output budget ----
    while len(cases) < N_CASES:
        remaining_cases = N_CASES - len(cases)
        budget_left = OUTPUT_BUDGET_BYTES - used
        # average bytes we can still afford per remaining case
        avg_left = max(8, budget_left // max(1, remaining_cases))
        max_n_affordable = max(1, min(BIG_CAP, avg_left // BYTES_PER_NODE))

        r = random.random()
        if r < 0.6:
            n = random.randint(0, min(40, max_n_affordable))   # many small lists
        elif r < 0.9:
            n = random.randint(0, min(150, max_n_affordable))  # medium
        else:
            n = random.randint(0, max_n_affordable)            # larger
        cases.append(rand_list(n))
        used += len(cases[-1]) * BYTES_PER_NODE + 2

    return cases[:N_CASES]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    cases = gen_cases()
    with open(OUT, "w") as f:
        for arr in cases:
            # sanity: enforce constraints
            assert 0 <= len(arr) <= MAX_NODES
            assert all(0 <= v <= MAX_VAL for v in arr)
            expected = odd_even_list(arr)
            obj = {"inputs": {"head": fmt(arr)}, "expected": fmt(expected)}
            f.write(json.dumps(obj) + "\n")
    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
