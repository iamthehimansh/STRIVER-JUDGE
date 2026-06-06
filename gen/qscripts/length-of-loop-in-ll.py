#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Length of loop in LL"
(slug: length-of-loop-in-ll)

Signature (starterCpp):
    class Solution { public: int findLengthOfLoop(ListNode *head); };

IMPORTANT — judge harness reality
---------------------------------
The judge builds the ListNode* `head` from a single input string via its
`rdList` helper, which constructs a PLAIN, ACYCLIC singly linked list. The
harness cannot inject a loop: `pos`/`index` is NOT representable through the
deserialization path (rdList only reads the value list and links i -> i+1).
Therefore the only self-consistent expected output the judge can ever produce
for a harness-built list is `0` (an acyclic list has no loop, so loop length 0).

This mirrors the sibling problem `detect-a-loop-in-ll`, whose generated set is
entirely `false` for the same reason.

To stay self-consistent with the judge:
  * The single jsonl input key is named EXACTLY `head` so it name-binds to the
    `ListNode *head` parameter (in batch/submit mode every param must bind to a
    column).
  * The value is the list of node values, formatted like a ListNode input
    array: "[1, 2, 3]".
  * Every `expected` is "0", computed by the same logic the judge runs:
    Floyd's cycle detection + node count over the acyclic list the harness
    builds (no cycle -> length 0).

Constraints from the problem:
  * 0 <= number of nodes in the cycle <= 1e5  (we cap list length modestly for
    batch judging speed; the loop itself is never representable anyway)
  * 0 <= ListNode.val <= 1e4
  * pos is -1 or a valid index (not representable; harness always builds acyclic)

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/length-of-loop-in-ll.jsonl
        one JSON object per line: {"inputs": {"head": "[...]"}, "expected": "0"}
"""

import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/length-of-loop-in-ll.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = 0, 10_000   # 0 <= ListNode.val <= 1e4

random.seed(20260606)


def length_of_loop(values):
    """Floyd's cycle detection + loop-node count on a freshly built ACYCLIC
    list of `values` (the exact list the judge builds via rdList).

    Mirrors the reference algorithm a correct submission runs. For an acyclic
    chain this always returns 0, guaranteeing self-consistency with the judge.
    """
    n = len(values)

    def nxt(i):
        if i is None:
            return None
        return i + 1 if (i + 1) < n else None

    slow = 0 if n > 0 else None
    fast = 0 if n > 0 else None

    while fast is not None and nxt(fast) is not None:
        slow = nxt(slow)
        fast = nxt(nxt(fast))
        if slow == fast and slow is not None:
            # Count nodes in the loop (impossible for acyclic chain; kept for
            # fidelity with the reference implementation).
            cnt = 1
            s = nxt(slow)
            while s != fast:
                s = nxt(s)
                cnt += 1
            return cnt
    return 0


def fmt_list(values):
    return "[" + ", ".join(str(v) for v in values) + "]"


def gen_lengths():
    """Yield a varied set of list lengths covering edges + random sizes."""
    lengths = []
    # edge cases
    lengths.append(0)          # empty list -> head == NULL
    lengths.append(1)          # single node
    lengths.append(2)
    lengths.append(3)
    # a handful of larger ones (kept modest for batch speed)
    for L in (50, 100, 500, 1000, 2000):
        lengths.append(L)
    # fill the rest randomly
    while len(lengths) < N_CASES:
        r = random.random()
        if r < 0.55:
            lengths.append(random.randint(0, 12))      # many small lists
        elif r < 0.85:
            lengths.append(random.randint(13, 200))    # medium
        else:
            lengths.append(random.randint(201, 3000))  # large-ish, fast in batch
    random.shuffle(lengths)
    return lengths[:N_CASES]


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    lengths = gen_lengths()
    n_written = 0
    with open(OUT, "w") as f:
        for L in lengths:
            if L == 0:
                values = []
            else:
                values = [random.randint(VAL_MIN, VAL_MAX) for _ in range(L)]
            expected = str(length_of_loop(values))
            rec = {"inputs": {"head": fmt_list(values)}, "expected": expected}
            f.write(json.dumps(rec) + "\n")
            n_written += 1
    print(f"wrote {n_written} cases to {OUT}")


if __name__ == "__main__":
    main()
