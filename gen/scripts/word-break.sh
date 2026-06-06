#!/usr/bin/env bash
# Test-case generator for: Word Break
#   slug      : word-break
#   reference : 05.Recursion/3.Try Out All Combos/06.Word Break.cpp
#   mapping   : func-name (score 0.999)
#   entry     : wordBreak  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/word-break.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "word-break" --count "$COUNT" --seed "$SEED" --maxn 200
