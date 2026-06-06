#!/usr/bin/env bash
# Test-case generator for: Assign Cookies
#   slug      : assign-cookies-1
#   reference : Assign Cookies.cpp
#   mapping   : fuzzy (score 1.03)
#   entry     : findContentChildren  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/assign-cookies-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "assign-cookies-1" --count "$COUNT" --seed "$SEED" --maxn 200
