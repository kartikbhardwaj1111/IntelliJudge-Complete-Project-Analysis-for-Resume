"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { FeedbackResponse, Language, Submission } from "@/types";

interface Props {
  problemId: string;
  language: Language;
  code: string;
  submission: Submission;
}

export default function FeedbackPanel({ problemId, language, code, submission }: Props) {
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const firstFailing = submission.results?.find(
    (r) => r.verdict !== "AC" && r.is_visible
  );

  async function fetchFeedback() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.post<FeedbackResponse>("/ai/feedback", {
        problem_id: problemId,
        language,
        code,
        verdict: submission.verdict,
        failing_input: firstFailing?.input ?? null,
        failing_expected: firstFailing?.expected_output ?? null,
        failing_actual: firstFailing?.actual_output ?? null,
      });
      setFeedback(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to get feedback.");
    } finally {
      setLoading(false);
    }
  }

  if (feedback) {
    return (
      <div className="mt-4 flex flex-col gap-3 rounded-xl border border-violet-500/20 bg-violet-500/5 p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-violet-400">
          ✦ AI Feedback
        </p>
        <FeedbackBlock label="Analysis" text={feedback.analysis} />
        <FeedbackBlock label="Likely Bug" text={feedback.likely_bug} color="text-red-300" />
        <FeedbackBlock label="Suggested Fix" text={feedback.suggested_approach} color="text-emerald-300" />
        {feedback.code_snippet_hint && (
          <div>
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500">
              Hint Snippet
            </p>
            <pre className="overflow-x-auto rounded-lg bg-zinc-900 p-3 font-mono text-xs text-zinc-300">
              {feedback.code_snippet_hint}
            </pre>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="mt-4 flex flex-col items-start gap-2">
      {error && <p className="text-xs text-red-400">{error}</p>}
      <button
        onClick={fetchFeedback}
        disabled={loading}
        className="flex items-center gap-1.5 rounded-lg border border-violet-500/40 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold text-violet-300 transition-colors hover:bg-violet-500/20 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? <><Spinner /> Analysing your code…</> : "✦ Get AI Feedback"}
      </button>
    </div>
  );
}

function FeedbackBlock({
  label,
  text,
  color = "text-zinc-300",
}: {
  label: string;
  text: string;
  color?: string;
}) {
  return (
    <div>
      <p className="mb-0.5 text-xs font-medium uppercase tracking-wide text-zinc-500">
        {label}
      </p>
      <p className={`text-sm leading-relaxed ${color}`}>{text}</p>
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
