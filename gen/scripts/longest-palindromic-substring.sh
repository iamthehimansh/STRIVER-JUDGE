#!/usr/bin/env bash
# Test-case generator for: Longest Palindromic Substring
#   slug      : longest-palindromic-substring
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : longestPalindrome  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-palindromic-substring.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-palindromic-substring" --count "$COUNT" --seed "$SEED" --maxn 200
