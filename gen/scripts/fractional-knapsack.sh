#!/usr/bin/env bash
# Test-case generator for: Fractional Knapsack
#   slug      : fractional-knapsack
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : fractionalKnapsack  ->  returns double
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/fractional-knapsack.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "fractional-knapsack" --count "$COUNT" --seed "$SEED" --maxn 200
