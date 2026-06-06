#!/usr/bin/env bash
# Test-case generator for: Kth element of 2 sorted arrays
#   slug      : kth-element-of-2-sorted-arrays
#   reference : 02.Binary Search/In Search Space/14.Kth_element_of_two_sorted_arrays.cpp
#   mapping   : func-name (score 0.999)
#   entry     : kthElement  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/kth-element-of-2-sorted-arrays.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "kth-element-of-2-sorted-arrays" --count "$COUNT" --seed "$SEED" --maxn 200
