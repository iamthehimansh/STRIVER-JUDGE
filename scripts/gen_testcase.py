#!/usr/bin/env python3
"""
Generate a full answer key (input/output pairs) for a problem's "Submit" run.

Flow:
  1. Infer each input's shape (scalar / int-array / int-matrix / string) from the
     problem's example testcases.
  2. Generate randomized cases + deterministic edge cases of that shape.
  3. Run the REFERENCE solution against those inputs (via the dev server's
     /api/run `cases` override) to obtain the correct expected outputs.
  4. Write public/data/answers/<slug>.json — the "Submit" judge then uses it.

Usage:
  # 1. start the dev server:  npm run dev
  # 2. provide a known-correct reference solution and generate:
  python3 scripts/gen_testcase.py --slug largest-element \
      --reference path/to/reference_solution.cpp --count 40

Notes:
  * Randomness is seeded for reproducibility (pass --seed to vary).
  * Without --reference, inputs are still generated but expected outputs are
    left null (placeholder) so you can wire them later.
  * This is the integration point for your "repo of real code": point
    --reference at the matching solution file.
"""
import argparse
import json
import os
import random
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROB_DIR = os.path.join(ROOT, "public", "data", "problems")
ANS_DIR = os.path.join(ROOT, "public", "data", "answers")


# --- shape inference -------------------------------------------------------
def infer_shape(value: str) -> str:
    v = value.strip()
    if re.match(r"^\[\s*\[", v):
        return "matrix_int"
    if v.startswith("["):
        inner = v.strip("[] ")
        # empty array or all-numeric inner -> int array (don't misclassify "[]")
        if inner == "" or re.fullmatch(r"[\s,\-0-9]*", inner):
            return "array_int"
        return "array_str"
    if re.fullmatch(r"-?\d+", v):
        return "int"
    if re.fullmatch(r"-?\d*\.\d+", v):
        return "float"
    return "string"


# --- generators ------------------------------------------------------------
def gen_int(rng, edge=None):
    if edge is not None:
        return str(edge)
    return str(rng.randint(-1000, 1000))


def gen_array_int(rng, edge=None):
    if edge == "empty":
        return "[]"
    if edge == "single":
        return f"[{rng.randint(-1000, 1000)}]"
    n = rng.randint(2, 12)
    return "[" + ", ".join(str(rng.randint(-1000, 1000)) for _ in range(n)) + "]"


def gen_matrix_int(rng, edge=None):
    r = rng.randint(1, 4)
    c = rng.randint(1, 4)
    rows = ["[" + ", ".join(str(rng.randint(-100, 100)) for _ in range(c)) + "]" for _ in range(r)]
    return "[" + ", ".join(rows) + "]"


def gen_string(rng, edge=None):
    if edge == "empty":
        return ""
    n = rng.randint(1, 12)
    return "".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(n))


GENERATORS = {
    "int": gen_int,
    "float": lambda rng, edge=None: str(round(rng.uniform(-100, 100), 3)),
    "array_int": gen_array_int,
    "array_str": gen_string,
    "matrix_int": gen_matrix_int,
    "string": gen_string,
}

EDGES = {
    "int": [0, 1, -1, 1000, -1000],
    # NOTE: empty containers are valid edges only when a problem's constraints
    # allow n == 0. Enable per-problem when you wire the real reference.
    "array_int": ["single"],
    "string": [],
}


def build_cases(shapes, rng, count):
    """shapes: dict[input_key] = shape. Returns list of {name, inputs}."""
    cases = []
    # edge combinations (apply one edge to one key, rest random)
    idx = 1
    for key, shape in shapes.items():
        for edge in EDGES.get(shape, []):
            inputs = {}
            for k, s in shapes.items():
                gen = GENERATORS.get(s, gen_string)
                inputs[k] = gen(rng, edge if k == key else None)
            cases.append({"name": f"Edge {idx}", "inputs": inputs})
            idx += 1
    # random fill
    while len(cases) < count:
        inputs = {k: GENERATORS.get(s, gen_string)(rng) for k, s in shapes.items()}
        cases.append({"name": f"Case {len(cases) + 1}", "inputs": inputs})
    return cases[:count]


def compute_expected(server, slug, reference_code, cases):
    payload = json.dumps({
        "slug": slug, "language": "cpp", "mode": "run",
        "code": reference_code, "cases": cases,
    }).encode()
    req = urllib.request.Request(
        f"{server}/api/run", data=payload,
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        sys.exit(f"could not reach the judge at {server} (is `npm run dev` running?): {e}")
    except Exception as e:
        sys.exit(f"reference run failed: {e}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--reference", help="path to a known-correct C++ reference solution")
    ap.add_argument("--count", type=int, default=30)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--server", default="http://localhost:3000")
    args = ap.parse_args()

    pfile = os.path.join(PROB_DIR, f"{args.slug}.json")
    if not os.path.exists(pfile):
        sys.exit(f"problem not found: {args.slug}")
    prob = json.load(open(pfile))

    sample = next((tc for tc in prob["testcases"] if tc.get("inputs")), None)
    if not sample:
        sys.exit("no example inputs to infer shape from")
    shapes = {k: infer_shape(v) for k, v in sample["inputs"].items()}
    print(f"inferred shapes: {shapes}")

    rng = random.Random(args.seed)
    cases = build_cases(shapes, rng, args.count)

    if args.reference:
        ref = open(args.reference).read()
        print(f"running reference against {len(cases)} cases via {args.server} ...")
        res = compute_expected(args.server, args.slug, ref, cases)
        if not res.get("compile", {}).get("ok", False):
            sys.exit("reference failed to compile:\n" + res.get("compile", {}).get("stderr", ""))
        out_cases = []
        for c, r in zip(cases, res.get("cases", [])):
            out_cases.append({"name": c["name"], "inputs": c["inputs"],
                              "expected": r.get("stdout", ""), "hidden": True})
    else:
        print("no --reference given; writing inputs with null expected (placeholder)")
        out_cases = [{**c, "expected": None, "hidden": True} for c in cases]

    os.makedirs(ANS_DIR, exist_ok=True)
    out = os.path.join(ANS_DIR, f"{args.slug}.json")
    json.dump({"slug": args.slug, "testcases": out_cases}, open(out, "w"))
    print(f"wrote {len(out_cases)} testcases -> {out}")


if __name__ == "__main__":
    main()
