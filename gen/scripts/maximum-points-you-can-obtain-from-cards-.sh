#!/usr/bin/env bash
# Test-case generator for: Maximum Points You Can Obtain from Cards 
#   slug      : maximum-points-you-can-obtain-from-cards-
#   reference : Maximum Points You can obtain from cards.cpp
#   mapping   : func-name (score 1.03)
#   entry     : maxScore  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-points-you-can-obtain-from-cards-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-points-you-can-obtain-from-cards-" --count "$COUNT" --seed "$SEED" --maxn 200
