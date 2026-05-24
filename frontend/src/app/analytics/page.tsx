"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type {
  ActivityStats,
  DifficultyStats,
  OverviewStats,
  SubmissionHistory,
  TagStats,
} from "@/types";
import StatsCard from "@/components/analytics/StatsCard";
import DifficultyChart from "@/components/analytics/DifficultyChart";
import TopicChart from "@/components/analytics/TopicChart";
import TrendChart from "@/components/analytics/TrendChart";
import SubmissionTable from "@/components/analytics/SubmissionTable";

// ── Skeleton helpers ──────────────────────────────────────────────────────────

function CardSkeleton() {
  return <div className="h-24 animate-pulse rounded-xl bg-zinc-900" />;
}
function ChartSkeleton({ h = "h-72" }: { h?: string }) {
  return <div className={`${h} animate-pulse rounded-xl bg-zinc-900`} />;
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const { user } = useAuthStore();

  const [overview,   setOverview]   = useState<OverviewStats | null>(null);
  const [difficulty, setDifficulty] = useState<DifficultyStats | null>(null);
  const [topics,     setTopics]     = useState<TagStats | null>(null);
  const [trends,     setTrends]     = useState<ActivityStats | null>(null);
  const [history,    setHistory]    = useState<SubmissionHistory | null>(null);
  const [histLoading, setHistLoading] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState<string | null>(null);

  // Initial load — all 5 endpoints in parallel
  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const [ov, diff, tpc, trd, hist] = await Promise.all([
          api.get<OverviewStats>("/analytics/overview"),
          api.get<DifficultyStats>("/analytics/difficulty"),
          api.get<TagStats>("/analytics/topics"),
          api.get<ActivityStats>("/analytics/trends?days=30"),
          api.get<SubmissionHistory>("/analytics/submissions?page=1&page_size=20"),
        ]);
        setOverview(ov);
        setDifficulty(diff);
        setTopics(tpc);
        setTrends(trd);
        setHistory(hist);
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : "Could not load analytics. Make sure the backend is running."
        );
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  // Pagination
  async function handlePageChange(page: number) {
    setHistLoading(true);
    try {
      const hist = await api.get<SubmissionHistory>(
        `/analytics/submissions?page=${page}&page_size=20`
      );
      setHistory(hist);
    } catch {
      // keep existing data on error
    } finally {
      setHistLoading(false);
    }
  }

  // ── Stat cards config ────────────────────────────────────────────────────
  const cards = overview
    ? [
        {
          label: "Problems Saved",
          value: overview.total_problems,
          sub:   null,
          icon:  "📚",
          accent: "violet",
        },
        {
          label: "Total Submissions",
          value: overview.total_submissions,
          sub:   null,
          icon:  "🚀",
          accent: "sky",
        },
        {
          label: "Problems Solved",
          value: overview.solved_problems,
          sub:
            overview.total_problems > 0
              ? `${Math.round(
                  (overview.solved_problems / overview.total_problems) * 100
                )}% of total`
              : null,
          icon:  "✅",
          accent: "emerald",
        },
        {
          label: "Acceptance Rate",
          value: `${Math.round(overview.acceptance_rate * 100)}%`,
          sub:   overview.avg_runtime_ms
            ? `Avg ${Math.round(overview.avg_runtime_ms)} ms`
            : null,
          icon:  "🎯",
          accent: "amber",
        },
        {
          label: "Current Streak",
          value: `${overview.current_streak} day${overview.current_streak !== 1 ? "s" : ""}`,
          sub:   overview.current_streak > 0 ? "Keep it going!" : "Submit today to start",
          icon:  "🔥",
          accent: "orange",
        },
      ]
    : null;

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8">

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Analytics</h1>
        <p className="mt-1 text-sm text-zinc-400">
          {user?.username
            ? `Your performance overview, ${user.username}`
            : "Your performance overview"}
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* Stat cards */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-5">
        {loading
          ? [...Array(5)].map((_, i) => <CardSkeleton key={i} />)
          : cards?.map((c) => <StatsCard key={c.label} {...c} />)}
      </div>

      {/* Trend chart — full width */}
      <div className="mb-4">
        {loading || !trends ? (
          <ChartSkeleton h="h-64" />
        ) : (
          <TrendChart data={trends} />
        )}
      </div>

      {/* Difficulty + Topic charts side by side */}
      <div className="mb-4 grid gap-4 lg:grid-cols-2">
        <div>
          {loading || !difficulty ? (
            <ChartSkeleton h="h-72" />
          ) : (
            <DifficultyChart data={difficulty} />
          )}
        </div>
        <div>
          {loading || !topics ? (
            <ChartSkeleton h="h-72" />
          ) : (
            <TopicChart data={topics} />
          )}
        </div>
      </div>

      {/* Submission history table */}
      {loading || !history ? (
        <ChartSkeleton h="h-64" />
      ) : (
        <SubmissionTable
          history={history}
          onPageChange={handlePageChange}
          loading={histLoading}
        />
      )}
    </div>
  );
}
