"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { HintResponse, Language } from "@/types";

interface Props {
  problemId: string;
  language: Language;
  code: string;
}

export default function HintPanel({ problemId, language, code }: Props) {
  const [hints, setHints] = useState<HintResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nextLevel = hints.length + 1;
  const canAskMore = hints.length === 0 || hints[hints.length - 1].can_go_deeper;

  async function fetchHint() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.post<HintResponse>("/ai/hints", {
        problem_id: problemId,
        language,
        code,
        hint_level: nextLevel,
      });
      setHints((prev) => [...prev, result]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to get hint.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-3 p-4">
      <p className="text-xs text-zinc-500">
        Hints reveal progressively — start gentle, go deeper only if needed.
      </p>

      {hints.map((h, i) => (
        <div key={i} className="rounded-xl border border-zinc-800 bg-zinc-950 p-3">
          <p className="mb-1.5 text-xs font-semibold text-violet-400">
            Hint {h.hint_level} / 3
          </p>
          <p className="text-sm leading-relaxed text-zinc-300">{h.hint}</p>
        </div>
      ))}

      {error && <p className="text-xs text-red-400">{error}</p>}

      {canAskMore ? (
        <button
          onClick={fetchHint}
          disabled={loading}
          className="self-start flex items-center gap-1.5 rounded-lg border border-violet-500/40 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold text-violet-300 transition-colors hover:bg-violet-500/20 disabled:opacity-50"
        >
          {loading ? (
            <><Spinner /> Loading…</>
          ) : hints.length === 0 ? (
            "✦ Get Hint"
          ) : (
            `Next Hint (Level ${nextLevel})`
          )}
        </button>
      ) : (
        <p className="text-xs text-zinc-600">
          All hints revealed. Try implementing the approach above.
        </p>
      )}
    </div>
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
