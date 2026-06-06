#!/usr/bin/env python3
"""
Test-case generator for Striver problem: "Detect a loop in LL" (slug: detect-a-loop-in-ll)

Signature (starterCpp):
    class Solution { public: bool hasCycle(ListNode *head); };

IMPORTANT — judge harness reality
---------------------------------
The judge builds the ListNode* `head` from a single input string via its `rdList`
helper, which constructs a PLAIN, ACYCLIC singly linked list (it cannot inject a
loop; `pos`/`index` is NOT representable through the harness). Therefore the only
self-consistent expected output the judge can ever produce for a built list is
`false` (an acyclic list never has a cycle).

To stay self-consistent with the judge:
  * The single jsonl input key is named EXACTLY `head` so it name-binds to the
    `ListNode *head` parameter (in batch/submit mode every param must bind to a
    column; the key order's first key drives binding).
  * The value is the list of node values, formatted like a ListNode input array:
    "[1, 2, 3]".
  * Every `expected` is "false", computed by the same logic the judge runs
    (Floyd's cycle detection over the acyclic list the harness builds).

Constraints from the problem:
  * 0 <= number of nodes <= 1e5  (we cap list length modestly for batch speed)
  * 0 <= ListNode.val <= 1e4
  * pos is -1 or a valid index (not representable; harness always builds acyclic)

Output: /Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/detect-a-loop-in-ll.jsonl
        one JSON object per line: {"inputs": {"head": "[...]"}, "expected": "false"}
"""

import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/detect-a-loop-in-ll.jsonl"
N_CASES = 2000
VAL_MIN, VAL_MAX = 0, 10_000   # 0 <= ListNode.val <= 1e4

random.seed(20260606)


def has_cycle(values):
    """Floyd's cycle detection on a freshly built ACYCLIC list of `values`.

    This mirrors exactly what the judge does: it builds an acyclic list from the
    given values, so the result is always False. We still run the real algorithm
    so the expected output is computed by the same oracle a correct submission
    uses (guaranteeing self-consistency).
    """
    # Build acyclic singly linked list as (val, next_index) — next is i+1 or None.
    n = len(values)
    # slow/fast pointers as indices into the acyclic chain
    slow = 0 if n > 0 else None
    fast = 0 if n > 0 else None

    def nxt(i):
        if i is None:
            return None
        return i + 1 if i + 1 < n else None

    while fast is not None and nxt(fast) is not None:
        slow = nxt(slow)
        fast = nxt(nxt(fast))
        if slow == fast and slow is not None:
            # impossible for an acyclic chain, but kept for fidelity
            return True
    return False


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
            expected = "true" if has_cycle(values) else "false"
            rec = {"inputs": {"head": fmt_list(values)}, "expected": expected}
            f.write(json.dumps(rec) + "\n")
            n_written += 1
    print(f"wrote {n_written} cases to {OUT}")


if __name__ == "__main__":
    main()
