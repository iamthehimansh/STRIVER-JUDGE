import type { StatsResponse } from "@/lib/db";

interface Props {
  totalProblems: number;
  stats: StatsResponse;
}

function pct(n: number) {
  return `${Math.round(n * 100)}%`;
}

export default function StatsHero({ totalProblems, stats }: Props) {
  const solved = stats.totals.problems_solved;
  const tried = stats.totals.problems_tried;
  const rate = stats.totals.success_rate;
  const todays = stats.today.runs + stats.today.submits;
  const weeks = stats.week.runs + stats.week.submits;
  // current streak — consecutive trailing days (oldest -> newest) with activity
  let streak = 0;
  for (let i = stats.byDay.length - 1; i >= 0; i--) {
    const d = stats.byDay[i];
    if (d.runs + d.submits > 0) streak++;
    else break;
  }

  const cards: { label: string; value: string; sub: string; tone: string }[] = [
    {
      label: "Problems Solved",
      value: `${solved}`,
      sub: `${tried} tried · ${totalProblems} total`,
      tone: "from-ok/20 to-ok/0 ring-ok/30",
    },
    {
      label: "Success Rate",
      value: pct(rate),
      sub: `${stats.totals.accepted} accepted / ${stats.totals.submits} submits`,
      tone: "from-accent/20 to-accent/0 ring-accent/30",
    },
    {
      label: "Today",
      value: `${todays}`,
      sub: `${stats.today.accepted} accepted · ${stats.today.submits} submits`,
      tone: "from-brand/20 to-brand/0 ring-brand/30",
    },
    {
      label: "Streak",
      value: streak === 0 ? "—" : `${streak}d`,
      sub: streak ? "consecutive active days" : "submit any problem to start",
      tone: "from-warn/20 to-warn/0 ring-warn/30",
    },
    {
      label: "This Week",
      value: `${weeks}`,
      sub: `${stats.week.accepted} accepted · ${stats.week.problems_solved} new solved`,
      tone: "from-diff-medium/20 to-diff-medium/0 ring-diff-medium/30",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${c.tone} bg-bg-panel p-4 ring-1`}
        >
          <div className="text-xs uppercase tracking-wide text-ink-faint">{c.label}</div>
          <div className="mt-1 text-3xl font-semibold tracking-tight text-ink">
            {c.value}
          </div>
          <div className="mt-1 text-xs text-ink-dim">{c.sub}</div>
        </div>
      ))}
    </div>
  );
}
