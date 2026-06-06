#!/usr/bin/env bash
# Test-case generator for: Power Set Bit Manipulation
#   slug      : power-set-bit-manipulation
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : powerSet  ->  returns vector<vector<int>>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/power-set-bit-manipulation.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "power-set-bit-manipulation" --count "$COUNT" --seed "$SEED" --maxn 200
