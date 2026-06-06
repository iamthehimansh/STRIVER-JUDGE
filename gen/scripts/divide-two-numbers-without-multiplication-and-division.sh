#!/usr/bin/env bash
# Test-case generator for: Divide two numbers without multiplication and division
#   slug      : divide-two-numbers-without-multiplication-and-division
#   reference : Divide two integers without using multiplication and division sign.cpp
#   mapping   : func-name (score 1.03)
#   entry     : divide  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/divide-two-numbers-without-multiplication-and-division.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "divide-two-numbers-without-multiplication-and-division" --count "$COUNT" --seed "$SEED" --maxn 200
