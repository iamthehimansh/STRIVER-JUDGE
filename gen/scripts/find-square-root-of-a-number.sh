#!/usr/bin/env bash
# Test-case generator for: Find square root of a number
#   slug      : find-square-root-of-a-number
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : floorSqrt  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/find-square-root-of-a-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-square-root-of-a-number" --count "$COUNT" --seed "$SEED" --maxn 200
