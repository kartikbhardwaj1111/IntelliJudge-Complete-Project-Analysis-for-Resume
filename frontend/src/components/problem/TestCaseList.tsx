"use client";

import { useState } from "react";
import { api, ApiError } from "@/lib/api";
import type { TestCase } from "@/types";

interface TestCaseListProps {
  problemId: string;
  initialTestCases: TestCase[];
}

const CATEGORY_BADGE: Record<string, string> = {
  sample: "bg-blue-500/15 text-blue-400 border-blue-500/20",
  edge: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  hidden: "bg-zinc-500/15 text-zinc-400 border-zinc-700",
  stress: "bg-purple-500/15 text-purple-400 border-purple-500/20",
};

export default function TestCaseList({
  problemId,
  initialTestCases,
}: TestCaseListProps) {
  const [testCases, setTestCases] = useState<TestCase[]>(initialTestCases);
  const [generating, setGenerating] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [banner, setBanner] = useState<{
    kind: "success" | "error";
    text: string;
  } | null>(null);

  function showBanner(kind: "success" | "error", text: string) {
    setBanner({ kind, text });
    setTimeout(() => setBanner(null), 4000);
  }

  async function handleGenerate() {
    setGenerating(true);
    setBanner(null);
    try {
      const generated = await api.post<TestCase[]>(
        `/problems/${problemId}/generate-tests`,
        { count: 6, categories: ["sample", "edge", "hidden"] }
      );
      setTestCases((prev) => [...prev, ...generated]);
      showBanner("success", `${generated.length} test cases generated.`);
    } catch (err) {
      showBanner(
        "error",
        err instanceof ApiError ? err.message : "Generation failed."
      );
    } finally {
      setGenerating(false);
    }
  }

  async function handleDelete(tcId: string) {
    setDeletingId(tcId);
    setBanner(null);
    try {
      await api.delete(`/problems/${problemId}/test-cases/${tcId}`);
      setTestCases((prev) => prev.filter((tc) => tc.id !== tcId));
      if (expandedId === tcId) setExpandedId(null);
    } catch (err) {
      showBanner(
        "error",
        err instanceof ApiError ? err.message : "Delete failed."
      );
    } finally {
      setDeletingId(null);
    }
  }

  function toggleExpand(id: string) {
    setExpandedId((prev) => (prev === id ? null : id));
  }

  return (
    <section className="flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">
          Test Cases
          <span className="ml-2 text-sm font-normal text-zinc-500">
            ({testCases.length})
          </span>
        </h2>
        <button
          onClick={handleGenerate}
          disabled={generating}
          className="flex items-center gap-1.5 rounded-lg border border-violet-500/30 bg-violet-500/10 px-3 py-1.5 text-xs font-semibold text-violet-400 transition-colors hover:border-violet-500/60 hover:bg-violet-500/20 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {generating ? (
            <>
              <Spinner />
              Generating…
            </>
          ) : (
            "✦ Generate with AI"
          )}
        </button>
      </div>

      {/* Banner */}
      {banner && (
        <div
          className={`rounded-lg border px-3 py-2 text-sm ${
            banner.kind === "success"
              ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
              : "border-red-500/30 bg-red-500/10 text-red-400"
          }`}
        >
          {banner.text}
        </div>
      )}

      {/* Empty state */}
      {testCases.length === 0 && (
        <div className="rounded-xl border border-dashed border-zinc-700 py-12 text-center text-sm text-zinc-500">
          No test cases yet.{" "}
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="text-violet-400 hover:underline disabled:opacity-50"
          >
            Generate with AI
          </button>{" "}
          to create some automatically.
        </div>
      )}

      {/* Test case list */}
      {testCases.length > 0 && (
        <div className="flex flex-col gap-2">
          {testCases.map((tc, i) => {
            const expanded = expandedId === tc.id;
            const isDeleting = deletingId === tc.id;

            return (
              <div
                key={tc.id}
                className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900"
              >
                {/* Row header */}
                <button
                  onClick={() => toggleExpand(tc.id)}
                  className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-zinc-800/50"
                >
                  <div className="flex items-center gap-3">
                    <span className="w-6 text-right font-mono text-xs text-zinc-600">
                      #{i + 1}
                    </span>
                    <span
                      className={`rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${
                        CATEGORY_BADGE[tc.category] ?? ""
                      }`}
                    >
                      {tc.category}
                    </span>
                    {!tc.is_visible && (
                      <span className="text-xs text-zinc-600">hidden</span>
                    )}
                  </div>
                  <svg
                    className={`h-3.5 w-3.5 text-zinc-600 transition-transform ${
                      expanded ? "rotate-180" : ""
                    }`}
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>

                {/* Expanded body */}
                {expanded && (
                  <div className="border-t border-zinc-800 px-4 pb-4 pt-3">
                    <div className="grid gap-3 sm:grid-cols-2">
                      <div>
                        <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-zinc-500">
                          Input
                        </p>
                        <pre className="overflow-x-auto rounded-lg bg-zinc-950 px-3 py-2.5 font-mono text-xs leading-relaxed text-zinc-300">
                          {tc.input || "(empty)"}
                        </pre>
                      </div>
                      <div>
                        <p className="mb-1.5 text-xs font-medium uppercase tracking-wide text-zinc-500">
                          Expected Output
                        </p>
                        <pre className="overflow-x-auto rounded-lg bg-zinc-950 px-3 py-2.5 font-mono text-xs leading-relaxed text-zinc-300">
                          {tc.expected_output || "(empty)"}
                        </pre>
                      </div>
                    </div>

                    <div className="mt-3 flex justify-end">
                      <button
                        onClick={() => handleDelete(tc.id)}
                        disabled={isDeleting}
                        className="text-xs text-zinc-600 transition-colors hover:text-red-400 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isDeleting ? "Deleting…" : "Delete"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function Spinner() {
  return (
    <svg
      className="h-3 w-3 animate-spin"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}
