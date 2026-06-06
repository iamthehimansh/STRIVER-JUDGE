#!/usr/bin/env bash
# Test-case generator for: Minimum Cost to Connect Sticks
#   slug      : minimum-cost-to-connect-sticks
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : connectSticks  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-cost-to-connect-sticks.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-cost-to-connect-sticks" --count "$COUNT" --seed "$SEED" --maxn 200
