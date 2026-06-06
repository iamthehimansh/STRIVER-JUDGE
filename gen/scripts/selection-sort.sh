#!/usr/bin/env bash
# Test-case generator for: Selection Sort
#   slug      : selection-sort
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : selectionSort  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/selection-sort.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "selection-sort" --count "$COUNT" --seed "$SEED" --maxn 200
