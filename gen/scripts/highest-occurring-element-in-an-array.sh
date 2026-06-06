#!/usr/bin/env bash
# Test-case generator for: Highest Occurring Element in an Array
#   slug      : highest-occurring-element-in-an-array
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : mostFrequentElement  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/highest-occurring-element-in-an-array.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "highest-occurring-element-in-an-array" --count "$COUNT" --seed "$SEED" --maxn 200
