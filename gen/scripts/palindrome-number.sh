#!/usr/bin/env bash
# Test-case generator for: Palindrome Number
#   slug      : palindrome-number
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : isPalindrome  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/palindrome-number.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "palindrome-number" --count "$COUNT" --seed "$SEED" --maxn 200
