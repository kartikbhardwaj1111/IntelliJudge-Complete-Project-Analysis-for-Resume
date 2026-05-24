import type { Submission, TestCaseResult, Verdict } from "@/types";

interface SubmissionResultProps {
  submission: Submission;
}

const VERDICT_CONFIG: Record<
  string,
  { label: string; short: string; cls: string; dot: string }
> = {
  AC:  { label: "Accepted",              short: "AC",  cls: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30", dot: "bg-emerald-400" },
  WA:  { label: "Wrong Answer",          short: "WA",  cls: "bg-red-500/15 text-red-400 border-red-500/30",             dot: "bg-red-400" },
  TLE: { label: "Time Limit Exceeded",   short: "TLE", cls: "bg-blue-500/15 text-blue-400 border-blue-500/30",          dot: "bg-blue-400" },
  CE:  { label: "Compilation Error",     short: "CE",  cls: "bg-amber-500/15 text-amber-400 border-amber-500/30",       dot: "bg-amber-400" },
  RE:  { label: "Runtime Error",         short: "RE",  cls: "bg-orange-500/15 text-orange-400 border-orange-500/30",    dot: "bg-orange-400" },
  MLE: { label: "Memory Limit Exceeded", short: "MLE", cls: "bg-purple-500/15 text-purple-400 border-purple-500/30",   dot: "bg-purple-400" },
  pending: { label: "Pending",           short: "...", cls: "bg-zinc-500/15 text-zinc-400 border-zinc-700",             dot: "bg-zinc-500" },
};

function VerdictBadge({ verdict }: { verdict: string }) {
  const cfg = VERDICT_CONFIG[verdict] ?? VERDICT_CONFIG.RE;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${cfg.cls}`}
    >
      {cfg.short}
    </span>
  );
}

export default function SubmissionResult({ submission }: SubmissionResultProps) {
  const cfg = VERDICT_CONFIG[submission.verdict] ?? VERDICT_CONFIG.RE;
  const { test_cases_passed: passed, total_test_cases: total } = submission;
  const pct = total > 0 ? Math.round((passed / total) * 100) : 0;

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Overall verdict */}
      <div className="flex flex-wrap items-center gap-3">
        <span
          className={`rounded-full border px-3 py-1 text-sm font-bold ${cfg.cls}`}
        >
          {submission.verdict} &mdash; {cfg.label}
        </span>
        {submission.runtime_ms != null && (
          <span className="text-xs text-zinc-500">
            {submission.runtime_ms} ms
          </span>
        )}
        {submission.memory_kb != null && (
          <span className="text-xs text-zinc-500">
            {(submission.memory_kb / 1024).toFixed(1)} MB
          </span>
        )}
      </div>

      {/* Progress bar */}
      <div>
        <div className="mb-1 flex items-center justify-between text-xs text-zinc-500">
          <span>
            {passed} / {total} test cases passed
          </span>
          <span>{pct}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-zinc-800">
          <div
            className={`h-full rounded-full transition-all ${
              passed === total ? "bg-emerald-500" : "bg-red-500"
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Per-test-case grid */}
      {submission.results && submission.results.length > 0 && (
        <div className="flex flex-col gap-1.5">
          <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">
            Test Cases
          </p>
          <div className="flex flex-wrap gap-1.5">
            {submission.results.map((r: TestCaseResult, i: number) => {
              const tcfg = VERDICT_CONFIG[r.verdict] ?? VERDICT_CONFIG.RE;
              return (
                <div
                  key={r.test_case_id}
                  title={`Test ${i + 1} — ${tcfg.label}${r.runtime_ms != null ? ` — ${r.runtime_ms.toFixed(0)} ms` : ""}`}
                  className={`flex h-8 w-8 items-center justify-center rounded-md border text-xs font-bold ${tcfg.cls} cursor-default`}
                >
                  {r.verdict === "AC" ? "✓" : r.verdict === "WA" ? "✗" : tcfg.short}
                </div>
              );
            })}
          </div>

          {/* Expanded wrong answer detail — show first WA with visible input */}
          {(() => {
            const firstWA = submission.results.find(
              (r: TestCaseResult) => r.verdict !== "AC" && r.is_visible
            );
            if (!firstWA) return null;
            return (
              <div className="mt-2 rounded-xl border border-zinc-800 bg-zinc-950 p-3">
                <p className="mb-2 text-xs font-medium text-zinc-500">
                  First failing visible test case
                </p>
                <div className="grid gap-2 text-xs sm:grid-cols-3">
                  <div>
                    <p className="mb-1 font-medium uppercase tracking-wide text-zinc-600">
                      Input
                    </p>
                    <pre className="overflow-x-auto rounded bg-zinc-900 px-2 py-1.5 font-mono text-zinc-300">
                      {firstWA.input || "(empty)"}
                    </pre>
                  </div>
                  <div>
                    <p className="mb-1 font-medium uppercase tracking-wide text-zinc-600">
                      Expected
                    </p>
                    <pre className="overflow-x-auto rounded bg-zinc-900 px-2 py-1.5 font-mono text-emerald-300">
                      {firstWA.expected_output || "(empty)"}
                    </pre>
                  </div>
                  <div>
                    <p className="mb-1 font-medium uppercase tracking-wide text-zinc-600">
                      Your Output
                    </p>
                    <pre className="overflow-x-auto rounded bg-zinc-900 px-2 py-1.5 font-mono text-red-300">
                      {firstWA.actual_output ?? "(no output)"}
                    </pre>
                  </div>
                </div>
              </div>
            );
          })()}
        </div>
      )}
    </div>
  );
}
