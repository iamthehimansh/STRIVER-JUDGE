import { getIndex } from "@/lib/data";
import { getStats, getSlugStatuses } from "@/lib/db";
import ProblemBrowser from "@/components/ProblemBrowser";
import StatsHero from "@/components/StatsHero";
import WeekChart from "@/components/WeekChart";
import RecentActivity from "@/components/RecentActivity";
import CategoryBreakdown from "@/components/CategoryBreakdown";

export const dynamic = "force-dynamic";

export default async function Home() {
  const items = await getIndex();
  let stats;
  let statuses: Record<string, { solved: boolean; attempts: number; best_passed: number; best_total: number }> = {};
  try {
    stats = getStats();
    statuses = Object.fromEntries(getSlugStatuses());
  } catch {
    // db unavailable (first boot before any write) → render an empty shell
    stats = {
      generated_at: Math.floor(Date.now() / 1000),
      totals: { runs: 0, submits: 0, accepted: 0, success_rate: 0, problems_tried: 0, problems_solved: 0 },
      today:  { runs: 0, submits: 0, accepted: 0, success_rate: 0, problems_tried: 0, problems_solved: 0 },
      week:   { runs: 0, submits: 0, accepted: 0, success_rate: 0, problems_tried: 0, problems_solved: 0 },
      byDay: Array.from({ length: 7 }).map((_, i) => {
        const d = new Date(Date.now() - (6 - i) * 86400_000);
        const day = `${d.getUTCFullYear()}-${String(d.getUTCMonth() + 1).padStart(2, "0")}-${String(d.getUTCDate()).padStart(2, "0")}`;
        return { day, runs: 0, submits: 0, accepted: 0 };
      }),
      byCategory: [],
      recent: [],
    };
  }

  const byDifficulty = items.reduce(
    (acc, it) => {
      const k = it.difficulty.toLowerCase().startsWith("hard")
        ? "hard"
        : it.difficulty.toLowerCase().startsWith("med")
        ? "medium"
        : "easy";
      acc[k]++;
      return acc;
    },
    { easy: 0, medium: 0, hard: 0 } as Record<string, number>,
  );

  return (
    <main className="mx-auto min-h-screen max-w-6xl px-5 py-8">
      {/* header */}
      <header className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="flex items-baseline gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-ink">Striver Judge</h1>
            <span className="text-sm text-ink-faint">{items.length} problems · C / C++</span>
          </div>
          <p className="mt-1 text-sm text-ink-dim">
            A local LeetCode-style judge over the takeUforward A2Z problem set —
            <span className="text-diff-easy"> {byDifficulty.easy} easy</span> ·
            <span className="text-diff-medium"> {byDifficulty.medium} medium</span> ·
            <span className="text-diff-hard"> {byDifficulty.hard} hard</span>.
          </p>
        </div>
        <a
          href="https://github.com/iamthehimansh/STRIVER-JUDGE"
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-edge bg-bg-panel px-3 py-1.5 text-xs text-ink-dim hover:bg-bg-hover hover:text-ink"
        >
          GitHub ↗
        </a>
      </header>

      {/* stat cards */}
      <section className="mb-6">
        <StatsHero totalProblems={items.length} stats={stats} />
      </section>

      {/* main grid: charts/categories on the left, recent activity on the right */}
      <section className="mb-8 grid gap-4 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-4">
          <WeekChart byDay={stats.byDay} />
          <CategoryBreakdown byCategory={stats.byCategory} />
        </div>
        <RecentActivity recent={stats.recent} />
      </section>

      {/* problem browser */}
      <section>
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-lg font-semibold text-ink">All problems</h2>
          <span className="text-xs text-ink-faint">click to open the workspace</span>
        </div>
        <ProblemBrowser items={items} statuses={statuses} />
      </section>

      <footer className="mt-10 pb-4 text-center text-xs text-ink-faint">
        stats refreshed at {new Date(stats.generated_at * 1000).toLocaleString()}
      </footer>
    </main>
  );
}
