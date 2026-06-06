#!/usr/bin/env bash
# Test-case generator for: Union of two sorted arrays
#   slug      : union-of-two-sorted-arrays
#   reference : Union of two sorted arrays.cpp
#   mapping   : func-name (score 1.03)
#   entry     : unionArray  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/union-of-two-sorted-arrays.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "union-of-two-sorted-arrays" --count "$COUNT" --seed "$SEED" --maxn 200
