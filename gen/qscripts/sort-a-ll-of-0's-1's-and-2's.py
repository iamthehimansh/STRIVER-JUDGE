#!/usr/bin/env python3
"""
Generator for: Sort a Linked List of 0's 1's and 2's
slug: sort-a-ll-of-0's-1's-and-2's

Problem: given the head of a singly linked list whose nodes contain only
0, 1 or 2, sort it in-place and return the new head.

Constraints:
  0 <= number of nodes <= 1e5
  0 <= ListNode.val <= 2

Signature (starterCpp):
  ListNode* sortList(ListNode* &head)
Single param. The dataset's own testcases use the input key "linkedList"
(the judge binds positionally for a single param, so the key name is fine).

Oracle: sorting a multiset of {0,1,2} is exactly the required output, which is
identical to the counting-sort reference (10.Sort_0_1_2_in_LL.cpp / segregate()).
The judge serializes a ListNode* output as the space-separated values, and the
example outputs are written as "[0, 0, 1, 1, 2]"; we emit the bracketed form
(the judge compares leniently, ignoring brackets/commas/whitespace).

Output: ONE json object per line:
  {"inputs": {"linkedList": "[..]"}, "expected": "[..]"}
"""
import json
import random
import os

OUT = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/sort-a-ll-of-0's-1's-and-2's.jsonl"
N_CASES = 2000
MAX_NODES = 10 ** 5  # constraint upper bound (validation only)

# The judge runs all cases through a single batch process and captures stdout
# with a 1 MB cap (runner.ts `cap = 1024*1024`). Each output value prints as
# "0 1 2 ..." (~2 bytes/value), so the SUM of node counts across all 2000 cases
# must stay well under ~450k values to keep combined output < ~900 KB. We bound
# per-case sizes accordingly while still covering edge cases and a large case.
LARGE_CASE_NODES = 5000   # "big" representative case (output ~10 KB)

random.seed(20260606)


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def expected(a):
    # sorting a list of 0/1/2 == counting sort == reference output
    return sorted(a)


def gen_case(i):
    r = random.random()
    if i == 0:
        arr = []                       # empty list (0 nodes -> valid)
    elif i == 1:
        arr = [0]                      # single 0
    elif i == 2:
        arr = [2]                      # single 2
    elif i == 3:
        arr = [1]                      # single 1
    elif i == 4:
        arr = [2, 1, 0]                # reverse sorted
    elif i == 5:
        arr = [2, 2, 2, 2, 2]          # all 2s
    elif i == 6:
        arr = [0, 0, 0, 0, 0]          # all 0s
    elif i == 7:
        arr = [1, 1, 1, 1, 1]          # all 1s
    elif i == 8:
        arr = [0, 1, 2, 0, 1, 2]       # already pattern
    elif i == 9:
        # large representative case (kept modest so total batch stdout < 1 MB)
        arr = [random.randint(0, 2) for _ in range(LARGE_CASE_NODES)]
    else:
        # random sizes, biased toward small/medium with occasional larger.
        # Sizes bounded so the SUM of all outputs stays under the 1 MB cap.
        if r < 0.60:
            n = random.randint(0, 30)
        elif r < 0.88:
            n = random.randint(31, 200)
        elif r < 0.98:
            n = random.randint(201, 800)
        else:
            n = random.randint(801, 2000)
        arr = [random.randint(0, 2) for _ in range(n)]
    return arr


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    total_output_bytes = 0  # approx bytes the batch process will print for all cases
    with open(OUT, "w") as f:
        for i in range(N_CASES):
            arr = gen_case(i)
            assert 0 <= len(arr) <= MAX_NODES
            assert all(0 <= v <= 2 for v in arr)
            out = expected(arr)
            # the judge's pr(ListNode*) prints values space-separated (2 bytes/value)
            total_output_bytes += 2 * len(out) + 1
            obj = {
                "inputs": {"linkedList": fmt_arr(arr)},
                "expected": fmt_arr(out),
            }
            f.write(json.dumps(obj) + "\n")
    # the judge captures batch stdout with a 1 MB cap; stay safely under it
    assert total_output_bytes < 900_000, total_output_bytes
    print("wrote", N_CASES, "cases ->", OUT,
          "| approx batch stdout bytes:", total_output_bytes)


if __name__ == "__main__":
    main()
