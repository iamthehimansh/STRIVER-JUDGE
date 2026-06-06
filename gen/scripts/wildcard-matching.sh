#!/usr/bin/env bash
# Test-case generator for: Wildcard matching
#   slug      : wildcard-matching
#   reference : Wildcard matching.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : isMatch  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/wildcard-matching.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "wildcard-matching" --count "$COUNT" --seed "$SEED" --maxn 200
