#!/usr/bin/env bash
# Test-case generator for: Celebrity Problem
#   slug      : celebrity-problem
#   reference : 07.Stack and Queues/4. Implementation/03. Celebrity Problem.cpp
#   mapping   : func-name (score 0.999)
#   entry     : celebrity  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/celebrity-problem.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "celebrity-problem" --count "$COUNT" --seed "$SEED" --maxn 200
