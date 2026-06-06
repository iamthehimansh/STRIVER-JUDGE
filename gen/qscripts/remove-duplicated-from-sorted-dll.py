#!/usr/bin/env python3
"""
Test-case generator for Striver problem
"Remove duplicates from sorted DLL"  (slug: remove-duplicated-from-sorted-dll).

Problem: Given the head of a doubly linked list whose values are sorted in
non-decreasing order, remove all duplicate occurrences of any value so that only
distinct values remain (keeping the first occurrence). Return the head.

Because the list is sorted non-decreasing, equal values are consecutive, so the
result is simply the input values with consecutive duplicates collapsed -- i.e.
the sorted sequence of DISTINCT values, preserving order.

starterCpp signature:
    ListNode* removeDuplicates(ListNode* head)
=> the single input parameter name is "head".

Serialization (matches lib/judge/harness.ts):
  - ListNode INPUT  : array of node values, e.g. "[1, 1, 3]"  (rdList builds the
    list from the array; note the judge's ListNode has only .val/.next -- no
    .prev -- so a reference must traverse with .next only).
  - ListNode OUTPUT : node values space-separated; an empty list -> "" (pr).
    The judge compares leniently (ignoring brackets/commas/whitespace), so we
    emit the result as a bracketed list "[a, b, c]" which canonicalizes to the
    same token stream the judge produces. (The list always has >=1 node here, so
    the output is never empty.)

Constraints:
  - 1 <= number of nodes in the linked list <= 1e5
  - -1e4 <= ListNode.val <= 1e4
  - Values sorted in non-decreasing order.

The expected output is computed directly (collapse consecutive equal values).
This matches the reference logic in
strivers-a2z-ref/.../03.Remove_duplicates_from_dll.cpp and is independently
verified against the live judge with an equivalent `class Solution`.
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/remove-duplicated-from-sorted-dll.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = -10_000, 10_000
NODES_HARD = 100_000  # true upper bound (used only for the in-range assertion)
# In submit mode ALL 2000 case outputs are produced by a SINGLE batch process
# whose combined stdout is capped at 256 KB (scripts/judge_exec.py OUT_CAP).
# Beyond that, output is truncated mid-line and every later case misaligns.
# Bound emitted sizes so the TOTAL batched stdout (sum of all distinct-value
# output lines) stays comfortably under that cap (target ~130 KB) while still
# covering every relevant case (n=1, all-same, all-distinct, mixed, runs,
# value extremes, larger sizes). MEAN_OUT_BUDGET is enforced post-generation.
SIZE_CAP = 120
OUT_BYTE_BUDGET = 150 * 1024  # keep total batched stdout well under 256 KB


def remove_dups(vals):
    """Collapse consecutive equal values -> distinct values in order."""
    out = []
    for x in vals:
        if not out or out[-1] != x:
            out.append(x)
    return out


def fmt_list(vals):
    return "[" + ", ".join(str(x) for x in vals) + "]"


def rand_sorted(n, lo=VAL_MIN, hi=VAL_MAX):
    """A non-decreasing sequence of n values in [lo, hi]."""
    return sorted(random.randint(lo, hi) for _ in range(n))


def rand_sorted_with_runs(n):
    """A sorted sequence built from random value 'runs' to force duplicates."""
    vals = []
    cur = random.randint(VAL_MIN, VAL_MAX)
    while len(vals) < n:
        run = random.randint(1, 8)
        for _ in range(min(run, n - len(vals))):
            vals.append(cur)
        cur = min(VAL_MAX, cur + random.randint(0, 50))
    return vals[:n]


def gen_cases():
    cases = []  # list of value-lists (each already sorted non-decreasing)

    # --- deterministic edge cases ---
    cases.append([1, 1, 3, 3, 4, 5])        # dataset example 1 -> [1,3,4,5]
    cases.append([1, 1, 1, 1, 1, 2])        # dataset example 2 -> [1,2]
    cases.append([1, 2, 3])                 # dataset "now your turn" -> [1,2,3]
    cases.append([7])                       # n=1, single node
    cases.append([0])                       # n=1, zero
    cases.append([-10000])                  # n=1, min value
    cases.append([10000])                   # n=1, max value
    cases.append([5, 5])                    # n=2, both same -> [5]
    cases.append([5, 6])                    # n=2, distinct -> [5,6]
    cases.append([-10000, 10000])           # extremes spread
    cases.append([-1, -1, 0, 0, 1, 1])      # negatives + dup runs
    cases.append([3, 3, 3, 3, 3])           # all identical -> [3]
    cases.append([-10000] * 50)             # long run of min -> [-10000]
    cases.append([10000] * 50)              # long run of max -> [10000]
    cases.append(list(range(-200, 200)))    # all distinct, full range step 1
    cases.append([-10000, -10000, 0, 0, 10000, 10000])  # extremes w/ dups
    # alternating-ish small with heavy duplication
    cases.append(sorted([v for v in range(-5, 6) for _ in range(4)]))
    # a larger all-distinct case (size cap) -> large distinct output line
    cases.append(list(range(SIZE_CAP)))
    # a larger all-same case -> tiny output (single distinct value)
    cases.append([42] * 5000)
    # large input that collapses to few distinct values (heavy duplication)
    cases.append(sorted([v for v in range(-10, 11) for _ in range(300)]))

    # --- randomized cases ---
    while len(cases) < N_CASES:
        kind = random.random()
        if kind < 0.30:
            n = random.randint(1, 12)            # tiny
            vals = rand_sorted(n)
        elif kind < 0.55:
            n = random.randint(1, 12)            # tiny, narrow range -> many dups
            vals = sorted(random.randint(-3, 3) for _ in range(n))
        elif kind < 0.80:
            n = random.randint(1, 120)           # medium with runs
            vals = rand_sorted_with_runs(n)
        elif kind < 0.92:
            # larger input but NARROW value range -> few distinct -> small output
            n = random.randint(120, 2000)
            vals = sorted(random.randint(-30, 30) for _ in range(n))
        else:
            n = random.randint(1, SIZE_CAP)      # larger, wider range
            if random.random() < 0.5:
                vals = rand_sorted(n)
            else:
                vals = rand_sorted_with_runs(n)
        cases.append(vals)

    return cases[:N_CASES]


def main():
    random.seed(20260606)
    cases = gen_cases()
    lines = []
    batched_out_bytes = 0  # judge prints one space-separated line per case
    for vals in cases:
        # constraint checks
        assert 1 <= len(vals) <= NODES_HARD, len(vals)
        assert all(VAL_MIN <= v <= VAL_MAX for v in vals)
        assert all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1)), "not sorted"
        expected = remove_dups(vals)
        assert len(expected) >= 1
        batched_out_bytes += len(" ".join(str(x) for x in expected)) + 1
        rec = {"inputs": {"head": fmt_list(vals)}, "expected": fmt_list(expected)}
        lines.append(json.dumps(rec, separators=(",", ":")))
    # Guard against the 256 KB OUT_CAP on the batch process's combined stdout.
    assert batched_out_bytes < OUT_BYTE_BUDGET, (
        f"batched stdout {batched_out_bytes} >= budget {OUT_BYTE_BUDGET}"
    )
    with open(OUT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} cases to {OUT_PATH}; "
          f"batched stdout ~{batched_out_bytes} bytes "
          f"({batched_out_bytes/1024:.1f} KB, budget {OUT_BYTE_BUDGET/1024:.0f} KB)")


if __name__ == "__main__":
    main()
