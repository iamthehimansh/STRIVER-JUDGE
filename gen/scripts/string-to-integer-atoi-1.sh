#!/usr/bin/env bash
# Test-case generator for: Recursive Implementation of atoi()
#   slug      : string-to-integer-atoi-1
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : myAtoi  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/string-to-integer-atoi-1.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "string-to-integer-atoi-1" --count "$COUNT" --seed "$SEED" --maxn 200
