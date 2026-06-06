"use client";

import Editor, { loader, type BeforeMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import type { Language } from "@/lib/types";

// Self-host the Monaco assets copied into /public/vs (no CDN dependency).
loader.config({ paths: { vs: "/vs" } });

interface Props {
  value: string;
  language: Language;
  onChange: (v: string) => void;
}

// Intentionally NO C/C++ language server: only Monaco's built-in tokenizer
// keyword completions + word-based suggestions from the current document —
// i.e. the plain "what the editor already knows" autocomplete, nothing heavier.
const OPTIONS: editor.IStandaloneEditorConstructionOptions = {
  fontSize: 14,
  fontFamily: "var(--font-mono)",
  fontLigatures: false,
  minimap: { enabled: false },
  tabSize: 4,
  insertSpaces: true,
  automaticLayout: true,
  scrollBeyondLastLine: false,
  smoothScrolling: true,
  padding: { top: 12, bottom: 12 },
  lineNumbersMinChars: 3,
  glyphMargin: false,
  renderLineHighlight: "line",
  cursorBlinking: "smooth",
  roundedSelection: true,
  quickSuggestions: { other: true, comments: false, strings: false },
  wordBasedSuggestions: "currentDocument",
  suggestOnTriggerCharacters: true,
  acceptSuggestionOnEnter: "smart",
  tabCompletion: "on",
  parameterHints: { enabled: false },
  suggest: { showWords: true, showKeywords: true, preview: true },
  bracketPairColorization: { enabled: true },
  scrollbar: { verticalScrollbarSize: 10, horizontalScrollbarSize: 10, useShadows: false },
  overviewRulerLanes: 0,
  fixedOverflowWidgets: true,
};

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
      "editor.selectionBackground": "#3b3565",
      "editorCursor.foreground": "#a99bff",
      "editorIndentGuide.background1": "#23273350",
      "editorWidget.background": "#1c1f28",
      "editorWidget.border": "#262a35",
      "editorSuggestWidget.background": "#1c1f28",
      "editorSuggestWidget.selectedBackground": "#2b3040",
      "editorSuggestWidget.border": "#262a35",
      "input.background": "#0f1117",
      "scrollbarSlider.background": "#262a3580",
    },
  });
};

export default function CodeEditor({ value, language, onChange }: Props) {
  return (
    <Editor
      language={language === "c" ? "c" : "cpp"}
      value={value}
      theme="striver-dark"
      beforeMount={beforeMount}
      onChange={(v) => onChange(v ?? "")}
      options={OPTIONS}
      loading={<div className="p-4 text-sm text-ink-dim">Loading editor…</div>}
    />
  );
}
