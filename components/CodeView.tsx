"use client";

import Editor, { loader, type BeforeMount, type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { useState } from "react";
import type { Language } from "@/lib/types";

// Self-host Monaco from /public/vs (no CDN, works offline). Calling
// loader.config more than once across mounts is safe — Monaco caches the
// already-loaded instance.
loader.config({ paths: { vs: "/vs" } });

interface Props {
  value: string;
  language: Language;
}

const OPTIONS: editor.IStandaloneEditorConstructionOptions = {
  fontSize: 13,
  fontFamily: "var(--font-mono)",
  fontLigatures: false,
  readOnly: true,
  domReadOnly: true,
  minimap: { enabled: false },
  tabSize: 4,
  automaticLayout: true,
  scrollBeyondLastLine: false,
  wordWrap: "on",                  // submitted minified code shouldn't overflow
  wrappingStrategy: "advanced",
  padding: { top: 12, bottom: 12 },
  lineNumbersMinChars: 3,
  glyphMargin: false,
  renderLineHighlight: "none",
  cursorBlinking: "solid",
  scrollbar: { verticalScrollbarSize: 8, horizontalScrollbarSize: 8, useShadows: false },
  overviewRulerLanes: 0,
  fixedOverflowWidgets: true,
  contextmenu: false,
};

// shared with CodeEditor so the read-only history view feels like the
// workspace editor. Re-registering the theme is idempotent so it's safe to
// call on every mount.
const beforeMount: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("striver-dark", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "keyword", foreground: "c792ea" },
      { token: "keyword.directive", foreground: "c792ea" },
      { token: "type", foreground: "82aaff" },
      { token: "identifier", foreground: "e6e8ee" },
      { token: "string", foreground: "c3e88d" },
      { token: "number", foreground: "f78c6c" },
      { token: "comment", foreground: "5c6678", fontStyle: "italic" },
      { token: "delimiter", foreground: "89ddff" },
    ],
    colors: {
      "editor.background": "#16181f",
      "editor.foreground": "#e6e8ee",
      "editorLineNumber.foreground": "#3b4150",
      "editorLineNumber.activeForeground": "#9aa1b1",
      "editor.lineHighlightBackground": "#1c1f2880",
      "editorCursor.foreground": "#a99bff",
      "editorIndentGuide.background1": "#23273350",
      "editorWidget.background": "#1c1f28",
      "editorWidget.border": "#262a35",
      "input.background": "#0f1117",
      "scrollbarSlider.background": "#262a3580",
    },
  });
};

export default function CodeView({ value, language }: Props) {
  // size the editor to the content so we never get a tiny pane or a giant
  // empty box. Capped so megabyte-sized history records don't break layout.
  const [height, setHeight] = useState(220);
  const onMount: OnMount = (ed) => {
    const update = () => {
      const ch = ed.getContentHeight();
      const next = Math.min(800, Math.max(160, ch + 12));
      setHeight(next);
    };
    update();
    ed.onDidContentSizeChange(update);
  };

  return (
    <div
      className="overflow-hidden rounded-lg ring-1 ring-edge"
      style={{ height }}
    >
      <Editor
        height="100%"
        language={language === "c" ? "c" : "cpp"}
        value={value}
        theme="striver-dark"
        beforeMount={beforeMount}
        onMount={onMount}
        options={OPTIONS}
        loading={<div className="p-4 text-sm text-ink-dim">Loading editor…</div>}
      />
    </div>
  );
}
