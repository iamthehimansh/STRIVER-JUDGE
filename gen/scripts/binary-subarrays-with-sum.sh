#!/usr/bin/env bash
# Test-case generator for: Binary Subarrays With Sum
#   slug      : binary-subarrays-with-sum
#   reference : Binary Subarray With Sum.cpp
#   mapping   : func-name (score 1.03)
#   entry     : func  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/binary-subarrays-with-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "binary-subarrays-with-sum" --count "$COUNT" --seed "$SEED" --maxn 200
