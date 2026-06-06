import type { CategoryStats } from "@/lib/db";

interface Props {
  byCategory: CategoryStats[];
}

export default function CategoryBreakdown({ byCategory }: Props) {
  const max = Math.max(1, ...byCategory.map((c) => c.attempts));
  return (
    <div className="rounded-xl bg-bg-panel p-4 ring-1 ring-edge">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-ink">By section</h3>
        <span className="text-xs text-ink-faint">attempts · solved</span>
      </div>
      {byCategory.length === 0 ? (
        <div className="rounded-md bg-bg/40 px-3 py-6 text-center text-sm text-ink-dim">
          Submit a few problems to see your activity grouped by section.
        </div>
      ) : (
        <ul className="space-y-2">
          {byCategory.map((c) => {
            const rate = c.attempts > 0 ? c.accepted / c.attempts : 0;
            return (
              <li key={c.category}>
                <div className="mb-1 flex items-baseline justify-between gap-3">
                  <span className="truncate text-sm text-ink">{c.category}</span>
                  <span className="shrink-0 font-mono text-xs text-ink-dim">
                    {c.attempts} · <span className="text-ok">{c.accepted}</span>
                  </span>
                </div>
                <div className="relative h-1.5 overflow-hidden rounded-full bg-bg ring-1 ring-edge">
                  <div
                    className="h-full bg-accent/50"
                    style={{ width: `${(c.attempts / max) * 100}%` }}
                  />
                  <div
                    className="absolute inset-y-0 left-0 bg-ok/80"
                    style={{ width: `${(c.accepted / max) * 100}%` }}
                  />
                </div>
                <div className="mt-0.5 flex justify-between text-[10px] text-ink-faint">
                  <span>{c.distinct_problems} problems</span>
                  <span>{Math.round(rate * 100)}% success</span>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
