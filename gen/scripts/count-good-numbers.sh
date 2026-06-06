#!/usr/bin/env bash
# Test-case generator for: Count Good Numbers
#   slug      : count-good-numbers
#   reference : Count Good Numbers.cpp
#   mapping   : func-name (score 1.03)
#   entry     : countGoodNumbers  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/count-good-numbers.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-good-numbers" --count "$COUNT" --seed "$SEED" --maxn 200
