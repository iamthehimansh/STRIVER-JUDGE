#!/usr/bin/env bash
# Test-case generator for: Largest rectangle in a histogram
#   slug      : largest-rectangle-in-a-histogram
#   reference : Largest Rectangle in Histogram.cpp
#   mapping   : func-name (score 1.03)
#   entry     : largestRectangleArea  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/largest-rectangle-in-a-histogram.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "largest-rectangle-in-a-histogram" --count "$COUNT" --seed "$SEED" --maxn 200
