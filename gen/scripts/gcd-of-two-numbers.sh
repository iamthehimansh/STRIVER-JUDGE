#!/usr/bin/env bash
# Test-case generator for: GCD of Two Numbers
#   slug      : gcd-of-two-numbers
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : GCD  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/gcd-of-two-numbers.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "gcd-of-two-numbers" --count "$COUNT" --seed "$SEED" --maxn 200
