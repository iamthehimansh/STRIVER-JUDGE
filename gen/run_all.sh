#!/usr/bin/env bash
# Run every per-question generator. Override count for all: COUNT=10000 bash gen/run_all.sh
# Parallelism: JOBS=4 bash gen/run_all.sh
set -uo pipefail
cd "$(dirname "$0")/.."
JOBS="${JOBS:-4}"
COUNT="${COUNT:-}"
run_one() { bash "$1" $COUNT; }
export -f run_one
ls gen/scripts/*.sh | xargs -P "$JOBS" -I{} bash -c 'run_one "$@"' _ {}
echo "done -> generated-tests/"
