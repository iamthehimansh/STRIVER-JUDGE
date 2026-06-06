#!/usr/bin/env python3
"""
Compute the agent-workflow target list: problems NOT yet covered by a validated
generator, but whose publicCpp signature the generator CAN feed inputs to
(scalar / vector / string / matrix params). For those, an agent-written correct
reference unlocks generation. Structural-signature problems (tree/list/graph)
are reported separately — they need generator extensions, not just a reference.

Writes gen/agent_targets.json (the workflow `args`).
"""
import json, os, re, glob, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import generate as G

PROB_DIR = G.PROB_DIR
GEN_LIST = os.path.join(ROOT, "gen", "generatable.json")
OUT = os.path.join(ROOT, "gen", "agent_targets.json")


def text(html):
    s = re.sub(r"<[^>]+>", " ", html or "")
    s = (s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&nbsp;", " "))
    return re.sub(r"\s+", " ", s).strip()


def sig_supported(cpp):
    """True if the publicCpp method's params + return are all generator-feedable."""
    m = re.search(r"(?:public:)?\s*([A-Za-z_][\w:<>,\*&\s]*?)\s+([A-Za-z_]\w*)\s*\(([^)]*)\)", cpp or "")
    if not m:
        return False, "no signature"
    ret = G.canon(re.sub(r"\b(public|private|protected)\s*:", "", m.group(1)))
    if ret == "void":
        return False, "void-return"  # generator can't emit in-place outputs yet
    if ret not in G.RET_SUPPORTED:
        return False, f"return {ret}"
    params = G.split_params(m.group(3)) if m.group(3).strip() else []
    for praw in params:
        p = G.parse_param(praw)
        base = p["ctype"]
        if p["is_c_array"]:
            base = G.canon("vector<" + base.replace("[]", "").strip() + ">")
        if base not in G.GEN_SUPPORTED:
            return False, f"param {base}"
    return True, "ok"


def main():
    covered = set(json.load(open(GEN_LIST))) if os.path.exists(GEN_LIST) else set()
    targets, structural = [], []
    for f in glob.glob(os.path.join(PROB_DIR, "*.json")):
        d = json.load(open(f))
        if d["slug"] in covered or not d.get("starterCpp", "").strip():
            continue
        ok, why = sig_supported(d["starterCpp"])
        if not ok:
            structural.append((d["slug"], why))
            continue
        targets.append({
            "slug": d["slug"],
            "name": d["name"],
            "difficulty": d["difficulty"],
            "statement": text(d.get("statement", ""))[:1500],
            "constraints": text(d.get("constraints", ""))[:600],
            "publicCpp": d.get("starterCpp", ""),
            "examples": [{"input": e["input"], "output": e["output"]} for e in d.get("examples", [])[:3]],
        })

    json.dump(targets, open(OUT, "w"), indent=1)
    print(f"covered (validated)        : {len(covered)}")
    print(f"agent targets (feedable)   : {len(targets)}  -> {os.path.relpath(OUT, ROOT)}")
    print(f"structural (need gen ext.) : {len(structural)}")
    from collections import Counter
    print("  structural blockers:", dict(Counter(w.split()[0] for _, w in structural)))


if __name__ == "__main__":
    main()
