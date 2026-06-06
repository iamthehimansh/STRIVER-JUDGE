#!/usr/bin/env bash
# Test-case generator for: Search X in sorted array
#   slug      : search-x-in-sorted-array
#   reference : 02.Binary Search/1D Arrays/01.Find_x_in_sorted_array.cpp
#   mapping   : fuzzy (score 0.7894)
#   entry     : search  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-x-in-sorted-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-x-in-sorted-array" --count "$COUNT" --seed "$SEED" --maxn 200
