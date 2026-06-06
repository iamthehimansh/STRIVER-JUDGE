#!/usr/bin/env python3
"""
Test-case generator for Striver problem: recursive-insertion-sort

Problem: Given an array of integers nums, sort the array in non-decreasing
order (recursive Insertion Sort) and return the sorted array.

Signature: vector<int> insertionSort(vector<int>& nums)
  -> single param "nums" (int array)
  -> expected: the sorted array

Constraints:
  1 <= nums.length <= 1000
  -10^4 <= nums[i] <= 10^4
  duplicates allowed

Reference oracle: the expected output is simply the non-decreasing sort of nums.
This is trivially correct (Python's stable sort produces non-decreasing order,
identical to any correct insertion sort). Verified against dataset examples.
"""
import json
import random

OUT_PATH = "/Users/iamthehimansh/Downloads/stiver'sdata/generated-tests/recursive-insertion-sort.jsonl"

LO, HI = -10**4, 10**4
MAX_N = 1000
N_CASES = 2000


def fmt_arr(a):
    return "[" + ", ".join(str(x) for x in a) + "]"


def solve(nums):
    return sorted(nums)


def gen_array(rng):
    """Produce a random array within constraints, mixing several distributions."""
    kind = rng.random()
    if kind < 0.10:
        # min size
        n = 1
    elif kind < 0.20:
        # max / near-max size
        n = rng.randint(990, MAX_N)
    elif kind < 0.40:
        n = rng.randint(1, 10)
    else:
        n = rng.randint(1, 200)

    style = rng.random()
    if style < 0.15:
        # full extreme value range
        return [rng.choice([LO, HI]) for _ in range(n)]
    elif style < 0.35:
        # heavy duplicates from a tiny pool
        pool = [rng.randint(LO, HI) for _ in range(rng.randint(1, 3))]
        return [rng.choice(pool) for _ in range(n)]
    elif style < 0.50:
        # small value window -> many dups
        base = rng.randint(LO, HI - 5)
        return [rng.randint(base, base + 5) for _ in range(n)]
    elif style < 0.65:
        # already sorted ascending
        arr = [rng.randint(LO, HI) for _ in range(n)]
        arr.sort()
        return arr
    elif style < 0.75:
        # already sorted descending (worst case for insertion sort)
        arr = [rng.randint(LO, HI) for _ in range(n)]
        arr.sort(reverse=True)
        return arr
    else:
        # uniform random over full range
        return [rng.randint(LO, HI) for _ in range(n)]


def main():
    rng = random.Random(20260606)

    cases = []
    # explicit edge cases first
    cases.append([0])
    cases.append([LO])
    cases.append([HI])
    cases.append([LO, HI])
    cases.append([HI, LO])
    cases.append([5, 5, 5, 5, 5])
    cases.append([7, 4, 1, 5, 3])          # dataset example 1
    cases.append([5, 4, 4, 1, 1])          # dataset example 2
    cases.append([3, 2, 3, 4, 5])          # dataset example 3 (unverified in ds)
    cases.append(list(range(-10, 11)))     # already sorted
    cases.append(list(range(10, -11, -1))) # reverse sorted

    while len(cases) < N_CASES:
        cases.append(gen_array(rng))

    cases = cases[:N_CASES]

    with open(OUT_PATH, "w") as f:
        for arr in cases:
            # sanity: enforce constraints
            assert 1 <= len(arr) <= MAX_N
            assert all(LO <= x <= HI for x in arr)
            rec = {
                "inputs": {"nums": fmt_arr(arr)},
                "expected": fmt_arr(solve(arr)),
            }
            f.write(json.dumps(rec) + "\n")

    print(f"Wrote {len(cases)} cases to {OUT_PATH}")


if __name__ == "__main__":
    main()
