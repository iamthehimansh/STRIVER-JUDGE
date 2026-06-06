#!/usr/bin/env bash
# Test-case generator for: Requirements needed to construct a unique BT
#   slug      : requirements-needed-to-construct-a-unique-bt
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : uniqueBinaryTree  ->  returns bool
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/requirements-needed-to-construct-a-unique-bt.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "requirements-needed-to-construct-a-unique-bt" --count "$COUNT" --seed "$SEED" --maxn 200
