#!/usr/bin/env bash
# Test-case generator for: Print Longest Increasing Subsequence
#   slug      : print-longest-increasing-subsequence
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : longestIncreasingSubsequence  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/print-longest-increasing-subsequence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "print-longest-increasing-subsequence" --count "$COUNT" --seed "$SEED" --maxn 200
