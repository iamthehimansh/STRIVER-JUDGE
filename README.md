# Striver Judge

A local LeetCode/takeUforward-style judge for the Striver A2Z problem set. It
renders a problem (Description / Editor / Result) and compiles + runs your
**C / C++** against test cases — either on the host (clang) or in a per-run
Docker sandbox with memory + time limits.

```
┌───────────────────────┬───────────────────────────────────┐
│  Description          │  [C++ ▾]            Reset  ▷Run  ▣ │
│  ───────────          │  ┌─────────────────────────────┐  │
│  Largest Element      │  │ class Solution {            │  │
│  [Easy] [Arrays]      │  │ public:                     │  │
│                       │  │   int largestElement(...)   │  │
│  Example 1 …          │  └─────────────────────────────┘  │
│  Now your turn! ○ ○   ├───────────────────────────────────┤
│                   ○ ○ │  Test Cases | Result    💻 local  │
│                       │  Case 1 ✓  Case 2 ✓  Case 3 •     │
└───────────────────────┴───────────────────────────────────┘
```

## Quick start

```bash
python3 scripts/restore_data.py   # reassemble split generated-tests/ (post-clone, one-time)
npm install                       # deps + self-hosts Monaco into public/vs
npm run data                      # build cleaned + per-problem JSON from the raw DB
npm run dev                       # http://localhost:3000
```

> `generated-tests/` ships split into ~40 MB chunks (`.partNNN`) so no single
> file exceeds GitHub's 100 MB limit. `restore_data.py` is idempotent —
> reassembles each `<base>.jsonl.part000` + siblings into `<base>.jsonl` and
> removes the parts. Re-running after a successful restore is a no-op.

Open the browser, pick a problem (e.g. **Largest Element**), write a solution,
and hit **Run**.

## What you get

- **Problem browser** (`/`) — all 462 problems grouped by category, with
  search + difficulty filter.
- **Workspace** (`/problem/<slug>`) — a 3-pane, resizable layout:
  - **Description** — statement, examples, constraints, and the "Now your
    turn!" MCQ (graded against your solution's actual output).
  - **Editor** — Monaco, **C / C++ only**, with plain built-in autocomplete
    (keyword + word-based suggestions from the buffer — no heavyweight language
    server). Self-hosted from `public/vs`, so it works offline.
  - **Test Cases / Result** — per-case pass/fail, your output vs expected,
    stderr, timing, and the active backend.

## Run vs Submit

| Action     | Test cases                                                            |
| ---------- | -------------------------------------------------------------------- |
| **Run**    | The 2–3 visible example cases (expected outputs parsed from the DB).  |
| **Submit** | The full generated answer key in `public/data/answers/<slug>.json`, if present — otherwise it falls back to the example cases (and says so). |

### Generating a full answer key (Submit)

When you have a known-correct **reference solution**, generate randomized +
edge-case inputs and compute expected outputs by running the reference:

```bash
# dev server must be running
python3 scripts/gen_testcase.py --slug largest-element \
    --reference path/to/reference.cpp --count 40
```

This writes `public/data/answers/largest-element.json`, which `Submit` then
judges against. Edge-case generation is shape-inferred from the example inputs;
tune `EDGES`/generators per problem constraints as you wire real solutions.

### Bulk generation from the reference repo (`gen/`)

For large static test sets across the whole sheet, `gen/` maps the cloned
[Codensity30 reference repo](https://github.com/Codensity30/Strivers-A2Z-DSA-Sheet)
to our problems and generates up to **1,000,000 constraint-valid cases per
question** via a batched C++ generator. **Submit** judges against these in a
single process. See **[gen/README.md](gen/README.md)**. Quick path:

```bash
git clone https://github.com/Codensity30/Strivers-A2Z-DSA-Sheet.git ../strivers-a2z-ref
python3 gen/build_mapping.py && python3 gen/validate.py && python3 gen/emit_scripts.py
python3 gen/run_all.py --count 100000        # -> generated-tests/<slug>.jsonl
```

## How judging works

1. **Harness mode (C++)** — `lib/judge/harness.ts` parses your `class Solution`
   method signature, binds each test input to a parameter (by name, then
   position), and generates a `main()` driver that parses inputs, calls your
   method, and prints the result canonically. One compile; the binary is run
   once per case (`argv[1]` selects the case). `void` methods either print
   their mutated non-const reference args (in-place problems) or rely on their
   own `cout` (cin/cout problems); unbound inputs are fed via stdin.
   - Supported types: scalars (`int/long long/double/bool/char/string`),
     `vector<...>` of those, `vector<vector<...>>`, **`TreeNode*` / `ListNode*`**
     (the harness defines the structs — `TreeNode::data`, `ListNode::val` — and
     deserializes from the dataset's level-order tree (`"1 4 null 4 2"`) and
     value-array list (`"[1, 2, 3]"`) formats), and **C-array params** like
     `string dict[]`, `int arr[]`, `vector<int> adj[]` (read into a vector
     internally; `.data()` is passed at the call site).
   - **Auto-derived size params**: an unbound parameter named `n / m / size /
     sz / len / length / count` of integer type is computed from the previous
     array argument's `.size()` (so e.g. `findOrder(string dict[], int N, int K)`
     binds `dict` and `K` from the dataset and `N = dict.size()` automatically).
   - Unsupported (e.g. exotic templates, function-object params) fall back to a
     clear "write a full `main()`" message.
2. **Free-form mode** — if your code has its own `main()` (always for **C**),
   it's compiled as-is and fed the case inputs on stdin; stdout is compared.
3. **Comparison** (`lib/judge/compare.ts`) is lenient: ignores brackets/commas/
   whitespace, compares numbers with tolerance, and normalizes boolean
   spellings.

A `<bits/stdc++.h>` shim is injected at compile time so competitive-style
includes work on macOS clang (libc++).

## Execution backends

Execution is delegated to `scripts/judge_exec.py` (compile + run + limits),
used identically by both backends so verdicts match.

- **Docker (production)** — a fresh, locked-down container per run:
  ```bash
  npm run judge:build      # docker build -t striver-judge:latest -f judge/Dockerfile .
  JUDGE_BACKEND=docker npm run dev
  ```
  Flags: `--network none --memory --memory-swap --cpus 1 --pids-limit 128
  --cap-drop ALL --security-opt no-new-privileges`, run as the host uid.
- **Local (fallback)** — host `clang++`/`clang`. Used automatically when Docker
  is absent; memory limits are best-effort on macOS. The Result panel shows
  which backend ran (`🐳 docker` / `💻 local`).

### Environment variables

| Var                 | Default               | Meaning                          |
| ------------------- | --------------------- | -------------------------------- |
| `JUDGE_BACKEND`     | auto                  | `docker` \| `local` \| auto      |
| `JUDGE_IMAGE`       | `striver-judge:latest`| Docker image tag                 |
| `JUDGE_MEMORY_MB`   | `256`                 | Per-run memory limit             |
| `JUDGE_TIME_MS`     | `3000`                | Per-case wall-time limit         |
| `JUDGE_COMPILE_MS`  | `15000`               | Compile timeout                  |

## Production deployment (Docker / Kubernetes)

Two images, one socket mount.

| Image                       | What it is                                  | Built from           |
| --------------------------- | ------------------------------------------- | -------------------- |
| `striver-judge:latest`      | Per-run **sandbox** (clang + g++ + python3) | `judge/Dockerfile`   |
| `striver-judge-app:latest`  | The **Next.js app + Docker CLI**            | `Dockerfile` (root)  |

The app spawns one fresh sandbox container per submission via the host
Docker daemon (Docker-out-of-Docker via the mounted socket — the app is *not*
nested inside Docker). Both images must be available on whichever node runs
the app.

### One-shot: Docker Compose

```bash
# on the host VM, in the repo:
python3 scripts/restore_data.py                                # 1. stitch the .partNNN files
docker build -t striver-judge:latest -f judge/Dockerfile .     # 2. build sandbox image
docker compose up -d --build                                   # 3. start app on :3000
```

`docker-compose.yml` mounts three things into the app container:

1. `/var/run/docker.sock` → the app shells out to `docker run …` for each
   submission. The spawned sandbox is a **sibling** of the app, not a child.
2. `/tmp` ↔ host `/tmp` → the per-job temp dir the app creates must resolve
   to the **same path** on the host (where the daemon runs), so the
   `-v <jobdir>:/work` mount the app emits actually finds something.
3. `./generated-tests` → the (restored) Submit test data, read-only.

### Kubernetes pod

`judge/pod.yaml` is a working Pod + Service example. The default shape uses
the same DooD pattern (mounts the node's Docker socket). For clusters where
the node runs containerd (no Docker daemon to talk to), the file has a DinD
sidecar variant commented at the bottom.

### Verify Docker mode is actually in use

After starting, hit **Run** on any problem and check the badge in the Result
panel: `🐳 docker` confirms the per-run sandbox path; `💻 local` means the
runner couldn't reach the daemon and fell back to host clang. Force-on:
`JUDGE_BACKEND=docker`; force-off: `JUDGE_BACKEND=local`.

## Data

`scripts/build_data.py` reads `FULL_STRIVER_DATABASE.json` and:

- Strips the paywalled `details` keys (`company_tags`, `difficulty`,
  `editorial`, `frequently_occuring_doubts`, `hints`,
  `interview_followup_questions`, `topic_tags`) — `meta` is left untouched.
- Writes `FULL_STRIVER_DATABASE.cleaned.json` (original kept intact).
- Parses example HTML into `{input, output, explanation}`, aligns example
  outputs to testcase inputs by index, and extracts the "Now your turn" MCQ.
- Emits `public/data/index.json` + `public/data/problems/<slug>.json`.

## Known limitations

- **Non-unique outputs.** "Run" compares against the single example output from
  the dataset, so problems with multiple valid answers (e.g. longest
  palindromic substring, combination order) can show a false "Wrong Answer".
  Use **Submit** with a reference solution (and, where needed, a custom checker)
  for those.
- **Unsupported signatures.** Linked-list / binary-tree / graph-adjacency /
  pointer parameters aren't auto-harnessed — those fall back to writing a full
  `main()` (free-form). Supported: scalars, `vector<...>`, `vector<vector<...>>`.
- **Editorials are intentionally dropped** from the app data (paywalled). They
  remain in the untouched original `FULL_STRIVER_DATABASE.json` if ever needed.
- **C judging is free-form.** Since the dataset is function-signature based
  (C++ `Solution` class), C is compiled as a full stdin→stdout program.

## Security note

This tool **compiles and executes arbitrary C/C++**. Run it locally / trusted
only. The Docker backend sandboxes execution (no network, dropped caps, memory/
pid/time limits); the local backend does not isolate beyond timeouts and output
caps. Problem `slug`s are validated against `[a-z0-9-]` before any filesystem
access.
