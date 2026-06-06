import { NextRequest, NextResponse } from "next/server";
import { getProblem, getSubmitTestcases, getGeneratedCases } from "@/lib/data";
import { buildHarness, buildBatchHarness } from "@/lib/judge/harness";
import { runJob, type JobCase } from "@/lib/judge/runner";
import { compareOutput } from "@/lib/judge/compare";
import type {
  CaseResult,
  CaseStatus,
  JudgeMode,
  Language,
  RunLimits,
  RunMode,
  RunResponse,
  Testcase,
} from "@/lib/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const DEFAULT_LIMITS: RunLimits = {
  memoryMb: Number(process.env.JUDGE_MEMORY_MB) || 256,
  timeMs: Number(process.env.JUDGE_TIME_MS) || 3000,
  compileMs: Number(process.env.JUDGE_COMPILE_MS) || 15000,
};

const MAX_CASES = 60;
const MAX_CODE = 200_000;

function joinInputs(tc: Testcase): string {
  return Object.values(tc.inputs).join("\n");
}

const CAP_SUBMIT = 2000; // cases judged interactively from the (much larger) generated set

// problems whose output is a SET/collection where order doesn't matter
const UNORDERED_RE =
  /(?:^|-)(?:3-sum|4-sum|subset|combination|permutation|power-set|powerset|generate-parentheses|generate-binary-strings|letter-combinations|palindrome-partition|expression-add-operators|different-ways|n-queen)/;
function isUnordered(slug: string): boolean {
  return UNORDERED_RE.test(slug);
}

// Submit against the large static generated set (generated-tests/<slug>.jsonl),
// run in ONE batched process. Returns null if there's no generated set or the
// signature isn't batch-harnessable (caller then falls back to the normal flow).
async function tryBatchSubmit(slug: string, code: string): Promise<RunResponse | null> {
  const gen = await getGeneratedCases(slug, CAP_SUBMIT);
  if (!gen) return null;
  const batch = buildBatchHarness(code, gen.inputKeys);
  if (!batch.supported) return null;
  const unordered = isUnordered(slug);

  const limits: RunLimits = { ...DEFAULT_LIMITS, timeMs: 20000, memoryMb: 512 };
  const tsv = gen.cases
    .map((c) => gen.inputKeys.map((k) => (c.inputs[k] ?? "").replace(/[\t\n]/g, " ")).join("\t"))
    .join("\n");
  const result = await runJob("cpp", batch.source, [{ argv: [], stdin: tsv }], limits);

  const msg = `Judged against the generated test set — ${gen.cases.length.toLocaleString()} of ${gen.total.toLocaleString()} cases (batched).`;
  const base = {
    ok: true as const, mode: "harness" as JudgeMode, backend: result.backend,
    language: "cpp" as Language, runMode: "submit" as RunMode, limits,
  };
  if (!result.compile.ok) {
    return { ...base, compile: result.compile, cases: [], verdict: "compile_error", passed: 0, total: gen.cases.length, message: msg };
  }

  const raw = result.cases[0];
  const outLines = (raw?.stdout ?? "").split("\n");
  let passed = 0, firstFail = -1;
  for (let i = 0; i < gen.cases.length; i++) {
    const ran = i < outLines.length;
    if (ran && compareOutput(outLines[i].trim(), gen.cases[i].expected ?? "", unordered)) passed++;
    else if (firstFail < 0) firstFail = i;
  }

  const idxs = Array.from(new Set([0, 1, firstFail >= 0 ? firstFail : 2].filter((i) => i >= 0 && i < gen.cases.length))).sort((a, b) => a - b);
  const shown: CaseResult[] = idxs.map((i) => {
    const ran = i < outLines.length;
    const out = ran ? outLines[i].trim() : "";
    const ok = ran && compareOutput(out, gen.cases[i].expected ?? "", unordered);
    return {
      name: `Case ${i + 1}`,
      status: (ok ? "passed" : ran ? "failed" : "runtime_error") as CaseStatus,
      input: gen.cases[i].inputs, stdout: out, stderr: "", expected: gen.cases[i].expected,
      exitCode: raw?.exitCode ?? 0, timedOut: raw?.timedOut ?? false, durationMs: raw?.durationMs ?? 0,
    };
  });

  let verdict: RunResponse["verdict"];
  if (raw?.timedOut) verdict = "tle";
  else if (outLines.length < gen.cases.length && raw?.exitCode !== 0) verdict = "runtime_error";
  else if (passed === gen.cases.length) verdict = "accepted";
  else verdict = "wrong_answer";

  return {
    ...base, compile: result.compile, cases: shown, verdict, passed, total: gen.cases.length,
    message: msg + (raw?.stderr ? ` · ${raw.stderr.slice(0, 160)}` : ""),
  };
}

export async function POST(req: NextRequest) {
  let body: any;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "invalid json" }, { status: 400 });
  }

  const slug: string = body?.slug ?? "";
  const language: Language = body?.language === "c" ? "c" : "cpp";
  const code: string = typeof body?.code === "string" ? body.code : "";
  const runMode: RunMode = body?.mode === "submit" ? "submit" : "run";

  if (!slug || !code.trim()) {
    return NextResponse.json({ error: "missing slug or code" }, { status: 400 });
  }
  if (code.length > MAX_CODE) {
    return NextResponse.json({ error: "code too large" }, { status: 413 });
  }

  const problem = await getProblem(slug);
  if (!problem) {
    return NextResponse.json({ error: "problem not found" }, { status: 404 });
  }

  // Submit + a generated static set available -> batched judging.
  if (runMode === "submit" && language === "cpp" && !Array.isArray(body?.cases)) {
    const batched = await tryBatchSubmit(slug, code);
    if (batched) return NextResponse.json(batched);
  }

  // pick testcase set
  let testcases: Testcase[];
  let generated = false;
  if (Array.isArray(body?.cases) && body.cases.length) {
    // explicit input override (used by scripts/gen_testcase.py to compute
    // expected outputs from a reference solution; outputs are returned as-is)
    testcases = body.cases.map((c: any, i: number) => ({
      name: typeof c?.name === "string" ? c.name : `Case ${i + 1}`,
      inputs: c?.inputs && typeof c.inputs === "object" ? c.inputs : {},
      expected: typeof c?.expected === "string" ? c.expected : null,
    }));
  } else if (runMode === "submit") {
    const sub = await getSubmitTestcases(slug);
    testcases = sub.cases;
    generated = sub.generated;
  } else {
    testcases = problem.testcases;
  }
  testcases = testcases.slice(0, MAX_CASES);

  if (testcases.length === 0) {
    return NextResponse.json({ error: "no testcases for this problem" }, { status: 422 });
  }

  // decide judge mode + build source
  let mode: JudgeMode;
  let source: string;
  let cases: JobCase[];
  let message: string | undefined;

  if (language === "cpp") {
    const built = buildHarness(code, testcases);
    if (built.supported) {
      mode = "harness";
      source = built.source;
      cases = testcases.map((_, i) => ({ argv: [String(i)], stdin: built.stdinPerCase[i] ?? "" }));
    } else if (built.reason === "user-main") {
      mode = "freeform";
      source = code;
      cases = testcases.map((tc) => ({ argv: [], stdin: joinInputs(tc) }));
      message = "Detected a main() — running as a full program (stdin → stdout).";
    } else {
      return NextResponse.json(
        emptyResponse(language, runMode, "unsupported",
          built.reason ||
            "Auto-judge does not support this problem's signature yet. Write a full program with main() that reads stdin.",
          testcases.length),
      );
    }
  } else {
    // C: always free-form full program
    mode = "freeform";
    source = code;
    cases = testcases.map((tc) => ({ argv: [], stdin: joinInputs(tc) }));
  }

  const totalStdin = cases.reduce((n, c) => n + (c.stdin?.length || 0), 0);
  if (totalStdin > 5_000_000) {
    return NextResponse.json({ error: "input too large" }, { status: 413 });
  }

  const result = await runJob(language, source, cases, DEFAULT_LIMITS);

  if (!result.compile.ok) {
    return NextResponse.json(<RunResponse>{
      ok: true,
      mode,
      backend: result.backend,
      language,
      runMode,
      compile: result.compile,
      cases: [],
      verdict: "compile_error",
      passed: 0,
      total: testcases.length,
      message,
      limits: DEFAULT_LIMITS,
    });
  }

  const unordered = isUnordered(slug);
  const caseResults: CaseResult[] = testcases.map((tc, i) => {
    const raw = result.cases[i];
    if (!raw) {
      return blankCase(tc, "skipped");
    }
    let status: CaseStatus;
    const oom =
      raw.signal === 9 || // SIGKILL: cgroup OOM-kill in the Docker sandbox
      /bad_alloc|out of memory|std::bad_alloc|std::length_error/i.test(raw.stderr);
    if (raw.timedOut) {
      status = "tle";
    } else if (raw.signal != null) {
      // terminated by a signal (SIGKILL/SIGSEGV/SIGXCPU/…)
      status = oom ? "mle" : "runtime_error";
    } else if (raw.exitCode !== 0 && raw.exitCode !== null) {
      status = oom ? "mle" : "runtime_error";
    } else if (tc.expected == null) {
      status = "unknown";
    } else {
      status = compareOutput(raw.stdout, tc.expected, unordered) ? "passed" : "failed";
    }
    return {
      name: tc.name,
      status,
      input: tc.inputs,
      stdout: raw.stdout,
      stderr: raw.stderr,
      expected: tc.expected,
      exitCode: raw.exitCode,
      timedOut: raw.timedOut,
      durationMs: raw.durationMs,
    };
  });

  const gradable = caseResults.filter((c) => c.expected != null);
  const passed = gradable.filter((c) => c.status === "passed").length;

  let verdict: RunResponse["verdict"];
  if (caseResults.some((c) => c.status === "tle")) verdict = "tle";
  else if (gradable.length > 0 && passed === gradable.length) verdict = "accepted";
  else if (caseResults.some((c) => c.status === "runtime_error" || c.status === "mle")) verdict = "runtime_error";
  else if (gradable.some((c) => c.status === "failed")) verdict = "wrong_answer";
  else verdict = "ran";

  if (runMode === "submit" && !generated) {
    message = (message ? message + " " : "") +
      "Submitting against example testcases (no generated answer key yet for this problem).";
  }

  return NextResponse.json(<RunResponse>{
    ok: true,
    mode,
    backend: result.backend,
    language,
    runMode,
    compile: result.compile,
    cases: caseResults,
    verdict,
    passed,
    total: gradable.length || caseResults.length,
    message,
    limits: DEFAULT_LIMITS,
  });
}

function blankCase(tc: Testcase, status: CaseStatus): CaseResult {
  return {
    name: tc.name,
    status,
    input: tc.inputs,
    stdout: "",
    stderr: "",
    expected: tc.expected,
    exitCode: null,
    timedOut: false,
    durationMs: 0,
  };
}

function emptyResponse(
  language: Language,
  runMode: RunMode,
  mode: JudgeMode,
  message: string,
  total: number,
): RunResponse {
  return {
    ok: true,
    mode,
    backend: "local",
    language,
    runMode,
    compile: { ok: false, stderr: "" },
    cases: [],
    verdict: "error",
    passed: 0,
    total,
    message,
    limits: DEFAULT_LIMITS,
  };
}
