#!/usr/bin/env bash
# Test-case generator for: Recursive Bubble Sort
#   slug      : recursive-bubble-sort
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : bubbleSort  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/recursive-bubble-sort.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "recursive-bubble-sort" --count "$COUNT" --seed "$SEED" --maxn 200
