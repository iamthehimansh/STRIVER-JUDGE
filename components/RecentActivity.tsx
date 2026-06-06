import Link from "next/link";
import type { RecentRow } from "@/lib/db";

const VERDICT_STYLES: Record<string, { dot: string; text: string; ring: string }> = {
  accepted:      { dot: "bg-ok",   text: "text-ok",   ring: "ring-ok/30"   },
  wrong_answer:  { dot: "bg-bad",  text: "text-bad",  ring: "ring-bad/30"  },
  compile_error: { dot: "bg-brand",text: "text-brand",ring: "ring-brand/30"},
  runtime_error: { dot: "bg-bad",  text: "text-bad",  ring: "ring-bad/30"  },
  tle:           { dot: "bg-warn", text: "text-warn", ring: "ring-warn/30" },
  ran:           { dot: "bg-accent",text:"text-accent-soft",ring:"ring-accent/30"},
  error:         { dot: "bg-brand",text: "text-brand",ring: "ring-brand/30"},
};

function ago(ts: number): string {
  const s = Math.floor(Date.now() / 1000 - ts);
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

function verdictLabel(v: string) {
  if (v === "accepted") return "Accepted";
  if (v === "wrong_answer") return "Wrong Answer";
  if (v === "compile_error") return "Compile Error";
  if (v === "runtime_error") return "Runtime Error";
  if (v === "tle") return "TLE";
  if (v === "ran") return "Ran";
  return v;
}

interface Props { recent: RecentRow[] }

export default function RecentActivity({ recent }: Props) {
  return (
    <div className="rounded-xl bg-bg-panel p-4 ring-1 ring-edge">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink">Recent activity</h3>
        <span className="text-xs text-ink-faint">last {recent.length}</span>
      </div>

      {recent.length === 0 ? (
        <div className="rounded-md bg-bg/40 px-3 py-6 text-center text-sm text-ink-dim">
          No submissions yet. Pick a problem below and hit Run / Submit.
        </div>
      ) : (
        <ul className="divide-y divide-edge/40">
          {recent.map((r) => {
            const v = VERDICT_STYLES[r.verdict] ?? VERDICT_STYLES.error;
            return (
              <li key={r.id} className="group">
                <Link
                  href={`/history/${r.id}`}
                  className="flex items-center gap-3 px-1 py-2.5 transition hover:bg-bg-hover/50"
                >
                  <span className={`h-2 w-2 shrink-0 rounded-full ${v.dot}`} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-baseline justify-between gap-2">
                      <span className="truncate text-sm text-ink group-hover:text-accent-soft">
                        {r.problem_name || r.slug}
                      </span>
                      <span className="shrink-0 text-[11px] text-ink-faint">{ago(r.created_at)}</span>
                    </div>
                    <div className="mt-0.5 flex flex-wrap items-center gap-1.5 text-[11px]">
                      <span className={`rounded px-1.5 py-0.5 ring-1 ${v.ring} ${v.text}`}>
                        {verdictLabel(r.verdict)}
                      </span>
                      <span className="rounded bg-bg-raised px-1.5 py-0.5 text-ink-dim ring-1 ring-edge">
                        {r.mode}
                      </span>
                      <span className="rounded bg-bg-raised px-1.5 py-0.5 text-ink-dim ring-1 ring-edge">
                        {r.language}
                      </span>
                      {r.total > 0 && (
                        <span className="font-mono text-ink-dim">
                          {r.passed}/{r.total}
                        </span>
                      )}
                      {r.category && (
                        <span className="truncate text-ink-faint">· {r.category}</span>
                      )}
                    </div>
                  </div>
                </Link>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
