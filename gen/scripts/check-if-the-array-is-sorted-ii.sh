#!/usr/bin/env bash
# Test-case generator for: Check if the Array is Sorted II
#   slug      : check-if-the-array-is-sorted-ii
#   reference : 3. Arrays/1. Easy/3.1.3. Check if the array is sorted.cpp
#   mapping   : func-name (score 0.998)
#   entry     : isSorted  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/check-if-the-array-is-sorted-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-the-array-is-sorted-ii" --count "$COUNT" --seed "$SEED" --maxn 200
