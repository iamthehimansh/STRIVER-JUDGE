#!/usr/bin/env bash
# Test-case generator for: Check if a Number is Power of 2 or Not
#   slug      : check-if-a-number-is-power-of-2-or-not
#   reference : Check If the number is power of 2.cpp
#   mapping   : func-name (score 1.03)
#   entry     : isPowerOfTwo  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/check-if-a-number-is-power-of-2-or-not.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-a-number-is-power-of-2-or-not" --count "$COUNT" --seed "$SEED" --maxn 200
