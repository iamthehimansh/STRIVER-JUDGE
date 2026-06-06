#!/usr/bin/env bash
# Test-case generator for: Check if a Number is Odd or Not
#   slug      : check-if-a-number-is-odd-or-not
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : isOdd  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/check-if-a-number-is-odd-or-not.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-a-number-is-odd-or-not" --count "$COUNT" --seed "$SEED" --maxn 200
