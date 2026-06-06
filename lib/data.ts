// Server-side data access. Reads the preprocessed JSON from public/data.
import "server-only";
import { readFile } from "node:fs/promises";
import { createReadStream, existsSync, readdirSync } from "node:fs";
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

// Locate the actual file(s) that hold a slug's generated test data. Prefers a
// single `<slug>.jsonl` if present; otherwise finds and lexically sorts the
// `<slug>.jsonl.partNNN` chunks. Returns an empty array when nothing exists.
//
// This is what makes scripts/restore_data.py OPTIONAL: when the test set
// shipped as chunks (because individual files were >100 MB), the judge streams
// the chunks back-to-back instead of requiring a pre-clone reassembly pass.
function resolveTestcaseFiles(slug: string): string[] {
  const intact = path.join(GEN_DIR, `${slug}.jsonl`);
  if (existsSync(intact)) return [intact];
  if (!existsSync(GEN_DIR)) return [];
  const prefix = `${slug}.jsonl.part`;
  let parts: string[];
  try {
    parts = readdirSync(GEN_DIR).filter((f) => f.startsWith(prefix));
  } catch {
    return [];
  }
  if (!parts.length) return [];
  parts.sort(); // partNNN is fixed-width, so a plain sort gives chunk order
  return parts.map((p) => path.join(GEN_DIR, p));
}

// Read up to `cap` cases from the large static set in generated-tests/<slug>.jsonl
// (produced by gen/generate.py). Returns the input-key order too, for batching.
// Transparently stitches across `.partNNN` chunks if the intact file is absent.
export async function getGeneratedCases(
  slug: string,
  cap: number
): Promise<{ cases: Testcase[]; inputKeys: string[]; total: number } | null> {
  if (!validSlug(slug)) return null;
  const files = resolveTestcaseFiles(slug);
  if (!files.length) return null;

  const cases: Testcase[] = [];
  let inputKeys: string[] = [];
  let total = 0;
  for (const f of files) {
    const rl = readline.createInterface({ input: createReadStream(f), crlfDelay: Infinity });
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
  }
  if (!cases.length) return null;
  return { cases, inputKeys, total };
}
