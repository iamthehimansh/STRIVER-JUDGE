#!/usr/bin/env bash
# Test-case generator for: Hand of Straights
#   slug      : hand-of-straights
#   reference : Hands Of Straights.cpp
#   mapping   : func-name (score 1.03)
#   entry     : isNStraightHand  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/hand-of-straights.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "hand-of-straights" --count "$COUNT" --seed "$SEED" --maxn 200
