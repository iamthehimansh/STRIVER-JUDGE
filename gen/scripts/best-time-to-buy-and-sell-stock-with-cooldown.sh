#!/usr/bin/env bash
# Test-case generator for: Best Time to Buy and Sell Stock with Cooldown
#   slug      : best-time-to-buy-and-sell-stock-with-cooldown
#   reference : Best Time to Buy and Sell Stock II.cpp
#   mapping   : func-name (score 1.03)
#   entry     : maxProfit  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/best-time-to-buy-and-sell-stock-with-cooldown.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "best-time-to-buy-and-sell-stock-with-cooldown" --count "$COUNT" --seed "$SEED" --maxn 200
