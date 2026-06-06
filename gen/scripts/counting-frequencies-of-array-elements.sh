#!/usr/bin/env bash
# Test-case generator for: Counting Frequencies of Array Elements
#   slug      : counting-frequencies-of-array-elements
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : countFrequencies  ->  returns vector<vector<int>>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/counting-frequencies-of-array-elements.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "counting-frequencies-of-array-elements" --count "$COUNT" --seed "$SEED" --maxn 200
