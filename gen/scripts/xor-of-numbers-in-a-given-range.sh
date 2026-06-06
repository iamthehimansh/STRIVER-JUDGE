#!/usr/bin/env bash
# Test-case generator for: XOR of numbers in a given range
#   slug      : xor-of-numbers-in-a-given-range
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : findRangeXOR  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/xor-of-numbers-in-a-given-range.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "xor-of-numbers-in-a-given-range" --count "$COUNT" --seed "$SEED" --maxn 200
