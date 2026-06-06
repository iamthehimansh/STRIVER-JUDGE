#!/usr/bin/env python3
"""
Compile every mapped problem's generator, run a small sanity sample, and record
which problems can produce VALID test data. Writes gen/generatable.json — the
source of truth for which per-question generators are trustworthy.

Run:  python3 gen/validate.py [--maxn 200]
"""
import argparse, json, os, subprocess, tempfile, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import generate as G  # reuse spec inference + codegen

PROB_DIR = G.PROB_DIR
MAPPING = G.MAPPING
OUT = os.path.join(ROOT, "gen", "generatable.json")


def target_count(spec):
    """Sized per problem: big input space -> more cases (server may raise to 1M)."""
    has_collection = any(p["gtype"].startswith("vector") or p["gtype"] == "string" for p in spec["plan"])
    return 200_000 if has_collection else 20_000


def sanity(sample_lines, keys):
    if not sample_lines:
        return "empty output"
    for ln in sample_lines:
        cols = ln.split("\t")
        if len(cols) != len(keys) + 1:
            return f"column/key mismatch ({len(cols)-1} vs {len(keys)})"
        if cols[-1] == "":
            return "empty expected"
    # variety: expected shouldn't be identical across all (a stuck reference)
    if len({l.split("\t")[-1] for l in sample_lines}) == 1 and len(sample_lines) > 4:
        return None  # could legitimately be constant; don't fail, just allow
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maxn", type=int, default=200)
    ap.add_argument("--only", default=None, help="comma-separated slugs to (re)validate; merges into existing generatable.json")
    args = ap.parse_args()

    mapping = json.load(open(MAPPING))
    G.ensure_shim()
    cc = "clang++" if G._which("clang++") else "g++"

    only = set(args.only.split(",")) if args.only else None
    # when validating a subset, start from the existing list and update it
    good = (json.load(open(OUT)) if (only and os.path.exists(OUT)) else {})
    skipped = {}
    slugs_iter = [s for s in mapping if (only is None or s in only)]
    for slug in slugs_iter:
        good.pop(slug, None)  # re-add only if it still validates
        prob = json.load(open(os.path.join(PROB_DIR, f"{slug}.json")))
        spec, err = G.infer_spec(slug, mapping, prob, 20, args.maxn)
        if err:
            skipped[slug] = err.split(":")[0]; continue
        src, err = G.build_cpp(spec)
        if err:
            skipped[slug] = err.split(":")[0]; continue
        with tempfile.TemporaryDirectory() as d:
            cpp, binp = os.path.join(d, "g.cpp"), os.path.join(d, "g")
            open(cpp, "w").write(src)
            r = subprocess.run([cc, "-std=c++17", "-O2", "-w", "-I", G.SHIM_DIR, "-o", binp, cpp],
                               capture_output=True, text=True)
            if r.returncode != 0:
                skipped[slug] = "compile-fail"; continue
            try:
                rr = subprocess.run([binp, "20", "7"], capture_output=True, text=True, timeout=30)
            except subprocess.TimeoutExpired:
                skipped[slug] = "sample-timeout"; continue
            lines = [l for l in rr.stdout.split("\n") if l.strip()]
            why = sanity(lines, spec["input_keys"])
            if why:
                skipped[slug] = why; continue
        good[slug] = {
            "entry": spec["entry"], "ret": spec["ret"], "input_keys": spec["input_keys"],
            "how": mapping[slug]["how"], "score": mapping[slug]["score"],
            "ref_file": mapping[slug]["ref_file"],
            "maxn": args.maxn, "count": target_count(spec),
        }

    json.dump(good, open(OUT, "w"), indent=1)
    from collections import Counter
    print(f"VALIDATED (compile + sample OK): {len(good)} / {len(mapping)} mapped")
    print(f"  high-confidence (func-name): {sum(1 for v in good.values() if v['how']=='func-name')}")
    print(f"  fuzzy-mapped               : {sum(1 for v in good.values() if v['how']=='fuzzy')}")
    print(f"  -> wrote {os.path.relpath(OUT, ROOT)}")
    print("skip reasons:", json.dumps(dict(Counter(skipped.values())), indent=1))


if __name__ == "__main__":
    main()
