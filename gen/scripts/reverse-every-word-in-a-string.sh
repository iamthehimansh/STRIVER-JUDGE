#!/usr/bin/env bash
# Test-case generator for: Reverse words in a given string / Palindrome Check
#   slug      : reverse-every-word-in-a-string
#   reference : 03.Strings/1.Easy/02.Reverse_words_in_string.cpp
#   mapping   : fuzzy (score 0.8053)
#   entry     : reverseWords  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/reverse-every-word-in-a-string.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "reverse-every-word-in-a-string" --count "$COUNT" --seed "$SEED" --maxn 200
