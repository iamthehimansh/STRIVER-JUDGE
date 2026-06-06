// Generates a complete, compile-ready C++ program from a user's `class Solution`
// plus the problem's testcases, by parsing the method signature and emitting a
// driver `main()` that parses inputs, calls the method, and prints the result
// in a canonical form. Falls back gracefully for unsupported signatures.

import type { Testcase } from "../types";

export interface Param {
  raw: string;
  name: string;
  type: CanonType;
}

export interface CanonType {
  base: string; // normalized, e.g. "vector<int>"
  decl: string; // C++ value declaration type (no &/const)
  reader: string | null; // _io reader fn name, null if unsupported
  isRef: boolean;
  isConst: boolean;
  isPtr: boolean;
  isArray: boolean;
  supported: boolean;
}

export interface Signature {
  ok: boolean;
  className: string;
  methodName: string;
  returnType: CanonType;
  returnIsVoid: boolean;
  params: Param[];
  hasUserMain: boolean;
  reason?: string;
}

// base C++ type -> { reader fn, value decl }. Anything not here is unsupported.
const TYPE_TABLE: Record<string, { reader: string; decl: string }> = {
  "int": { reader: "rdInt", decl: "int" },
  "long": { reader: "rdLong", decl: "long" },
  "long long": { reader: "rdLL", decl: "long long" },
  "size_t": { reader: "rdLL", decl: "long long" },
  "double": { reader: "rdD", decl: "double" },
  "float": { reader: "rdD", decl: "double" },
  "bool": { reader: "rdBool", decl: "bool" },
  "char": { reader: "rdChar", decl: "char" },
  "string": { reader: "rdStr", decl: "string" },
  "vector<int>": { reader: "rdVI", decl: "vector<int>" },
  "vector<long>": { reader: "rdVLL", decl: "vector<long long>" },
  "vector<long long>": { reader: "rdVLL", decl: "vector<long long>" },
  "vector<double>": { reader: "rdVD", decl: "vector<double>" },
  "vector<char>": { reader: "rdVC", decl: "vector<char>" },
  "vector<bool>": { reader: "rdVB", decl: "vector<bool>" },
  "vector<string>": { reader: "rdVS", decl: "vector<string>" },
  "vector<vector<int>>": { reader: "rdVVI", decl: "vector<vector<int>>" },
  "vector<vector<long long>>": { reader: "rdVVLL", decl: "vector<vector<long long>>" },
  "vector<vector<double>>": { reader: "rdVVD", decl: "vector<vector<double>>" },
  "vector<vector<char>>": { reader: "rdVVC", decl: "vector<vector<char>>" },
  "vector<vector<string>>": { reader: "rdVVS", decl: "vector<vector<string>>" },
  // structural pointer types — the harness defines the structs (the starter
  // comments them out) and (de)serializes from the dataset's formats.
  "TreeNode": { reader: "rdTree", decl: "TreeNode*" },
  "ListNode": { reader: "rdList", decl: "ListNode*" },
};

// pointer base types the harness can build/print
const POINTER_OK = new Set(["TreeNode", "ListNode"]);

// return types we know how to print (void handled separately)
const PRINTABLE = new Set(Object.keys(TYPE_TABLE));

function normalizeBase(t: string): string {
  return t
    .replace(/\bconst\b/g, "")
    .replace(/[&*]/g, "")
    .replace(/\[\s*\]/g, "")
    .replace(/\s*<\s*/g, "<")
    .replace(/\s*>\s*/g, ">")
    .replace(/\s*,\s*/g, ",")
    .replace(/\s+/g, " ")
    .trim();
}

export function canonType(raw: string): CanonType {
  const isConst = /\bconst\b/.test(raw);
  const isArray = /\[\s*\]/.test(raw);
  const isPtr = /\*/.test(raw);
  const isRef = /&/.test(raw);
  const base = normalizeBase(raw);

  // C-array params (string dict[], int arr[], vector<int> adj[]) — treat as the
  // vector equivalent (so we can read JSON-array inputs), then pass .data() at
  // the call site to get the pointer the user's signature wants.
  if (isArray) {
    const vecKey = `vector<${base}>`;
    const vecEntry = TYPE_TABLE[vecKey];
    if (vecEntry) {
      return {
        base: vecKey,
        decl: vecEntry.decl,
        reader: vecEntry.reader,
        isRef: false,
        isConst,
        isPtr: false,
        isArray: true,
        supported: true,
      };
    }
  }

  const entry = TYPE_TABLE[base];
  const supported = !!entry && !isArray && (!isPtr || POINTER_OK.has(base));
  return {
    base,
    decl: entry ? entry.decl : base,
    reader: entry ? entry.reader : null,
    isRef,
    isConst,
    isPtr,
    isArray,
    supported,
  };
}

// param names treated as "the previous array's size" (auto-derived, not from
// data) — covers (string dict[], int N, int K) / (vector<int>& arr, int n).
// K is intentionally NOT in this list (it's almost always a real parameter).
const LEN_NAMES = new Set(["n", "m", "size", "sz", "len", "length", "count"]);

function isLengthParam(p: Param): boolean {
  if (!p.name || !LEN_NAMES.has(p.name.toLowerCase())) return false;
  return ["int", "long", "long long", "size_t"].includes(p.type.base);
}

function isArrayLike(p: Param): boolean {
  return p.type.isArray || p.type.base.startsWith("vector<");
}

// split a parameter list on top-level commas (ignoring those inside <>, (), [])
function splitParams(s: string): string[] {
  const out: string[] = [];
  let depth = 0;
  let cur = "";
  for (const ch of s) {
    if (ch === "<" || ch === "(" || ch === "[") depth++;
    else if (ch === ">" || ch === ")" || ch === "]") depth = Math.max(0, depth - 1);
    if (ch === "," && depth === 0) {
      out.push(cur);
      cur = "";
    } else cur += ch;
  }
  if (cur.trim()) out.push(cur);
  return out;
}

function parseParam(raw: string): Param {
  const trimmed = raw.trim();
  // name = trailing identifier (with optional [] suffix); type = the rest
  const m = trimmed.match(/([A-Za-z_]\w*)\s*(\[\s*\])?\s*$/);
  let name = "";
  let typeStr = trimmed;
  if (m && !["int", "long", "double", "char", "bool", "void", "float", "string", "unsigned"].includes(m[1])) {
    name = m[1];
    typeStr = trimmed.slice(0, m.index).trim() + (m[2] ? "[]" : "");
  }
  return { raw: trimmed, name, type: canonType(typeStr) };
}

const KEYWORDS = new Set([
  "if", "for", "while", "switch", "return", "sizeof", "new", "delete",
  "else", "do", "catch", "throw",
]);

// Parse the first real method inside `class Solution`.
export function parseSignature(code: string): Signature {
  const hasUserMain = /\b(?:int|void|auto)\s+main\s*\(/.test(code);

  const classMatch = code.match(/\b(?:class|struct)\s+(Solution)\b/);
  const className = classMatch ? classMatch[1] : "Solution";

  // search region: prefer inside the Solution class body
  let region = code;
  if (classMatch) {
    const start = (classMatch.index ?? 0) + classMatch[0].length;
    region = code.slice(start);
  }

  const methodRe =
    /([A-Za-z_][\w:<>,\*&\s]*?)\s+([A-Za-z_]\w*)\s*\(([^;{)]*)\)\s*(?:const\s*)?(?:noexcept\s*)?\{/g;

  let mm: RegExpExecArray | null;
  while ((mm = methodRe.exec(region)) !== null) {
    let retRaw = mm[1];
    const name = mm[2];
    const paramsRaw = mm[3];
    if (KEYWORDS.has(name) || name === "Solution" || name === "main") continue;
    // strip access specifiers / leading scope from the return type
    retRaw = retRaw.replace(/\b(public|private|protected)\s*:/g, "").trim();
    if (!retRaw) continue;
    const returnType = canonType(retRaw);
    const returnIsVoid = returnType.base === "void";
    const params = paramsRaw.trim() ? splitParams(paramsRaw).map(parseParam) : [];

    // validate support
    const returnSupported = returnIsVoid || PRINTABLE.has(returnType.base);
    const paramsSupported = params.every((p) => p.type.supported);
    const ok = returnSupported && paramsSupported;
    return {
      ok,
      className,
      methodName: name,
      returnType,
      returnIsVoid,
      params,
      hasUserMain,
      reason: ok
        ? undefined
        : !returnSupported
        ? `Unsupported return type: ${returnType.base}`
        : `Unsupported parameter type: ${params.find((p) => !p.type.supported)?.type.base}`,
    };
  }

  return {
    ok: false,
    className,
    methodName: "",
    returnType: canonType("void"),
    returnIsVoid: true,
    params: [],
    hasUserMain,
    reason: "Could not find a Solution method to call.",
  };
}

// Bind testcase input keys to method params: name-match first, then positional.
export function bindInputs(
  params: Param[],
  inputKeys: string[]
): { binding: (string | null)[]; unboundKeys: string[] } {
  const used = new Set<number>();
  const binding: (string | null)[] = params.map(() => null);
  const norm = (s: string) => s.toLowerCase().replace(/^_+/, "");

  // pass 1: name match
  params.forEach((p, i) => {
    if (!p.name) return;
    const k = inputKeys.findIndex((key, idx) => !used.has(idx) && norm(key) === norm(p.name));
    if (k >= 0) {
      binding[i] = inputKeys[k];
      used.add(k);
    }
  });
  // pass 2: positional for still-unbound params
  const remaining = inputKeys.map((k, i) => i).filter((i) => !used.has(i));
  let r = 0;
  params.forEach((p, i) => {
    if (binding[i] === null && r < remaining.length) {
      binding[i] = inputKeys[remaining[r]];
      used.add(remaining[r]);
      r++;
    }
  });
  const unboundKeys = inputKeys.filter((_, i) => !used.has(i));
  return { binding, unboundKeys };
}

const RAW_DELIM = "STRIVERIO";
function cppRawString(s: string): string {
  // Raw string literal; guard against the (extremely unlikely) delimiter clash.
  if (s.includes(`)${RAW_DELIM}"`)) {
    return JSON.stringify(s); // fall back to escaped literal
  }
  return `R"${RAW_DELIM}(${s})${RAW_DELIM}"`;
}

export interface HarnessBuild {
  supported: boolean;
  source: string;
  // per-case extra stdin (unbound inputs), aligned with testcases order
  stdinPerCase: string[];
  reason?: string;
}

// Build the full single-compile C++ program. Run binary with argv[1] = case index.
export function buildHarness(code: string, testcases: Testcase[]): HarnessBuild {
  const sig = parseSignature(code);

  if (sig.hasUserMain) {
    // user wrote a complete program -> free-form handled by caller
    return { supported: false, source: "", stdinPerCase: [], reason: "user-main" };
  }
  if (!sig.ok) {
    return { supported: false, source: "", stdinPerCase: [], reason: sig.reason };
  }

  const params = sig.params;
  // Determine input-key ordering from first testcase that has inputs.
  const sampleKeys = (testcases.find((t) => Object.keys(t.inputs).length) || testcases[0] || { inputs: {} })
    .inputs;
  const inputKeys = Object.keys(sampleKeys);
  const { binding } = bindInputs(params, inputKeys);

  const nParam = params.length;
  const nCase = testcases.length;

  // Build the [case][param] raw-value table + per-case unbound stdin.
  const stdinPerCase: string[] = [];
  const dataRows: string[] = [];
  for (const tc of testcases) {
    const keys = Object.keys(tc.inputs);
    const usedKeys = new Set(binding.filter((b): b is string => b !== null));
    const row = params.map((_, i) => {
      const key = binding[i];
      const val = key != null ? tc.inputs[key] ?? "" : "";
      return cppRawString(val);
    });
    if (nParam > 0) dataRows.push(`    { ${row.join(", ")} },`);
    // unbound inputs -> stdin (in their declared order)
    const extra = keys.filter((k) => !usedKeys.has(k)).map((k) => tc.inputs[k]);
    stdinPerCase.push(extra.join("\n"));
  }

  // declarations + call
  const decls: string[] = [];
  let lastArrayIdx = -1;
  params.forEach((p, i) => {
    const varName = p.name || `_a${i}`;
    const unbound = binding[i] === null;
    if (unbound && isLengthParam(p) && lastArrayIdx >= 0) {
      // size auto-derived from the previous array param (covers e.g.
      // `findOrder(string dict[], int N, int K)` where the dataset omits N).
      const prev = params[lastArrayIdx].name || `_a${lastArrayIdx}`;
      decls.push(`  ${p.type.decl} ${varName} = (${p.type.decl})${prev}.size();`);
    } else {
      decls.push(
        `  ${p.type.decl} ${varName} = _io::${p.type.reader!}(string(_DATA[_c][${i}]));`
      );
    }
    if (isArrayLike(p)) lastArrayIdx = i;
  });
  // C-array params take a pointer; vector exposes one via .data()
  const argList = params
    .map((p, i) => (p.name || `_a${i}`) + (p.type.isArray ? ".data()" : ""))
    .join(", ");

  let callBlock: string;
  if (sig.returnIsVoid) {
    // void methods mutate refs OR C-array params in place — print both. The
    // C-array is held as a vector locally so post-call vector content reflects
    // the mutation that came through .data().
    const printRefs = params.filter(
      (p) => (p.type.isRef || p.type.isArray) && !p.type.isConst
    );
    const printStmts = printRefs
      .map((p, idx) => {
        const v = p.name || `_a${params.indexOf(p)}`;
        return `${idx ? '  cout << "\\n";\n' : ""}  _io::pr(${v});`;
      })
      .join("\n");
    callBlock = `  _sol.${sig.methodName}(${argList});\n${printStmts}`;
  } else {
    callBlock = `  auto _ret = _sol.${sig.methodName}(${argList});\n  _io::pr(_ret);`;
  }

  const dataDecl =
    nParam > 0
      ? `  static const char* _DATA[${nCase}][${nParam}] = {\n${dataRows.join("\n")}\n  };`
      : "";

  const source = `${PREAMBLE}
/* ===================== user code ===================== */
${code}
/* ======================= driver ====================== */
int main(int argc, char** argv) {
  ios_base::sync_with_stdio(false);
  cin.tie(nullptr);
  int _c = (argc > 1) ? atoi(argv[1]) : 0;
${dataDecl}
  ${sig.className} _sol;
${decls.join("\n")}
${callBlock}
  cout.flush();
  return 0;
}
`;

  return { supported: true, source, stdinPerCase };
}

export interface BatchBuild {
  supported: boolean;
  source: string;
  inputKeys: string[];
  reason?: string;
}

// Build a harness that judges MANY cases in a single process: it reads one
// tab-separated line of input values per case from stdin (columns ordered by
// `inputKeys`), calls the method, and prints one output line per case. Used by
// "Submit" against the large generated test sets (a process-per-case would be
// far too slow at 100k+ cases).
export function buildBatchHarness(code: string, inputKeys: string[]): BatchBuild {
  const sig = parseSignature(code);
  if (sig.hasUserMain) return { supported: false, source: "", inputKeys, reason: "user-main" };
  if (!sig.ok) return { supported: false, source: "", inputKeys, reason: sig.reason };

  const { binding } = bindInputs(sig.params, inputKeys);
  const cols = sig.params.map((p, i) => (binding[i] != null ? inputKeys.indexOf(binding[i] as string) : -1));

  // unbound params are OK in batch mode only if they're length-named and a
  // prior array param can supply .size() (covers (string dict[], int N, int K)).
  let lastArr = -1;
  for (let i = 0; i < sig.params.length; i++) {
    const p = sig.params[i];
    if (cols[i] < 0) {
      if (!(isLengthParam(p) && lastArr >= 0)) {
        return {
          supported: false, source: "", inputKeys,
          reason: `unbound parameter in batch mode: ${p.name || "?"}`,
        };
      }
    }
    if (isArrayLike(p)) lastArr = i;
  }

  const decls = sig.params
    .map((p, i) => {
      const v = p.name || `_a${i}`;
      if (cols[i] < 0) {
        // find the array param that precedes us
        let arr = -1;
        for (let j = 0; j < i; j++) if (isArrayLike(sig.params[j])) arr = j;
        const prev = sig.params[arr].name || `_a${arr}`;
        return `    ${p.type.decl} ${v} = (${p.type.decl})${prev}.size();`;
      }
      return `    ${p.type.decl} ${v} = _io::${p.type.reader}(_f[${cols[i]}]);`;
    })
    .join("\n");
  const argList = sig.params
    .map((p, i) => (p.name || `_a${i}`) + (p.type.isArray ? ".data()" : ""))
    .join(", ");

  // Each case must emit exactly ONE line. Capture pr() into a buffer and flatten
  // any internal newlines (e.g. nested-vector row separators) to spaces.
  let call: string;
  let printBody: string;
  if (sig.returnIsVoid) {
    const refs = sig.params.filter(
      (p) => (p.type.isRef || p.type.isArray) && !p.type.isConst
    );
    const stmts = refs
      .map((p, idx) => {
        const v = p.name || `_a${sig.params.indexOf(p)}`;
        return `${idx ? '      _o << " ";\n' : ""}      { streambuf* _sb=cout.rdbuf(_o.rdbuf()); _io::pr(${v}); cout.rdbuf(_sb); }`;
      })
      .join("\n");
    call = `    _sol.${sig.methodName}(${argList});`;
    printBody = stmts || "      ;";
  } else {
    call = `    auto _ret = _sol.${sig.methodName}(${argList});`;
    printBody = `      { streambuf* _sb=cout.rdbuf(_o.rdbuf()); _io::pr(_ret); cout.rdbuf(_sb); }`;
  }

  const source = `${PREAMBLE}
/* ===================== user code ===================== */
${code}
/* ==================== batch driver =================== */
static vector<string> _split(const string& s) {
  vector<string> o; string c;
  for (char ch : s) { if (ch == '\\t') { o.push_back(c); c.clear(); } else c += ch; }
  o.push_back(c); return o;
}
int main() {
  ios_base::sync_with_stdio(false);
  cin.tie(nullptr);
  ${sig.className} _sol;
  string line;
  while (getline(cin, line)) {
    if (line.empty()) continue;
    vector<string> _f = _split(line);
    while ((int)_f.size() < ${inputKeys.length}) _f.push_back("");
${decls}
${call}
    { ostringstream _o;
${printBody}
      string _s = _o.str(); for (char& ch : _s) if (ch == '\\n') ch = ' '; cout << _s << '\\n'; }
  }
  cout.flush();
  return 0;
}
`;
  return { supported: true, source, inputKeys };
}

// ----------------------------------------------------------------------------
// C++ preamble: explicit includes (libc++/clang on macOS lacks <bits/stdc++.h>,
// but a shim header is also injected at compile time for user code that uses it)
// plus the _io parsing/printing helpers.
// ----------------------------------------------------------------------------
export const PREAMBLE = String.raw`#include <bits/stdc++.h>
using namespace std;

// Structural types — the problem starters comment these out and expect the
// judge to provide them (TreeNode uses .data, ListNode uses .val, per dataset).
struct TreeNode {
  int data;
  TreeNode *left, *right;
  TreeNode(int x) : data(x), left(nullptr), right(nullptr) {}
};
struct ListNode {
  int val;
  ListNode *next;
  ListNode() : val(0), next(nullptr) {}
  ListNode(int x) : val(x), next(nullptr) {}
  ListNode(int x, ListNode* n) : val(x), next(n) {}
};

namespace _io {

static inline string trim(const string& s) {
  size_t a = 0, b = s.size();
  while (a < b && isspace((unsigned char)s[a])) a++;
  while (b > a && isspace((unsigned char)s[b - 1])) b--;
  return s.substr(a, b - a);
}

static inline string strip_brackets(const string& in) {
  string s = trim(in);
  if (s.size() >= 2) {
    char c = s.front(), d = s.back();
    if ((c == '[' && d == ']') || (c == '{' && d == '}') || (c == '(' && d == ')'))
      return s.substr(1, s.size() - 2);
  }
  return s;
}

// scalar tokens at any depth; quoted strings kept whole (without quotes)
static vector<string> tokens(const string& in) {
  vector<string> out; string cur; bool inq = false; char q = 0;
  auto flush = [&]() { if (!cur.empty()) { out.push_back(cur); cur.clear(); } };
  for (size_t i = 0; i < in.size(); ++i) {
    char ch = in[i];
    if (inq) { if (ch == q) { inq = false; out.push_back(cur); cur.clear(); } else cur.push_back(ch); continue; }
    if (ch == '"' || ch == '\'') { flush(); inq = true; q = ch; cur.clear(); continue; }
    if (ch == '[' || ch == '{' || ch == '(' || ch == ']' || ch == '}' || ch == ')' ||
        ch == ',' || isspace((unsigned char)ch)) { flush(); continue; }
    cur.push_back(ch);
  }
  flush();
  return out;
}

// top-level bracket groups: "[1,2],[3,4]" -> {"[1,2]","[3,4]"}
static vector<string> groups(const string& in) {
  string s = strip_brackets(in);
  vector<string> out; string cur; int depth = 0;
  for (char ch : s) {
    if (ch == '[' || ch == '{' || ch == '(') { if (depth == 0) cur.clear(); depth++; cur.push_back(ch); }
    else if (ch == ']' || ch == '}' || ch == ')') { depth--; cur.push_back(ch); if (depth == 0) { out.push_back(cur); cur.clear(); } }
    else if (depth > 0) cur.push_back(ch);
  }
  return out;
}

static long long toLL(const string& s) { string t = trim(s); if (t.empty()) return 0; try { return stoll(t); } catch (...) { try { return (long long)stod(t); } catch (...) { return 0; } } }
static double toD(const string& s) { string t = trim(s); if (t.empty()) return 0; try { return stod(t); } catch (...) { return 0; } }
static string unquote(const string& s) { string t = trim(s); if (t.size() >= 2 && ((t.front() == '"' && t.back() == '"') || (t.front() == '\'' && t.back() == '\''))) return t.substr(1, t.size() - 2); return t; }

static int        rdInt (const string& s) { return (int)toLL(s); }
static long       rdLong(const string& s) { return (long)toLL(s); }
static long long  rdLL  (const string& s) { return toLL(s); }
static double     rdD   (const string& s) { return toD(s); }
static bool       rdBool(const string& s) { string t = trim(s); for (auto& c : t) c = tolower((unsigned char)c); return t == "1" || t == "true" || t == "yes" || t == "y"; }
static char       rdChar(const string& s) { string t = unquote(s); return t.empty() ? 0 : t[0]; }
static string     rdStr (const string& s) { return unquote(s); }

static vector<int>            rdVI (const string& s) { vector<int> v;            for (auto& t : tokens(strip_brackets(s))) v.push_back((int)toLL(t)); return v; }
static vector<long long>      rdVLL(const string& s) { vector<long long> v;      for (auto& t : tokens(strip_brackets(s))) v.push_back(toLL(t)); return v; }
static vector<double>         rdVD (const string& s) { vector<double> v;         for (auto& t : tokens(strip_brackets(s))) v.push_back(toD(t)); return v; }
static vector<char>           rdVC (const string& s) { vector<char> v;           for (auto& t : tokens(strip_brackets(s))) { string u = unquote(t); if (!u.empty()) v.push_back(u[0]); } return v; }
static vector<bool>           rdVB (const string& s) { vector<bool> v;           for (auto& t : tokens(strip_brackets(s))) { string u = trim(t); for (auto& c : u) c = tolower((unsigned char)c); v.push_back(u == "1" || u == "true"); } return v; }
static vector<string>         rdVS (const string& s) { vector<string> v;         for (auto& t : tokens(strip_brackets(s))) v.push_back(t); return v; }
static vector<vector<int>>       rdVVI (const string& s) { vector<vector<int>> v;       for (auto& g : groups(s)) v.push_back(rdVI(g)); return v; }
static vector<vector<long long>> rdVVLL(const string& s) { vector<vector<long long>> v; for (auto& g : groups(s)) v.push_back(rdVLL(g)); return v; }
static vector<vector<double>>    rdVVD (const string& s) { vector<vector<double>> v;    for (auto& g : groups(s)) v.push_back(rdVD(g)); return v; }
static vector<vector<char>>      rdVVC (const string& s) { vector<vector<char>> v;      for (auto& g : groups(s)) v.push_back(rdVC(g)); return v; }
static vector<vector<string>> rdVVS(const string& s) { vector<vector<string>> v; for (auto& g : groups(s)) v.push_back(rdVS(g)); return v; }

// level-order, space/comma separated, "null"/"N" = missing child (LeetCode-style)
static TreeNode* rdTree(const string& s) {
  vector<string> toks = tokens(strip_brackets(s));
  if (toks.empty() || toks[0] == "null" || toks[0] == "N") return nullptr;
  TreeNode* root = new TreeNode((int)toLL(toks[0]));
  queue<TreeNode*> q; q.push(root);
  size_t i = 1;
  while (!q.empty() && i < toks.size()) {
    TreeNode* node = q.front(); q.pop();
    if (i < toks.size()) { if (toks[i] != "null" && toks[i] != "N") { node->left = new TreeNode((int)toLL(toks[i])); q.push(node->left); } i++; }
    if (i < toks.size()) { if (toks[i] != "null" && toks[i] != "N") { node->right = new TreeNode((int)toLL(toks[i])); q.push(node->right); } i++; }
  }
  return root;
}
static ListNode* rdList(const string& s) {
  ListNode dummy; ListNode* cur = &dummy;
  for (auto& t : tokens(strip_brackets(s))) { if (t == "null" || t == "N") continue; cur->next = new ListNode((int)toLL(t)); cur = cur->next; }
  return dummy.next;
}

static void pr(long long x) { cout << x; }
static void pr(int x) { cout << x; }
static void pr(long x) { cout << x; }
static void pr(unsigned x) { cout << x; }
static void pr(unsigned long x) { cout << x; }
static void pr(unsigned long long x) { cout << x; }
static void pr(bool x) { cout << (x ? "true" : "false"); }
static void pr(char x) { cout << x; }
static void pr(double x) { ostringstream o; o << setprecision(10) << x; cout << o.str(); }
static void pr(const string& x) { cout << x; }
static void pr(const char* x) { cout << x; }
static void pr(const vector<bool>& v) { for (size_t i = 0; i < v.size(); ++i) { if (i) cout << ' '; cout << (v[i] ? "true" : "false"); } }
template <class T> static void pr(const vector<T>& v) { for (size_t i = 0; i < v.size(); ++i) { if (i) cout << ' '; pr(v[i]); } }
template <class T> static void pr(const vector<vector<T>>& v) { for (size_t i = 0; i < v.size(); ++i) { if (i) cout << '\n'; pr(v[i]); } }
static void pr(TreeNode* root) {
  vector<string> out; queue<TreeNode*> q; if (root) q.push(root);
  while (!q.empty()) { TreeNode* n = q.front(); q.pop(); if (n) { out.push_back(to_string(n->data)); q.push(n->left); q.push(n->right); } else out.push_back("null"); }
  while (!out.empty() && out.back() == "null") out.pop_back();
  for (size_t i = 0; i < out.size(); ++i) { if (i) cout << ' '; cout << out[i]; }
}
static void pr(ListNode* head) {
  bool first = true; for (ListNode* c = head; c; c = c->next) { if (!first) cout << ' '; cout << c->val; first = false; }
}

} // namespace _io
`;

// The <bits/stdc++.h> shim injected so competitive-style includes work on macOS clang.
export const BITS_SHIM = `#pragma once
#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <algorithm>
#include <numeric>
#include <queue>
#include <stack>
#include <deque>
#include <list>
#include <utility>
#include <functional>
#include <climits>
#include <cmath>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <cctype>
#include <cstdint>
#include <bitset>
#include <array>
#include <tuple>
#include <limits>
#include <cassert>
#include <iterator>
#include <complex>
#include <random>
#include <chrono>
#include <memory>
`;
