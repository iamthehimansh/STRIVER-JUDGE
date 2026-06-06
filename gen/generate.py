#!/usr/bin/env python3
"""
Batched, reference-driven test-case generator.

For a problem with a known reference solution (from gen/mapping.json), this:
  1. infers an input spec (param types + light constraint heuristics),
  2. emits a single C++ program that embeds the reference and generates N
     constraint-valid inputs, calling the reference to compute each expected
     output (a million cases compile+run in seconds),
  3. writes generated-tests/<slug>.jsonl  (one {"inputs":{...},"expected":...}
     per line) — the format the Submit judge consumes.

Usage:
  python3 gen/generate.py <slug> [--count N] [--seed S] [--maxn M] [--dry]
  python3 gen/generate.py --list                 # show generatable problems

This is intentionally conservative: it only generates when it can build a
constraint-valid input for every parameter, so it never emits garbage. Problems
whose signature/structure it can't handle yet are reported, not faked.
"""
import argparse, json, os, re, subprocess, sys, tempfile, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROB_DIR = os.path.join(ROOT, "public", "data", "problems")
MAPPING = os.path.join(ROOT, "gen", "mapping.json")
OUT_DIR = os.path.join(ROOT, "generated-tests")
SHIM_DIR = os.path.join(ROOT, "gen", "_shim")  # holds bits/stdc++.h for macOS clang
OVERRIDES_FILE = os.path.join(ROOT, "gen", "overrides.json")
try:
    OVERRIDES = json.load(open(OVERRIDES_FILE))  # per-problem constraint refinements
except FileNotFoundError:
    OVERRIDES = {}

# ---- type model ---------------------------------------------------------------
# canonical param/return type -> how to generate + how to print
SCALAR = {"int", "long", "long long", "double", "bool", "char"}


def canon(t):
    t = t.replace("const", "")
    t = re.sub(r"[&*]", "", t)
    t = re.sub(r"\s*<\s*", "<", t)
    t = re.sub(r"\s*>\s*", ">", t)
    t = re.sub(r"\s*,\s*", ",", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


GEN_SUPPORTED = {
    "int", "long", "long long", "double", "bool", "char", "string",
    "vector<int>", "vector<long long>", "vector<double>", "vector<char>",
    "vector<string>", "vector<vector<int>>",
}
RET_SUPPORTED = GEN_SUPPORTED | {"void"}


def split_params(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return out


def parse_param(raw):
    raw = raw.strip()
    m = re.search(r"([A-Za-z_]\w*)\s*(\[\s*\])?\s*$", raw)
    name, type_str = "", raw
    if m and m.group(1) not in ("int", "long", "double", "char", "bool", "string", "unsigned"):
        name = m.group(1)
        type_str = raw[: m.start()] + (" []" if m.group(2) else "")
    is_array = bool(re.search(r"\[\s*\]", raw))
    ct = canon(type_str)
    return {"name": name, "ctype": ct, "is_c_array": is_array, "raw": raw}


# ---- spec inference -----------------------------------------------------------
def infer_spec(slug, mapping, prob, count, maxn):
    if slug not in mapping:
        return None, "no reference mapped"
    m = mapping[slug]
    funcs = m["funcs"]
    if not funcs:
        return None, "no function in reference"
    # choose entry: prefer the function whose name best matches, else most params
    def fscore(f):
        return len(split_params(f["params_raw"])) + (5 if f["name"].lower() in slug.replace("-", "") else 0)
    entry = max(funcs, key=fscore)
    params = [parse_param(p) for p in split_params(entry["params_raw"])] if entry["params_raw"].strip() else []

    ret = canon(re.sub(r"\b(public|private|protected)\s*:", "", entry["ret"]))
    if ret not in RET_SUPPORTED:
        return None, f"unsupported return type: {ret}"

    # constraint heuristics — base "sorted" on the STATEMENT (e.g. "given a
    # sorted array"), NOT the broad category, so binary-search-on-answer problems
    # (find peak, etc.) keep arbitrary inputs instead of degenerate sorted ones.
    name_l = prob["name"].lower()
    stmt = re.sub(r"<[^>]+>", " ", prob.get("statement", "") or "").lower()
    text = name_l + " " + stmt
    rotated = "rotated" in text
    sorted_in = rotated or ("sorted" in text and "unsorted" not in text) or any(
        k in name_l for k in ["lower bound", "upper bound", "floor", "ceil",
                              "search insert", "first and last", "occurrence"])
    distinct = "distinct" in text or "without duplicates" in text or "no duplicates" in text

    # build generation plan per param
    plan = []
    # detect a length param paired with an array (common: (arr[], n) or (vector v, n))
    array_idxs = [i for i, p in enumerate(params) if p["ctype"].startswith("vector") or p["is_c_array"]]
    for i, p in enumerate(params):
        base = p["ctype"]
        if p["is_c_array"]:
            base = "vector<" + base.replace("[]", "").strip() + ">"  # int[] -> vector<int> semantics
            base = canon(base)
        gtype = base
        # an int/long right after an array, named n/size/len -> the array length
        is_len = (
            base in ("int", "long", "long long")
            and p["name"].lower() in ("n", "m", "size", "len", "length", "k")
            and any(j < i for j in array_idxs)
            and p["name"].lower() != "k"  # k is usually a real parameter, keep generating it
        )
        if base not in GEN_SUPPORTED and not (p["is_c_array"]):
            return None, f"unsupported param type: {base} ({p['raw']})"
        plan.append({
            "name": p["name"] or f"a{i}",
            "gtype": gtype,
            "c_array": p["is_c_array"],
            "elem": gtype[len("vector<"):-1] if gtype.startswith("vector<") else None,
            "is_len": is_len,
            "sorted": sorted_in and gtype.startswith("vector"),
            "rotated": rotated and gtype.startswith("vector"),
            "distinct": distinct and gtype.startswith("vector"),
        })

    # input keys MUST be in emitted-column (param) order so each jsonl record's
    # labels line up with its values. The judge binds these to the user's
    # publicCpp params by name (agent refs match exactly) or position.
    input_keys = [p["name"] for p in plan if not p.get("is_len")]

    # per-problem overrides (the "refine it" hook) — constrain inputs so generic
    # random data becomes valid for structurally-constrained problems.
    ov = OVERRIDES.get(slug, {})
    if ov.get("exclude"):
        return None, f"excluded: {ov.get('reason', 'manual override')}"
    if "sorted" in ov or "distinct" in ov:
        for p in plan:
            if p["gtype"].startswith("vector"):
                if "sorted" in ov:
                    p["sorted"] = ov["sorted"]
                if "distinct" in ov:
                    p["distinct"] = ov["distinct"]

    return {
        "slug": slug,
        "ref_file": m["ref_file"],
        "entry": entry["name"],
        "is_class": m.get("is_class", False),
        "ret": ret,
        "plan": plan,
        "input_keys": input_keys,
        "count": count,
        # cap generation array length so bulk runs stay fast/small even when a
        # problem's stated constraint (e.g. 1e5) is large
        "maxn": min(int(ov.get("maxn", maxn)), 500),
        "lo": ov.get("lo"),
        "hi": ov.get("hi"),
        "domain": ov.get("domain"),  # e.g. "binary" -> values in {0,1}
        "code": m["code"],
    }, None


# ---- C++ codegen --------------------------------------------------------------
def gen_decl(idx, p, maxn, domain=None):
    """C++ to declare+populate variable v{idx} per its plan."""
    name = f"v{idx}"
    t = p["gtype"]
    L = []
    scalar_rhs = "(long long)(rng()&1)" if domain == "binary" else "randint(LO, HI)"
    vec_fill = "(rng()&1)" if domain == "binary" else "randint(LO, HI)"
    if p["is_len"]:
        # length of the most recent array -> filled later via placeholder
        L.append(f"long long {name} = _lastN;")
        return name, L
    if t in ("int", "long", "long long"):
        L.append(f"{t} {name} = ({t})({scalar_rhs});")
    elif t == "double":
        L.append(f"double {name} = randint(LO, HI) + (rng()%1000)/1000.0;")
    elif t == "bool":
        L.append(f"bool {name} = rng()&1;")
    elif t == "char":
        L.append(f"char {name} = 'a' + rng()%26;")
    elif t == "string":
        L.append(f"int _n{idx} = randint(1, {maxn}); string {name}; for(int i=0;i<_n{idx};i++) {name}+= (char)('a'+rng()%26); _lastN={name}.size();")
    elif t == "vector<int>" or t == "vector<long long>":
        elem = "long long" if t == "vector<long long>" else "int"
        if domain in ("permutation", "permutation0"):
            L.append(f"int _n{idx} = randint(1, {maxn}); vector<{elem}> {name}(_n{idx}); iota({name}.begin(),{name}.end(),0); shuffle({name}.begin(),{name}.end(),rng); _lastN=_n{idx};")
        elif domain == "permutation1":
            L.append(f"int _n{idx} = randint(1, {maxn}); vector<{elem}> {name}(_n{idx}); iota({name}.begin(),{name}.end(),1); shuffle({name}.begin(),{name}.end(),rng); _lastN=_n{idx};")
        else:
            L.append(f"int _n{idx} = randint(1, {maxn}); vector<{elem}> {name}(_n{idx}); for(auto&x:{name}) x = {vec_fill}; _lastN=_n{idx};")
        if p["distinct"]:
            L.append(f"{{ set<{elem}> s({name}.begin(),{name}.end()); {name}.assign(s.begin(),s.end()); }}")
        if p["sorted"]:
            L.append(f"sort({name}.begin(), {name}.end());")
        if p["rotated"]:
            L.append(f"sort({name}.begin(), {name}.end()); {{ int r=rng()%{name}.size(); rotate({name}.begin(), {name}.begin()+r, {name}.end()); }}")
    elif t == "vector<double>":
        L.append(f"int _n{idx} = randint(1, {maxn}); vector<double> {name}(_n{idx}); for(auto&x:{name}) x = randint(LO,HI)+(rng()%1000)/1000.0; _lastN=_n{idx};")
    elif t == "vector<char>":
        L.append(f"int _n{idx} = randint(1, {maxn}); vector<char> {name}(_n{idx}); for(auto&x:{name}) x = 'a'+rng()%26; _lastN=_n{idx};")
    elif t == "vector<string>":
        L.append(f"int _n{idx} = randint(1, {min(maxn,20)}); vector<string> {name}(_n{idx}); for(auto&s:{name}){{ int l=randint(1,8); for(int i=0;i<l;i++) s+=(char)('a'+rng()%26);}} _lastN=_n{idx};")
    elif t == "vector<vector<int>>":
        L.append(f"int _r{idx}=randint(1,{min(maxn,40)}),_c{idx}=randint(1,{min(maxn,40)}); vector<vector<int>> {name}(_r{idx}, vector<int>(_c{idx})); for(auto&row:{name})for(auto&x:row)x=randint(LO,HI); _lastN=_r{idx};")
    else:
        return None, None
    return name, L


def emit_input(idx, p):
    """C++ to print variable v{idx} in our on-screen input format."""
    name = f"v{idx}"
    t = p["gtype"]
    if p["is_len"]:
        return None  # length params are not surfaced as input keys
    if t in ("int", "long", "long long", "double", "char"):
        return f'os << {name};'
    if t == "bool":
        return f'os << ({name} ? "true" : "false");'
    if t == "string":
        return f'os << {name};'
    if t in ("vector<int>", "vector<long long>", "vector<double>", "vector<char>"):
        return (f'os << "["; for(size_t i=0;i<{name}.size();++i){{ if(i) os << ", "; os << {name}[i]; }} os << "]";')
    if t == "vector<string>":
        return (f'os << "["; for(size_t i=0;i<{name}.size();++i){{ if(i) os << ", "; os << "\\"" << {name}[i] << "\\""; }} os << "]";')
    if t == "vector<vector<int>>":
        return (f'os << "["; for(size_t i=0;i<{name}.size();++i){{ if(i) os << ", "; os << "["; for(size_t j=0;j<{name}[i].size();++j){{ if(j) os<<", "; os<<{name}[i][j]; }} os << "]"; }} os << "]";')
    return None


def emit_ret(ret):
    if ret in ("int", "long", "long long", "double", "char"):
        return "os << _ans;"
    if ret == "bool":
        return 'os << (_ans ? "true" : "false");'
    if ret == "string":
        return "os << _ans;"
    if ret in ("vector<int>", "vector<long long>", "vector<double>", "vector<char>"):
        return 'for(size_t i=0;i<_ans.size();++i){ if(i) os<<" "; os<<_ans[i]; }'
    if ret == "vector<string>":
        return 'for(size_t i=0;i<_ans.size();++i){ if(i) os<<" "; os<<_ans[i]; }'
    if ret == "vector<vector<int>>":
        # flatten to one line (a tab-separated record can't contain newlines);
        # the judge compares token sequences, so row separators don't matter
        return 'for(size_t i=0;i<_ans.size();++i){ for(size_t j=0;j<_ans[i].size();++j){ if(i||j) os<<" "; os<<_ans[i][j]; } }'
    return None


def build_cpp(spec):
    plan = spec["plan"]
    decls, inputs = [], []
    args = []
    for i, p in enumerate(plan):
        name, dlines = gen_decl(i, p, spec["maxn"], spec.get("domain"))
        if name is None:
            return None, f"cannot generate param {p['name']} ({p['gtype']})"
        decls.append("    " + "\n    ".join(dlines))
        # C-array params (int arr[]) take a pointer; a vector exposes one via .data()
        args.append(name + (".data()" if p.get("c_array") else ""))
        ei = emit_input(i, p)
        if ei is not None:
            inputs.append(ei)

    if spec["ret"] == "void":
        return None, "void-return reference (needs in-place output spec)"
    ret_emit = emit_ret(spec["ret"])
    if ret_emit is None:
        return None, f"cannot print return type {spec['ret']}"

    # join input columns with \t; last column is expected
    input_block = '\n        os << "\\t";\n'.join("        " + s for s in inputs)
    arglist = ", ".join(args)
    call_prefix = "_gsol." if spec.get("is_class") else ""
    inst_decl = "    Solution _gsol;\n" if spec.get("is_class") else ""

    src = f"""#include <bits/stdc++.h>
using namespace std;

/* ===== reference solution ({spec['ref_file']}) ===== */
{spec['code']}
/* ===== generator ===== */
static long long LO = -1000, HI = 1000;
int main(int argc, char** argv) {{
    long long N = argc>1 ? atoll(argv[1]) : 10000;
    unsigned seed = argc>2 ? (unsigned)atoll(argv[2]) : 12345u;
    if (argc>3) {{ LO = atoll(argv[3]); }}
    if (argc>4) {{ HI = atoll(argv[4]); }}
    mt19937_64 rng(seed);
    auto randint = [&](long long lo, long long hi) -> long long {{
        if (hi < lo) hi = lo;
        return lo + (long long)(rng() % (unsigned long long)(hi - lo + 1));
    }};
{inst_decl}    string buf; buf.reserve(1<<20);
    for (long long t = 0; t < N; t++) {{
        long long _lastN = 1;
        ostringstream os;
{chr(10).join(decls)}
        auto _ans = {call_prefix}{spec['entry']}({arglist});
{input_block}
        os << "\\t";
        {ret_emit}
        buf += os.str(); buf += '\\n';
        if (buf.size() > (1<<20)) {{ fwrite(buf.data(),1,buf.size(),stdout); buf.clear(); }}
    }}
    fwrite(buf.data(),1,buf.size(),stdout);
    return 0;
}}
"""
    return src, None


# ---- run ----------------------------------------------------------------------
def ensure_shim():
    os.makedirs(os.path.join(SHIM_DIR, "bits"), exist_ok=True)
    shim = os.path.join(SHIM_DIR, "bits", "stdc++.h")
    if not os.path.exists(shim):
        from importlib import import_module  # avoid hard dep; write inline list
        with open(shim, "w") as f:
            f.write("#pragma once\n" + "\n".join(
                f"#include <{h}>" for h in [
                    "iostream","iomanip","sstream","string","vector","map","unordered_map",
                    "set","unordered_set","algorithm","numeric","queue","stack","deque","list",
                    "utility","functional","climits","cmath","cstring","cstdlib","cstdio","cctype",
                    "cstdint","bitset","array","tuple","limits","cassert","iterator","random","chrono","memory",
                ]) + "\n")


def run(slug, count, seed, maxn, dry):
    prob = json.load(open(os.path.join(PROB_DIR, f"{slug}.json")))
    mapping = json.load(open(MAPPING))
    spec, err = infer_spec(slug, mapping, prob, count, maxn)
    if err:
        print(f"SKIP {slug}: {err}")
        return False
    src, err = build_cpp(spec)
    if err:
        print(f"SKIP {slug}: {err}")
        return False

    ensure_shim()
    with tempfile.TemporaryDirectory() as d:
        cpp = os.path.join(d, "gen.cpp")
        binp = os.path.join(d, "gen")
        open(cpp, "w").write(src)
        cc = "clang++" if _which("clang++") else "g++"
        r = subprocess.run([cc, "-std=c++17", "-O2", "-w", "-I", SHIM_DIR, "-o", binp, cpp],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"SKIP {slug}: reference did not compile")
            if dry:
                print(r.stderr[:1500])
            return False
        rng_args = []
        if spec.get("lo") is not None:
            rng_args = [str(spec["lo"]), str(spec["hi"] if spec.get("hi") is not None else 1000)]
        if dry:
            # tiny sample to validate
            rr = subprocess.run([binp, "5", str(seed), *rng_args], capture_output=True, text=True, timeout=30)
            print(f"OK   {slug}: entry={spec['entry']} ret={spec['ret']} keys={spec['input_keys']}")
            print("  sample:")
            for line in rr.stdout.strip().split("\n")[:5]:
                cols = line.split("\t")
                print("   ", cols[:-1], "->", cols[-1][:50])
            return True

        os.makedirs(OUT_DIR, exist_ok=True)
        out = os.path.join(OUT_DIR, f"{slug}.jsonl")
        rr = subprocess.run([binp, str(count), str(seed), *rng_args], capture_output=True, text=True, timeout=600)
        keys = spec["input_keys"]
        n = 0
        with open(out, "w") as f:
            for line in rr.stdout.split("\n"):
                if not line.strip():
                    continue
                cols = line.split("\t")
                vals, expected = cols[:-1], cols[-1]
                if len(vals) != len(keys):
                    # column/key mismatch -> skip this problem rather than emit wrong data
                    print(f"SKIP {slug}: column/key mismatch ({len(vals)} vals vs {len(keys)} keys)")
                    return False
                f.write(json.dumps({"inputs": dict(zip(keys, vals)), "expected": expected}) + "\n")
                n += 1
        size = os.path.getsize(out)
        print(f"OK   {slug}: {n} cases -> {os.path.relpath(out, ROOT)} ({size/1e6:.1f} MB)")
        return True


def _which(p):
    return any(os.access(os.path.join(d, p), os.X_OK) for d in os.environ.get("PATH", "").split(os.pathsep) if d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--count", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--maxn", type=int, default=200)
    ap.add_argument("--dry", action="store_true", help="compile + 5-case sample, don't write")
    ap.add_argument("--list", action="store_true", help="dry-run every mapped problem, report generatable count")
    args = ap.parse_args()

    if args.list:
        mapping = json.load(open(MAPPING))
        ok = 0; reasons = {}
        for slug in mapping:
            prob = json.load(open(os.path.join(PROB_DIR, f"{slug}.json")))
            spec, err = infer_spec(slug, mapping, prob, 10, args.maxn)
            if not err:
                src, err = build_cpp(spec)
            if err:
                reasons[err.split(":")[0]] = reasons.get(err.split(":")[0], 0) + 1
            else:
                ok += 1
        print(f"infer-OK (pre-compile): {ok} / {len(mapping)} mapped problems")
        print("blockers:", json.dumps(reasons, indent=1))
        return

    if not args.slug:
        ap.error("provide a slug or --list")
    run(args.slug, args.count, args.seed, args.maxn, args.dry)


if __name__ == "__main__":
    main()
