#!/usr/bin/env bash
# Test-case generator for: Print subarray with maximum subarray sum (extended version of above problem)
#   slug      : kadane's-algorithm-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : maxSubArray  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/kadane's-algorithm-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "kadane's-algorithm-1" --count "$COUNT" --seed "$SEED" --maxn 200
