#!/usr/bin/env python3
"""
Build cleaned + app-ready data from FULL_STRIVER_DATABASE.json.

Outputs:
  1. FULL_STRIVER_DATABASE.cleaned.json  -> full DB with the 7 paywalled
     `details` keys removed (meta untouched). Original file is left intact.
  2. public/data/index.json              -> slim list for the problem browser.
  3. public/data/problems/<slug>.json    -> per-problem payload the UI needs,
     with example outputs parsed into testcase `expected` values.
"""
import json, os, re, html, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "FULL_STRIVER_DATABASE.json")
CLEAN_FULL = os.path.join(ROOT, "FULL_STRIVER_DATABASE.cleaned.json")
OUT_DIR = os.path.join(ROOT, "public", "data")
PROB_DIR = os.path.join(OUT_DIR, "problems")
A2Z = os.path.join(ROOT, "striver_a2z.json")           # article/youtube/leetcode by problem_id
EXTRA = os.path.join(ROOT, "stiverextralinks.json")    # cn/gfg/lc by problem_id

# Keys under `details` to drop: everything that only ever holds the
# "Subscribe to TUF+" paywall placeholder, plus the locked editorial.
DROP_KEYS = {
    "company_tags",
    "difficulty",          # paywall placeholder; meta.difficulty is the real one
    "editorial",
    "frequently_occuring_doubts",
    "hints",
    "interview_followup_questions",
    "topic_tags",
}

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"[ \t ]+")


def clean_text(s: str) -> str:
    """Strip HTML tags + unescape entities -> plain text."""
    if not s:
        return ""
    s = re.sub(r"</p>|</li>|<br\s*/?>|</div>|</h\d>", "\n", s, flags=re.I)
    s = TAG_RE.sub("", s)
    s = html.unescape(s)
    s = s.replace(" ", " ")
    lines = [WS_RE.sub(" ", ln).strip() for ln in s.split("\n")]
    return "\n".join(ln for ln in lines if ln)


LABEL_RE = re.compile(r"^\s*(Input|Output|Explanation)\b([^:]*):?\s*(.*)$", re.I)


def parse_example(html_str: str):
    """Parse a TUF example block into {input, output, explanation}."""
    if not html_str:
        return None
    text = clean_text(html_str)
    if not text:
        return None
    cur = {"input": "", "output": "", "explanation": ""}
    found = False
    active = None
    for line in text.split("\n"):
        m = LABEL_RE.match(line)
        if m:
            found = True
            label = m.group(1).lower()
            val = m.group(3).strip()
            active = label
            cur[label] = (cur[label] + " " + val).strip() if cur[label] else val
        elif active:
            # continuation line for the current label
            cur[active] = (cur[active] + " " + line).strip()
    if not found:
        return None
    cur["has_output"] = bool(cur["output"])
    return cur


def main():
    with open(SRC) as f:
        data = json.load(f)
    problems = data.get("problems", [])

    # link sources keyed by problem_id
    a2z_map = {}
    try:
        for cat in json.load(open(A2Z)):
            for sub in cat.get("subcategories", []):
                for p in sub.get("problems", []):
                    a2z_map[str(p.get("problem_id"))] = p
    except FileNotFoundError:
        pass
    try:
        extralinks = json.load(open(EXTRA))
    except FileNotFoundError:
        extralinks = {}

    # ---- 1. cleaned full DB ----
    cleaned_problems = []
    for p in problems:
        np = dict(p)
        det = p.get("details")
        if isinstance(det, dict):
            np["details"] = {k: v for k, v in det.items() if k not in DROP_KEYS}
        cleaned_problems.append(np)
    cleaned_full = dict(data)
    cleaned_full["problems"] = cleaned_problems
    with open(CLEAN_FULL, "w") as f:
        json.dump(cleaned_full, f, ensure_ascii=False)

    # ---- 2 + 3. app data ----
    os.makedirs(PROB_DIR, exist_ok=True)
    index = []
    seen_slugs = {}
    diffmap = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}
    stats = Counter()

    for p in problems:
        meta = p.get("meta") or {}
        det = p.get("details") or {}
        slug = (meta.get("slug") or det.get("problem_slug") or
                meta.get("problem_id") or "").strip()
        if not slug:
            continue
        # de-dupe slug collisions
        if slug in seen_slugs:
            seen_slugs[slug] += 1
            slug = f"{slug}-{seen_slugs[slug]}"
        else:
            seen_slugs[slug] = 0

        difficulty = diffmap.get((meta.get("difficulty") or "").lower(), meta.get("difficulty") or "Easy")
        starter_cpp = det.get("publicCpp") or ""
        has_cpp = bool(starter_cpp.strip())

        # Parse examples 1..4 POSITIONALLY (None placeholder for missing/empty
        # ones) so testcase[idx] always lines up with example{idx+1}, even when a
        # middle example is blank. (Filtering would shift later indices.)
        parsed = [parse_example(det.get(f"example{i}")) for i in (1, 2, 3, 4)]

        # testcases with expected aligned by index to examples
        raw_tcs = det.get("testcases") or []
        testcases = []
        now_your_turn = None
        opts = det.get("gamificationOptions") or []
        for idx, tc in enumerate(raw_tcs):
            inputs = tc.get("inputs") if isinstance(tc, dict) else None
            inputs = inputs if isinstance(inputs, dict) else {}
            ex = parsed[idx] if idx < len(parsed) else None
            expected = ex["output"] if (ex and ex.get("has_output")) else None
            testcases.append({
                "name": f"Case {idx + 1}",
                "inputs": inputs,
                "expected": expected,
            })
            # the testcase that has options-but-no-expected becomes the MCQ
            if expected is None and ex and opts and now_your_turn is None:
                now_your_turn = {
                    "input": ex.get("input", ""),
                    "options": opts,
                    "tcIndex": idx,
                }

        pid = str(meta.get("problem_id"))
        a2z = a2z_map.get(pid, {})
        extra = extralinks.get(pid) if isinstance(extralinks.get(pid), dict) else {}
        links = {
            "article": meta.get("article") or a2z.get("article"),
            "youtube": meta.get("youtube") or a2z.get("youtube"),
            "leetcode": meta.get("leetcode") or a2z.get("leetcode") or extra.get("lc"),
            "gfg": extra.get("gfg"),
            "cn": extra.get("cn"),
        }

        record = {
            "id": meta.get("problem_id"),
            "name": meta.get("problem_name") or det.get("problem_name") or slug,
            "slug": slug,
            "difficulty": difficulty,
            "category": meta.get("category_name"),
            "subcategory": meta.get("subcategory_name"),
            "links": links,
            "isPremium": bool(det.get("isPremium")),
            "hasCpp": has_cpp,
            "statement": det.get("problem_statement") or "",
            "constraints": det.get("constraints") or "",
            "starterCpp": starter_cpp,
            "languages": det.get("languages_supported") or [],
            "examples": [
                {"input": e.get("input", ""), "output": e.get("output", ""),
                 "explanation": e.get("explanation", "")}
                for e in parsed if e and e.get("has_output")
            ],
            "nowYourTurn": now_your_turn,
            "testcases": testcases,
        }

        with open(os.path.join(PROB_DIR, f"{slug}.json"), "w") as f:
            json.dump(record, f, ensure_ascii=False)

        index.append({
            "id": record["id"],
            "name": record["name"],
            "slug": slug,
            "difficulty": difficulty,
            "category": record["category"],
            "subcategory": record["subcategory"],
            "hasCpp": has_cpp,
            "nTests": len(testcases),
        })
        stats[difficulty] += 1
        if has_cpp:
            stats["__hasCpp"] += 1

    with open(os.path.join(OUT_DIR, "index.json"), "w") as f:
        json.dump(index, f, ensure_ascii=False)

    print(f"problems written : {len(index)}")
    print(f"  with C++ starter: {stats['__hasCpp']}")
    print(f"  by difficulty   : { {k: v for k, v in stats.items() if not k.startswith('__')} }")
    print(f"cleaned full DB  : {os.path.getsize(CLEAN_FULL)/1e6:.1f} MB "
          f"(orig {os.path.getsize(SRC)/1e6:.1f} MB)")
    print(f"index.json       : {os.path.getsize(os.path.join(OUT_DIR,'index.json'))/1e3:.0f} KB")


if __name__ == "__main__":
    main()
