#!/usr/bin/env bash
# Test-case generator for: Shortest Job First
#   slug      : shortest-job-first
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : solve  ->  returns long long
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/shortest-job-first.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "shortest-job-first" --count "$COUNT" --seed "$SEED" --maxn 200
