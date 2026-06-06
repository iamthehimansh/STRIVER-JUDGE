#!/usr/bin/env bash
# Test-case generator for:  Fruit Into Baskets
#   slug      : fruit-into-baskets
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : totalFruits  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/fruit-into-baskets.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "fruit-into-baskets" --count "$COUNT" --seed "$SEED" --maxn 200
