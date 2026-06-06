#!/usr/bin/env bash
# Test-case generator for: Minimum Bit Flips to Convert Number
#   slug      : minimum-bit-flips-to-convert-number
#   reference : 06.Bit Manipulation/2. Interview Problems/01. Minimum bit flips.cpp
#   mapping   : fuzzy (score 0.8086)
#   entry     : minBitFlips  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/minimum-bit-flips-to-convert-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-bit-flips-to-convert-number" --count "$COUNT" --seed "$SEED" --maxn 200
