#!/usr/bin/env bash
# Test-case generator for: Valid Paranthesis Checker
#   slug      : valid-paranthesis-checker
#   reference : Valid Parenthesis.cpp
#   mapping   : fuzzy (score 0.674)
#   entry     : isValid  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/valid-paranthesis-checker.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "valid-paranthesis-checker" --count "$COUNT" --seed "$SEED" --maxn 200
