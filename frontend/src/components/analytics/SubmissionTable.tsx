"use client";

import Link from "next/link";
import type { SubmissionHistory } from "@/types";

interface Props {
  history: SubmissionHistory;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

const VERDICT_CLS: Record<string, string> = {
  AC:      "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  WA:      "text-red-400 bg-red-500/10 border-red-500/20",
  TLE:     "text-sky-400 bg-sky-500/10 border-sky-500/20",
  CE:      "text-amber-400 bg-amber-500/10 border-amber-500/20",
  RE:      "text-orange-400 bg-orange-500/10 border-orange-500/20",
  MLE:     "text-purple-400 bg-purple-500/10 border-purple-500/20",
  pending: "text-zinc-400 bg-zinc-500/10 border-zinc-700",
};

const LANG_LABEL: Record<string, string> = {
  cpp: "C++", java: "Java", python: "Python", javascript: "JS",
};

export default function SubmissionTable({ history, onPageChange, loading }: Props) {
  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-3.5">
        <div>
          <p className="text-sm font-semibold text-white">Submission History</p>
          <p className="mt-0.5 text-xs text-zinc-500">
            {history.total} total submission{history.total !== 1 ? "s" : ""}
          </p>
        </div>
        {loading && (
          <span className="text-xs text-zinc-600 animate-pulse">Loading…</span>
        )}
      </div>

      {history.items.length === 0 ? (
        <div className="px-5 py-14 text-center text-sm text-zinc-600">
          No submissions yet — open a problem and hit Submit!
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 text-left">
                  {["Problem", "Verdict", "Language", "Passed", "Runtime", "Date"].map((h) => (
                    <th
                      key={h}
                      className="px-5 py-2.5 text-xs font-medium text-zinc-500"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {history.items.map((sub) => (
                  <tr
                    key={sub.id}
                    className="border-b border-zinc-900 transition-colors last:border-0 hover:bg-zinc-900/40"
                  >
                    <td className="max-w-[200px] truncate px-5 py-3">
                      <Link
                        href={`/problem/${sub.problem_id}`}
                        className="text-zinc-300 hover:text-white hover:underline"
                      >
                        {sub.problem_title}
                      </Link>
                    </td>
                    <td className="px-5 py-3">
                      <span
                        className={`rounded border px-1.5 py-0.5 text-xs font-bold ${
                          VERDICT_CLS[sub.verdict] ?? VERDICT_CLS.pending
                        }`}
                      >
                        {sub.verdict}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-xs text-zinc-400">
                      {LANG_LABEL[sub.language] ?? sub.language}
                    </td>
                    <td className="px-5 py-3 text-xs text-zinc-400">
                      {sub.total_test_cases > 0
                        ? `${sub.test_cases_passed} / ${sub.total_test_cases}`
                        : "—"}
                    </td>
                    <td className="px-5 py-3 text-xs text-zinc-500">
                      {sub.runtime_ms != null ? `${sub.runtime_ms} ms` : "—"}
                    </td>
                    <td className="px-5 py-3 text-xs text-zinc-500">
                      {new Date(sub.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {history.pages > 1 && (
            <div className="flex items-center justify-between border-t border-zinc-800 px-5 py-3">
              <p className="text-xs text-zinc-500">
                Page {history.page} of {history.pages} &mdash; {history.total} submissions
              </p>
              <div className="flex gap-2">
                <button
                  disabled={history.page <= 1}
                  onClick={() => onPageChange(history.page - 1)}
                  className="rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-400 transition-colors hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  ← Prev
                </button>
                <button
                  disabled={history.page >= history.pages}
                  onClick={() => onPageChange(history.page + 1)}
                  className="rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-400 transition-colors hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
