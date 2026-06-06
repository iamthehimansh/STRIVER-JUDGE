#!/usr/bin/env bash
# Test-case generator for: Check if the i-th bit is Set or Not
#   slug      : check-if-the-i-th-bit-is-set-or-not
#   reference : 06.Bit Manipulation/1. Learn Bit Manipulation/02.Check for the ith bit.cpp
#   mapping   : fuzzy (score 0.6422)
#   entry     : checkKthBit  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/check-if-the-i-th-bit-is-set-or-not.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-the-i-th-bit-is-set-or-not" --count "$COUNT" --seed "$SEED" --maxn 200
