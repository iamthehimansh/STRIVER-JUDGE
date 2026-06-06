#!/usr/bin/env bash
# Test-case generator for: Search insert position
#   slug      : search-insert-position
#   reference : Search Insert Position.cpp
#   mapping   : func-name (score 1.03)
#   entry     : searchInsert  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/search-insert-position.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "search-insert-position" --count "$COUNT" --seed "$SEED" --maxn 200
