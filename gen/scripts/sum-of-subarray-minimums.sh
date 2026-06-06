#!/usr/bin/env bash
# Test-case generator for: Sum of Subarray Minimums
#   slug      : sum-of-subarray-minimums
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : sumSubarrayMins  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/sum-of-subarray-minimums.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "sum-of-subarray-minimums" --count "$COUNT" --seed "$SEED" --maxn 200
