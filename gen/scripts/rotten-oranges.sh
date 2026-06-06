#!/usr/bin/env bash
# Test-case generator for: Rotten Oranges
#   slug      : rotten-oranges
#   reference : Rotten Oranges(Based on BFS).cpp
#   mapping   : func-name (score 1.03)
#   entry     : orangesRotting  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/rotten-oranges.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "rotten-oranges" --count "$COUNT" --seed "$SEED" --maxn 200
