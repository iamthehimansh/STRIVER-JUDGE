#!/usr/bin/env bash
# Test-case generator for: Longest Increasing Subsequence |(DP-43)
#   slug      : longest-increasing-subsequence-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : LIS  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-increasing-subsequence-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-increasing-subsequence-1" --count "$COUNT" --seed "$SEED" --maxn 200
