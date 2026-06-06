#!/usr/bin/env bash
# Test-case generator for: Find minimum in Rotated Sorted Array
#   slug      : find-minimum-in-rotated-sorted-array
#   reference : Minimum in a rotated sorted array.cpp
#   mapping   : func-name (score 1.03)
#   entry     : findMin  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/find-minimum-in-rotated-sorted-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-minimum-in-rotated-sorted-array" --count "$COUNT" --seed "$SEED" --maxn 200
