#!/usr/bin/env bash
# Test-case generator for: Reverse every word in a string
#   slug      : reverse-every-word-in-a-string-1
#   reference : Reverse Words in a string.cpp
#   mapping   : fuzzy (score 0.87)
#   entry     : reverseWords  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/reverse-every-word-in-a-string-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "reverse-every-word-in-a-string-1" --count "$COUNT" --seed "$SEED" --maxn 200
