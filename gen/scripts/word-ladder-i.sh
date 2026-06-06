#!/usr/bin/env bash
# Test-case generator for: Word ladder I
#   slug      : word-ladder-i
#   reference : Word Ladder.cpp
#   mapping   : fuzzy (score 0.9842)
#   entry     : ladderLength  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/word-ladder-i.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "word-ladder-i" --count "$COUNT" --seed "$SEED" --maxn 200
