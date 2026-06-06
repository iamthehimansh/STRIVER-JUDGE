#!/usr/bin/env bash
# Test-case generator for: Trapping Rainwater
#   slug      : trapping-rainwater
#   reference : Trapping Rain Water.cpp
#   mapping   : func-name (score 1.03)
#   entry     : trap  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/trapping-rainwater.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "trapping-rainwater" --count "$COUNT" --seed "$SEED" --maxn 200
