#!/usr/bin/env bash
# Test-case generator for: House robber
#   slug      : house-robber
#   reference : 14. Dynamic Programming/2. 1D DP/04. House Robber.cpp
#   mapping   : fuzzy (score 0.999)
#   entry     : rob  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/house-robber.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "house-robber" --count "$COUNT" --seed "$SEED" --maxn 200
