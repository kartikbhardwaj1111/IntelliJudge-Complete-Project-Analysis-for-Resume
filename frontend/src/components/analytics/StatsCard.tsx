interface Props {
  label: string;
  value: string | number;
  sub?: string | null;
  icon: string;
  accent: string; // tailwind border + text color pair e.g. "violet"
}

const ACCENT: Record<string, { border: string; text: string }> = {
  violet: { border: "border-violet-500/25", text: "text-violet-400" },
  sky:    { border: "border-sky-500/25",    text: "text-sky-400" },
  emerald:{ border: "border-emerald-500/25",text: "text-emerald-400" },
  amber:  { border: "border-amber-500/25",  text: "text-amber-400" },
  orange: { border: "border-orange-500/25", text: "text-orange-400" },
};

export default function StatsCard({ label, value, sub, icon, accent }: Props) {
  const { border, text } = ACCENT[accent] ?? ACCENT.violet;
  return (
    <div className={`rounded-xl border bg-zinc-950 p-4 ${border}`}>
      <div className="flex items-center justify-between">
        <p className="text-xs text-zinc-500">{label}</p>
        <span className="text-lg">{icon}</span>
      </div>
      <p className={`mt-1.5 text-2xl font-bold ${text}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-zinc-600">{sub}</p>}
    </div>
  );
}
