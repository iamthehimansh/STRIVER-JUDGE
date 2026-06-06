#!/usr/bin/env bash
# Test-case generator for:  Max Consecutive Ones III
#   slug      : max-consecutive-ones-iii
#   reference : Max Consecutive Ones III.cpp
#   mapping   : func-name (score 1.03)
#   entry     : longestOnes  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/max-consecutive-ones-iii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "max-consecutive-ones-iii" --count "$COUNT" --seed "$SEED" --maxn 200
