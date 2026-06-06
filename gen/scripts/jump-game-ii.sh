#!/usr/bin/env bash
# Test-case generator for: Jump Game II
#   slug      : jump-game-ii
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : jump  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/jump-game-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "jump-game-ii" --count "$COUNT" --seed "$SEED" --maxn 200
