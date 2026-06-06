#!/usr/bin/env bash
# Test-case generator for: Maximum sum of non adjacent elements
#   slug      : maximum-sum-of-non-adjacent-elements
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : nonAdjacent  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-sum-of-non-adjacent-elements.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-sum-of-non-adjacent-elements" --count "$COUNT" --seed "$SEED" --maxn 200
