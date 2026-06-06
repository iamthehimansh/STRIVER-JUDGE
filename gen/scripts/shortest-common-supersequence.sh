#!/usr/bin/env bash
# Test-case generator for: Shortest common supersequence
#   slug      : shortest-common-supersequence
#   reference : Shortest common supersequence.cpp
#   mapping   : func-name (score 1.03)
#   entry     : shortestCommonSupersequence  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/shortest-common-supersequence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "shortest-common-supersequence" --count "$COUNT" --seed "$SEED" --maxn 200
