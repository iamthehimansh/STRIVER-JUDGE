#!/usr/bin/env bash
# Test-case generator for: Number of Longest Increasing Subsequences
#   slug      : number-of-longest-increasing-subsequences
#   reference : Number of longest increasing subsequences.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : findNumberOfLIS  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/number-of-longest-increasing-subsequences.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "number-of-longest-increasing-subsequences" --count "$COUNT" --seed "$SEED" --maxn 200
