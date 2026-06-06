#!/usr/bin/env bash
# Test-case generator for: Longest Bitonic Subsequence
#   slug      : longest-bitonic-subsequence
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : LongestBitonicSequence  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-bitonic-subsequence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-bitonic-subsequence" --count "$COUNT" --seed "$SEED" --maxn 200
