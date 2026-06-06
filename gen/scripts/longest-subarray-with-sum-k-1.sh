#!/usr/bin/env bash
# Test-case generator for: Longest subarray with sum K
#   slug      : longest-subarray-with-sum-k-1
#   reference : Continuous Subarray Sum.cpp
#   mapping   : fuzzy (score 0.682)
#   entry     : checkSubarraySum  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-subarray-with-sum-k-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-subarray-with-sum-k-1" --count "$COUNT" --seed "$SEED" --maxn 200
