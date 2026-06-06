#!/usr/bin/env bash
# Test-case generator for: Stock span problem
#   slug      : stock-span-problem
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : stockSpan  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/stock-span-problem.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "stock-span-problem" --count "$COUNT" --seed "$SEED" --maxn 200
