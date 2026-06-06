#!/usr/bin/env bash
# Test-case generator for: Longest common substring
#   slug      : longest-common-substring
#   reference : Longest Common Substring.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : findLength  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-common-substring.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-common-substring" --count "$COUNT" --seed "$SEED" --maxn 200
