#!/usr/bin/env bash
# Test-case generator for: Lemonade Change
#   slug      : lemonade-change
#   reference : Lemonade Change.cpp
#   mapping   : func-name (score 1.03)
#   entry     : lemonadeChange  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/lemonade-change.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "lemonade-change" --count "$COUNT" --seed "$SEED" --maxn 200
