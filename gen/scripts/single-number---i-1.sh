#!/usr/bin/env bash
# Test-case generator for: Single Number - I
#   slug      : single-number---i-1
#   reference : Single Number.cpp
#   mapping   : fuzzy (score 0.9907)
#   entry     : singleNumber  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/single-number---i-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "single-number---i-1" --count "$COUNT" --seed "$SEED" --maxn 200
