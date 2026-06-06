#!/usr/bin/env bash
# Test-case generator for: Check if two strings are anagram of each other
#   slug      : valid-anagram
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : anagramStrings  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/valid-anagram.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "valid-anagram" --count "$COUNT" --seed "$SEED" --maxn 200
