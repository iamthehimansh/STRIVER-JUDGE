#!/usr/bin/env python3
"""
Map each reference solution (.cpp) across MULTIPLE cloned Striver repos to one of
our problem slugs, and extract runnable code (comments + any main() stripped).

Matching priority (reliability — wrong mapping = garbage data):
  1. EXACT: a reference function/method name == our publicCpp method name (unique).
  2. FUZZY: problem-name similarity (flagged).
Ties prefer `class Solution` refs (signature matches our publicCpp) and earlier repos.

Output: gen/mapping.json
  { slug: { ref_repo, ref_file, ref_name, entry, is_class, funcs, code, score, how } }
"""
import json, os, re, sys, glob, difflib
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = os.path.dirname(ROOT)  # ~/Downloads
# (dir, label, priority) — lower priority value wins ties
REF_DIRS = [
    (os.path.join(DL, "strivers-a2z-ref"), "codensity", 1),
    (os.path.join(DL, "ref2"), "aditya", 0),   # class Solution, matches publicCpp -> prefer
    (os.path.join(DL, "ref3"), "arindal", 2),
]
PROB_DIR = os.path.join(ROOT, "public", "data", "problems")
OUT = os.path.join(ROOT, "gen", "mapping.json")

BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
LINE_COMMENT = re.compile(r"//[^\n]*")
FUNC_RE = re.compile(r"([A-Za-z_][\w:<>,\*&\s]*?)\s+([A-Za-z_]\w*)\s*\(([^;{)]*)\)\s*(?:const\s*)?\{", re.S)
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "main", "else", "catch"}


def strip_comments(src):
    return LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", src))


def strip_main(code):
    m = re.search(r"\b(?:int|void)\s+main\s*\([^)]*\)\s*\{", code)
    if not m:
        return code
    depth, j = 0, m.end() - 1
    while j < len(code):
        if code[j] == "{":
            depth += 1
        elif code[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return (code[: m.start()] + code[j + 1:]).strip()


def extract_funcs(code):
    out = []
    for m in FUNC_RE.finditer(code):
        ret, name, params = m.group(1).strip(), m.group(2), m.group(3).strip()
        ret = re.sub(r"\b(public|private|protected)\s*:", "", ret).strip()
        if name in KEYWORDS or ret in ("struct", "class") or not ret:
            continue
        out.append({"ret": re.sub(r"\s+", " ", ret), "name": name, "params_raw": params})
    return out


def our_method(cpp):
    m = re.search(r"(?:public:)?\s*[A-Za-z_][\w:<>,\*&\s]*?\s+([A-Za-z_]\w*)\s*\(", cpp or "")
    return m.group(1) if m else None


def norm(s):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s.lower())).strip()


def ref_name_from_path(path):
    base = os.path.splitext(os.path.basename(path))[0]
    base = re.sub(r"^\d+[.\)]?\s*", "", base).replace("_", " ").replace("'", "")
    return base


def main():
    problems = [json.load(open(f)) for f in glob.glob(os.path.join(PROB_DIR, "*.json"))]
    method_index = {}
    for p in problems:
        mn = our_method(p.get("starterCpp", ""))
        if mn:
            method_index.setdefault(mn.lower(), []).append(p)
    prob_norm = [(p, norm(p["name"]), set(norm(p["name"]).split())) for p in problems]

    mapping = OrderedDict()
    claimed = {}  # slug -> score
    stats = {"codensity": 0, "aditya": 0, "arindal": 0}
    no_code = 0

    def consider(slug, rec, score):
        if slug in claimed and claimed[slug] >= score:
            return
        claimed[slug] = score
        mapping[slug] = rec

    for ref_dir, label, prio in REF_DIRS:
        if not os.path.isdir(ref_dir):
            print(f"(skip missing repo: {ref_dir})")
            continue
        for rf in sorted(glob.glob(os.path.join(ref_dir, "**", "*.cpp"), recursive=True)):
            rel = os.path.relpath(rf, ref_dir)
            raw = strip_comments(open(rf, errors="replace").read())
            is_class = bool(re.search(r"\b(class|struct)\s+Solution\b", raw))
            code = strip_main(raw).strip()
            funcs = extract_funcs(code)
            if not code or not funcs:
                no_code += 1
                continue
            rname = ref_name_from_path(rf)
            tiebreak = (0.03 if is_class else 0) - prio * 0.001

            # priority 1: exact method-name match to a unique slug
            hits = [(method_index[fn["name"].lower()][0], fn)
                    for fn in funcs
                    if len(method_index.get(fn["name"].lower(), [])) == 1]
            if hits:
                p, fn = max(hits, key=lambda h: difflib.SequenceMatcher(None, norm(rname), norm(h[0]["name"])).ratio())
                consider(p["slug"], {
                    "ref_repo": label, "ref_file": rel, "ref_name": rname,
                    "problem_name": p["name"], "entry": fn["name"], "is_class": is_class,
                    "funcs": funcs, "code": code, "score": round(1.0 + tiebreak, 4), "how": "func-name",
                }, 1.0 + tiebreak)
                continue

            # priority 2: fuzzy
            rn = norm(rname); rtok = set(rn.split())
            best, bs = None, 0.0
            for p, pn, ptok in prob_norm:
                sc = 0.55 * difflib.SequenceMatcher(None, rn, pn).ratio() + 0.45 * (len(rtok & ptok) / max(1, len(rtok)))
                if sc > bs:
                    best, bs = p, sc
            if best and bs >= 0.62:
                entry = max(funcs, key=lambda f: difflib.SequenceMatcher(None, f["name"].lower(), norm(best["name"]).replace(" ", "")).ratio())
                consider(best["slug"], {
                    "ref_repo": label, "ref_file": rel, "ref_name": rname,
                    "problem_name": best["name"], "entry": entry["name"], "is_class": is_class,
                    "funcs": funcs, "code": code, "score": round(bs + tiebreak, 4), "how": "fuzzy",
                }, bs + tiebreak)

    # agent-authored references (highest priority — these match publicCpp exactly)
    AGENT = os.path.join(ROOT, "gen", "agent_refs.json")
    if os.path.exists(AGENT):
        for slug, a in json.load(open(AGENT)).items():
            code = strip_main(strip_comments(a["code"])).strip()
            funcs = extract_funcs(code)
            if not funcs:
                continue
            consider(slug, {
                "ref_repo": "agent", "ref_file": "agent", "ref_name": slug,
                "problem_name": slug, "entry": a["entry"],
                "is_class": a.get("is_class", bool(re.search(r"\b(class|struct)\s+Solution\b", code))),
                "funcs": funcs, "code": code, "score": 2.0, "how": "agent",
            }, 2.0)

    for m in mapping.values():
        stats[m["ref_repo"]] = stats.get(m["ref_repo"], 0) + 1
    json.dump(mapping, open(OUT, "w"), indent=1)
    fn = sum(1 for m in mapping.values() if m["how"] == "func-name")
    print(f"mapped: {len(mapping)} / {len(problems)} problems   (func-name {fn}, fuzzy {len(mapping)-fn})")
    print(f"  by repo: {stats}")
    print(f"  class-Solution refs: {sum(1 for m in mapping.values() if m['is_class'])}")


if __name__ == "__main__":
    main()
