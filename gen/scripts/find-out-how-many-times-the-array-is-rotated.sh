#!/usr/bin/env bash
# Test-case generator for: Find out how many times the array is rotated
#   slug      : find-out-how-many-times-the-array-is-rotated
#   reference : Count Number of rotations in rotated sorted array.cpp
#   mapping   : func-name (score 1.0)
#   entry     : findKRotation  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/find-out-how-many-times-the-array-is-rotated.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "find-out-how-many-times-the-array-is-rotated" --count "$COUNT" --seed "$SEED" --maxn 200
