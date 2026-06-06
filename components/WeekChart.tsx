import type { DayStats } from "@/lib/db";

interface Props {
  byDay: DayStats[];
}

const DOW = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export default function WeekChart({ byDay }: Props) {
  const max = Math.max(1, ...byDay.map((d) => d.runs + d.submits));
  return (
    <div className="rounded-xl bg-bg-panel p-4 ring-1 ring-edge">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink">Activity — last 7 days</h3>
        <div className="flex items-center gap-3 text-[11px] text-ink-dim">
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-ok" /> accepted</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-accent" /> submits</span>
          <span className="flex items-center gap-1"><span className="h-2 w-2 rounded-sm bg-ink-faint/50" /> runs</span>
        </div>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {byDay.map((d) => {
          const dt = new Date(d.day + "T00:00:00Z");
          const dow = DOW[dt.getUTCDay()];
          const total = d.runs + d.submits;
          const hAccept = (d.accepted / max) * 100;
          const hSubmit = ((d.submits - d.accepted) / max) * 100;
          const hRun = (d.runs / max) * 100;
          return (
            <div key={d.day} className="flex flex-col items-center gap-1.5">
              <div className="relative flex h-28 w-full items-end overflow-hidden rounded-md bg-bg ring-1 ring-edge">
                <div className="flex w-full flex-col-reverse">
                  <div style={{ height: `${hAccept}%` }} className="w-full bg-ok/80" />
                  <div style={{ height: `${hSubmit}%` }} className="w-full bg-accent/80" />
                  <div style={{ height: `${hRun}%` }} className="w-full bg-ink-faint/40" />
                </div>
                {total > 0 && (
                  <span className="absolute inset-x-0 top-1 text-center text-[10px] font-mono text-ink/80">
                    {total}
                  </span>
                )}
              </div>
              <div className="text-[10px] text-ink-faint">{dow}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
