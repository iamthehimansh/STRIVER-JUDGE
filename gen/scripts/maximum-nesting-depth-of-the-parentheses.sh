#!/usr/bin/env bash
# Test-case generator for: Maximum Nesting Depth of the Parentheses
#   slug      : maximum-nesting-depth-of-the-parentheses
#   reference : Maximum Nesting Depth of parenthesis.cpp
#   mapping   : fuzzy (score 0.8966)
#   entry     : maxDepth  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-nesting-depth-of-the-parentheses.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-nesting-depth-of-the-parentheses" --count "$COUNT" --seed "$SEED" --maxn 200
