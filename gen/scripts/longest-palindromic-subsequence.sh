#!/usr/bin/env bash
# Test-case generator for: Longest palindromic subsequence
#   slug      : longest-palindromic-subsequence
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : longestPalinSubseq  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-palindromic-subsequence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-palindromic-subsequence" --count "$COUNT" --seed "$SEED" --maxn 200
