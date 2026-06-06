#!/usr/bin/env bash
# Test-case generator for: Aggressive Cows
#   slug      : aggressive-cows
#   reference : Aggressive Cows Problem.cpp
#   mapping   : func-name (score 1.0)
#   entry     : aggressiveCows  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/aggressive-cows.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "aggressive-cows" --count "$COUNT" --seed "$SEED" --maxn 200
