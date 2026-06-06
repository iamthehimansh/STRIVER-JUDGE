#!/usr/bin/env bash
# Test-case generator for: Best time to buy and sell stock
#   slug      : best-time-to-buy-and-sell-stock-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : stockBuySell  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/best-time-to-buy-and-sell-stock-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "best-time-to-buy-and-sell-stock-1" --count "$COUNT" --seed "$SEED" --maxn 200
