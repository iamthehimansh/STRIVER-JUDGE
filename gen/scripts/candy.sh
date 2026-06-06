#!/usr/bin/env bash
# Test-case generator for: Candy
#   slug      : candy
#   reference : Candy.cpp
#   mapping   : func-name (score 1.03)
#   entry     : candy  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/candy.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "candy" --count "$COUNT" --seed "$SEED" --maxn 200
