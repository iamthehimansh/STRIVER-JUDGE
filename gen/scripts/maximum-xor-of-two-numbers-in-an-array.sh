#!/usr/bin/env bash
# Test-case generator for: Maximum XOR of two numbers in an array
#   slug      : maximum-xor-of-two-numbers-in-an-array
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : findMaximumXOR  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-xor-of-two-numbers-in-an-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-xor-of-two-numbers-in-an-array" --count "$COUNT" --seed "$SEED" --maxn 200
