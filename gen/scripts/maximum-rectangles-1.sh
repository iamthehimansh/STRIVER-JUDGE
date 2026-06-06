#!/usr/bin/env bash
# Test-case generator for: Maximum Rectangle Area with all 1's|(DP-55)
#   slug      : maximum-rectangles-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : maximalAreaOfSubMatrixOfAll1  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-rectangles-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-rectangles-1" --count "$COUNT" --seed "$SEED" --maxn 200
