#!/usr/bin/env bash
# Test-case generator for: Sum of Subarray Ranges
#   slug      : sum-of-subarray-ranges
#   reference : 07.Stack and Queues/3. Monotonic Stack and Queue/06. Sum of range of all subarray.cpp
#   mapping   : func-name (score 0.999)
#   entry     : subArrayRanges  ->  returns long long
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/sum-of-subarray-ranges.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "sum-of-subarray-ranges" --count "$COUNT" --seed "$SEED" --maxn 200
