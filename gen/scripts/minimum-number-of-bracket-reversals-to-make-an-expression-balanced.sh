#!/usr/bin/env bash
# Test-case generator for: Minimum number of bracket reversals to make an expression balanced
#   slug      : minimum-number-of-bracket-reversals-to-make-an-expression-balanced
#   reference : Minimum Number Of Moves To make elements equal.cpp
#   mapping   : fuzzy (score 0.655)
#   entry     : minMoves2  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-number-of-bracket-reversals-to-make-an-expression-balanced.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-number-of-bracket-reversals-to-make-an-expression-balanced" --count "$COUNT" --seed "$SEED" --maxn 200
