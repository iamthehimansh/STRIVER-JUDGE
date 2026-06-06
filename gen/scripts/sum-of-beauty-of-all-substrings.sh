#!/usr/bin/env bash
# Test-case generator for: Sum of Beauty of All Substrings
#   slug      : sum-of-beauty-of-all-substrings
#   reference : Sum Of Beauty of Substrings.cpp
#   mapping   : func-name (score 1.03)
#   entry     : beautySum  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/sum-of-beauty-of-all-substrings.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "sum-of-beauty-of-all-substrings" --count "$COUNT" --seed "$SEED" --maxn 200
