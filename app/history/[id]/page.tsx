import Link from "next/link";
import { notFound } from "next/navigation";
import { getSubmission } from "@/lib/db";

export const dynamic = "force-dynamic";

const VERDICT_LABEL: Record<string, string> = {
  accepted: "Accepted",
  wrong_answer: "Wrong Answer",
  compile_error: "Compile Error",
  runtime_error: "Runtime Error",
  tle: "Time Limit Exceeded",
  ran: "Executed",
  error: "Unsupported",
};

const VERDICT_TONE: Record<string, string> = {
  accepted: "text-ok",
  wrong_answer: "text-bad",
  compile_error: "text-brand",
  runtime_error: "text-bad",
  tle: "text-warn",
  ran: "text-accent-soft",
  error: "text-brand",
};

function fmtTime(ts: number) {
  return new Date(ts * 1000).toLocaleString();
}

export default async function HistoryDetail({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  if (!Number.isFinite(id) || id <= 0) notFound();
  let sub: Awaited<ReturnType<typeof getSubmission>> = null;
  try {
    sub = getSubmission(id);
  } catch {
    sub = null;
  }
  if (!sub) notFound();

  const tone = VERDICT_TONE[sub.verdict] ?? "text-ink";
  const label = VERDICT_LABEL[sub.verdict] ?? sub.verdict;

  return (
    <main className="mx-auto min-h-screen max-w-5xl px-5 py-8">
      <nav className="mb-5 flex items-center gap-3 text-sm text-ink-dim">
        <Link href="/" className="hover:text-ink">← Dashboard</Link>
        <span className="text-edge">|</span>
        <Link href={`/problem/${sub.slug}`} className="hover:text-ink">
          {sub.problem_name || sub.slug}
        </Link>
      </nav>

      <header className="mb-6 rounded-xl bg-bg-panel p-5 ring-1 ring-edge">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div>
            <h1 className={`text-2xl font-semibold ${tone}`}>{label}</h1>
            <p className="mt-1 text-sm text-ink-dim">
              {sub.problem_name || sub.slug}
              {sub.category && <span className="text-ink-faint"> · {sub.category}</span>}
              {sub.difficulty && <span className="text-ink-faint"> · {sub.difficulty}</span>}
            </p>
          </div>
          <div className="flex flex-wrap gap-2 text-xs">
            <span className="rounded bg-bg-raised px-2 py-1 text-ink-dim ring-1 ring-edge">{sub.mode}</span>
            <span className="rounded bg-bg-raised px-2 py-1 text-ink-dim ring-1 ring-edge">{sub.language}</span>
            <span className="rounded bg-bg-raised px-2 py-1 text-ink-dim ring-1 ring-edge">
              {sub.backend === "docker" ? "🐳 docker" : "💻 local"}
            </span>
            {sub.total > 0 && (
              <span className="rounded bg-bg-raised px-2 py-1 font-mono ring-1 ring-edge">
                <span className="text-ok">{sub.passed}</span>
                <span className="text-ink-faint"> / {sub.total}</span>
              </span>
            )}
            <span className="rounded bg-bg-raised px-2 py-1 text-ink-faint ring-1 ring-edge">
              {sub.duration_ms} ms
            </span>
          </div>
        </div>
        <p className="mt-3 text-xs text-ink-faint">{fmtTime(sub.created_at)}</p>
      </header>

      {sub.failed.length > 0 && (
        <section className="mb-6">
          <h2 className="mb-2 text-sm font-semibold text-ink">
            Failed cases <span className="text-ink-faint">({sub.failed.length} shown)</span>
          </h2>
          <div className="space-y-3">
            {sub.failed.map((f) => (
              <article key={f.case_idx} className="rounded-lg bg-bg-panel p-4 ring-1 ring-edge">
                <div className="mb-2 flex items-center justify-between text-xs">
                  <span className="font-mono text-ink-dim">Case {f.case_idx + 1}</span>
                  <span className="rounded bg-bad/10 px-1.5 py-0.5 text-bad ring-1 ring-bad/30">
                    {f.status}
                  </span>
                </div>
                <div className="grid gap-3 sm:grid-cols-3">
                  <div>
                    <div className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">Inputs</div>
                    <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded bg-bg px-2 py-1.5 font-mono text-[12px] text-ink/90 ring-1 ring-edge">
                      {Object.entries(f.inputs).map(([k, v]) => `${k} = ${v}`).join("\n") || "(empty)"}
                    </pre>
                  </div>
                  <div>
                    <div className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">Expected</div>
                    <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded bg-bg px-2 py-1.5 font-mono text-[12px] text-ink/90 ring-1 ring-edge">
                      {f.expected ?? "(none)"}
                    </pre>
                  </div>
                  <div>
                    <div className="mb-1 text-[10px] uppercase tracking-wide text-ink-faint">Your output</div>
                    <pre className="max-h-40 overflow-auto whitespace-pre-wrap rounded bg-bg px-2 py-1.5 font-mono text-[12px] text-ink/90 ring-1 ring-edge">
                      {f.actual || "(empty)"}
                    </pre>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <section>
        <h2 className="mb-2 text-sm font-semibold text-ink">Submitted code</h2>
        <pre className="overflow-auto rounded-lg bg-bg p-4 font-mono text-[12.5px] text-ink/90 ring-1 ring-edge">
          {sub.code}
        </pre>
      </section>
    </main>
  );
}
