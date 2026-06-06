#!/usr/bin/env bash
# Test-case generator for: Prime factorisation of a Number
#   slug      : prime-factorisation-of-a-number-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : primeFactors  ->  returns vector<vector<int>>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/prime-factorisation-of-a-number-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "prime-factorisation-of-a-number-1" --count "$COUNT" --seed "$SEED" --maxn 200
