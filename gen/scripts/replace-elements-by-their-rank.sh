#!/usr/bin/env bash
# Test-case generator for: Replace Elements by Their Rank
#   slug      : replace-elements-by-their-rank
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : replaceWithRank  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/replace-elements-by-their-rank.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "replace-elements-by-their-rank" --count "$COUNT" --seed "$SEED" --maxn 200
