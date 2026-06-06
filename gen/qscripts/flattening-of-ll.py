#!/usr/bin/env python3
"""
Generator for Striver problem: "Flattening of LL" (slug: flattening-of-ll).

Problem: a special linked list of `n` head nodes; each head node owns a child
linked list (sorted non-decreasing). Flatten everything into one sorted list and
return the head.

Judge model (important):
  The dev judge's ListNode struct has only {val, next} (NO `child`). The method
  signature is `ListNode* flattenLinkedList(ListNode* &head)`. The harness binds
  the single input value (key "nums") to `head` and builds the list with rdList,
  whose tokenizer flattens a 2D array `[[...],[...]]` into ONE next-linked list in
  row-major order. The correct reference (operating on val/next) therefore simply
  collects all values, sorts them, and rebuilds the list. The output is serialized
  as the space-separated value list.

So:
  input  "nums"  = 2D array of sorted child lists, e.g. "[[3], [2, 10], [1, 7]]"
  expected       = sorted multiset of all values as a flat array, e.g. "[1, 2, 3, 7, 10]"

Constraints enforced:
  1 <= n <= 100                            (number of head/child lists)
  1 <= nodes in each child list <= 100
  0 <= val <= 1000
  each child list sorted non-decreasing

Output: generated-tests/flattening-of-ll.jsonl  (2000 lines)
"""
import json
import os
import random

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/flattening-of-ll.jsonl"

random.seed(20260606)

N_CASES = 2000
MAX_HEADS = 100          # 1 <= n <= 100
MAX_CHILD = 100          # 1 <= nodes per child <= 100
MIN_VAL, MAX_VAL = 0, 1000


def make_child(length):
    """A sorted (non-decreasing) child list of given length, values in range."""
    vals = [random.randint(MIN_VAL, MAX_VAL) for _ in range(length)]
    vals.sort()
    return vals


def reference(nums):
    """Ground-truth flatten: gather all vals (row-major), sort, return flat list.
    This matches the judge's ListNode(val/next) model exactly."""
    flat = []
    for row in nums:
        flat.extend(row)
    flat.sort()
    return flat


def fmt_2d(nums):
    return "[" + ", ".join("[" + ", ".join(str(v) for v in row) + "]" for row in nums) + "]"


def fmt_1d(arr):
    return "[" + ", ".join(str(v) for v in arr) + "]"


def gen_case(i):
    # A spread of structural edge cases plus random sizes.
    #
    # NOTE on sizing: the live batch judge concatenates ALL case outputs into a
    # single stdout stream that is capped at ~1MB by the runner. Constraints
    # ALLOW up to 100x100 = 10000 nodes, but emitting many huge cases blows the
    # cap and silently truncates later cases. We therefore include a SMALL set of
    # true max-constraint edge cases (indices < 8) and keep the bulk small so the
    # full 2000-case stream stays comfortably under the cap. Every input still
    # strictly satisfies the stated constraints.
    if i == 0:
        # absolute minimum: 1 head, 1 node
        nums = [[0]]
    elif i == 1:
        nums = [[MAX_VAL]]               # single node, max value
    elif i == 2:
        nums = [[0] * MAX_CHILD]         # one full child list, all zeros (100 nodes)
    elif i == 3:
        nums = [[MIN_VAL, MAX_VAL]]      # extremes together
    elif i == 4:
        # max heads, each a single node (100 nodes)
        nums = [[random.randint(MIN_VAL, MAX_VAL)] for _ in range(MAX_HEADS)]
    elif i == 5:
        # max heads, each full child list (largest total: 100 x 100 = 10000 nodes)
        nums = [make_child(MAX_CHILD) for _ in range(MAX_HEADS)]
    elif i == 6:
        # all identical values across everything
        v = random.randint(MIN_VAL, MAX_VAL)
        nums = [[v] * random.randint(1, MAX_CHILD) for _ in range(random.randint(1, 10))]
    elif i == 7:
        # already globally sorted, disjoint ranges
        nums = []
        base = 0
        for _ in range(random.randint(2, 8)):
            ln = random.randint(1, 12)
            row = sorted(random.randint(base, min(base + 50, MAX_VAL)) for _ in range(ln))
            nums.append(row)
            base = min(base + 60, MAX_VAL)
    else:
        # general random — kept small so the concatenated batch output stays
        # under the judge's ~1MB stdout cap (mean total nodes ~6).
        bucket = random.random()
        if bucket < 0.30:
            n = random.randint(1, 2)
            cmax = random.randint(1, 3)
        elif bucket < 0.92:
            n = random.randint(1, 5)
            cmax = random.randint(1, 5)
        else:
            # occasional larger case, still bounded so totals stay modest
            n = random.randint(1, 12)
            cmax = random.randint(1, 8)
        nums = [make_child(random.randint(1, cmax)) for _ in range(n)]

    # safety clamp to constraints
    assert 1 <= len(nums) <= MAX_HEADS
    for row in nums:
        assert 1 <= len(row) <= MAX_CHILD
        assert all(MIN_VAL <= v <= MAX_VAL for v in row)
        assert row == sorted(row)

    expected = reference(nums)
    return {"inputs": {"nums": fmt_2d(nums)}, "expected": fmt_1d(expected)}


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for i in range(N_CASES):
            rec = gen_case(i)
            f.write(json.dumps(rec) + "\n")
    print("wrote", N_CASES, "cases to", OUT)


if __name__ == "__main__":
    main()
