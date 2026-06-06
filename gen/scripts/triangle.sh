#!/usr/bin/env bash
# Test-case generator for: Triangle
#   slug      : triangle
#   reference : Triangle.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : minimumTotal  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/triangle.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "triangle" --count "$COUNT" --seed "$SEED" --maxn 200
