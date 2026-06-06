#!/usr/bin/env bash
# Test-case generator for: Find peak element
#   slug      : find-peak-element
#   reference : Find peak element.cpp
#   mapping   : func-name (score 1.03)
#   entry     : findPeakElement  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/find-peak-element.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-peak-element" --count "$COUNT" --seed "$SEED" --maxn 200
