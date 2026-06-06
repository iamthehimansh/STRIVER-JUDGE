#!/usr/bin/env bash
# Test-case generator for: Find the smallest divisor
#   slug      : find-the-smallest-divisor
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : smallestDivisor  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/find-the-smallest-divisor.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-the-smallest-divisor" --count "$COUNT" --seed "$SEED" --maxn 200
