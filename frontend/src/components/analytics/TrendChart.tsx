"use client";

import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ActivityStats } from "@/types";

interface Props {
  data: ActivityStats;
}

const TOOLTIP_STYLE = {
  backgroundColor: "#18181b",
  border: "1px solid #27272a",
  borderRadius: "8px",
  fontSize: 12,
};

export default function TrendChart({ data }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const chartData = data.days.map((d) => ({
    ...d,
    label: new Date(d.date + "T12:00:00").toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    }),
  }));

  const totalSubs = data.days.reduce((s, d) => s + d.submissions, 0);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
        Submission Activity
      </p>
      <p className="mb-3 text-xs text-zinc-600">
        {totalSubs} submission{totalSubs !== 1 ? "s" : ""} in the last {data.days.length} days
      </p>

      {!mounted ? (
        <div className="h-[200px] animate-pulse rounded bg-zinc-900" />
      ) : (
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData} margin={{ top: 4, right: 4, left: -24, bottom: 0 }}>
            <defs>
              <linearGradient id="trendSubs" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%"  stopColor="#8b5cf6" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="trendAC" x1="0" y1="0" x2="0" y2="1">
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
              interval={Math.floor(data.days.length / 6)}
            />
            <YAxis
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
            />
            <Tooltip contentStyle={TOOLTIP_STYLE} labelStyle={{ color: "#a1a1aa" }} />
            <Legend
              iconType="circle"
              iconSize={7}
              wrapperStyle={{ fontSize: 11, color: "#71717a" }}
            />
            <Area
              type="monotone"
              dataKey="submissions"
              name="Submissions"
              stroke="#8b5cf6"
              strokeWidth={2}
              fill="url(#trendSubs)"
              dot={false}
            />
            <Area
              type="monotone"
              dataKey="accepted"
              name="Accepted"
              stroke="#10b981"
              strokeWidth={2}
              fill="url(#trendAC)"
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
