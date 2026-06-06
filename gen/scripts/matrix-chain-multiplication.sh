#!/usr/bin/env bash
# Test-case generator for: Matrix chain multiplication
#   slug      : matrix-chain-multiplication
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : matrixMultiplication  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/matrix-chain-multiplication.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "matrix-chain-multiplication" --count "$COUNT" --seed "$SEED" --maxn 200
