#!/usr/bin/env bash
# Test-case generator for: Longest Consecutive Sequence in an Array
#   slug      : longest-consecutive-sequence-in-an-array
#   reference : Longest Consecutive Sequence.cpp
#   mapping   : func-name (score 1.03)
#   entry     : longestConsecutive  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-consecutive-sequence-in-an-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-consecutive-sequence-in-an-array" --count "$COUNT" --seed "$SEED" --maxn 200
