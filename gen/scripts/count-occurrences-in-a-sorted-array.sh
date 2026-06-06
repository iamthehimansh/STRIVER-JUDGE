#!/usr/bin/env bash
# Test-case generator for: Count Occurrences in a Sorted Array
#   slug      : count-occurrences-in-a-sorted-array
#   reference : 02.Binary Search/1D Arrays/07.Number_of_occurences.cpp
#   mapping   : func-name (score 0.999)
#   entry     : countOccurrences  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/count-occurrences-in-a-sorted-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-occurrences-in-a-sorted-array" --count "$COUNT" --seed "$SEED" --maxn 200
