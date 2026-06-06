#!/usr/bin/env bash
# Test-case generator for: Longest Substring Without Repeating Characters
#   slug      : longest-substring-without-repeating-characters
#   reference : Longest Substring without repeating Characters.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : lengthOfLongestSubstring  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-substring-without-repeating-characters.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-substring-without-repeating-characters" --count "$COUNT" --seed "$SEED" --maxn 200
