#!/usr/bin/env bash
# Test-case generator for: Search in a 2D matrix
#   slug      : search-in-a-2d-matrix
#   reference : Search a 2D matrix.cpp
#   mapping   : fuzzy (score 0.9877)
#   entry     : f  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-in-a-2d-matrix.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-in-a-2d-matrix" --count "$COUNT" --seed "$SEED" --maxn 200
