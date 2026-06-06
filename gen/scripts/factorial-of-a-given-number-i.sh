#!/usr/bin/env bash
# Test-case generator for: Factorial of a given number
#   slug      : factorial-of-a-given-number-i
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : factorial  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/factorial-of-a-given-number-i.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "factorial-of-a-given-number-i" --count "$COUNT" --seed "$SEED" --maxn 200
