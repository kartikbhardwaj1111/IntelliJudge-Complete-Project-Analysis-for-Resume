import Link from "next/link";
import type { ProblemListItem } from "@/types";

const DIFFICULTY_BADGE: Record<string, string> = {
  easy: "bg-emerald-500/15 text-emerald-400 border-emerald-500/20",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/20",
  hard: "bg-red-500/15 text-red-400 border-red-500/20",
};

export default function ProblemCard({ problem }: { problem: ProblemListItem }) {
  const diff = problem.difficulty;

  return (
    <Link
      href={`/problem/${problem.id}`}
      className="group flex flex-col gap-3 rounded-xl border border-zinc-800 bg-zinc-900 p-5 transition-colors hover:border-zinc-700"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="line-clamp-2 font-semibold text-white transition-colors group-hover:text-violet-300">
          {problem.title}
        </h3>
        {diff && (
          <span
            className={`shrink-0 rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${
              DIFFICULTY_BADGE[diff] ?? ""
            }`}
          >
            {diff}
          </span>
        )}
      </div>

      {problem.tags && problem.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {problem.tags.slice(0, 4).map((tag) => (
            <span
              key={tag}
              className="rounded-md bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-4 text-xs text-zinc-500">
        <span>
          {problem.test_case_count} test case
          {problem.test_case_count !== 1 ? "s" : ""}
        </span>
        <span>
          {new Date(problem.created_at).toLocaleDateString("en-US", {
            month: "short",
            day: "numeric",
            year: "numeric",
          })}
        </span>
      </div>
    </Link>
  );
}
