#!/usr/bin/env bash
# Test-case generator for: Print the matrix in spiral manner
#   slug      : print-the-matrix-in-spiral-manner
#   reference : Spiral a Matrix.cpp
#   mapping   : func-name (score 1.03)
#   entry     : spiralOrder  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/print-the-matrix-in-spiral-manner.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "print-the-matrix-in-spiral-manner" --count "$COUNT" --seed "$SEED" --maxn 200
