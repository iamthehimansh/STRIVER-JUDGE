#!/usr/bin/env bash
# Test-case generator for: Maximum Product Subarray in an Array
#   slug      : maximum-product-subarray-in-an-array
#   reference : Maximum Product Subarray.cpp
#   mapping   : func-name (score 1.03)
#   entry     : maxProduct  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-product-subarray-in-an-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-product-subarray-in-an-array" --count "$COUNT" --seed "$SEED" --maxn 200
