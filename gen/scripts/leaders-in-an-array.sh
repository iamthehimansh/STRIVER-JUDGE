#!/usr/bin/env bash
# Test-case generator for: Leaders in an Array
#   slug      : leaders-in-an-array
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : leaders  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/leaders-in-an-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "leaders-in-an-array" --count "$COUNT" --seed "$SEED" --maxn 200
