#!/usr/bin/env bash
# Test-case generator for: Introduction to BST
#   slug      : introduction-to-bst
#   reference : 12. Binary Search Trees/1. Concept/01. Intro to BST.cpp
#   mapping   : fuzzy (score 0.7248)
#   entry     : isValidBST  ->  returns bool
#
# Regenerate (count defaults to 200000, up to 1000000):
#   bash gen/scripts/introduction-to-bst.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${1:-200000}"
SEED="${2:-12345}"
exec python3 gen/generate.py "introduction-to-bst" --count "$COUNT" --seed "$SEED" --maxn 200
