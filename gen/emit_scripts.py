#!/usr/bin/env python3
"""
Emit one self-contained generator script per validated problem (gen/scripts/<slug>.sh)
plus a master runner (gen/run_all.sh). Each script regenerates that problem's
static test cases and is safe to run standalone on a server.

Run:  python3 gen/emit_scripts.py
"""
import json, os, stat, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN_LIST = os.path.join(ROOT, "gen", "generatable.json")
PROB_DIR = os.path.join(ROOT, "public", "data", "problems")
SCRIPTS = os.path.join(ROOT, "gen", "scripts")


def chmod_x(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)


def main():
    good = json.load(open(GEN_LIST))
    os.makedirs(SCRIPTS, exist_ok=True)
    # clear stale scripts
    for f in glob.glob(os.path.join(SCRIPTS, "*.sh")):
        os.remove(f)

    names = {}
    for f in glob.glob(os.path.join(PROB_DIR, "*.json")):
        d = json.load(open(f))
        names[d["slug"]] = d["name"]

    for slug, info in good.items():
        name = names.get(slug, slug)
        path = os.path.join(SCRIPTS, f"{slug}.sh")
        body = f"""#!/usr/bin/env bash
# Test-case generator for: {name}
#   slug      : {slug}
#   reference : {info['ref_file']}
#   mapping   : {info['how']} (score {info['score']})
#   entry     : {info['entry']}  ->  returns {info['ret']}
#
# Regenerate (count defaults to {info['count']}, up to 1000000):
#   bash gen/scripts/{slug}.sh [COUNT] [SEED]
set -euo pipefail
cd "$(dirname "$0")/../.."
COUNT="${{1:-{info['count']}}}"
SEED="${{2:-12345}}"
exec python3 gen/generate.py "{slug}" --count "$COUNT" --seed "$SEED" --maxn {info['maxn']}
"""
        open(path, "w").write(body)
        chmod_x(path)

    # master runner
    runner = os.path.join(ROOT, "gen", "run_all.sh")
    open(runner, "w").write(f"""#!/usr/bin/env bash
# Run every per-question generator. Override count for all: COUNT=10000 bash gen/run_all.sh
# Parallelism: JOBS=4 bash gen/run_all.sh
set -uo pipefail
cd "$(dirname "$0")/.."
JOBS="${{JOBS:-4}}"
COUNT="${{COUNT:-}}"
run_one() {{ bash "$1" $COUNT; }}
export -f run_one
ls gen/scripts/*.sh | xargs -P "$JOBS" -I{{}} bash -c 'run_one "$@"' _ {{}}
echo "done -> generated-tests/"
""")
    chmod_x(runner)

    print(f"wrote {len(good)} per-question scripts -> gen/scripts/")
    print("wrote master runner            -> gen/run_all.sh")


if __name__ == "__main__":
    main()
