#!/usr/bin/env bash
# Test-case generator for: Quick Sorting
#   slug      : quick-sorting
#   reference : QuickSort.cpp
#   mapping   : func-name (score 1.0)
#   entry     : quickSort  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/quick-sorting.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "quick-sorting" --count "$COUNT" --seed "$SEED" --maxn 200
