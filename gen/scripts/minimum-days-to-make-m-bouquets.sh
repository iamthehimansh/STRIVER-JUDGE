#!/usr/bin/env bash
# Test-case generator for: Minimum days to make M bouquets
#   slug      : minimum-days-to-make-m-bouquets
#   reference : 02.Binary Search/In Search Space/04.Minimum_days_to_make_boquets.cpp
#   mapping   : fuzzy (score 0.881)
#   entry     : isPossible  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-days-to-make-m-bouquets.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-days-to-make-m-bouquets" --count "$COUNT" --seed "$SEED" --maxn 200
