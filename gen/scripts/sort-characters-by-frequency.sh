#!/usr/bin/env bash
# Test-case generator for: Sort Characters by Frequency
#   slug      : sort-characters-by-frequency
#   reference : Sort Characters by frequency.cpp
#   mapping   : func-name (score 1.03)
#   entry     : frequencySort  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/sort-characters-by-frequency.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "sort-characters-by-frequency" --count "$COUNT" --seed "$SEED" --maxn 200
