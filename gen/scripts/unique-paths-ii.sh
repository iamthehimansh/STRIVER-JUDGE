#!/usr/bin/env bash
# Test-case generator for: Unique paths II
#   slug      : unique-paths-ii
#   reference : Unique Paths 2.cpp
#   mapping   : func-name (score 1.03)
#   entry     : uniquePathsWithObstacles  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/unique-paths-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "unique-paths-ii" --count "$COUNT" --seed "$SEED" --maxn 200
