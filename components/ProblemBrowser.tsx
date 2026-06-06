"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { ProblemIndexItem } from "@/lib/types";
import { difficultyKey } from "@/lib/starter";

const DOT: Record<string, string> = {
  easy: "bg-diff-easy",
  medium: "bg-diff-medium",
  hard: "bg-diff-hard",
};

const FILTERS = ["all", "easy", "medium", "hard"] as const;

export default function ProblemBrowser({ items }: { items: ProblemIndexItem[] }) {
  const [query, setQuery] = useState("");
  const [diff, setDiff] = useState<(typeof FILTERS)[number]>("all");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((it) => {
      if (diff !== "all" && difficultyKey(it.difficulty) !== diff) return false;
      if (q && !it.name.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [items, query, diff]);

  // group by category preserving first-seen order
  const groups = useMemo(() => {
    const map = new Map<string, ProblemIndexItem[]>();
    for (const it of filtered) {
      const key = it.category || "Other";
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(it);
    }
    return Array.from(map.entries());
  }, [filtered]);

  return (
    <div>
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search problems…"
          className="w-full flex-1 rounded-lg border border-edge bg-bg-panel px-4 py-2.5 text-sm text-ink outline-none placeholder:text-ink-faint focus:ring-1 focus:ring-accent"
        />
        <div className="flex gap-1.5">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setDiff(f)}
              className={`rounded-lg px-3 py-2 text-xs font-medium capitalize ring-1 transition ${
                diff === f
                  ? "bg-accent/15 text-accent-soft ring-accent/40"
                  : "bg-bg-panel text-ink-dim ring-edge hover:bg-bg-hover"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="rounded-lg border border-edge bg-bg-panel p-8 text-center text-sm text-ink-dim">
          No problems match.
        </div>
      )}

      <div className="space-y-7">
        {groups.map(([cat, list]) => (
          <section key={cat}>
            <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-faint">
              {cat} <span className="text-ink-faint/60">({list.length})</span>
            </h2>
            <div className="overflow-hidden rounded-lg border border-edge">
              {list.map((it, i) => (
                <Link
                  key={it.slug}
                  href={`/problem/${it.slug}`}
                  className={`flex items-center gap-3 bg-bg-panel px-4 py-2.5 transition hover:bg-bg-hover ${
                    i > 0 ? "border-t border-edge" : ""
                  }`}
                >
                  <span
                    className={`h-2 w-2 shrink-0 rounded-full ${DOT[difficultyKey(it.difficulty)]}`}
                  />
                  <span className="flex-1 truncate text-sm text-ink">{it.name}</span>
                  {!it.hasCpp && (
                    <span className="rounded bg-bg-raised px-1.5 py-0.5 text-[10px] text-ink-faint ring-1 ring-edge">
                      no starter
                    </span>
                  )}
                  <span className="hidden text-xs text-ink-faint sm:block">{it.subcategory}</span>
                  <span className="text-ink-faint">→</span>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
