#!/usr/bin/env bash
# Test-case generator for: Grid Unique Paths : DP on Grids (DP8)
#   slug      : grid-unique-paths
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : uniquePaths  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/grid-unique-paths.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "grid-unique-paths" --count "$COUNT" --seed "$SEED" --maxn 200
