#!/usr/bin/env bash
# Test-case generator for: Next Smaller Element
#   slug      : next-smaller-element
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : nextSmallerElements  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/next-smaller-element.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "next-smaller-element" --count "$COUNT" --seed "$SEED" --maxn 200
