// Lenient output comparison: tolerant of formatting differences (brackets,
// commas, whitespace), numeric precision, and boolean spellings.

function tokenize(s: string): string[] {
  // Strip structural punctuation AND quotes so that the dataset's quoted
  // string outputs (e.g. "bab", [ "DDR" , "DRD" ]) compare equal to the
  // driver's raw prints (bab, DDR DRD).
  return s
    .replace(/[\[\]\{\}\(\),"']/g, " ")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

const BOOL_TRUE = new Set(["true", "1", "yes", "y", "t"]);
const BOOL_FALSE = new Set(["false", "0", "no", "n", "f"]);

function boolNorm(t: string): string | null {
  const l = t.toLowerCase();
  if (BOOL_TRUE.has(l)) return "T";
  if (BOOL_FALSE.has(l)) return "F";
  return null;
}

function numeric(t: string): number | null {
  if (!/^[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?$/.test(t.trim())) return null;
  const n = Number(t);
  return Number.isFinite(n) ? n : null;
}

function numEq(a: number, b: number): boolean {
  if (a === b) return true;
  const diff = Math.abs(a - b);
  return diff <= 1e-6 * Math.max(1, Math.abs(a), Math.abs(b));
}

// canonical key for a token (so 5 == 5.0, true == 1, case-insensitive strings)
function tokenKey(t: string): string {
  const n = numeric(t);
  if (n !== null) return "#" + (Object.is(n, -0) ? 0 : n);
  const b = boolNorm(t);
  if (b !== null) return "@" + b;
  return "$" + t.toLowerCase();
}

// For set/order-insensitive outputs (3-sum, subsets, combinations, …): compare
// the multiset of tokens, ignoring order. (Flattened user output loses row
// grouping, so this is multiset-of-values — adequate for these problems.)
export function compareUnordered(actual: string, expected: string): boolean {
  const at = tokenize(actual ?? "").map(tokenKey).sort();
  const et = tokenize(expected ?? "").map(tokenKey).sort();
  if (at.length !== et.length) return false;
  for (let i = 0; i < at.length; i++) if (at[i] !== et[i]) return false;
  return true;
}

export function compareOutput(actual: string, expected: string, unordered = false): boolean {
  const a = (actual ?? "").trim();
  const e = (expected ?? "").trim();
  if (a === e) return true;
  if (unordered) return compareUnordered(a, e);
  if (a.toLowerCase() === e.toLowerCase()) return true;

  const at = tokenize(a);
  const et = tokenize(e);
  if (at.length !== et.length) return false;
  if (at.length === 0) return true;

  for (let i = 0; i < at.length; i++) {
    const ai = at[i];
    const ei = et[i];
    if (ai === ei) continue;
    const an = numeric(ai);
    const en = numeric(ei);
    if (an !== null && en !== null) {
      if (numEq(an, en)) continue;
      return false;
    }
    const ab = boolNorm(ai);
    const eb = boolNorm(ei);
    if (ab !== null && eb !== null) {
      if (ab === eb) continue;
      return false;
    }
    if (ai.toLowerCase() === ei.toLowerCase()) continue;
    return false;
  }
  return true;
}
