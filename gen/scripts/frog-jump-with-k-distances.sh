#!/usr/bin/env bash
# Test-case generator for: Frog jump with K distances
#   slug      : frog-jump-with-k-distances
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : frogJump  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/frog-jump-with-k-distances.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "frog-jump-with-k-distances" --count "$COUNT" --seed "$SEED" --maxn 200
