#!/usr/bin/env bash
# Test-case generator for: Insert Interval
#   slug      : insert-interval
#   reference : 10. Greedy Approach/2. Medium/07. Insert Interval.cpp
#   mapping   : fuzzy (score 0.999)
#   entry     : insert  ->  returns vector<vector<int>>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/insert-interval.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "insert-interval" --count "$COUNT" --seed "$SEED" --maxn 200
