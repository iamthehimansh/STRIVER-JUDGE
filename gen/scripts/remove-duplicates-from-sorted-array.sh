#!/usr/bin/env bash
# Test-case generator for: Remove duplicates from Sorted array
#   slug      : remove-duplicates-from-sorted-array
#   reference : Remove duplicates from sorted array.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : removeDuplicates  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/remove-duplicates-from-sorted-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "remove-duplicates-from-sorted-array" --count "$COUNT" --seed "$SEED" --maxn 200
