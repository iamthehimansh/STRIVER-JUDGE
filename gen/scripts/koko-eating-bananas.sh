#!/usr/bin/env bash
# Test-case generator for: Koko eating bananas
#   slug      : koko-eating-bananas
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : minimumRateToEatBananas  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/koko-eating-bananas.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "koko-eating-bananas" --count "$COUNT" --seed "$SEED" --maxn 200
