// Server-side data access. Reads the preprocessed JSON from public/data.
import "server-only";
import { readFile } from "node:fs/promises";
import { createReadStream, existsSync } from "node:fs";
import readline from "node:readline";
import path from "node:path";
import type { Problem, ProblemIndexItem, Testcase } from "./types";

const DATA_DIR = path.join(process.cwd(), "public", "data");
const GEN_DIR = path.join(process.cwd(), "generated-tests");

// Slugs come from request input — only allow the safe charset so a value like
// "../../etc/passwd" can never escape the data directory. Real slugs include
// apostrophes/parens/commas (e.g. kadane's-algorithm, pow(x,n)); none contain
// '.' or '/', so path traversal remains impossible.
const SLUG_RE = /^[a-z0-9'(),-]+$/;
export function validSlug(slug: string): boolean {
  return typeof slug === "string" && SLUG_RE.test(slug);
}

export async function getIndex(): Promise<ProblemIndexItem[]> {
  const raw = await readFile(path.join(DATA_DIR, "index.json"), "utf8");
  return JSON.parse(raw);
}

export async function getProblem(slug: string): Promise<Problem | null> {
  if (!validSlug(slug)) return null;
  const file = path.join(DATA_DIR, "problems", `${slug}.json`);
  if (!existsSync(file)) return null;
  return JSON.parse(await readFile(file, "utf8"));
}

// Full generated testcases for "Submit" (produced by scripts/gen_testcase.py).
// Falls back to the problem's example testcases when none exist yet.
export async function getSubmitTestcases(slug: string): Promise<{ cases: Testcase[]; generated: boolean }> {
  if (!validSlug(slug)) return { cases: [], generated: false };
  const file = path.join(DATA_DIR, "answers", `${slug}.json`);
  if (existsSync(file)) {
    try {
      const data = JSON.parse(await readFile(file, "utf8"));
      if (Array.isArray(data?.testcases) && data.testcases.length) {
        return { cases: data.testcases, generated: true };
      }
    } catch {
      /* fall through */
    }
  }
  const prob = await getProblem(slug);
  return { cases: prob?.testcases ?? [], generated: false };
}

// Read up to `cap` cases from the large static set in generated-tests/<slug>.jsonl
// (produced by gen/generate.py). Returns the input-key order too, for batching.
export async function getGeneratedCases(
  slug: string,
  cap: number
): Promise<{ cases: Testcase[]; inputKeys: string[]; total: number } | null> {
  if (!validSlug(slug)) return null;
  const file = path.join(GEN_DIR, `${slug}.jsonl`);
  if (!existsSync(file)) return null;

  const cases: Testcase[] = [];
  let inputKeys: string[] = [];
  let total = 0;
  const rl = readline.createInterface({ input: createReadStream(file), crlfDelay: Infinity });
  try {
    for await (const line of rl) {
      if (!line.trim()) continue;
      total++;
      if (cases.length >= cap) continue; // keep counting total, stop collecting
      try {
        const rec = JSON.parse(line);
        if (!inputKeys.length) inputKeys = Object.keys(rec.inputs ?? {});
        cases.push({
          name: `Case ${cases.length + 1}`,
          inputs: rec.inputs ?? {},
          expected: typeof rec.expected === "string" ? rec.expected : null,
          hidden: true,
        });
      } catch {
        /* skip malformed line */
      }
    }
  } finally {
    rl.close();
  }
  if (!cases.length) return null;
  return { cases, inputKeys, total };
}
