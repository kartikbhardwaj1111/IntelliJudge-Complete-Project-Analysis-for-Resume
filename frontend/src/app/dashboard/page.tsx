"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { api, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type {
  ActivityStats,
  DifficultyStats,
  OverviewStats,
  ProblemListItem,
  SubmissionHistory,
  TagStats,
} from "@/types";
import ProblemCard from "@/components/problem/ProblemCard";

// Charts use browser APIs — skip SSR
const AnalyticsCharts = dynamic(
  () => import("@/components/analytics/AnalyticsCharts"),
  {
    ssr: false,
    loading: () => (
      <div className="h-[460px] animate-pulse rounded-xl bg-zinc-900" />
    ),
  }
);

// ── Constants ─────────────────────────────────────────────────────────────────

type Tab = "overview" | "problems";

const VERDICT_CLS: Record<string, string> = {
  AC:      "text-emerald-400 bg-emerald-500/10",
  WA:      "text-red-400 bg-red-500/10",
  TLE:     "text-sky-400 bg-sky-500/10",
  CE:      "text-amber-400 bg-amber-500/10",
  RE:      "text-orange-400 bg-orange-500/10",
  MLE:     "text-purple-400 bg-purple-500/10",
  pending: "text-zinc-400 bg-zinc-500/10",
};

const LANG_LABEL: Record<string, string> = {
  cpp: "C++", java: "Java", python: "Python", javascript: "JS",
};

// ── Page ───────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [tab, setTab] = useState<Tab>("overview");

  // ── Problems tab ────────────────────────────────────────────────────────────
  const [problems, setProblems]       = useState<ProblemListItem[]>([]);
  const [probLoading, setProbLoading] = useState(true);
  const [probError, setProbError]     = useState<string | null>(null);

  // ── Overview tab ────────────────────────────────────────────────────────────
  const [overview,  setOverview]  = useState<OverviewStats | null>(null);
  const [difficulty, setDiff]     = useState<DifficultyStats | null>(null);
  const [tags,      setTags]      = useState<TagStats | null>(null);
  const [activity,  setActivity]  = useState<ActivityStats | null>(null);
  const [history,   setHistory]   = useState<SubmissionHistory | null>(null);
  const [analytics_loading, setAL]    = useState(false);
  const [analytics_error,   setAE]    = useState<string | null>(null);

  // ── Fetch problems once ─────────────────────────────────────────────────────
  useEffect(() => {
    api
      .get<{ items: ProblemListItem[] }>("/problems")
      .then((d) => setProblems(d.items))
      .catch((err) => setProbError(err instanceof ApiError ? err.message : "Failed to load"))
      .finally(() => setProbLoading(false));
  }, []);

  // ── Fetch analytics when overview tab first opens ───────────────────────────
  useEffect(() => {
    if (tab !== "overview" || overview !== null) return;

    const run = async () => {
      setAL(true);
      setAE(null);
      try {
        const [ov, diff, tg, act, hist] = await Promise.all([
          api.get<OverviewStats>("/analytics/overview"),
          api.get<DifficultyStats>("/analytics/difficulty"),
          api.get<TagStats>("/analytics/tags"),
          api.get<ActivityStats>("/analytics/activity"),
          api.get<SubmissionHistory>("/analytics/submissions?page=1&page_size=10"),
        ]);
        setOverview(ov);
        setDiff(diff);
        setTags(tg);
        setActivity(act);
        setHistory(hist);
      } catch {
        setAE("Could not load analytics. Make sure the backend is running.");
      } finally {
        setAL(false);
      }
    };
    run();
  }, [tab, overview]);

  // ── Submission history pagination ────────────────────────────────────────────
  async function fetchHistoryPage(page: number) {
    try {
      const hist = await api.get<SubmissionHistory>(
        `/analytics/submissions?page=${page}&page_size=10`
      );
      setHistory(hist);
    } catch {
      // silent — keep existing data
    }
  }

  // ── Stat card data ──────────────────────────────────────────────────────────
  const statCards = overview
    ? [
        {
          label: "Problems Saved",
          value: overview.total_problems,
          sub: null,
          color: "text-violet-400",
          bg: "border-violet-500/20",
        },
        {
          label: "Total Submissions",
          value: overview.total_submissions,
          sub: null,
          color: "text-sky-400",
          bg: "border-sky-500/20",
        },
        {
          label: "Problems Solved",
          value: overview.solved_problems,
          sub:
            overview.total_problems > 0
              ? `${Math.round((overview.solved_problems / overview.total_problems) * 100)}% of total`
              : null,
          color: "text-emerald-400",
          bg: "border-emerald-500/20",
        },
        {
          label: "Acceptance Rate",
          value: `${Math.round(overview.acceptance_rate * 100)}%`,
          sub: overview.avg_runtime_ms
            ? `Avg ${Math.round(overview.avg_runtime_ms)} ms`
            : null,
          color: "text-amber-400",
          bg: "border-amber-500/20",
        },
      ]
    : null;

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8">

      {/* Header */}
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Welcome back, {user?.username}
          </h1>
          <p className="mt-1 text-sm text-zinc-400">
            {probLoading
              ? "Loading…"
              : problems.length > 0
              ? `${problems.length} problem${problems.length !== 1 ? "s" : ""} in your collection`
              : "Upload a screenshot to get started"}
          </p>
        </div>
        <Link
          href="/upload"
          className="shrink-0 flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-500"
        >
          + Upload problem
        </Link>
      </div>

      {/* Tab bar */}
      <div className="mb-6 flex border-b border-zinc-800">
        {(["overview", "problems"] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={[
              "border-b-2 px-5 py-2.5 text-sm font-medium transition-colors",
              tab === t
                ? "border-violet-500 text-white"
                : "border-transparent text-zinc-500 hover:text-zinc-300",
            ].join(" ")}
          >
            {t === "overview"
              ? "Overview"
              : `Problems${!probLoading ? ` (${problems.length})` : ""}`}
          </button>
        ))}
      </div>

      {/* ─── Overview tab ──────────────────────────────────────────────────── */}
      {tab === "overview" && (
        analytics_loading ? (
          <div className="flex flex-col gap-5">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-24 animate-pulse rounded-xl bg-zinc-900" />
              ))}
            </div>
            <div className="h-[460px] animate-pulse rounded-xl bg-zinc-900" />
            <div className="h-64 animate-pulse rounded-xl bg-zinc-900" />
          </div>
        ) : analytics_error ? (
          <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {analytics_error}
          </div>
        ) : (
          <div className="flex flex-col gap-5">

            {/* Stat cards */}
            {statCards && (
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                {statCards.map((c) => (
                  <div
                    key={c.label}
                    className={`rounded-xl border bg-zinc-950 p-4 ${c.bg}`}
                  >
                    <p className="text-xs text-zinc-500">{c.label}</p>
                    <p className={`mt-1 text-2xl font-bold ${c.color}`}>{c.value}</p>
                    {c.sub && <p className="mt-0.5 text-xs text-zinc-600">{c.sub}</p>}
                  </div>
                ))}
              </div>
            )}

            {/* Charts */}
            {activity && difficulty && tags && (
              <AnalyticsCharts
                activity={activity}
                difficulty={difficulty}
                tags={tags}
              />
            )}

            {/* Submission history table */}
            {history && (
              <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950">
                <div className="border-b border-zinc-800 px-4 py-3">
                  <p className="text-sm font-semibold text-white">Recent Submissions</p>
                  <p className="mt-0.5 text-xs text-zinc-500">
                    {history.total} total submission{history.total !== 1 ? "s" : ""}
                  </p>
                </div>

                {history.items.length === 0 ? (
                  <div className="px-4 py-12 text-center text-sm text-zinc-600">
                    No submissions yet — solve some problems first!
                  </div>
                ) : (
                  <>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b border-zinc-800 text-left">
                            {["Problem", "Verdict", "Lang", "Passed", "Time", "Date"].map((h) => (
                              <th
                                key={h}
                                className="px-4 py-2.5 text-xs font-medium text-zinc-500"
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
                              <td className="px-4 py-2.5 max-w-[200px] truncate">
                                <Link
                                  href={`/problem/${sub.problem_id}`}
                                  className="text-zinc-300 hover:text-white hover:underline"
                                >
                                  {sub.problem_title}
                                </Link>
                              </td>
                              <td className="px-4 py-2.5">
                                <span
                                  className={`rounded px-1.5 py-0.5 text-xs font-bold ${
                                    VERDICT_CLS[sub.verdict] ?? VERDICT_CLS.pending
                                  }`}
                                >
                                  {sub.verdict}
                                </span>
                              </td>
                              <td className="px-4 py-2.5 text-xs text-zinc-400">
                                {LANG_LABEL[sub.language] ?? sub.language}
                              </td>
                              <td className="px-4 py-2.5 text-xs text-zinc-400">
                                {sub.total_test_cases > 0
                                  ? `${sub.test_cases_passed}/${sub.total_test_cases}`
                                  : "—"}
                              </td>
                              <td className="px-4 py-2.5 text-xs text-zinc-500">
                                {sub.runtime_ms != null ? `${sub.runtime_ms} ms` : "—"}
                              </td>
                              <td className="px-4 py-2.5 text-xs text-zinc-500">
                                {new Date(sub.created_at).toLocaleDateString("en-US", {
                                  month: "short",
                                  day: "numeric",
                                })}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>

                    {/* Pagination */}
                    {history.pages > 1 && (
                      <div className="flex items-center justify-between border-t border-zinc-800 px-4 py-3">
                        <p className="text-xs text-zinc-500">
                          Page {history.page} of {history.pages}
                        </p>
                        <div className="flex gap-2">
                          <button
                            disabled={history.page <= 1}
                            onClick={() => fetchHistoryPage(history.page - 1)}
                            className="rounded border border-zinc-700 px-3 py-1 text-xs text-zinc-400 transition-colors hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
                          >
                            ← Prev
                          </button>
                          <button
                            disabled={history.page >= history.pages}
                            onClick={() => fetchHistoryPage(history.page + 1)}
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
            )}
          </div>
        )
      )}

      {/* ─── Problems tab ──────────────────────────────────────────────────── */}
      {tab === "problems" && (
        <>
          {probLoading && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="h-36 animate-pulse rounded-xl border border-zinc-800 bg-zinc-900"
                />
              ))}
            </div>
          )}

          {!probLoading && probError && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {probError}
            </div>
          )}

          {!probLoading && !probError && problems.length === 0 && (
            <div className="flex flex-col items-center gap-4 rounded-xl border border-dashed border-zinc-700 py-20 text-center">
              <div className="text-4xl">📸</div>
              <p className="font-medium text-zinc-300">No problems yet</p>
              <p className="max-w-xs text-sm text-zinc-500">
                Upload a screenshot of a coding problem and AI will reconstruct it for
                you.
              </p>
              <Link
                href="/upload"
                className="mt-2 rounded-lg bg-violet-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-500"
              >
                Upload your first problem →
              </Link>
            </div>
          )}

          {!probLoading && !probError && problems.length > 0 && (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {problems.map((p) => (
                <ProblemCard key={p.id} problem={p} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
