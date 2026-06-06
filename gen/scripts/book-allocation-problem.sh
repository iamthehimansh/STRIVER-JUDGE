#!/usr/bin/env bash
# Test-case generator for: Book Allocation Problem
#   slug      : book-allocation-problem
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : findPages  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/book-allocation-problem.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "book-allocation-problem" --count "$COUNT" --seed "$SEED" --maxn 200
