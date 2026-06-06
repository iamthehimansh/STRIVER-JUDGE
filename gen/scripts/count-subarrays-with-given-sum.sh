#!/usr/bin/env bash
# Test-case generator for: Count subarrays with given sum
#   slug      : count-subarrays-with-given-sum
#   reference : SubArraySum equalsK.cpp
#   mapping   : func-name (score 1.03)
#   entry     : subarraySum  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/count-subarrays-with-given-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-subarrays-with-given-sum" --count "$COUNT" --seed "$SEED" --maxn 200
