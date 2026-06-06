#!/usr/bin/env bash
# Test-case generator for: Subarrays with K Different Integers
#   slug      : subarrays-with-k-different-integers
#   reference : Subarrays with k different integers.cpp
#   mapping   : func-name (score 1.03)
#   entry     : f  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/subarrays-with-k-different-integers.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "subarrays-with-k-different-integers" --count "$COUNT" --seed "$SEED" --maxn 200
