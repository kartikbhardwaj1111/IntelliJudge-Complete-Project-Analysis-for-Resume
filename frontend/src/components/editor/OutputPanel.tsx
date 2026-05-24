import type { RunResult } from "@/types";

interface OutputPanelProps {
  result: RunResult;
}

const VERDICT_CONFIG: Record<
  string,
  { label: string; cls: string }
> = {
  AC:  { label: "Accepted",             cls: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30" },
  WA:  { label: "Wrong Answer",         cls: "bg-red-500/15 text-red-400 border-red-500/30" },
  TLE: { label: "Time Limit Exceeded",  cls: "bg-blue-500/15 text-blue-400 border-blue-500/30" },
  CE:  { label: "Compilation Error",    cls: "bg-amber-500/15 text-amber-400 border-amber-500/30" },
  RE:  { label: "Runtime Error",        cls: "bg-orange-500/15 text-orange-400 border-orange-500/30" },
  MLE: { label: "Memory Limit Exceeded",cls: "bg-purple-500/15 text-purple-400 border-purple-500/30" },
};

export default function OutputPanel({ result }: OutputPanelProps) {
  const cfg = VERDICT_CONFIG[result.verdict] ?? VERDICT_CONFIG.RE;

  return (
    <div className="flex flex-col gap-3 p-4">
      {/* Verdict + stats row */}
      <div className="flex flex-wrap items-center gap-3">
        <span
          className={`rounded-full border px-3 py-0.5 text-sm font-semibold ${cfg.cls}`}
        >
          {result.verdict} &mdash; {cfg.label}
        </span>
        {result.runtime_ms != null && (
          <span className="text-xs text-zinc-500">
            {result.runtime_ms.toFixed(0)} ms
          </span>
        )}
        {result.memory_kb != null && (
          <span className="text-xs text-zinc-500">
            {(result.memory_kb / 1024).toFixed(1)} MB
          </span>
        )}
      </div>

      {/* Compilation Error */}
      {result.compile_output && (
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-amber-500">
            Compilation Error
          </p>
          <pre className="overflow-x-auto rounded-lg bg-zinc-950 px-3 py-2.5 font-mono text-xs leading-relaxed text-amber-300 whitespace-pre-wrap">
            {result.compile_output}
          </pre>
        </div>
      )}

      {/* Runtime Error / stderr */}
      {result.stderr && !result.compile_output && (
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-orange-500">
            Runtime Error
          </p>
          <pre className="overflow-x-auto rounded-lg bg-zinc-950 px-3 py-2.5 font-mono text-xs leading-relaxed text-orange-300 whitespace-pre-wrap">
            {result.stderr}
          </pre>
        </div>
      )}

      {/* Standard Output */}
      {result.stdout != null && (
        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500">
            Output
          </p>
          <pre className="overflow-x-auto rounded-lg bg-zinc-950 px-3 py-2.5 font-mono text-xs leading-relaxed text-zinc-300 whitespace-pre-wrap">
            {result.stdout || "(no output)"}
          </pre>
        </div>
      )}
    </div>
  );
}
