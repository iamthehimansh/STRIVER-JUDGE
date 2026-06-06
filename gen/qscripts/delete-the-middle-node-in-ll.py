#!/usr/bin/env python3
"""
Test-case generator for Striver problem
"Delete the middle node in LL"  (slug: delete-the-middle-node-in-ll).

Problem: Given the head of a non-empty singly linked list, delete the middle
node. The middle node of a list of size n is the (floor(n/2) + 1)-th node
using 1-based indexing. Return the head of the modified list.

In a 0-indexed array representation of the n node values, the middle node is at
index floor(n/2). Deleting it yields the result list. For n == 1 the only node
is deleted, leaving an EMPTY list (the judge prints nothing -> empty "expected").

starterCpp signature:
    ListNode* deleteMiddle(ListNode* head)
=> the single input parameter name is "head".

Serialization (matches lib/judge/harness.ts):
  - ListNode INPUT  : array of node values, e.g. "[1, 2, 3]"  (rdList)
  - ListNode OUTPUT : node values space-separated; an empty/NULL list -> "" (pr)
    The judge compares leniently (ignoring brackets/commas/whitespace), so we
    emit the result as a bracketed list "[a, b, c]" (and "" / "[]" for empty),
    which canonicalizes to the same token stream the judge produces.

Constraints:
  - 1 <= number of nodes <= 1e5
  - 0 <= ListNode.val <= 1e4

Reference logic is equivalent to ref2/"Delete Middle of linked List.cpp" and
strivers-a2z-ref ".../09.Delete_mid_of_LL.cpp" (slow/fast pointer => delete the
(floor(n/2)+1)-th node).
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/delete-the-middle-node-in-ll.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = 0, 10_000
# Problem constraint allows up to 1e5 nodes, BUT the judge's batch runner caps
# captured stdout at 1 MiB (lib/judge/runner.ts: cap = 1024*1024). The batched
# submit streams ALL 2000 case outputs through that single 1 MiB buffer, so a
# huge case would truncate the stream and misalign every later case. We therefore
# bound the generated sizes so the TOTAL batched stdout stays well under 1 MiB
# while still covering every algorithmically-relevant case (n=1, even/odd parity,
# small, medium, larger). NODES_HARD is the true constraint, kept for the
# in-range assertion; SIZE_CAP bounds what we actually emit.
NODES_HARD = 100_000
SIZE_CAP = 500


def delete_middle(vals):
    """Return the list with the (floor(n/2)+1)-th node (1-based) removed.

    For n == 1 returns [] (empty list)."""
    n = len(vals)
    mid = n // 2  # 0-indexed position of the middle node
    return vals[:mid] + vals[mid + 1:]


def fmt_list(vals):
    return "[" + ", ".join(str(x) for x in vals) + "]"


def rand_vals(n):
    return [random.randint(VAL_MIN, VAL_MAX) for _ in range(n)]


def gen_cases():
    cases = []  # list of value-lists

    # --- deterministic edge cases ---
    cases.append([7])                       # n=1 -> empty result (dataset case 3)
    cases.append([0])                       # n=1, min value
    cases.append([10000])                   # n=1, max value
    cases.append([1, 2])                    # n=2 -> delete idx 1 -> [1]
    cases.append([5, 9])                    # n=2
    cases.append([1, 2, 3])                 # n=3 -> delete idx 1 -> [1,3]
    cases.append([1, 2, 3, 4, 5])           # dataset case 1 -> [1,2,4,5]
    cases.append([7, 6, 5, 4])              # dataset case 2 -> [7,6,4]
    cases.append([0, 0, 0, 0])              # all min
    cases.append([10000, 10000, 10000])     # all max
    cases.append([0, 10000])                # extremes, n=2
    cases.append(list(range(1, 11)))        # n=10
    cases.append(list(range(1, 12)))        # n=11 (odd)
    # a few larger lists to exercise scale (bounded by SIZE_CAP, see note above)
    cases.append([random.randint(VAL_MIN, VAL_MAX) for _ in range(SIZE_CAP)])
    cases.append([random.randint(VAL_MIN, VAL_MAX) for _ in range(SIZE_CAP - 1)])
    cases.append([i % (VAL_MAX + 1) for i in range(SIZE_CAP)])

    # small exhaustive-ish sizes 1..40 with random values (covers both parities)
    for n in range(1, 41):
        cases.append(rand_vals(n))

    # --- random cases up to N_CASES ---
    # Keep the bulk small so total batched stdout stays well under the 1 MiB cap.
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.75:
            n = random.randint(1, 20)            # many tiny lists
        elif r < 0.95:
            n = random.randint(1, 60)            # small/medium
        else:
            n = random.randint(1, SIZE_CAP)      # larger (bounded)
        cases.append(rand_vals(n))

    return cases[:N_CASES]


def main():
    random.seed(20240606)
    cases = gen_cases()
    with open(OUT_PATH, "w") as f:
        for vals in cases:
            assert 1 <= len(vals) <= NODES_HARD
            assert all(VAL_MIN <= v <= VAL_MAX for v in vals)
            res = delete_middle(vals)
            obj = {
                "inputs": {"head": fmt_list(vals)},
                "expected": fmt_list(res),  # "[]" when empty
            }
            f.write(json.dumps(obj) + "\n")
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
