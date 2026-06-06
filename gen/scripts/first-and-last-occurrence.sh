#!/usr/bin/env bash
# Test-case generator for: First and last occurrence
#   slug      : first-and-last-occurrence
#   reference : Find First and last position of element in sorted array.cpp
#   mapping   : func-name (score 1.03)
#   entry     : searchRange  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/first-and-last-occurrence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "first-and-last-occurrence" --count "$COUNT" --seed "$SEED" --maxn 200
