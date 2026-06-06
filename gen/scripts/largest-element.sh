#!/usr/bin/env bash
# Test-case generator for: Largest Element 
#   slug      : largest-element
#   reference : 3. Arrays/1. Easy/3.1.1. Largest Element in an Array.cpp
#   mapping   : func-name (score 0.998)
#   entry     : largestElement  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/largest-element.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "largest-element" --count "$COUNT" --seed "$SEED" --maxn 200
