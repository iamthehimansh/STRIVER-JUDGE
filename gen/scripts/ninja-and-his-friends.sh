#!/usr/bin/env bash
# Test-case generator for: Ninja and his Friends
#   slug      : ninja-and-his-friends
#   reference : agent
#   mapping   : agent (score 2.0)
#   entry     : maxChocolates  ->  returns int
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/ninja-and-his-friends.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "ninja-and-his-friends" --count "$COUNT" --seed "$SEED" --maxn 200
