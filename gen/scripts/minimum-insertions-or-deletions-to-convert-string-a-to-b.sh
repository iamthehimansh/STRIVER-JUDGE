#!/usr/bin/env bash
# Test-case generator for: Minimum insertions or deletions to convert string A to B
#   slug      : minimum-insertions-or-deletions-to-convert-string-a-to-b
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : minOperations  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/minimum-insertions-or-deletions-to-convert-string-a-to-b.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "minimum-insertions-or-deletions-to-convert-string-a-to-b" --count "$COUNT" --seed "$SEED" --maxn 200
