"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { EdgeCasesResponse } from "@/types";

interface Props {
  problemId: string;
}

export default function EdgeCasePanel({ problemId }: Props) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<EdgeCasesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function fetchEdgeCases() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.post<EdgeCasesResponse>("/ai/edge-cases", {
        problem_id: problemId,
      });
      setData(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to detect edge cases.");
    } finally {
      setLoading(false);
    }
  }

  if (data) {
    return (
      <section className="flex flex-col gap-2.5">
        <h2 className="border-b border-zinc-800 pb-1.5 text-sm font-semibold text-white">
          Edge Cases to Watch
        </h2>
        <div className="flex flex-col gap-2">
          {data.edge_cases.map((ec, i) => (
            <div key={i} className="rounded-lg border border-zinc-800 bg-zinc-950/50 p-3">
              <p className="text-xs font-semibold text-amber-400">{ec.description}</p>
              {ec.example_input && (
                <pre className="mt-1 overflow-x-auto rounded bg-zinc-900 px-2 py-1 font-mono text-xs text-zinc-400">
                  {ec.example_input}
                </pre>
              )}
              <p className="mt-1 text-xs text-zinc-500">{ec.why_tricky}</p>
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="flex flex-col gap-2.5">
      <h2 className="border-b border-zinc-800 pb-1.5 text-sm font-semibold text-white">
        Edge Cases
      </h2>
      {error && <p className="text-xs text-red-400">{error}</p>}
      <button
        onClick={fetchEdgeCases}
        disabled={loading}
        className="self-start flex items-center gap-1.5 rounded-lg border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-xs font-semibold text-amber-400 transition-colors hover:bg-amber-500/20 disabled:opacity-50"
      >
        {loading ? <><Spinner /> Detecting…</> : "✦ Detect Edge Cases"}
      </button>
    </section>
  );
}

function Spinner() {
  return (
    <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}
