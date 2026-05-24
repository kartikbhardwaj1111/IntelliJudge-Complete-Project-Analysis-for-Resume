"use client";

import { useEffect, useState } from "react";
import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { TagStats } from "@/types";

interface Props {
  data: TagStats;
}

const TOOLTIP_STYLE = {
  backgroundColor: "#18181b",
  border: "1px solid #27272a",
  borderRadius: "8px",
  fontSize: 12,
};

export default function TopicChart({ data }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  const radarData = data.tags.map((t) => ({
    tag:      t.tag.length > 12 ? t.tag.slice(0, 12) + "…" : t.tag,
    fullTag:  t.tag,
    accuracy: Math.round(t.accuracy * 100),
    solved:   t.solved,
    total:    t.total,
  }));

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-950 p-4">
      <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-zinc-400">
        Topic Accuracy
      </p>
      <p className="mb-3 text-xs text-zinc-600">
        % of problems solved per tag (top {data.tags.length})
      </p>

      {!mounted || radarData.length === 0 ? (
        <div className="flex h-[240px] items-center justify-center text-xs text-zinc-600">
          {mounted
            ? "Add tags to your problems to see topic accuracy"
            : ""}
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={240}>
          <RadarChart data={radarData} margin={{ top: 10, right: 40, bottom: 10, left: 40 }}>
            <PolarGrid stroke="#27272a" />
            <PolarAngleAxis
              dataKey="tag"
              tick={{ fill: "#a1a1aa", fontSize: 11 }}
            />
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
              formatter={(v, _name, props) => [
                `${v}% (${props.payload.solved}/${props.payload.total})`,
                "Solved",
              ]}
            />
          </RadarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
