#!/usr/bin/env bash
# Test-case generator for: Count number of Nice subarrays
#   slug      : count-number-of-nice-subarrays
#   reference : Count Number of Subarrays.cpp
#   mapping   : fuzzy (score 0.98)
#   entry     : f  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/count-number-of-nice-subarrays.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-number-of-nice-subarrays" --count "$COUNT" --seed "$SEED" --maxn 200
