#!/usr/bin/env bash
# Test-case generator for: Longest Substring With At Most K Distinct Characters
#   slug      : longest-substring-with-at-most-k-distinct-characters
#   reference : 08. Sliding Window/2. Hard Problems/01. Longest Substring with at most K unique characters.cpp
#   mapping   : fuzzy (score 0.878)
#   entry     : kDistinctChars  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-substring-with-at-most-k-distinct-characters.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-substring-with-at-most-k-distinct-characters" --count "$COUNT" --seed "$SEED" --maxn 200
