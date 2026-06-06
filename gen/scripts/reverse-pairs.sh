#!/usr/bin/env bash
# Test-case generator for: Reverse Pairs
#   slug      : reverse-pairs
#   reference : 01.Arrays/3.Hard/11.Reverse_pairs.cpp
#   mapping   : func-name (score 0.999)
#   entry     : reversePairs  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/reverse-pairs.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "reverse-pairs" --count "$COUNT" --seed "$SEED" --maxn 200
