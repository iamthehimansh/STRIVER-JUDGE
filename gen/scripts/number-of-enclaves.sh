#!/usr/bin/env bash
# Test-case generator for: Number of enclaves
#   slug      : number-of-enclaves
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : numberOfEnclaves  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/number-of-enclaves.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "number-of-enclaves" --count "$COUNT" --seed "$SEED" --maxn 200
