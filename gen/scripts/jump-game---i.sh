#!/usr/bin/env bash
# Test-case generator for: Jump Game - I
#   slug      : jump-game---i
#   reference : Jump Game 1.cpp
#   mapping   : func-name (score 1.03)
#   entry     : canJump  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/jump-game---i.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "jump-game---i" --count "$COUNT" --seed "$SEED" --maxn 200
