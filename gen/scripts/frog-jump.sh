#!/usr/bin/env bash
# Test-case generator for: Frog Jump
#   slug      : frog-jump
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : frogJump  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/frog-jump.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "frog-jump" --count "$COUNT" --seed "$SEED" --maxn 200
