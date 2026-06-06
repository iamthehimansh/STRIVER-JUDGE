#!/usr/bin/env python3
"""
Integrate agent-authored references (workflow results) into the generation
pipeline: writes gen/agent_refs.json (picked up by build_mapping.py) and merges
input constraints into gen/overrides.json.

Usage:  python3 gen/integrate_agent.py <results.json>
where results.json is an array of:
  { slug, reference_cpp, entry_method, value_lo, value_hi, max_n,
    sorted, distinct, domain, generatable, confidence, notes }
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT_REFS = os.path.join(ROOT, "gen", "agent_refs.json")
OVERRIDES = os.path.join(ROOT, "gen", "overrides.json")
SUPPORTED_DOMAINS = {None, "", "binary", "permutation", "permutation0", "permutation1"}


def load(path):
    return json.load(open(path)) if os.path.exists(path) else {}


def main():
    results = json.load(open(sys.argv[1]))
    refs = load(AGENT_REFS)
    overrides = load(OVERRIDES)
    added = excluded = skipped = 0

    for r in results:
        if not r:
            continue
        slug = r.get("slug")
        if not slug:
            continue
        code = (r.get("reference_cpp") or "").strip()
        conf = r.get("confidence", 0) or 0
        dom = r.get("domain") or None
        if dom in ("none", "null", "None", ""):
            dom = None

        if not r.get("generatable", True) or not code or conf < 0.5 or dom not in SUPPORTED_DOMAINS:
            overrides[slug] = {"exclude": True,
                               "reason": ("agent: " + (r.get("notes") or "not auto-generatable"))[:200]}
            excluded += 1
            continue

        refs[slug] = {"code": code, "entry": r.get("entry_method") or "", "is_class": True}
        ov = {}
        if r.get("value_lo") is not None:
            ov["lo"] = r["value_lo"]
        if r.get("value_hi") is not None:
            ov["hi"] = r["value_hi"]
        if r.get("max_n"):
            ov["maxn"] = r["max_n"]
        if r.get("sorted"):
            ov["sorted"] = True
        if r.get("distinct"):
            ov["distinct"] = True
        if dom:
            ov["domain"] = dom
        if ov:
            overrides[slug] = ov
        elif slug in overrides and overrides[slug].get("exclude"):
            del overrides[slug]  # un-exclude if a prior round excluded it
        added += 1

    json.dump(refs, open(AGENT_REFS, "w"), indent=1)
    json.dump(overrides, open(OVERRIDES, "w"), indent=1)
    print(f"agent refs added: {added}  | excluded (not generatable): {excluded}")
    print(f"  -> {os.path.relpath(AGENT_REFS, ROOT)} ({len(refs)} total), {os.path.relpath(OVERRIDES, ROOT)}")


if __name__ == "__main__":
    main()
