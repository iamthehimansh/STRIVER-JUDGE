#!/usr/bin/env bash
# Test-case generator for: Count all Digits of a Number
#   slug      : count-all-digits-of-a-number
#   reference : Count Digits.cpp
#   mapping   : fuzzy (score 0.78)
#   entry     : countDigits  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/count-all-digits-of-a-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-all-digits-of-a-number" --count "$COUNT" --seed "$SEED" --maxn 200
