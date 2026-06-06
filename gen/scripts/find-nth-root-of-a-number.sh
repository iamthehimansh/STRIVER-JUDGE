#!/usr/bin/env bash
# Test-case generator for: Find Nth root of a number
#   slug      : find-nth-root-of-a-number
#   reference : 02.Binary Search/In Search Space/02.Nth_root_of_integer.cpp
#   mapping   : func-name (score 0.999)
#   entry     : NthRoot  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/find-nth-root-of-a-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-nth-root-of-a-number" --count "$COUNT" --seed "$SEED" --maxn 200
