#!/usr/bin/env bash
# Test-case generator for: Largest Odd Number in a String
#   slug      : largest-odd-number-in-a-string
#   reference : Largest Odd Number In a string.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : largestOddNumber  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/largest-odd-number-in-a-string.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "largest-odd-number-in-a-string" --count "$COUNT" --seed "$SEED" --maxn 200
