#!/usr/bin/env bash
# Test-case generator for: Split array - largest sum
#   slug      : split-array---largest-sum
#   reference : Split Array Largest Sum.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : splitArray  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/split-array---largest-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "split-array---largest-sum" --count "$COUNT" --seed "$SEED" --maxn 200
