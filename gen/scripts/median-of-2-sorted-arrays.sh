#!/usr/bin/env bash
# Test-case generator for: Median of 2 sorted arrays
#   slug      : median-of-2-sorted-arrays
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : median  ->  returns double
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/median-of-2-sorted-arrays.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "median-of-2-sorted-arrays" --count "$COUNT" --seed "$SEED" --maxn 200
