#!/usr/bin/env python3
"""
Test-case generator for Striver problem:
    "Clone a LL with random and next pointer"
    slug: clone-a-ll-with-random-and-next-pointer

IMPORTANT — how the judge actually handles this problem
-------------------------------------------------------
The dataset's intended I/O uses a special [[val, random_index], ...] matrix and a
"<vals>, true" output to verify the random pointers. HOWEVER, the auto-judge that
runs the user's `class Solution` (lib/judge/harness.ts) provides its OWN ListNode:

    struct ListNode { int val; ListNode *next; ...};   // NO `random` field

and (de)serializes ListNode params/returns as a FLAT value array:
  - input  : rdList()  builds a list from "[v0, v1, ...]" (random pointers cannot exist)
  - output : pr(ListNode*) prints the node values space-separated

Therefore the only thing the judge can verify for `copyRandomList(ListNode* head)`
is the VALUE SEQUENCE of the returned (cloned) list. A correct deep copy returns a
new list whose values match the input in order, so:

    input  key  : "head"                (the param name in starterCpp)
    input  value: "[v0, v1, ...]"       (flat value array, the format rdList parses)
    expected    : "v0 v1 ..."           (space-separated values, the format pr() emits)

This was confirmed live against http://localhost:3000/api/run (passed == total).

Constraints enforced (from the problem JSON):
    1 <= n <= 1e5
    -1e4 <= ListNode.val <= 1e4

We keep the static set modest (2000 cases) with a spread of sizes incl. edge cases.

NOTE on sizing: the judge runner (scripts/judge_exec.py) caps captured stdout at
OUT_CAP = 256 KiB for the WHOLE batched run. With 2000 cases that means the *summed*
expected output must stay under 256 KiB, or trailing cases get truncated (they then
show as runtime_error / no output line and the submit reports < total passed).
So sizes here are intentionally small (max list ~256 nodes, summed output kept well
under 256 KiB) while still hitting edge cases. Larger sizes (up to n = 1e5) remain
fully valid per the constraints; the generator can produce them on demand by raising
the size bounds below (but then fewer cases fit under the 256 KiB output cap).
"""
import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/clone-a-ll-with-random-and-next-pointer.jsonl"

VAL_MIN, VAL_MAX = -10_000, 10_000
N_MIN, N_MAX = 1, 100_000
N_CASES = 2000

random.seed(20260606)


def rand_val():
    return random.randint(VAL_MIN, VAL_MAX)


def make_vals(n):
    return [rand_val() for _ in range(n)]


def case_from_vals(vals):
    # Input: flat value array (the format the judge's rdList parses for ListNode*)
    inp = "[" + ", ".join(str(v) for v in vals) + "]"
    # Expected: value sequence of the cloned list == input values in order
    # (matches the judge's pr(ListNode*): space-separated node values, no suffix)
    exp = " ".join(str(v) for v in vals)
    return {"inputs": {"head": inp}, "expected": exp}


def main():
    cases = []

    # ---- explicit edge cases -------------------------------------------------
    edge_sizes = [1, 1, 2, 2, 3, 4, 5, 10]
    for n in edge_sizes:
        cases.append(case_from_vals(make_vals(n)))

    # single-node extremes
    cases.append(case_from_vals([VAL_MIN]))
    cases.append(case_from_vals([VAL_MAX]))
    cases.append(case_from_vals([0]))
    # all-min / all-max / all-zero small lists
    cases.append(case_from_vals([VAL_MIN] * 5))
    cases.append(case_from_vals([VAL_MAX] * 5))
    cases.append(case_from_vals([0] * 7))
    # mixed extremes
    cases.append(case_from_vals([VAL_MIN, VAL_MAX, 0, VAL_MAX, VAL_MIN]))
    # a couple of larger lists (kept within the 256 KiB stdout-cap budget)
    cases.append(case_from_vals(make_vals(256)))
    cases.append(case_from_vals(make_vals(200)))

    # ---- random bulk ---------------------------------------------------------
    # Size distribution chosen so the SUMMED expected output stays comfortably
    # under the runner's 256 KiB stdout cap (avg ~12 nodes/case -> ~0.15 MiB).
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.70:
            n = random.randint(1, 12)          # many tiny lists
        elif r < 0.92:
            n = random.randint(13, 30)         # small
        elif r < 0.99:
            n = random.randint(31, 70)         # medium
        else:
            n = random.randint(71, 150)        # occasional larger
        cases.append(case_from_vals(make_vals(n)))

    cases = cases[:N_CASES]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for c in cases:
            f.write(json.dumps(c) + "\n")

    print(f"wrote {len(cases)} cases to {OUT}")


if __name__ == "__main__":
    main()
