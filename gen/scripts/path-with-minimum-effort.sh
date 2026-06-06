#!/usr/bin/env bash
# Test-case generator for: Path with minimum effort
#   slug      : path-with-minimum-effort
#   reference : 13. Graphs/4. Shortest Path Problems/05. Path with minimum effort.cpp
#   mapping   : fuzzy (score 0.999)
#   entry     : minimumEffortPath  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/path-with-minimum-effort.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "path-with-minimum-effort" --count "$COUNT" --seed "$SEED" --maxn 200
