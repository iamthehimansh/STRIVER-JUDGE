#!/usr/bin/env bash
# Test-case generator for: Infix to Postfix Conversion
#   slug      : infix-to-postfix-conversion
#   reference : Infix To Postfix.cpp
#   mapping   : func-name (score 1.0)
#   entry     : infixToPostfix  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/infix-to-postfix-conversion.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "infix-to-postfix-conversion" --count "$COUNT" --seed "$SEED" --maxn 200
