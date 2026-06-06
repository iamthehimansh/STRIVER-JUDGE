#!/usr/bin/env bash
# Test-case generator for: Check if an array represents a min heap 
#   slug      : check-if-an-array-represents-a-min-heap-
#   reference : Check if the array represents heap or not.cpp
#   mapping   : fuzzy (score 0.7375)
#   entry     : isMaxHeap  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/check-if-an-array-represents-a-min-heap-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-an-array-represents-a-min-heap-" --count "$COUNT" --seed "$SEED" --maxn 200
