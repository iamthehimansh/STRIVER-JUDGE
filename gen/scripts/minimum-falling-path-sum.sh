#!/usr/bin/env bash
# Test-case generator for: Minimum Falling Path Sum
#   slug      : minimum-falling-path-sum
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : minFallingPathSum  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-falling-path-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-falling-path-sum" --count "$COUNT" --seed "$SEED" --maxn 200
