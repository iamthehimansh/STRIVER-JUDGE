// Shared types for the local Striver judge.

export type Language = "cpp" | "c";

export type RunMode = "run" | "submit";

export interface ProblemIndexItem {
  id: string;
  name: string;
  slug: string;
  difficulty: string;
  category: string | null;
  subcategory: string | null;
  hasCpp: boolean;
  nTests: number;
}

export interface Example {
  input: string;
  output: string;
  explanation: string;
}

export interface Testcase {
  name: string;
  inputs: Record<string, string>;
  expected: string | null;
  hidden?: boolean;
}

export interface NowYourTurn {
  input: string;
  options: string[];
  tcIndex: number;
}

export interface Problem {
  id: string;
  name: string;
  slug: string;
  difficulty: string;
  category: string | null;
  subcategory: string | null;
  links: {
    article: string | null;
    youtube: string | null;
    leetcode: string | null;
    gfg?: string | null;
    cn?: string | null;
  };
  isPremium: boolean;
  hasCpp: boolean;
  statement: string;
  constraints: string;
  starterCpp: string;
  languages: string[];
  examples: Example[];
  nowYourTurn: NowYourTurn | null;
  testcases: Testcase[];
}

// A test case shown in the editable panel. `original` holds the example's
// initial inputs (so we can tell if the user edited it); null for custom cases.
export interface EditableCase {
  name: string;
  inputs: Record<string, string>;
  expected: string | null;
  original: Record<string, string> | null;
}

export type CaseStatus =
  | "passed"
  | "failed"
  | "tle"
  | "mle"
  | "runtime_error"
  | "unknown" // ran, but no expected output to compare against
  | "skipped";

export interface CaseResult {
  name: string;
  status: CaseStatus;
  input: Record<string, string>;
  stdout: string;
  stderr: string;
  expected: string | null;
  exitCode: number | null;
  timedOut: boolean;
  durationMs: number;
}

export type JudgeMode = "harness" | "freeform" | "unsupported";

export interface RunResponse {
  ok: boolean;
  mode: JudgeMode;
  backend: "docker" | "local";
  language: Language;
  runMode: RunMode;
  compile: { ok: boolean; stderr: string };
  cases: CaseResult[];
  verdict: "accepted" | "wrong_answer" | "compile_error" | "runtime_error" | "tle" | "ran" | "error";
  passed: number;
  total: number;
  message?: string;
  limits: { memoryMb: number; timeMs: number };
}

export interface RunLimits {
  memoryMb: number;
  timeMs: number;
  compileMs: number;
}
