#!/usr/bin/env bash
# Test-case generator for: Capacity to Ship Packages Within D Days
#   slug      : capacity-to-ship-packages-within-d-days
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : shipWithinDays  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/capacity-to-ship-packages-within-d-days.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "capacity-to-ship-packages-within-d-days" --count "$COUNT" --seed "$SEED" --maxn 200
