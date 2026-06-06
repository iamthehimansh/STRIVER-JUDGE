# Test-case generation

Reference-driven, batched generation of large static test sets — one per
question — used by **Submit**.

## Pipeline

```
clone Codensity30/Strivers-A2Z-DSA-Sheet
        │
        ▼
gen/build_mapping.py      ref .cpp  ──►  our slug   (exact publicCpp method-name
        │                                            match first, fuzzy fallback)
        ▼   gen/mapping.json
gen/validate.py           compile each generator + sample  ──►  gen/generatable.json
        │
        ▼
gen/emit_scripts.py       one gen/scripts/<slug>.sh per validated problem + run_all.sh
        │
        ▼
gen/run_all.py            run them all (parallel)  ──►  generated-tests/<slug>.jsonl
```

## How it generates

`gen/generate.py <slug>` emits a single C++ program that **embeds the reference
solution** and a constraint-aware input generator, compiles with `-O2`, and
prints `N` cases (input columns + expected) — a million cases run in seconds.
Each line becomes `{"inputs": {...}, "expected": "..."}` in
`generated-tests/<slug>.jsonl`.

Input constraints are inferred from the problem statement (e.g. "given a *sorted*
array" → sorted input; "rotated" → rotated; "distinct" → de-duped). It only
emits when it can build a valid input for **every** parameter — it never fakes
garbage; unsupported problems are reported, not guessed.

## Per-question scripts

Each `gen/scripts/<slug>.sh` is standalone and re-runnable on a server:

```bash
bash gen/scripts/two-sum.sh            # default count (sized per problem)
bash gen/scripts/two-sum.sh 1000000    # up to 1M
COUNT=10000 JOBS=8 bash gen/run_all.sh # everything, overriding count
# or:  python3 gen/run_all.py --count 50000 --jobs 8
```

## Coverage & how to extend

`gen/generatable.json` lists the problems with a trustworthy reference +
auto-derivable inputs (high-confidence `func-name` mappings + reviewed `fuzzy`).

Not yet covered, and why:
- **Structural inputs** (binary tree / linked list / graph-adjacency / pointer
  signatures) — need a typed builder per shape.
- **`void` references** that mutate an argument in place — need an output spec.
- **Signature mismatch** — the reference's parameters don't line up with our
  `publicCpp` (skipped to avoid wrong data).
- **No reference** — ~100 problems have no solution in the repo; they need a
  hand-written reference (or one sourced elsewhere).

To add a problem: ensure a correct reference is mapped in `mapping.json`, then
extend the type/constraint handling in `generate.py` (or add a per-problem
override) until `gen/validate.py` accepts it.
