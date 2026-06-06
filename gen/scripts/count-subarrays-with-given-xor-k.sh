#!/usr/bin/env bash
# Test-case generator for: Count subarrays with given xor K
#   slug      : count-subarrays-with-given-xor-k
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : subarraysWithXorK  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/count-subarrays-with-given-xor-k.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-subarrays-with-given-xor-k" --count "$COUNT" --seed "$SEED" --maxn 200
