#!/usr/bin/env bash
# Test-case generator for: Number of islands II
#   slug      : number-of-islands-ii
#   reference : 13. Graphs/5. MST Problems/06. Number of islands 2.cpp
#   mapping   : func-name (score 0.999)
#   entry     : isLand  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/number-of-islands-ii.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "number-of-islands-ii" --count "$COUNT" --seed "$SEED" --maxn 200
