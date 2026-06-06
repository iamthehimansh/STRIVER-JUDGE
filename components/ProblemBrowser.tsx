"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { ProblemIndexItem } from "@/lib/types";
import { difficultyKey } from "@/lib/starter";

const LS_OPEN_KEY = "striver:openCategory";

interface SlugStatusLite {
  solved: boolean;
  attempts: number;
  best_passed: number;
  best_total: number;
}

const DIFF_STYLE: Record<string, string> = {
  easy:   "text-diff-easy   ring-diff-easy/30   bg-diff-easy/10",
  medium: "text-diff-medium ring-diff-medium/30 bg-diff-medium/10",
  hard:   "text-diff-hard   ring-diff-hard/30   bg-diff-hard/10",
};

const DIFF_LABEL: Record<string, string> = { easy: "Easy", medium: "Medium", hard: "Hard" };
const DIFF_FILTERS = ["all", "easy", "medium", "hard"] as const;
const STATUS_FILTERS = ["any", "untried", "attempted", "solved"] as const;

interface Props {
  items: ProblemIndexItem[];
  statuses: Record<string, SlugStatusLite>;
}

function StatusIcon({ s }: { s: SlugStatusLite | undefined }) {
  if (s?.solved) {
    return (
      <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-ok/20 ring-1 ring-ok/40">
        <svg viewBox="0 0 16 16" className="h-3 w-3 fill-none stroke-ok" strokeWidth="2.5">
          <path d="M3 8.5 L6.5 12 L13 4.5" />
        </svg>
      </span>
    );
  }
  if (s && s.attempts > 0) {
    return (
      <span className="relative grid h-5 w-5 shrink-0 place-items-center rounded-full ring-1 ring-warn/50">
        <span className="h-2 w-2 rounded-full bg-warn" />
      </span>
    );
  }
  return <span className="h-5 w-5 shrink-0 rounded-full ring-1 ring-edge" />;
}

export default function ProblemBrowser({ items, statuses }: Props) {
  const [query, setQuery] = useState("");
  const [diff, setDiff] = useState<(typeof DIFF_FILTERS)[number]>("all");
  const [status, setStatus] = useState<(typeof STATUS_FILTERS)[number]>("any");

  // Single-active accordion: at most one category open at a time. The user's
  // choice is persisted to localStorage so it survives reloads. `null` is a
  // valid value (everything collapsed).  `undefined` is the pre-hydration
  // state (we don't render the dropdown body until we've read localStorage to
  // avoid a hydration mismatch / flash).
  const [openCat, setOpenCat] = useState<string | null | undefined>(undefined);
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_OPEN_KEY);
      if (raw === null) {
        // first visit -> open the first category; we set state to "" sentinel
        // and resolve to the first visible category in the render path
        setOpenCat("");
      } else {
        setOpenCat(raw === "__none__" ? null : raw);
      }
    } catch {
      setOpenCat("");
    }
  }, []);
  function toggleCat(cat: string) {
    setOpenCat((cur) => {
      const next = cur === cat ? null : cat;
      try {
        localStorage.setItem(LS_OPEN_KEY, next === null ? "__none__" : next);
      } catch {}
      return next;
    });
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((it) => {
      if (diff !== "all" && difficultyKey(it.difficulty) !== diff) return false;
      const s = statuses[it.slug];
      if (status === "solved" && !s?.solved) return false;
      if (status === "attempted" && (!s || s.solved || s.attempts === 0)) return false;
      if (status === "untried" && s) return false;
      if (q && !it.name.toLowerCase().includes(q)) return false;
      return true;
    });
  }, [items, query, diff, status, statuses]);

  // group: category -> subcategory -> items   (preserves first-seen order)
  const groups = useMemo(() => {
    const map = new Map<string, Map<string, ProblemIndexItem[]>>();
    for (const it of filtered) {
      const c = it.category || "Other";
      const s = it.subcategory || "—";
      let sub = map.get(c);
      if (!sub) {
        sub = new Map();
        map.set(c, sub);
      }
      let list = sub.get(s);
      if (!list) {
        list = [];
        sub.set(s, list);
      }
      list.push(it);
    }
    return Array.from(map.entries()).map(([cat, sub]) => ({
      cat,
      subs: Array.from(sub.entries()).map(([sc, list]) => ({ sc, items: list })),
    }));
  }, [filtered]);

  // overall numbers (across the whole sheet, not just the filtered slice)
  const totals = useMemo(() => {
    let solved = 0, attempted = 0;
    for (const it of items) {
      const s = statuses[it.slug];
      if (s?.solved) solved++;
      else if (s && s.attempts > 0) attempted++;
    }
    return { solved, attempted, untried: items.length - solved - attempted };
  }, [items, statuses]);

  return (
    <div>
      {/* search + filters */}
      <div className="mb-4 space-y-2">
        <div className="relative">
          <svg
            viewBox="0 0 24 24"
            className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 fill-none stroke-ink-faint"
            strokeWidth="2"
          >
            <circle cx="11" cy="11" r="6" />
            <path d="m20 20-3.5-3.5" />
          </svg>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={`Search ${items.length} problems…`}
            className="w-full rounded-lg border border-edge bg-bg-panel py-2.5 pl-10 pr-3 text-sm text-ink outline-none placeholder:text-ink-faint focus:border-accent/50 focus:ring-1 focus:ring-accent/40"
          />
        </div>

        <div className="flex flex-wrap items-center gap-1.5 text-xs">
          {STATUS_FILTERS.map((f) => {
            const count =
              f === "any" ? items.length
              : f === "solved" ? totals.solved
              : f === "attempted" ? totals.attempted
              : totals.untried;
            const active = status === f;
            return (
              <button
                key={f}
                onClick={() => setStatus(f)}
                className={`rounded-md px-2.5 py-1 capitalize ring-1 transition ${
                  active ? "bg-accent/15 text-accent-soft ring-accent/40"
                         : "bg-bg-panel text-ink-dim ring-edge hover:bg-bg-hover hover:text-ink"
                }`}
              >
                {f} <span className="text-ink-faint">{count}</span>
              </button>
            );
          })}
          <span className="mx-1 h-4 w-px bg-edge" />
          {DIFF_FILTERS.map((f) => {
            const active = diff === f;
            return (
              <button
                key={f}
                onClick={() => setDiff(f)}
                className={`rounded-md px-2.5 py-1 capitalize ring-1 transition ${
                  active ? "bg-accent/15 text-accent-soft ring-accent/40"
                         : "bg-bg-panel text-ink-dim ring-edge hover:bg-bg-hover hover:text-ink"
                }`}
              >
                {f}
              </button>
            );
          })}
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="rounded-xl border border-edge bg-bg-panel p-10 text-center text-sm text-ink-dim">
          Nothing matches these filters.
        </div>
      )}

      {(() => null)()}
      {/* Resolve the actually-open category for this render:
            - "" (sentinel "first-time visit") -> first visible category
            - a string that's still in the visible groups -> use it
            - everything else -> all collapsed                                  */}
      {undefined}
      <div className="space-y-3">
        {groups.map(({ cat, subs }, catIdx) => {
          const catItems = subs.flatMap((s) => s.items);
          const catSolved = catItems.filter((it) => statuses[it.slug]?.solved).length;
          const catAttempts = catItems.filter(
            (it) => !statuses[it.slug]?.solved && (statuses[it.slug]?.attempts ?? 0) > 0
          ).length;
          const pct = catItems.length > 0 ? Math.round((catSolved / catItems.length) * 100) : 0;
          const effectiveOpen =
            openCat === undefined
              ? null
              : openCat === ""
              ? groups[0]?.cat ?? null
              : openCat && groups.some((g) => g.cat === openCat)
              ? openCat
              : null;
          const isOpen = effectiveOpen === cat;
          return (
            <section key={cat} className="overflow-hidden rounded-xl bg-bg-panel ring-1 ring-edge">
              {/* clickable category header — toggles single-active accordion */}
              <button
                type="button"
                aria-expanded={isOpen}
                onClick={() => toggleCat(cat)}
                className={`group w-full bg-gradient-to-r from-bg-raised to-bg-panel px-4 py-3 text-left transition hover:from-bg-hover hover:to-bg-panel ${
                  isOpen ? "border-b border-edge/60" : ""
                }`}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h3 className="flex items-baseline gap-2 text-sm font-semibold text-ink">
                    <span className="font-mono text-xs text-ink-faint">
                      {String(catIdx + 1).padStart(2, "0")}
                    </span>
                    <span>{cat}</span>
                  </h3>
                  <div className="flex items-center gap-3 text-[11px] text-ink-dim">
                    <span className="font-mono">
                      <span className="text-ok">{catSolved}</span>
                      <span className="text-ink-faint"> / {catItems.length}</span>
                    </span>
                    {catAttempts > 0 && (
                      <span className="text-warn">⏵ {catAttempts} in progress</span>
                    )}
                    <span className="font-mono text-ink-faint">{pct}%</span>
                    <svg
                      viewBox="0 0 12 12"
                      className={`h-3 w-3 stroke-ink-faint transition-transform duration-200 ${
                        isOpen ? "rotate-180" : ""
                      }`}
                      fill="none"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M2.5 4 L6 7.5 L9.5 4" />
                    </svg>
                  </div>
                </div>
                <div className="mt-2 h-1 overflow-hidden rounded-full bg-bg">
                  <div className="h-full bg-ok/70" style={{ width: `${pct}%` }} />
                </div>
              </button>

              <div className={`divide-y divide-edge/40 ${isOpen ? "block" : "hidden"}`}>
                {subs.map(({ sc, items: list }) => (
                  <div key={sc}>
                    {sc !== "—" && sc !== cat && (
                      <div className="border-b border-edge/30 bg-bg-panel/40 px-4 py-1.5 text-[11px] uppercase tracking-wider text-ink-faint">
                        {sc}
                      </div>
                    )}
                    <ul className="divide-y divide-edge/30">
                      {list.map((it, i) => {
                        const s = statuses[it.slug];
                        const dk = difficultyKey(it.difficulty);
                        const inProgress = !!s && !s.solved && s.attempts > 0 && s.best_total > 0;
                        const bestPct = inProgress
                          ? Math.round((s.best_passed / s.best_total) * 100)
                          : 0;
                        return (
                          <li key={it.slug}>
                            <Link
                              href={`/problem/${it.slug}`}
                              className="flex items-center gap-3 px-4 py-2.5 transition hover:bg-bg-hover/60"
                            >
                              <span className="w-6 shrink-0 text-right font-mono text-[11px] text-ink-faint">
                                {i + 1}
                              </span>
                              <StatusIcon s={s} />
                              <span className="min-w-0 flex-1 truncate text-sm text-ink">
                                {it.name}
                              </span>
                              {!it.hasCpp && (
                                <span className="hidden rounded bg-bg-raised px-1.5 py-0.5 text-[10px] text-ink-faint ring-1 ring-edge sm:inline">
                                  no starter
                                </span>
                              )}
                              {inProgress && (
                                <span className="hidden font-mono text-[11px] text-warn sm:inline">
                                  {bestPct}%
                                </span>
                              )}
                              {s?.solved && (
                                <span className="hidden font-mono text-[11px] text-ok sm:inline">
                                  solved
                                </span>
                              )}
                              <span
                                className={`hidden shrink-0 rounded px-2 py-0.5 text-[11px] font-medium ring-1 sm:inline ${DIFF_STYLE[dk]}`}
                              >
                                {DIFF_LABEL[dk]}
                              </span>
                              <span className="shrink-0 text-ink-faint transition group-hover:translate-x-0.5">→</span>
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}
