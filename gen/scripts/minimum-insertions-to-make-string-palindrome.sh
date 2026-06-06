#!/usr/bin/env bash
# Test-case generator for: Minimum insertions to make string palindrome | DP-29
#   slug      : minimum-insertions-to-make-string-palindrome
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : minInsertion  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-insertions-to-make-string-palindrome.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-insertions-to-make-string-palindrome" --count "$COUNT" --seed "$SEED" --maxn 200
