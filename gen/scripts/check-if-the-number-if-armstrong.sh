#!/usr/bin/env bash
# Test-case generator for: Check if the Number is Armstrong
#   slug      : check-if-the-number-if-armstrong
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : isArmstrong  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/check-if-the-number-if-armstrong.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "check-if-the-number-if-armstrong" --count "$COUNT" --seed "$SEED" --maxn 200
