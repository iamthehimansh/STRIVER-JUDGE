#!/usr/bin/env bash
# Test-case generator for: Palindrome partitioning II 
#   slug      : palindrome-partitioning-ii-
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : minCut  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/palindrome-partitioning-ii-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "palindrome-partitioning-ii-" --count "$COUNT" --seed "$SEED" --maxn 200
