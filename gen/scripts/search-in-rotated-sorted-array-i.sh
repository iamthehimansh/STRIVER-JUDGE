#!/usr/bin/env bash
# Test-case generator for: Search in rotated sorted array-I
#   slug      : search-in-rotated-sorted-array-i
#   reference : 02.Binary Search/1D Arrays/09.Search_in_rotated_sorted_array.cpp
#   mapping   : fuzzy (score 0.9813)
#   entry     : search  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-in-rotated-sorted-array-i.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-in-rotated-sorted-array-i" --count "$COUNT" --seed "$SEED" --maxn 200
