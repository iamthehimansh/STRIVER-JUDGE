#!/usr/bin/env bash
# Test-case generator for: Search in rotated sorted array-II
#   slug      : search-in-rotated-sorted-array-2
#   reference : 02.Binary Search/1D Arrays/10.Search_in_rotated_sorted_array_with_duplicates.cpp
#   mapping   : fuzzy (score 0.7799)
#   entry     : search  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-in-rotated-sorted-array-2.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-in-rotated-sorted-array-2" --count "$COUNT" --seed "$SEED" --maxn 200
