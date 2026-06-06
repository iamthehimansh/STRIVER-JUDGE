#!/usr/bin/env bash
# Test-case generator for: Floor and Ceil in Sorted Array
#   slug      : floor-and-ceil-in-sorted-array
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : getFloorAndCeil  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/floor-and-ceil-in-sorted-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "floor-and-ceil-in-sorted-array" --count "$COUNT" --seed "$SEED" --maxn 200
