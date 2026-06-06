#!/usr/bin/env bash
# Test-case generator for: Kth Missing Positive Number
#   slug      : kth-missing-positive-number
#   reference : kth missing Positive number.cpp
#   mapping   : func-name (score 1.03)
#   entry     : findKthPositive  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/kth-missing-positive-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "kth-missing-positive-number" --count "$COUNT" --seed "$SEED" --maxn 200
