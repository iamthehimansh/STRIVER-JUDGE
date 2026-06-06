#!/usr/bin/env bash
# Test-case generator for: Insertion Sorting
#   slug      : insertion-sorting
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : insertionSort  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/insertion-sorting.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "insertion-sorting" --count "$COUNT" --seed "$SEED" --maxn 200
