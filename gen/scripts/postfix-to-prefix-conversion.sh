#!/usr/bin/env bash
# Test-case generator for: Postfix to Prefix Conversion
#   slug      : postfix-to-prefix-conversion
#   reference : 07.Stack and Queues/2. Infix, Postfix, and Prefix/06. Postfix to prefix.cpp
#   mapping   : func-name (score 0.999)
#   entry     : isAlphaNumeric  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/postfix-to-prefix-conversion.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "postfix-to-prefix-conversion" --count "$COUNT" --seed "$SEED" --maxn 200
