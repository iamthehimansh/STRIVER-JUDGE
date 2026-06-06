#!/usr/bin/env bash
# Test-case generator for: Swim in Rising Water
#   slug      : swim-in-rising-water
#   reference : 13. Graphs/5. MST Problems/08. Swim in rising water.cpp
#   mapping   : func-name (score 0.999)
#   entry     : swimInWater  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/swim-in-rising-water.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "swim-in-rising-water" --count "$COUNT" --seed "$SEED" --maxn 200
