#!/usr/bin/env bash
# Test-case generator for: Introduction to Trees
#   slug      : introduction-
#   reference : 11. Binary Trees/1. Traversals/01. Introduction to trees.cpp
#   mapping   : fuzzy (score 0.999)
#   entry     : numberOfNodes  ->  returns int
#
# Regenerate (count defaults to 20000, up to 1000000):
#   bash gen/scripts/introduction-.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-20000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "introduction-" --count "$COUNT" --seed "$SEED" --maxn 200
