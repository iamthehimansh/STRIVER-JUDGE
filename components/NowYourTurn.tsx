"use client";

import { useState } from "react";
import type { NowYourTurn as NYT } from "@/lib/types";
import { compareOutput } from "@/lib/judge/compare";

interface Props {
  data: NYT;
  // program output for this case after a Run (the ground-truth answer), or null
  computedAnswer: string | null;
}

export default function NowYourTurn({ data, computedAnswer }: Props) {
  const [selected, setSelected] = useState<string | null>(null);

  const correctOption =
    computedAnswer != null
      ? data.options.find((o) => compareOutput(o, computedAnswer)) ?? null
      : null;

  return (
    <div className="mt-6">
      <h3 className="mb-2 text-[15px] font-semibold text-ink">Now your turn!</h3>
      <p className="text-sm text-ink/90">
        <span className="font-semibold">Input:</span> {data.input}
      </p>
      <p className="mb-3 mt-1 text-sm">
        <span className="font-semibold text-ink">Output:</span>{" "}
        <span className="text-brand">
          {selected == null ? "Pick your answer" : `You picked ${selected}`}
        </span>
      </p>

      <div className="grid grid-cols-2 gap-3">
        {data.options.map((opt, i) => {
          const isSelected = selected === opt;
          const revealed = computedAnswer != null && (isSelected || opt === correctOption);
          const isCorrect = opt === correctOption;
          let ring = "ring-edge";
          let dot = "border-ink-faint";
          if (revealed && isCorrect) {
            ring = "ring-ok/60 bg-ok/10";
            dot = "border-ok bg-ok";
          } else if (revealed && isSelected && !isCorrect) {
            ring = "ring-bad/60 bg-bad/10";
            dot = "border-bad bg-bad";
          } else if (isSelected) {
            ring = "ring-accent/60 bg-accent/10";
            dot = "border-accent bg-accent";
          }
          return (
            <button
              key={i}
              onClick={() => setSelected(opt)}
              className={`flex items-center gap-3 rounded-lg bg-bg-raised px-4 py-3 text-left text-sm ring-1 transition ${ring} hover:bg-bg-hover`}
            >
              <span className={`h-3.5 w-3.5 shrink-0 rounded-full border-2 ${dot}`} />
              <span className="font-mono text-ink">{opt}</span>
            </button>
          );
        })}
      </div>

      <p className="mt-2 text-xs text-ink-faint">
        {computedAnswer == null
          ? "Run your solution to check your answer against it."
          : selected == null
          ? "Pick an option above."
          : selected === correctOption
          ? "✓ Correct — matches your solution's output."
          : `✗ Your solution outputs ${computedAnswer} for this input.`}
      </p>
    </div>
  );
}
