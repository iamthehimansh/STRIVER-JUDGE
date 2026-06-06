#!/usr/bin/env bash
# Test-case generator for: Best time to buy and sell stock II
#   slug      : best-time-to-buy-and-sell-stock-ii
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : stockBuySell  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/best-time-to-buy-and-sell-stock-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "best-time-to-buy-and-sell-stock-ii" --count "$COUNT" --seed "$SEED" --maxn 200
