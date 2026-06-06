"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import type { EditableCase, Language, Problem, RunResponse } from "@/lib/types";
import { LANGUAGES, starterFor } from "@/lib/starter";
import DescriptionPanel from "./DescriptionPanel";
import TestPanel from "./TestPanel";

// Monaco must be client-only.
const CodeEditor = dynamic(() => import("./CodeEditor"), {
  ssr: false,
  loading: () => <div className="p-4 text-sm text-ink-dim">Loading editor…</div>,
});

export default function Workspace({ problem }: { problem: Problem }) {
  const [language, setLanguage] = useState<Language>("cpp");
  const [codeMap, setCodeMap] = useState<Record<Language, string>>({
    cpp: starterFor("cpp", problem.starterCpp),
    c: starterFor("c", problem.starterCpp),
  });
  const [result, setResult] = useState<RunResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const initCases = (): EditableCase[] =>
    problem.testcases.map((tc) => ({
      name: tc.name,
      inputs: { ...tc.inputs },
      expected: tc.expected,
      original: { ...tc.inputs },
    }));
  const [cases, setCases] = useState<EditableCase[]>(initCases);
  const inputKeys = Object.keys(
    (problem.testcases.find((t) => Object.keys(t.inputs).length) ?? problem.testcases[0])?.inputs ?? {}
  );

  const [leftPct, setLeftPct] = useState(42);
  const [editorPct, setEditorPct] = useState(62);
  const rowRef = useRef<HTMLDivElement>(null);
  const rightRef = useRef<HTMLDivElement>(null);
  const dragRef = useRef<null | "h" | "v">(null);
  const runSeq = useRef(0);

  const storageKey = `striver:code:${problem.slug}`;

  // load persisted code + language (runs post-hydration, so no SSR mismatch)
  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const saved = JSON.parse(raw);
        setCodeMap((m) => ({
          cpp: typeof saved.cpp === "string" ? saved.cpp : m.cpp,
          c: typeof saved.c === "string" ? saved.c : m.c,
        }));
      }
      const lang = localStorage.getItem("striver:lang");
      if (lang === "c" || lang === "cpp") setLanguage(lang);
    } catch {}
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storageKey]);

  const changeLanguage = (lang: Language) => {
    setLanguage(lang);
    try {
      localStorage.setItem("striver:lang", lang);
    } catch {}
  };

  const setCode = useCallback(
    (v: string) => {
      setCodeMap((m) => {
        const next = { ...m, [language]: v };
        try {
          localStorage.setItem(storageKey, JSON.stringify(next));
        } catch {}
        return next;
      });
    },
    [language, storageKey]
  );

  const resetCode = () => setCode(starterFor(language, problem.starterCpp));

  // editable test case handlers
  const editCase = (i: number, key: string, value: string) =>
    setCases((cs) =>
      cs.map((c, idx) => (idx === i ? { ...c, inputs: { ...c.inputs, [key]: value } } : c))
    );
  const addCase = () =>
    setCases((cs) => [
      ...cs,
      {
        name: `Case ${cs.length + 1}`,
        inputs: Object.fromEntries(inputKeys.map((k) => [k, ""])),
        expected: null,
        original: null,
      },
    ]);
  const removeCase = (i: number) =>
    setCases((cs) => (cs.length <= 1 ? cs : cs.filter((_, idx) => idx !== i)));
  const resetCases = () => setCases(initCases());

  // ground-truth answer for the MCQ = output of the case whose input matches it
  const computedAnswer = useMemo(() => {
    if (!problem.nowYourTurn || !result || result.runMode !== "run") return null;
    const target = problem.testcases[problem.nowYourTurn.tcIndex]?.inputs;
    if (!target) return null;
    const tk = JSON.stringify(target);
    const c = result.cases.find((rc) => JSON.stringify(rc.input) === tk);
    return c ? c.stdout : null;
  }, [problem.nowYourTurn, problem.testcases, result]);

  async function run(mode: "run" | "submit") {
    const seq = ++runSeq.current;
    setRunning(true);
    setError(null);
    setResult(null);
    try {
      const body: Record<string, unknown> = {
        slug: problem.slug,
        language,
        code: codeMap[language],
        mode,
      };
      if (mode === "run") {
        // judge against the (possibly edited) on-screen cases; only grade ones
        // the user left untouched (custom/edited cases run output-only)
        body.cases = cases.map((c) => {
          const unchanged = c.original && JSON.stringify(c.original) === JSON.stringify(c.inputs);
          return { name: c.name, inputs: c.inputs, expected: unchanged ? c.expected : null };
        });
      }
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (runSeq.current !== seq) return; // superseded by a newer run
      if (!res.ok) setError(data?.error || "Run failed");
      else setResult(data as RunResponse);
    } catch (e: any) {
      if (runSeq.current === seq) setError(String(e?.message || e));
    } finally {
      if (runSeq.current === seq) setRunning(false);
    }
  }

  // resizers
  useEffect(() => {
    function onMove(e: PointerEvent) {
      if (dragRef.current === "h" && rowRef.current) {
        const r = rowRef.current.getBoundingClientRect();
        setLeftPct(clamp(((e.clientX - r.left) / r.width) * 100, 24, 72));
      } else if (dragRef.current === "v" && rightRef.current) {
        const r = rightRef.current.getBoundingClientRect();
        setEditorPct(clamp(((e.clientY - r.top) / r.height) * 100, 20, 82));
      }
    }
    function onUp() {
      dragRef.current = null;
      document.body.style.userSelect = "";
      document.body.style.cursor = "";
    }
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, []);
  const startDrag = (which: "h" | "v") => (e: React.PointerEvent) => {
    e.preventDefault();
    dragRef.current = which;
    document.body.style.userSelect = "none";
    document.body.style.cursor = which === "h" ? "col-resize" : "row-resize";
  };

  return (
    <div className="flex h-screen flex-col bg-bg text-ink">
      {/* top bar */}
      <header className="flex h-11 shrink-0 items-center justify-between border-b border-edge px-4">
        <div className="flex items-center gap-3">
          <Link href="/" className="text-sm text-ink-dim hover:text-ink">
            ← Problems
          </Link>
          <span className="text-edge">|</span>
          <span className="text-sm font-medium text-ink">{problem.name}</span>
        </div>
        <span className="text-xs font-semibold tracking-wide text-accent-soft">STRIVER JUDGE</span>
      </header>

      <div ref={rowRef} className="flex min-h-0 flex-1">
        {/* left: description */}
        <section
          className="min-w-0 overflow-hidden border-r border-edge bg-bg-panel"
          style={{ width: `${leftPct}%` }}
        >
          <div className="flex h-full flex-col">
            <div className="flex h-10 shrink-0 items-center border-b border-edge px-3">
              <span className="flex items-center gap-1.5 border-b-2 border-accent px-2 py-2 text-sm font-medium text-ink">
                📝 Description
              </span>
            </div>
            <div className="min-h-0 flex-1 overflow-auto">
              <DescriptionPanel problem={problem} computedAnswer={computedAnswer} />
            </div>
          </div>
        </section>

        {/* horizontal resizer */}
        <div
          onPointerDown={startDrag("h")}
          className="group w-1 shrink-0 cursor-col-resize bg-edge/40 transition hover:bg-accent/60"
        />

        {/* right column */}
        <section ref={rightRef} className="flex min-w-0 flex-1 flex-col">
          {/* editor pane */}
          <div className="flex min-h-0 flex-col" style={{ height: `${editorPct}%` }}>
            <div className="flex h-10 shrink-0 items-center justify-between border-b border-edge bg-bg-panel px-3">
              <select
                value={language}
                onChange={(e) => changeLanguage(e.target.value as Language)}
                className="rounded-md border border-edge bg-bg-raised px-2.5 py-1 text-sm text-ink outline-none hover:bg-bg-hover focus:ring-1 focus:ring-accent"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.label}
                  </option>
                ))}
              </select>
              <div className="flex items-center gap-2">
                <button
                  onClick={resetCode}
                  title="Reset to starter code"
                  className="rounded-md border border-edge bg-bg-raised px-2.5 py-1 text-xs text-ink-dim hover:bg-bg-hover hover:text-ink"
                >
                  Reset
                </button>
                <button
                  onClick={() => run("run")}
                  disabled={running}
                  className="rounded-md border border-edge bg-bg-raised px-3 py-1 text-sm text-ink hover:bg-bg-hover disabled:opacity-50"
                >
                  ▷ Run
                </button>
                <button
                  onClick={() => run("submit")}
                  disabled={running}
                  className="rounded-md bg-ok/90 px-3 py-1 text-sm font-medium text-black hover:bg-ok disabled:opacity-50"
                >
                  Submit
                </button>
              </div>
            </div>
            <div className="min-h-0 flex-1 bg-[#16181f]">
              <CodeEditor value={codeMap[language]} language={language} onChange={setCode} />
            </div>
          </div>

          {/* vertical resizer */}
          <div
            onPointerDown={startDrag("v")}
            className="h-1 shrink-0 cursor-row-resize bg-edge/40 transition hover:bg-accent/60"
          />

          {/* console pane */}
          <div className="min-h-0 flex-1 bg-bg-panel">
            {error && (
              <div className="border-b border-bad/30 bg-bad/10 px-3 py-2 text-xs text-bad">
                {error}
              </div>
            )}
            <TestPanel
              cases={cases}
              result={result}
              running={running}
              onEdit={editCase}
              onAdd={addCase}
              onRemove={removeCase}
              onReset={resetCases}
            />
          </div>
        </section>
      </div>
    </div>
  );
}

function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}
