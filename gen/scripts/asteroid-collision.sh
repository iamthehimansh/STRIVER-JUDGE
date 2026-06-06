#!/usr/bin/env bash
# Test-case generator for: Asteroid Collision
#   slug      : asteroid-collision
#   reference : Asteroid Collision.cpp
#   mapping   : func-name (score 1.03)
#   entry     : asteroidCollision  ->  returns vector<int>
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/asteroid-collision.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "asteroid-collision" --count "$COUNT" --seed "$SEED" --maxn 200
