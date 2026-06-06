#!/usr/bin/env bash
# Test-case generator for: Next Greater Element
#   slug      : next-greater-element
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : nextLargerElement  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/next-greater-element.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "next-greater-element" --count "$COUNT" --seed "$SEED" --maxn 200
