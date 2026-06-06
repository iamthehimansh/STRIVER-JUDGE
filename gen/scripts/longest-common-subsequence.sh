#!/usr/bin/env bash
# Test-case generator for: Longest common subsequence
#   slug      : longest-common-subsequence
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : lcs  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/longest-common-subsequence.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "longest-common-subsequence" --count "$COUNT" --seed "$SEED" --maxn 200
