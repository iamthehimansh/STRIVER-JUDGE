#!/usr/bin/env bash
# Test-case generator for: Next Greater Element - 2
#   slug      : next-greater-element---2
#   reference : Next Greater Element 2.cpp
#   mapping   : func-name (score 1.03)
#   entry     : nextGreaterElements  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/next-greater-element---2.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "next-greater-element---2" --count "$COUNT" --seed "$SEED" --maxn 200
