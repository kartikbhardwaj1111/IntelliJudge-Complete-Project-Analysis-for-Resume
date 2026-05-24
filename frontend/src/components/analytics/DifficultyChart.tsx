"use client";

import { useEffect, useState } from "react";
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DifficultyStats } from "@/types";

interface Props {
  data: DifficultyStats;
}

const SLICES = [
  { key: "easy",    label: "Easy",    color: "#10b981" },
  { key: "medium",  label: "Medium",  color: "#f59e0b" },
  { key: "hard",    label: "Hard",    color: "#ef4444" },
  { key: "unknown", label: "Unknown", color: "#71717a" },
] as const;

const TOOLTIP_STYLE = {
  backgroundColor: "#18181b",
  border: "1px solid #27272a",
  borderRadius: "8px",
  fontSize: 12,
};

export default function DifficultyChart({ data }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const pieData = SLICES.map((s) => ({
    name:  s.label,
    value: data[s.key].total,
    color: s.color,
  })).filter((d) => d.value > 0);

  const total = pieData.reduce((s, d) => s + d.value, 0);

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
        Difficulty Split
      </p>
      <p className="mb-3 text-xs text-zinc-600">{total} problems total</p>

      {!mounted || total === 0 ? (
        <div className="flex h-[200px] items-center justify-center text-xs text-zinc-600">
          {mounted ? "No problems yet" : ""}
        </div>
      ) : (
        <>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="45%"
                innerRadius={46}
                outerRadius={70}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(v, name) => [`${v} problems`, name]}
              />
              <Legend
                iconType="circle"
                iconSize={7}
                wrapperStyle={{ fontSize: 11, color: "#71717a" }}
              />
            </PieChart>
          </ResponsiveContainer>

          {/* Solved breakdown */}
          <div className="mt-3 grid grid-cols-3 gap-1.5 border-t border-zinc-800 pt-3">
            {SLICES.filter((s) => data[s.key].total > 0).map((s) => (
              <div key={s.key} className="text-center">
                <p className="text-[10px] uppercase tracking-wide text-zinc-600">
                  {s.label}
                </p>
                <p className="text-sm font-semibold" style={{ color: s.color }}>
                  {data[s.key].solved}/{data[s.key].total}
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
