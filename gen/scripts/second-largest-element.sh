#!/usr/bin/env bash
# Test-case generator for: Second Largest Element
#   slug      : second-largest-element
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : secondLargestElement  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/second-largest-element.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "second-largest-element" --count "$COUNT" --seed "$SEED" --maxn 200
