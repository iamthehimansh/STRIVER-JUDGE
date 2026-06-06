#!/usr/bin/env bash
# Test-case generator for: Longest Word with All Prefixes
#   slug      : longest-word-with-all-prefixes
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : completeString  ->  returns string
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-word-with-all-prefixes.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-word-with-all-prefixes" --count "$COUNT" --seed "$SEED" --maxn 200
