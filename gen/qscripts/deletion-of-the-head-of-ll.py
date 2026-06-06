#!/usr/bin/env python3
"""
Test-case generator for Striver problem "Deletion of the head of LL"
(slug: deletion-of-the-head-of-ll).

Given the head of a singly linked list, delete the head node and return the
head of the modified list.

starterCpp signature:
    ListNode* deleteHead(ListNode* &head)

Constraints:
  - 1 <= number of nodes in the Linked List <= 1000
  - 0 <= ListNode.data <= 100

ListNode is (de)serialized by the judge as the array of node values, e.g.
"[1, 2, 3]". The input key in the dataset is "linkedList" (bound positionally to
the single `head` parameter by the judge's harness). The output is a ListNode*
which the judge prints as the space-separated values; we format "expected" as
the example output shows: "[2, 3]" for a non-empty result, "[]" when the list
becomes empty.

Reference logic: deleting the head of [v0, v1, ..., vn] yields [v1, ..., vn].
This is exactly what `return head->next;` does and is verified against the live
judge (see notes).

NOTE on sizing: the live "Submit" judge batches all cases into ONE process and
caps the captured stdout at 256 KB (scripts/judge_exec.py: OUT_CAP). Because the
output is the (possibly long) modified list serialized per case, the TOTAL
serialized output across all 2000 cases must stay well under 256 KB or trailing
cases get truncated and (spuriously) fail. We therefore keep the vast majority
of lists short and include only a handful of large boundary cases (placed first,
within budget). The constraint range (up to 1000 nodes) is still exercised.
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/deletion-of-the-head-of-ll.jsonl"
N_CASES = 2000
MAX_NODES = 1000
MIN_VAL = 0
MAX_VAL = 100


def fmt_list(lst):
    return "[" + ", ".join(str(x) for x in lst) + "]"


def delete_head(lst):
    """Delete the first node and return the remaining values."""
    return lst[1:]


def gen_list(n):
    return [random.randint(MIN_VAL, MAX_VAL) for _ in range(n)]


def main():
    random.seed(20260606)
    cases = []

    # ---- Explicit edge cases (a few large boundary cases first, within the
    #      256 KB total-output budget; the rest are short) ----
    cases.append([0] * MAX_NODES)     # max length, all zeros
    cases.append([100] * MAX_NODES)   # max length, all max
    cases.append(gen_list(MAX_NODES)) # max length, random values
    cases.append(list(range(0, 101))) # 101 nodes, ascending 0..100
    cases.append([1])                 # dataset example 2 -> []
    cases.append([1, 2, 3])           # dataset example 1 -> [2, 3]
    cases.append([0])                 # min value, single node
    cases.append([100])               # max value, single node
    cases.append([0, 0])              # repeated min
    cases.append([100, 100])          # repeated max
    cases.append([0, 100])            # min then max
    cases.append([100, 0])            # max then min
    cases.append([5, 5, 5, 5, 5])     # all equal
    cases.append([7, 0])              # two nodes
    cases.append([42, 17])            # two nodes random-ish

    # ---- Random cases: kept SHORT so total serialized output stays under the
    #      judge's 256 KB stdout cap (see module docstring) ----
    while len(cases) < N_CASES:
        r = random.random()
        if r < 0.25:
            n = 1                                  # single node (becomes empty)
        elif r < 0.55:
            n = random.randint(2, 8)               # tiny lists
        elif r < 0.90:
            n = random.randint(2, 20)              # small lists
        else:
            n = random.randint(2, 40)              # slightly larger
        cases.append(gen_list(n))

    cases = cases[:N_CASES]

    # Total bytes of the batched output (one line per case, values space-joined
    # the way the judge serializes a ListNode*). Must stay under the judge's
    # 256 KB OUT_CAP with margin so no trailing case is truncated.
    OUT_CAP = 256 * 1024
    total_out_bytes = 0

    with open(OUT_PATH, "w") as f:
        for lst in cases:
            # validate constraints strictly
            assert 1 <= len(lst) <= MAX_NODES, f"bad length {len(lst)}"
            assert all(MIN_VAL <= v <= MAX_VAL for v in lst), "value out of range"
            res = delete_head(lst)
            # judge prints values space-separated, then a newline per case
            total_out_bytes += len(" ".join(str(x) for x in res)) + 1
            obj = {
                "inputs": {"linkedList": fmt_list(lst)},
                "expected": fmt_list(res),  # "[]" when empty
            }
            f.write(json.dumps(obj) + "\n")

    assert total_out_bytes < OUT_CAP, (
        f"batched output {total_out_bytes} bytes exceeds judge cap {OUT_CAP}"
    )
    print(f"Wrote {len(cases)} cases to {OUT_PATH}")
    print(f"Estimated batched stdout: {total_out_bytes} bytes "
          f"({100*total_out_bytes/OUT_CAP:.1f}% of 256 KB cap)")


if __name__ == "__main__":
    main()
