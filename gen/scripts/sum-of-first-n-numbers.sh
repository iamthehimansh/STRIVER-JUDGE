#!/usr/bin/env bash
# Test-case generator for: Sum of First N Numbers
#   slug      : sum-of-first-n-numbers
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : NnumbersSum  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/sum-of-first-n-numbers.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "sum-of-first-n-numbers" --count "$COUNT" --seed "$SEED" --maxn 200
