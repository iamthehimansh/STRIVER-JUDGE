#!/usr/bin/env bash
# Test-case generator for: Roman to Integer
#   slug      : roman-to-integer
#   reference : Roman Number to integer.cpp
#   mapping   : func-name (score 1.03)
#   entry     : romanToInt  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/roman-to-integer.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "roman-to-integer" --count "$COUNT" --seed "$SEED" --maxn 200
