#!/usr/bin/env bash
# Test-case generator for: Climbing stairs
#   slug      : climbing-stairs
#   reference : Climbing Stairs.cpp
#   mapping   : func-name (score 1.03)
#   entry     : climbStairs  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/climbing-stairs.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "climbing-stairs" --count "$COUNT" --seed "$SEED" --maxn 200
