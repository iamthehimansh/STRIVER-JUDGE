// Server-only SQLite store for run/submit history + stats.
// File at <project>/data/judge.db (gitignored; mounted as a volume in Docker
// so it persists across restarts).
import "server-only";
import path from "node:path";
import fs from "node:fs";
import Database from "better-sqlite3";

const DB_DIR = process.env.JUDGE_DB_DIR || path.join(process.cwd(), "data");
const DB_PATH = path.join(DB_DIR, "judge.db");

let _db: Database.Database | null = null;
function db(): Database.Database {
  if (_db) return _db;
  fs.mkdirSync(DB_DIR, { recursive: true });
  _db = new Database(DB_PATH);
  _db.pragma("journal_mode = WAL");
  _db.pragma("synchronous = NORMAL");
  _db.exec(`
    CREATE TABLE IF NOT EXISTS submissions (
      id           INTEGER PRIMARY KEY AUTOINCREMENT,
      slug         TEXT NOT NULL,
      problem_name TEXT,
      category     TEXT,
      difficulty   TEXT,
      language     TEXT NOT NULL,
      mode         TEXT NOT NULL CHECK(mode IN ('run','submit')),
      code         TEXT NOT NULL,
      verdict      TEXT NOT NULL,
      passed       INTEGER NOT NULL DEFAULT 0,
      total        INTEGER NOT NULL DEFAULT 0,
      runtime_mode TEXT,
      backend      TEXT,
      duration_ms  INTEGER NOT NULL DEFAULT 0,
      created_at   INTEGER NOT NULL DEFAULT (unixepoch())
    );
    CREATE INDEX IF NOT EXISTS idx_subs_created   ON submissions(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_subs_slug      ON submissions(slug, created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_subs_mode_vrdt ON submissions(mode, verdict);

    CREATE TABLE IF NOT EXISTS failed_cases (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      submission_id INTEGER NOT NULL REFERENCES submissions(id) ON DELETE CASCADE,
      case_idx      INTEGER NOT NULL,
      inputs_json   TEXT NOT NULL,
      expected      TEXT,
      actual        TEXT,
      status        TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_failed_sub ON failed_cases(submission_id);
  `);
  return _db;
}

// ---- writes -----------------------------------------------------------------
export interface RecordInput {
  slug: string;
  problem_name?: string | null;
  category?: string | null;
  difficulty?: string | null;
  language: string;
  mode: "run" | "submit";
  code: string;
  verdict: string;
  passed: number;
  total: number;
  runtime_mode?: string | null;
  backend?: string | null;
  duration_ms?: number;
  failed_cases?: Array<{
    case_idx: number;
    inputs: Record<string, string>;
    expected: string | null;
    actual: string;
    status: string;
  }>;
}

export function recordSubmission(rec: RecordInput): number {
  const d = db();
  const ins = d.prepare(`
    INSERT INTO submissions
      (slug, problem_name, category, difficulty, language, mode, code, verdict,
       passed, total, runtime_mode, backend, duration_ms)
    VALUES
      (@slug, @problem_name, @category, @difficulty, @language, @mode, @code, @verdict,
       @passed, @total, @runtime_mode, @backend, @duration_ms)
  `);
  const fail = d.prepare(`
    INSERT INTO failed_cases (submission_id, case_idx, inputs_json, expected, actual, status)
    VALUES (?, ?, ?, ?, ?, ?)
  `);
  const tx = d.transaction((r: RecordInput) => {
    const info = ins.run({
      slug: r.slug,
      problem_name: r.problem_name ?? null,
      category: r.category ?? null,
      difficulty: r.difficulty ?? null,
      language: r.language,
      mode: r.mode,
      code: r.code,
      verdict: r.verdict,
      passed: r.passed,
      total: r.total,
      runtime_mode: r.runtime_mode ?? null,
      backend: r.backend ?? null,
      duration_ms: r.duration_ms ?? 0,
    });
    const subId = Number(info.lastInsertRowid);
    if (r.failed_cases && r.failed_cases.length) {
      for (const fc of r.failed_cases) {
        fail.run(subId, fc.case_idx, JSON.stringify(fc.inputs), fc.expected, fc.actual, fc.status);
      }
    }
    return subId;
  });
  return tx(rec);
}

// ---- reads ------------------------------------------------------------------
export interface RecentRow {
  id: number;
  slug: string;
  problem_name: string | null;
  category: string | null;
  difficulty: string | null;
  language: string;
  mode: "run" | "submit";
  verdict: string;
  passed: number;
  total: number;
  duration_ms: number;
  created_at: number;
}

export function recentSubmissions(limit = 12): RecentRow[] {
  return db()
    .prepare(
      `SELECT id, slug, problem_name, category, difficulty, language, mode,
              verdict, passed, total, duration_ms, created_at
       FROM submissions
       ORDER BY created_at DESC
       LIMIT ?`
    )
    .all(limit) as RecentRow[];
}

export interface SubmissionDetail extends RecentRow {
  code: string;
  runtime_mode: string | null;
  backend: string | null;
  failed: Array<{
    case_idx: number;
    inputs: Record<string, string>;
    expected: string | null;
    actual: string;
    status: string;
  }>;
}

export function getSubmission(id: number): SubmissionDetail | null {
  const head = db()
    .prepare(`SELECT * FROM submissions WHERE id = ?`)
    .get(id) as any;
  if (!head) return null;
  const failed = db()
    .prepare(
      `SELECT case_idx, inputs_json, expected, actual, status
       FROM failed_cases WHERE submission_id = ? ORDER BY case_idx LIMIT 25`
    )
    .all(id) as Array<{
      case_idx: number;
      inputs_json: string;
      expected: string | null;
      actual: string;
      status: string;
    }>;
  return {
    ...head,
    failed: failed.map((f) => ({
      case_idx: f.case_idx,
      inputs: safeParse(f.inputs_json),
      expected: f.expected,
      actual: f.actual,
      status: f.status,
    })),
  };
}

function safeParse(s: string): Record<string, string> {
  try {
    const v = JSON.parse(s);
    return v && typeof v === "object" ? v : {};
  } catch {
    return {};
  }
}

// ---- stats ------------------------------------------------------------------
export interface WindowStats {
  runs: number;
  submits: number;
  accepted: number;
  success_rate: number; // accepted / submits (0..1)
  problems_tried: number;
  problems_solved: number;
}

function windowStats(sinceTs: number | null): WindowStats {
  const d = db();
  const where = sinceTs == null ? "" : "WHERE created_at >= " + Number(sinceTs);
  const row = d
    .prepare(
      `SELECT
        SUM(CASE WHEN mode='run' THEN 1 ELSE 0 END)                            AS runs,
        SUM(CASE WHEN mode='submit' THEN 1 ELSE 0 END)                          AS submits,
        SUM(CASE WHEN mode='submit' AND verdict='accepted' THEN 1 ELSE 0 END)   AS accepted,
        COUNT(DISTINCT slug)                                                    AS problems_tried,
        COUNT(DISTINCT CASE WHEN mode='submit' AND verdict='accepted' THEN slug END)
                                                                                AS problems_solved
       FROM submissions
       ${where}`
    )
    .get() as {
      runs: number | null;
      submits: number | null;
      accepted: number | null;
      problems_tried: number | null;
      problems_solved: number | null;
    };
  const runs = row.runs ?? 0;
  const submits = row.submits ?? 0;
  const accepted = row.accepted ?? 0;
  return {
    runs,
    submits,
    accepted,
    success_rate: submits ? accepted / submits : 0,
    problems_tried: row.problems_tried ?? 0,
    problems_solved: row.problems_solved ?? 0,
  };
}

export interface DayStats {
  day: string;   // YYYY-MM-DD (local-ish, in UTC)
  runs: number;
  submits: number;
  accepted: number;
}

export interface CategoryStats {
  category: string;
  attempts: number;       // all rows (run + submit)
  accepted: number;       // submit + accepted
  distinct_problems: number;
}

export interface StatsResponse {
  generated_at: number;
  totals: WindowStats;
  today: WindowStats;
  week: WindowStats;
  byDay: DayStats[];       // last 7 days, oldest first, with zeros for empty days
  byCategory: CategoryStats[];
  recent: RecentRow[];
}

export function getStats(): StatsResponse {
  const d = db();
  const now = Math.floor(Date.now() / 1000);
  const dayStart = (ts: number) => Math.floor(ts / 86400) * 86400;
  const startToday = dayStart(now);
  const startWeek = startToday - 6 * 86400; // last 7 days inclusive of today

  // byDay — group by floor(created_at / 86400)
  const dayRows = d
    .prepare(
      `SELECT (created_at / 86400) AS day_bucket,
              SUM(CASE WHEN mode='run' THEN 1 ELSE 0 END) AS runs,
              SUM(CASE WHEN mode='submit' THEN 1 ELSE 0 END) AS submits,
              SUM(CASE WHEN mode='submit' AND verdict='accepted' THEN 1 ELSE 0 END) AS accepted
       FROM submissions
       WHERE created_at >= ?
       GROUP BY day_bucket
       ORDER BY day_bucket`
    )
    .all(startWeek) as Array<{ day_bucket: number; runs: number; submits: number; accepted: number }>;
  const dayMap = new Map<number, { runs: number; submits: number; accepted: number }>();
  for (const r of dayRows) {
    dayMap.set(r.day_bucket, { runs: r.runs, submits: r.submits, accepted: r.accepted });
  }
  const todayBucket = Math.floor(startToday / 86400);
  const byDay: DayStats[] = [];
  for (let i = 6; i >= 0; i--) {
    const bucket = todayBucket - i;
    const ts = bucket * 86400;
    const date = new Date(ts * 1000);
    const day = `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, "0")}-${String(
      date.getUTCDate()
    ).padStart(2, "0")}`;
    const v = dayMap.get(bucket) || { runs: 0, submits: 0, accepted: 0 };
    byDay.push({ day, ...v });
  }

  // byCategory — group by category (NULL coalesced)
  const catRows = d
    .prepare(
      `SELECT COALESCE(category, 'Unknown') AS category,
              COUNT(*) AS attempts,
              SUM(CASE WHEN mode='submit' AND verdict='accepted' THEN 1 ELSE 0 END) AS accepted,
              COUNT(DISTINCT slug) AS distinct_problems
       FROM submissions
       GROUP BY COALESCE(category, 'Unknown')
       ORDER BY attempts DESC
       LIMIT 12`
    )
    .all() as CategoryStats[];

  return {
    generated_at: now,
    totals: windowStats(null),
    today: windowStats(startToday),
    week: windowStats(startWeek),
    byDay,
    byCategory: catRows,
    recent: recentSubmissions(15),
  };
}
