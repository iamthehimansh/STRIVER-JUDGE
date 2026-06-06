#!/usr/bin/env bash
# Test-case generator for: Search in 2D matrix - II
#   slug      : search-in-2d-matrix-ii
#   reference : Search in a 2D matrix II.cpp
#   mapping   : fuzzy (score 0.9311)
#   entry     : searchMatrix  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-in-2d-matrix-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-in-2d-matrix-ii" --count "$COUNT" --seed "$SEED" --maxn 200
