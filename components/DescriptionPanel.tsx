"use client";

import type { Problem } from "@/lib/types";
import DifficultyBadge from "./DifficultyBadge";
import NowYourTurn from "./NowYourTurn";

interface Props {
  problem: Problem;
  computedAnswer: string | null;
}

const LINKS = [
  { key: "article", label: "Article" },
  { key: "youtube", label: "YouTube" },
  { key: "leetcode", label: "LeetCode" },
  { key: "gfg", label: "GfG" },
  { key: "cn", label: "CodingNinjas" },
] as const;

export default function DescriptionPanel({ problem, computedAnswer }: Props) {
  return (
    <div className="space-y-4 px-5 py-5">
      <div>
        <h1 className="text-xl font-semibold text-ink">{problem.name}</h1>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          <DifficultyBadge difficulty={problem.difficulty} />
          {problem.category && (
            <span className="rounded-full bg-bg-raised px-2.5 py-0.5 text-xs text-ink-dim ring-1 ring-edge">
              {problem.category}
            </span>
          )}
          {LINKS.map(({ key, label }) => {
            const href = (problem.links as Record<string, string | null | undefined>)[key];
            return href ? (
              <a
                key={key}
                href={href}
                target="_blank"
                rel="noreferrer"
                className="rounded-full bg-bg-raised px-2.5 py-0.5 text-xs text-ink-dim ring-1 ring-edge hover:bg-bg-hover hover:text-accent-soft"
              >
                {label} ↗
              </a>
            ) : null;
          })}
        </div>
      </div>

      {problem.statement && (
        <div className="tuf-content" dangerouslySetInnerHTML={{ __html: problem.statement }} />
      )}

      {problem.examples.map((ex, i) => (
        <div key={i} className="space-y-1">
          <p className="text-[15px] font-semibold text-ink">Example {i + 1}</p>
          <div className="rounded-lg border border-edge bg-bg-panel/60 px-4 py-3 text-sm">
            <p>
              <span className="font-semibold text-ink">Input:</span>{" "}
              <span className="font-mono text-ink/90">{ex.input}</span>
            </p>
            <p className="mt-1">
              <span className="font-semibold text-ink">Output:</span>{" "}
              <span className="font-mono text-ink/90">{ex.output}</span>
            </p>
            {ex.explanation && (
              <p className="mt-1 text-ink-dim">
                <span className="font-semibold text-ink">Explanation:</span> {ex.explanation}
              </p>
            )}
          </div>
        </div>
      ))}

      {problem.nowYourTurn && (
        <NowYourTurn data={problem.nowYourTurn} computedAnswer={computedAnswer} />
      )}

      {problem.constraints && (
        <div>
          <p className="mb-1 text-[15px] font-semibold text-ink">Constraints</p>
          <div
            className="tuf-content"
            dangerouslySetInnerHTML={{ __html: problem.constraints }}
          />
        </div>
      )}
    </div>
  );
}
