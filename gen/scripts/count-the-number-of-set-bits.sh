#!/usr/bin/env bash
# Test-case generator for: Count the Number of Set Bits
#   slug      : count-the-number-of-set-bits
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : countSetBits  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/count-the-number-of-set-bits.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "count-the-number-of-set-bits" --count "$COUNT" --seed "$SEED" --maxn 200
