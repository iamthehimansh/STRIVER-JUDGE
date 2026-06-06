#!/usr/bin/env bash
# Test-case generator for: Kadane's Algorithm
#   slug      : kadane's-algorithm
#   reference : 01.Arrays/2.Medium/04.Kadane's_algorithm.cpp
#   mapping   : fuzzy (score 0.7583)
#   entry     : maxSubArray  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/kadane's-algorithm.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "kadane's-algorithm" --count "$COUNT" --seed "$SEED" --maxn 200
