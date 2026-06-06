"use client";

import { useEffect, useState } from "react";
import type { CaseResult, EditableCase, RunResponse } from "@/lib/types";

interface Props {
  cases: EditableCase[];
  result: RunResponse | null;
  running: boolean;
  onEdit: (caseIdx: number, key: string, value: string) => void;
  onAdd: () => void;
  onRemove: (caseIdx: number) => void;
  onReset: () => void;
}

const VERDICT: Record<string, { label: string; cls: string }> = {
  accepted: { label: "Accepted", cls: "text-ok" },
  wrong_answer: { label: "Wrong Answer", cls: "text-bad" },
  compile_error: { label: "Compilation Error", cls: "text-brand" },
  runtime_error: { label: "Runtime Error", cls: "text-bad" },
  tle: { label: "Time Limit Exceeded", cls: "text-warn" },
  ran: { label: "Executed", cls: "text-accent-soft" },
  error: { label: "Unsupported", cls: "text-brand" },
};

function statusIcon(s: CaseResult["status"]) {
  switch (s) {
    case "passed": return <span className="text-ok">✓</span>;
    case "failed": return <span className="text-bad">✗</span>;
    case "tle": return <span className="text-warn">⏱</span>;
    case "mle": return <span className="text-bad">⊘</span>;
    case "runtime_error": return <span className="text-bad">⚠</span>;
    case "unknown": return <span className="text-accent-soft">•</span>;
    default: return <span className="text-ink-faint">–</span>;
  }
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="mb-1 text-xs uppercase tracking-wide text-ink-faint">{label}</div>
      <pre className="max-h-32 overflow-auto whitespace-pre-wrap rounded-md bg-bg px-3 py-2 font-mono text-[13px] text-ink/90 ring-1 ring-edge">
        {value || <span className="text-ink-faint">(empty)</span>}
      </pre>
    </div>
  );
}

export default function TestPanel({
  cases, result, running, onEdit, onAdd, onRemove, onReset,
}: Props) {
  const [tab, setTab] = useState<"testcases" | "result">("testcases");
  const [sel, setSel] = useState(0);

  useEffect(() => {
    if (result) {
      setTab("result");
      setSel(0);
    }
  }, [result]);

  const activeCase = cases[Math.min(sel, cases.length - 1)];
  const resCases = result?.cases ?? [];
  const activeRes = resCases[Math.min(sel, resCases.length - 1)];

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-edge px-3">
        <div className="flex">
          {(["testcases", "result"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`relative px-3 py-2.5 text-sm transition ${
                tab === t ? "text-ink" : "text-ink-dim hover:text-ink"
              }`}
            >
              {t === "testcases" ? "Test Cases" : "Result"}
              {tab === t && <span className="absolute inset-x-2 -bottom-px h-0.5 rounded bg-accent" />}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2 text-xs text-ink-faint">
          {result && (
            <span className="rounded bg-bg-raised px-1.5 py-0.5 ring-1 ring-edge">
              {result.backend === "docker" ? "🐳 docker" : "💻 local"}
            </span>
          )}
          {result && (
            <span className="rounded bg-bg-raised px-1.5 py-0.5 ring-1 ring-edge">
              {result.limits.memoryMb}MB · {result.limits.timeMs}ms
            </span>
          )}
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-auto p-3">
        {running && (
          <div className="flex items-center gap-2 text-sm text-ink-dim">
            <span className="h-3 w-3 animate-spin rounded-full border-2 border-accent border-t-transparent" />
            Compiling &amp; running…
          </div>
        )}

        {!running && tab === "testcases" && (
          <div>
            <div className="mb-3 flex flex-wrap items-center gap-2">
              {cases.map((c, i) => (
                <button
                  key={i}
                  onClick={() => setSel(i)}
                  className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-xs ring-1 transition ${
                    sel === i
                      ? "bg-bg-raised text-ink ring-accent/50"
                      : "bg-bg-panel text-ink-dim ring-edge hover:bg-bg-hover"
                  }`}
                >
                  {c.name}
                  {c.original === null && <span className="text-[10px] text-accent-soft">•</span>}
                </button>
              ))}
              <button
                onClick={onAdd}
                className="rounded-md bg-bg-panel px-2.5 py-1.5 text-xs text-accent-soft ring-1 ring-edge hover:bg-bg-hover"
                title="Add a custom test case"
              >
                + Add
              </button>
              <button
                onClick={onReset}
                className="ml-auto rounded-md bg-bg-panel px-2.5 py-1.5 text-xs text-ink-dim ring-1 ring-edge hover:bg-bg-hover"
                title="Restore the original example cases"
              >
                Reset
              </button>
            </div>

            {activeCase ? (
              <div className="space-y-3">
                {Object.keys(activeCase.inputs).length === 0 && (
                  <p className="text-xs text-ink-faint">This problem takes no named inputs.</p>
                )}
                {Object.entries(activeCase.inputs).map(([k, v]) => (
                  <div key={k}>
                    <div className="mb-1 text-xs uppercase tracking-wide text-ink-faint">{k}</div>
                    <textarea
                      value={v}
                      spellCheck={false}
                      onChange={(e) => onEdit(sel, k, e.target.value)}
                      rows={Math.min(6, Math.max(1, v.split("\n").length))}
                      className="w-full resize-y rounded-md bg-bg px-3 py-2 font-mono text-[13px] text-ink/90 outline-none ring-1 ring-edge focus:ring-1 focus:ring-accent"
                    />
                  </div>
                ))}
                {activeCase.original !== null && activeCase.expected != null && (
                  <Field label="Expected (original input)" value={activeCase.expected} />
                )}
                <button
                  onClick={() => onRemove(sel)}
                  className="text-xs text-bad/80 hover:text-bad"
                >
                  Remove this case
                </button>
              </div>
            ) : (
              <p className="text-sm text-ink-dim">No test cases. Click “+ Add”.</p>
            )}
            <p className="mt-4 text-xs text-ink-faint">
              Edited or custom cases run without a known answer (shown as output only).
              Unmodified example cases are still graded. <b>Submit</b> always uses the
              hidden test set.
            </p>
          </div>
        )}

        {!running && tab === "result" && (
          <div>
            {!result && <div className="text-sm text-ink-dim">Run your code to see results.</div>}

            {result && (
              <>
                <div className="mb-3 flex items-center gap-3">
                  <span className={`text-base font-semibold ${VERDICT[result.verdict]?.cls ?? "text-ink"}`}>
                    {VERDICT[result.verdict]?.label ?? result.verdict}
                  </span>
                  {result.verdict !== "compile_error" && result.verdict !== "error" && (
                    <span className="text-sm text-ink-dim">
                      {result.passed} / {result.total} passed
                    </span>
                  )}
                  <span className="text-xs text-ink-faint">({result.mode} mode)</span>
                </div>

                {result.message && (
                  <div className="mb-3 rounded-md bg-brand/10 px-3 py-2 text-xs text-brand ring-1 ring-brand/20">
                    {result.message}
                  </div>
                )}

                {result.verdict === "compile_error" ? (
                  <Field label="Compiler output" value={result.compile.stderr} />
                ) : result.cases.length === 0 ? (
                  <div className="text-sm text-ink-dim">No cases executed.</div>
                ) : (
                  <>
                    <div className="mb-3 flex flex-wrap gap-2">
                      {result.cases.map((c, i) => (
                        <button
                          key={i}
                          onClick={() => setSel(i)}
                          className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs ring-1 transition ${
                            sel === i ? "bg-bg-raised ring-accent/50" : "bg-bg-panel ring-edge hover:bg-bg-hover"
                          }`}
                        >
                          {statusIcon(c.status)}
                          <span className="text-ink-dim">{c.name}</span>
                          <span className="text-ink-faint">{c.durationMs}ms</span>
                        </button>
                      ))}
                    </div>
                    {activeRes && (
                      <div className="space-y-3">
                        {Object.entries(activeRes.input).map(([k, v]) => (
                          <Field key={k} label={k} value={v} />
                        ))}
                        <Field label="Your Output" value={activeRes.stdout} />
                        {activeRes.expected != null && <Field label="Expected" value={activeRes.expected} />}
                        {activeRes.stderr && <Field label="Stderr" value={activeRes.stderr} />}
                      </div>
                    )}
                  </>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
