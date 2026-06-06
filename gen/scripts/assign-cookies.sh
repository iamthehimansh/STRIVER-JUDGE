#!/usr/bin/env bash
# Test-case generator for: Assign Cookies
#   slug      : assign-cookies
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : findMaximumCookieStudents  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/assign-cookies.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "assign-cookies" --count "$COUNT" --seed "$SEED" --maxn 200
