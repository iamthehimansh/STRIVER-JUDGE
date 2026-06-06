#!/usr/bin/env python3
"""
Reliable parallel runner for all validated generators. Replaces the fragile
bash xargs runner.

Run:  python3 gen/run_all.py [--count N] [--jobs K] [--only slug1,slug2]
"""
import argparse, json, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import generate as G

GEN_LIST = os.path.join(ROOT, "gen", "generatable.json")


def one(slug, count, seed, maxn):
    try:
        ok = G.run(slug, count, seed, maxn, dry=False)
        return slug, ok, None
    except Exception as e:  # noqa
        return slug, False, str(e)[:120]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=None, help="override count (else per-problem target)")
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--only", default=None, help="comma-separated slugs")
    args = ap.parse_args()

    good = json.load(open(GEN_LIST))
    slugs = list(good)
    if args.only:
        want = set(args.only.split(","))
        slugs = [s for s in slugs if s in want]

    t0 = time.time()
    done = ok = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as ex:
        futs = {
            ex.submit(one, s, args.count or good[s]["count"], args.seed, good[s]["maxn"]): s
            for s in slugs
        }
        for fut in as_completed(futs):
            slug, success, err = fut.result()
            done += 1
            ok += 1 if success else 0
            tag = "ok " if success else "FAIL"
            print(f"[{done}/{len(slugs)}] {tag} {slug}" + (f"  ({err})" if err else ""), flush=True)

    print(f"\ngenerated {ok}/{len(slugs)} in {time.time()-t0:.0f}s -> generated-tests/")


if __name__ == "__main__":
    main()
