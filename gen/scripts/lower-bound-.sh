#!/usr/bin/env bash
# Test-case generator for: Lower Bound 
#   slug      : lower-bound-
#   reference : 02.Binary Search/1D Arrays/03.Implement_lower_upper_bound.cpp
#   mapping   : func-name (score 0.999)
#   entry     : lowerbound  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/lower-bound-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "lower-bound-" --count "$COUNT" --seed "$SEED" --maxn 200
