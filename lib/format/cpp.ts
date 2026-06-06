// Best-effort C/C++ beautifier for displaying SUBMITTED code in the history
// view. The judge submits whatever the user wrote (often minified onto a
// single line for testing), so a structural reformat dramatically improves
// readability.
//
// Approach: a tiny state machine that recognises string/char/line/block
// comments and only injects newlines + indentation around top-level `{`, `}`,
// and `;`. After formatting, a strict sanity check confirms that the
// whitespace-stripped output is byte-identical to the input — if anything
// changed we discard the result and return the original, so we never corrupt
// the user's code.

const IND = "    ";

function reindent(src: string): string {
  let depth = 0;       // brace depth (for indentation)
  let paren = 0;       // paren depth — `;` inside `(...)` is part of for(;;), don't break the line
  let out = "";
  let inLine = false;
  let inBlock = false;
  let inStr: '"' | "'" | null = null;
  const indent = () => IND.repeat(Math.max(0, depth));

  for (let i = 0; i < src.length; i++) {
    const c = src[i];
    const n = src[i + 1] ?? "";

    if (inLine) {
      out += c;
      if (c === "\n") inLine = false;
      continue;
    }
    if (inBlock) {
      out += c;
      if (c === "*" && n === "/") {
        out += n;
        i++;
        inBlock = false;
      }
      continue;
    }
    if (inStr) {
      out += c;
      if (c === "\\" && n) {
        out += n;
        i++;
        continue;
      }
      if (c === inStr) inStr = null;
      continue;
    }
    if (c === "/" && n === "/") { inLine = true; out += c; continue; }
    if (c === "/" && n === "*") { inBlock = true; out += c; continue; }
    if (c === '"' || c === "'") { inStr = c as '"' | "'"; out += c; continue; }

    if (c === "(") { paren++; out += c; continue; }
    if (c === ")") { paren = Math.max(0, paren - 1); out += c; continue; }

    if (c === "{") {
      depth++;
      out += "{";
      // initialiser-list inside () (e.g. max({a,b,c})) — keep inline
      if (paren === 0) out += "\n" + indent();
    } else if (c === "}") {
      depth = Math.max(0, depth - 1);
      if (paren === 0) {
        out = out.replace(/[ \t]+$/, "");
        if (out.length && !out.endsWith("\n")) out += "\n";
        out += indent() + "}";
        const nx = src[i + 1] ?? "";
        if (nx !== ";" && nx !== "," && nx !== ")" && nx !== "") {
          out += "\n" + indent();
        }
      } else {
        out += "}";
      }
    } else if (c === ";" && paren === 0) {
      // statement terminator — break the line. Skip when inside (...) so
      // for(int i=0; i<n; i++) stays on one line.
      out += ";\n" + indent();
    } else {
      out += c;
    }
  }

  // tidy: strip trailing spaces per line, collapse runs of blank lines
  return out
    .split("\n")
    .map((l) => l.replace(/[ \t]+$/, ""))
    .filter((l, i, a) => !(l === "" && a[i - 1] === ""))
    .join("\n")
    .trim();
}

function stripWs(s: string): string {
  return s.replace(/\s+/g, "");
}

export function beautifyCpp(src: string): string {
  if (!src) return src;
  // If the code already has reasonable structure, leave it alone.
  const lines = src.split("\n").map((l) => l.trim()).filter(Boolean);
  if (lines.length >= 6) return src;

  let out: string;
  try {
    out = reindent(src);
  } catch {
    return src;
  }
  // strict sanity: format must only add whitespace, never lose / change chars
  if (stripWs(out) !== stripWs(src)) return src;
  return out;
}
