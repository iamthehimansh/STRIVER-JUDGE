#!/usr/bin/env bash
# Test-case generator for: Partition Array for Maximum Sum
#   slug      : partition-array-for-maximum-sum
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : maxSumAfterPartitioning  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/partition-array-for-maximum-sum.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "partition-array-for-maximum-sum" --count "$COUNT" --seed "$SEED" --maxn 200
