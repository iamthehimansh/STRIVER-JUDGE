#!/usr/bin/env bash
# Test-case generator for: Find row with maximum 1's
#   slug      : find-row-with-maximum-1's
#   reference : 02.Binary Search/2D Arrays/1.Row_with_maximum_number_of_1's.cpp
#   mapping   : func-name (score 0.999)
#   entry     : rowWithMax1s  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/find-row-with-maximum-1's.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-row-with-maximum-1's" --count "$COUNT" --seed "$SEED" --maxn 200
