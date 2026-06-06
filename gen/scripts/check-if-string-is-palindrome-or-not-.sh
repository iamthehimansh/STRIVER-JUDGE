#!/usr/bin/env bash
# Test-case generator for: Check if String is Palindrome or Not 
#   slug      : check-if-string-is-palindrome-or-not-
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : palindromeCheck  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/check-if-string-is-palindrome-or-not-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-string-is-palindrome-or-not-" --count "$COUNT" --seed "$SEED" --maxn 200
