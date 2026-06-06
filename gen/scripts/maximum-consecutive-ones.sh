#!/usr/bin/env bash
# Test-case generator for: Maximum Consecutive Ones
#   slug      : maximum-consecutive-ones
#   reference : Max Consecutive Ones.cpp
#   mapping   : func-name (score 1.03)
#   entry     : findMaxConsecutiveOnes  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/maximum-consecutive-ones.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "maximum-consecutive-ones" --count "$COUNT" --seed "$SEED" --maxn 200
