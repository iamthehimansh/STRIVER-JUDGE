#!/usr/bin/env bash
# Test-case generator for: Longest subarray with given sum K(positives)
#   slug      : longest-subarray-with-sum-k
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : longestSubarray  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-subarray-with-sum-k.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-subarray-with-sum-k" --count "$COUNT" --seed "$SEED" --maxn 200
