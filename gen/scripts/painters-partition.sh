#!/usr/bin/env bash
# Test-case generator for: Painter's Partition
#   slug      : painters-partition
#   reference : Painter's Partition.cpp
#   mapping   : fuzzy (score 0.7901)
#   entry     : f  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/painters-partition.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "painters-partition" --count "$COUNT" --seed "$SEED" --maxn 200
