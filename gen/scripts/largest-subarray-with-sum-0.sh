#!/usr/bin/env bash
# Test-case generator for: Largest Subarray with Sum 0
#   slug      : largest-subarray-with-sum-0
#   reference : Largest Subarray with zero Sum.cpp
#   mapping   : func-name (score 1.03)
#   entry     : maxLen  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/largest-subarray-with-sum-0.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "largest-subarray-with-sum-0" --count "$COUNT" --seed "$SEED" --maxn 200
