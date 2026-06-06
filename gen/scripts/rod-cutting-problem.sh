#!/usr/bin/env bash
# Test-case generator for: Rod Cutting Problem | (DP - 24)
#   slug      : rod-cutting-problem
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : rodCutting  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/rod-cutting-problem.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "rod-cutting-problem" --count "$COUNT" --seed "$SEED" --maxn 200
