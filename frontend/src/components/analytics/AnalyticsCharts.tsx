"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ActivityStats, DifficultyStats, TagStats } from "@/types";

interface Props {
  activity: ActivityStats;
  difficulty: DifficultyStats;
  tags: TagStats;
}

const DIFF_COLORS = {
  Easy: "#10b981",
  Medium: "#f59e0b",
  Hard: "#ef4444",
  Unknown: "#71717a",
};

const TOOLTIP_STYLE = {
  backgroundColor: "#18181b",
  border: "1px solid #27272a",
  borderRadius: "8px",
  fontSize: 12,
};

export default function AnalyticsCharts({ activity, difficulty, tags }: Props) {
  // Activity: format dates for X-axis
  const activityData = activity.days.map((d) => ({
    ...d,
    label: new Date(d.date + "T12:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  // Difficulty pie data — skip zeros
  const diffData = (
    [
      { name: "Easy",    value: difficulty.easy.total,    color: DIFF_COLORS.Easy },
      { name: "Medium",  value: difficulty.medium.total,  color: DIFF_COLORS.Medium },
      { name: "Hard",    value: difficulty.hard.total,    color: DIFF_COLORS.Hard },
      { name: "Unknown", value: difficulty.unknown.total, color: DIFF_COLORS.Unknown },
    ] as { name: string; value: number; color: string }[]
  ).filter((d) => d.value > 0);

  // Radar: accuracy as integer percent, truncate long tag names
  const radarData = tags.tags.map((t) => ({
    tag: t.tag.length > 12 ? t.tag.slice(0, 12) + "…" : t.tag,
    accuracy: Math.round(t.accuracy * 100),
  }));

  return (
    <div className="grid gap-4 lg:grid-cols-3">

      {/* ── Activity chart (2 col wide) ──────────────────────── */}
      <div className="lg:col-span-2 rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-zinc-400">
          Submission Activity — Last 30 Days
        </p>
        <ResponsiveContainer width="100%" height={180}>
          <AreaChart data={activityData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <defs>
              <linearGradient id="gSubs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#8b5cf6" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gAC" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#10b981" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
            <XAxis
              dataKey="label"
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval={4}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
            />
            <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: "#a1a1aa" }} />
            <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
            <Area
              type="monotone"
              dataKey="submissions"
              name="Submissions"
              stroke="#8b5cf6"
              strokeWidth={2}
              fill="url(#gSubs)"
              dot={false}
            />
            <Area
              type="monotone"
              dataKey="accepted"
              name="Accepted"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#gAC)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* ── Difficulty donut (1 col) ──────────────────────────── */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-zinc-400">
          Difficulty Split
        </p>
        {diffData.length > 0 ? (
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={diffData}
                cx="50%"
                cy="45%"
                innerRadius={46}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
              >
                {diffData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value, name) => [`${value}`, `${name}`]}
              />
              <Legend iconType="circle" iconSize={7} wrapperStyle={{ fontSize: 11, color: "#71717a" }} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[180px] items-center justify-center text-xs text-zinc-600">
            No problems yet
          </div>
        )}
      </div>

      {/* ── Tag accuracy radar (full width) ──────────────────── */}
      <div className="lg:col-span-3 rounded-xl border border-zinc-800 bg-zinc-950 p-4">
        <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
          Tag Accuracy (%)
        </p>
        <p className="mb-3 text-xs text-zinc-600">Top tags by problem count</p>
        {radarData.length > 0 ? (
          <ResponsiveContainer width="100%" height={220}>
            <RadarChart data={radarData} margin={{ top: 10, right: 40, bottom: 10, left: 40 }}>
              <PolarGrid stroke="#27272a" />
              <PolarAngleAxis dataKey="tag" tick={{ fill: "#a1a1aa", fontSize: 11 }} />
              <Radar
                name="Accuracy %"
                dataKey="accuracy"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.25}
                strokeWidth={2}
              />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(v) => [`${v}%`, "Accuracy"]}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-[220px] items-center justify-center text-xs text-zinc-600">
            Tag data appears after you add problems with tags
          </div>
        )}
      </div>
    </div>
  );
}
