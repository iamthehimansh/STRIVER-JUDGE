#!/usr/bin/env bash
# Test-case generator for: Prefix to Infix Conversion
#   slug      : prefix-to-infix-conversion
#   reference : Prefix to Infix.cpp
#   mapping   : fuzzy (score 0.8524)
#   entry     : prefixToInfixConversion  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/prefix-to-infix-conversion.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "prefix-to-infix-conversion" --count "$COUNT" --seed "$SEED" --maxn 200
