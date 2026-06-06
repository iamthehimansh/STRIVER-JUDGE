#!/usr/bin/env bash
# Test-case generator for: Target sum
#   slug      : target-sum
#   reference : Target Sum.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : findTargetSumWays  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/target-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "target-sum" --count "$COUNT" --seed "$SEED" --maxn 200
