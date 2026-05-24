"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import dynamic from "next/dynamic";
import { api, ApiError } from "@/lib/api";
import type {
  Language,
  Problem,
  ProblemExample,
  RunResult,
  Submission,
} from "@/types";
import { CODE_TEMPLATES } from "@/lib/templates";
import OutputPanel from "@/components/editor/OutputPanel";
import SubmissionResult from "@/components/problem/SubmissionResult";
import TestCaseList from "@/components/problem/TestCaseList";
import EdgeCasePanel from "@/components/ai/EdgeCasePanel";
import FeedbackPanel from "@/components/ai/FeedbackPanel";
import HintPanel from "@/components/ai/HintPanel";

// Monaco is browser-only — skip SSR to avoid hydration errors
const CodeEditor = dynamic(() => import("@/components/editor/CodeEditor"), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full animate-pulse bg-zinc-900" />
  ),
});

// ── Styling constants ─────────────────────────────────────────────────────────

const DIFF_BADGE: Record<string, string> = {
  easy:   "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  hard:   "bg-red-500/15 text-red-400 border-red-500/30",
};

const INPUT_CLS =
  "w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500";

// ── Edit form type ─────────────────────────────────────────────────────────────

interface EditForm {
  title: string;
  description: string;
  input_format: string;
  output_format: string;
  difficulty: "" | "easy" | "medium" | "hard";
  tags: string;
  time_limit: string;
  memory_limit: string;
  constraint_notes: string;
  examples: { input: string; output: string; explanation: string }[];
}

function toForm(p: Problem): EditForm {
  return {
    title: p.title,
    description: p.description,
    input_format: p.input_format ?? "",
    output_format: p.output_format ?? "",
    difficulty: (p.difficulty ?? "") as EditForm["difficulty"],
    tags: (p.tags ?? []).join(", "),
    time_limit: p.constraints?.time_limit ?? "",
    memory_limit: p.constraints?.memory_limit ?? "",
    constraint_notes: p.constraints?.notes ?? "",
    examples: (p.examples ?? []).map((ex) => ({
      input: (ex as ProblemExample).input,
      output: (ex as ProblemExample).output,
      explanation: (ex as ProblemExample).explanation ?? "",
    })),
  };
}

// ── Page ───────────────────────────────────────────────────────────────────────

export default function ProblemPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  // Problem data
  const [problem, setProblem] = useState<Problem | null>(null);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);

  // Edit state
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState<EditForm | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Delete state
  const [deletePhase, setDeletePhase] = useState<"idle" | "confirm" | "deleting">("idle");
  const [deleteError, setDeleteError] = useState<string | null>(null);

  // Editor state
  const [language, setLanguage] = useState<Language>("cpp");
  const [code, setCode] = useState<string>(CODE_TEMPLATES.cpp);

  // Run state
  const [customInput, setCustomInput] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [runError, setRunError] = useState<string | null>(null);

  // Submit state
  const [submitting, setSubmitting] = useState(false);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Active I/O tab
  const [ioTab, setIoTab] = useState<"input" | "output" | "result" | "hints">("input");

  useEffect(() => {
    api
      .get<Problem>(`/problems/${id}`)
      .then(setProblem)
      .catch((err) =>
        setFetchError(
          err instanceof ApiError ? err.message : "Failed to load problem."
        )
      )
      .finally(() => setLoading(false));
  }, [id]);

  // Swap template when language changes
  function handleLanguageChange(lang: Language) {
    setLanguage(lang);
    setCode(CODE_TEMPLATES[lang]);
    setRunResult(null);
    setSubmission(null);
    setRunError(null);
    setSubmitError(null);
  }

  // ── Run ───────────────────────────────────────────────────────────────────

  async function handleRun() {
    if (!problem) return;
    setRunning(true);
    setRunResult(null);
    setRunError(null);
    setIoTab("output");
    try {
      const result = await api.post<RunResult>("/submissions/run", {
        problem_id: problem.id,
        language,
        code,
        stdin: customInput,
      });
      setRunResult(result);
    } catch (err) {
      setRunError(err instanceof ApiError ? err.message : "Execution failed.");
    } finally {
      setRunning(false);
    }
  }

  // ── Submit ────────────────────────────────────────────────────────────────

  async function handleSubmit() {
    if (!problem) return;
    setSubmitting(true);
    setSubmission(null);
    setSubmitError(null);
    setIoTab("result");
    try {
      const result = await api.post<Submission>("/submissions/submit", {
        problem_id: problem.id,
        language,
        code,
      });
      setSubmission(result);
    } catch (err) {
      setSubmitError(err instanceof ApiError ? err.message : "Submission failed.");
    } finally {
      setSubmitting(false);
    }
  }

  // ── Edit handlers ──────────────────────────────────────────────────────────

  function startEdit() {
    if (!problem) return;
    setForm(toForm(problem));
    setSaveError(null);
    setEditing(true);
  }

  function cancelEdit() {
    setEditing(false);
    setForm(null);
    setSaveError(null);
  }

  async function handleSave() {
    if (!form || !problem) return;
    setSaveError(null);
    setSaving(true);
    try {
      const tags = form.tags.split(",").map((t) => t.trim().toLowerCase()).filter(Boolean);
      const examples = form.examples
        .filter((ex) => ex.input.trim() || ex.output.trim())
        .map((ex) => ({
          input: ex.input,
          output: ex.output,
          ...(ex.explanation.trim() ? { explanation: ex.explanation } : {}),
        }));
      const constraints: Record<string, string> = {};
      if (form.time_limit.trim()) constraints.time_limit = form.time_limit.trim();
      if (form.memory_limit.trim()) constraints.memory_limit = form.memory_limit.trim();
      if (form.constraint_notes.trim()) constraints.notes = form.constraint_notes.trim();

      const updated = await api.put<Problem>(`/problems/${problem.id}`, {
        title: form.title,
        description: form.description,
        input_format: form.input_format.trim() || null,
        output_format: form.output_format.trim() || null,
        difficulty: form.difficulty || null,
        tags: tags.length > 0 ? tags : null,
        constraints: Object.keys(constraints).length > 0 ? constraints : null,
        examples: examples.length > 0 ? examples : null,
      });

      setProblem(updated);
      setEditing(false);
      setForm(null);
    } catch (err) {
      setSaveError(err instanceof ApiError ? err.message : "Failed to save.");
    } finally {
      setSaving(false);
    }
  }

  // ── Delete handlers ────────────────────────────────────────────────────────

  async function handleDelete() {
    if (!problem) return;
    setDeletePhase("deleting");
    setDeleteError(null);
    try {
      await api.delete(`/problems/${problem.id}`);
      router.push("/dashboard");
    } catch (err) {
      setDeleteError(err instanceof ApiError ? err.message : "Delete failed.");
      setDeletePhase("idle");
    }
  }

  // ── Loading / error ────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="mx-auto w-full max-w-4xl px-4 py-10">
        <div className="mb-4 h-6 w-48 animate-pulse rounded-lg bg-zinc-800" />
        <div className="mb-8 h-8 w-2/3 animate-pulse rounded-lg bg-zinc-800" />
        {[80, 90, 60, 75].map((w, i) => (
          <div
            key={i}
            className="mb-2 h-4 animate-pulse rounded-lg bg-zinc-800"
            style={{ width: `${w}%` }}
          />
        ))}
      </div>
    );
  }

  if (fetchError || !problem) {
    return (
      <div className="mx-auto w-full max-w-4xl px-4 py-10">
        <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {fetchError ?? "Problem not found."}
        </div>
        <Link href="/dashboard" className="mt-4 inline-block text-sm text-violet-400 hover:underline">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  // ── Edit view ──────────────────────────────────────────────────────────────

  if (editing && form) {
    return (
      <div className="mx-auto w-full max-w-4xl px-4 py-10">
        <div className="mb-6 flex items-center justify-between gap-4">
          <h1 className="text-xl font-bold text-white">Edit Problem</h1>
          <div className="flex shrink-0 items-center gap-2">
            <button
              onClick={cancelEdit}
              disabled={saving}
              className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 rounded-lg bg-violet-600 px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:opacity-50"
            >
              {saving ? <><Spinner /> Saving…</> : "Save Changes"}
            </button>
          </div>
        </div>

        {saveError && (
          <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
            {saveError}
          </div>
        )}

        <div className="flex flex-col gap-5">
          <Field label="Title">
            <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className={INPUT_CLS} />
          </Field>
          <Field label="Description">
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} rows={8} className={`${INPUT_CLS} resize-y`} />
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Input Format">
              <textarea value={form.input_format} onChange={(e) => setForm({ ...form, input_format: e.target.value })} rows={4} className={`${INPUT_CLS} resize-y`} />
            </Field>
            <Field label="Output Format">
              <textarea value={form.output_format} onChange={(e) => setForm({ ...form, output_format: e.target.value })} rows={4} className={`${INPUT_CLS} resize-y`} />
            </Field>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Difficulty">
              <select value={form.difficulty} onChange={(e) => setForm({ ...form, difficulty: e.target.value as EditForm["difficulty"] })} className={INPUT_CLS}>
                <option value="">Not specified</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </Field>
            <Field label="Tags" hint="comma-separated">
              <input value={form.tags} onChange={(e) => setForm({ ...form, tags: e.target.value })} placeholder="dp, graphs, binary-search" className={INPUT_CLS} />
            </Field>
          </div>
          <fieldset className="rounded-xl border border-zinc-800 p-4">
            <legend className="px-2 text-sm font-medium text-zinc-300">Constraints</legend>
            <div className="grid gap-4 sm:grid-cols-3">
              <Field label="Time Limit"><input value={form.time_limit} onChange={(e) => setForm({ ...form, time_limit: e.target.value })} placeholder="1 second" className={INPUT_CLS} /></Field>
              <Field label="Memory Limit"><input value={form.memory_limit} onChange={(e) => setForm({ ...form, memory_limit: e.target.value })} placeholder="256 MB" className={INPUT_CLS} /></Field>
              <Field label="Notes"><input value={form.constraint_notes} onChange={(e) => setForm({ ...form, constraint_notes: e.target.value })} placeholder="n ≤ 10⁵" className={INPUT_CLS} /></Field>
            </div>
          </fieldset>
          <div>
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-300">Examples</span>
              <button type="button" onClick={() => setForm({ ...form, examples: [...form.examples, { input: "", output: "", explanation: "" }] })} className="text-xs text-violet-400 hover:text-violet-300">
                + Add Example
              </button>
            </div>
            {form.examples.map((ex, i) => (
              <div key={i} className="mb-3 rounded-xl border border-zinc-800 bg-zinc-950 p-4">
                <div className="mb-3 flex items-center justify-between">
                  <span className="text-xs font-medium text-zinc-500">Example {i + 1}</span>
                  <button type="button" onClick={() => setForm({ ...form, examples: form.examples.filter((_, idx) => idx !== i) })} className="text-xs text-zinc-600 hover:text-red-400">Remove</button>
                </div>
                <div className="grid gap-3 sm:grid-cols-2">
                  <Field label="Input">
                    <textarea value={ex.input} onChange={(e) => { const examples = [...form.examples]; examples[i] = { ...ex, input: e.target.value }; setForm({ ...form, examples }); }} rows={3} className={`${INPUT_CLS} resize-y font-mono text-xs`} />
                  </Field>
                  <Field label="Output">
                    <textarea value={ex.output} onChange={(e) => { const examples = [...form.examples]; examples[i] = { ...ex, output: e.target.value }; setForm({ ...form, examples }); }} rows={3} className={`${INPUT_CLS} resize-y font-mono text-xs`} />
                  </Field>
                </div>
                <div className="mt-3">
                  <Field label="Explanation (optional)">
                    <input value={ex.explanation} onChange={(e) => { const examples = [...form.examples]; examples[i] = { ...ex, explanation: e.target.value }; setForm({ ...form, examples }); }} className={INPUT_CLS} />
                  </Field>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // ── Split view (problem + editor) ──────────────────────────────────────────

  return (
    <div className="flex h-[calc(100vh-3.5rem)] flex-col overflow-hidden lg:flex-row">

      {/* ── LEFT PANEL: Problem content ───────────────────────────────────── */}
      <div className="flex w-full flex-col overflow-y-auto lg:w-[45%] lg:border-r lg:border-zinc-800">

        {/* Header */}
        <div className="sticky top-0 z-10 border-b border-zinc-800 bg-zinc-950/95 backdrop-blur px-5 py-3">
          <nav className="mb-2 flex items-center gap-2 text-xs text-zinc-600">
            <Link href="/dashboard" className="transition-colors hover:text-zinc-400">Dashboard</Link>
            <span>/</span>
            <span className="truncate max-w-[180px] text-zinc-400">{problem.title}</span>
          </nav>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h1 className="text-base font-bold text-white leading-snug">{problem.title}</h1>
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                {problem.difficulty && (
                  <span className={`rounded-full border px-2 py-0.5 text-xs font-medium capitalize ${DIFF_BADGE[problem.difficulty] ?? ""}`}>
                    {problem.difficulty}
                  </span>
                )}
                {problem.tags?.map((tag) => (
                  <span key={tag} className="rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400">{tag}</span>
                ))}
              </div>
            </div>
            <div className="flex shrink-0 items-center gap-1.5">
              <button onClick={startEdit} className="rounded border border-zinc-700 px-2.5 py-1 text-xs text-zinc-400 hover:border-zinc-500 hover:text-white transition-colors">Edit</button>
              {deletePhase === "idle" && (
                <button onClick={() => setDeletePhase("confirm")} className="rounded border border-red-900/40 px-2.5 py-1 text-xs text-red-600 hover:border-red-500/40 hover:text-red-400 transition-colors">Delete</button>
              )}
              {deletePhase === "confirm" && (
                <div className="flex items-center gap-1">
                  <button onClick={handleDelete} className="rounded bg-red-600 px-2.5 py-1 text-xs font-semibold text-white hover:bg-red-500">Confirm</button>
                  <button onClick={() => setDeletePhase("idle")} className="rounded border border-zinc-700 px-2.5 py-1 text-xs text-zinc-400 hover:text-white">Cancel</button>
                </div>
              )}
              {deletePhase === "deleting" && <span className="text-xs text-zinc-500">Deleting…</span>}
            </div>
          </div>
        </div>

        {/* Problem body */}
        <div className="flex flex-col gap-7 px-5 py-6">
          {deleteError && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">{deleteError}</div>
          )}

          <Section title="Problem Statement">
            <p className="whitespace-pre-wrap text-sm leading-7 text-zinc-300">{problem.description}</p>
          </Section>

          {(problem.input_format || problem.output_format) && (
            <div className="grid gap-5 sm:grid-cols-2">
              {problem.input_format && (
                <Section title="Input Format">
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">{problem.input_format}</p>
                </Section>
              )}
              {problem.output_format && (
                <Section title="Output Format">
                  <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-300">{problem.output_format}</p>
                </Section>
              )}
            </div>
          )}

          {problem.constraints && Object.keys(problem.constraints).length > 0 && (
            <Section title="Constraints">
              <div className="flex flex-col gap-1.5 text-sm text-zinc-300">
                {problem.constraints.time_limit && <p><span className="text-zinc-500">Time: </span>{problem.constraints.time_limit}</p>}
                {problem.constraints.memory_limit && <p><span className="text-zinc-500">Memory: </span>{problem.constraints.memory_limit}</p>}
                {problem.constraints.notes && <p className="mt-1 whitespace-pre-wrap">{problem.constraints.notes}</p>}
              </div>
            </Section>
          )}

          {problem.examples && problem.examples.length > 0 && (
            <Section title="Examples">
              <div className="flex flex-col gap-3">
                {(problem.examples as ProblemExample[]).map((ex, i) => (
                  <div key={i} className="overflow-hidden rounded-xl border border-zinc-800">
                    <div className="border-b border-zinc-800 bg-zinc-950/50 px-3 py-1.5">
                      <span className="text-xs text-zinc-500">Example {i + 1}</span>
                    </div>
                    <div className="grid divide-y divide-zinc-800 sm:grid-cols-2 sm:divide-x sm:divide-y-0">
                      <div className="p-3">
                        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500">Input</p>
                        <pre className="font-mono text-sm text-zinc-200 whitespace-pre-wrap">{ex.input}</pre>
                      </div>
                      <div className="p-3">
                        <p className="mb-1 text-xs font-medium uppercase tracking-wide text-zinc-500">Output</p>
                        <pre className="font-mono text-sm text-zinc-200 whitespace-pre-wrap">{ex.output}</pre>
                      </div>
                    </div>
                    {ex.explanation && (
                      <div className="border-t border-zinc-800 bg-zinc-950/50 px-3 py-2">
                        <p className="text-xs text-zinc-400"><span className="font-medium text-zinc-300">Explanation: </span>{ex.explanation}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </Section>
          )}

          <EdgeCasePanel problemId={problem.id} />

          <div className="border-t border-zinc-800 pt-6">
            <TestCaseList problemId={problem.id} initialTestCases={problem.test_cases ?? []} />
          </div>
        </div>
      </div>

      {/* ── RIGHT PANEL: Editor + I/O ──────────────────────────────────────── */}
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden">

        {/* Monaco editor — fills remaining height */}
        <div className="min-h-0 flex-1">
          <CodeEditor
            language={language}
            value={code}
            onChange={setCode}
            onLanguageChange={handleLanguageChange}
          />
        </div>

        {/* I/O panel — fixed height, tabbed */}
        <div className="flex shrink-0 flex-col border-t border-zinc-800 bg-zinc-950" style={{ maxHeight: "40%" }}>

          {/* Tab bar + action buttons */}
          <div className="flex items-center justify-between border-b border-zinc-800 px-3">
            <div className="flex">
              {(["input", "output", "result", "hints"] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setIoTab(tab)}
                  className={[
                    "border-b-2 px-3 py-2 text-xs font-medium capitalize transition-colors",
                    ioTab === tab
                      ? "border-violet-500 text-white"
                      : "border-transparent text-zinc-500 hover:text-zinc-300",
                  ].join(" ")}
                >
                  {tab === "hints" ? "✦ Hints" : tab}
                  {tab === "result" && submission && (
                    <span className={`ml-1.5 rounded-full px-1.5 py-0.5 text-[10px] font-bold ${
                      submission.verdict === "AC" ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                    }`}>
                      {submission.verdict}
                    </span>
                  )}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-2 py-1.5">
              <button
                onClick={handleRun}
                disabled={running || submitting}
                className="flex items-center gap-1.5 rounded-md border border-zinc-700 px-3 py-1.5 text-xs font-semibold text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {running ? <><Spinner /> Running…</> : "▶ Run"}
              </button>
              <button
                onClick={handleSubmit}
                disabled={running || submitting}
                className="flex items-center gap-1.5 rounded-md bg-violet-600 px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {submitting ? <><Spinner /> Judging…</> : "Submit →"}
              </button>
            </div>
          </div>

          {/* Tab content */}
          <div className="overflow-y-auto flex-1">
            {/* Input tab */}
            {ioTab === "input" && (
              <div className="p-4">
                <label className="mb-2 block text-xs font-medium text-zinc-500">
                  Custom Input (stdin)
                </label>
                <textarea
                  value={customInput}
                  onChange={(e) => setCustomInput(e.target.value)}
                  rows={5}
                  spellCheck={false}
                  placeholder="Enter custom input here…"
                  className="w-full resize-none rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-sm text-zinc-300 placeholder-zinc-600 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
                />
              </div>
            )}

            {/* Output tab */}
            {ioTab === "output" && (
              <>
                {running && (
                  <div className="flex items-center gap-2 p-4 text-sm text-zinc-400">
                    <Spinner /> Running code…
                  </div>
                )}
                {!running && runError && (
                  <div className="p-4 text-sm text-red-400">{runError}</div>
                )}
                {!running && !runResult && !runError && (
                  <div className="p-4 text-sm text-zinc-600">
                    Press <span className="font-medium text-zinc-400">Run</span> to execute your code.
                  </div>
                )}
                {!running && runResult && <OutputPanel result={runResult} />}
              </>
            )}

            {/* Result tab */}
            {ioTab === "result" && (
              <>
                {submitting && (
                  <div className="flex items-center gap-2 p-4 text-sm text-zinc-400">
                    <Spinner /> Judging against all test cases…
                  </div>
                )}
                {!submitting && submitError && (
                  <div className="p-4 text-sm text-red-400">{submitError}</div>
                )}
                {!submitting && !submission && !submitError && (
                  <div className="p-4 text-sm text-zinc-600">
                    Press <span className="font-medium text-zinc-400">Submit</span> to judge your code.
                  </div>
                )}
                {!submitting && submission && (
                  <>
                    <SubmissionResult submission={submission} />
                    {submission.verdict !== "AC" && (
                      <div className="px-4 pb-4">
                        <FeedbackPanel
                          problemId={problem.id}
                          language={language}
                          code={code}
                          submission={submission}
                        />
                      </div>
                    )}
                  </>
                )}
              </>
            )}

            {/* Hints tab */}
            {ioTab === "hints" && (
              <HintPanel problemId={problem.id} language={language} code={code} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── Helper sub-components ─────────────────────────────────────────────────────

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="flex flex-col gap-2.5">
      <h2 className="border-b border-zinc-800 pb-1.5 text-sm font-semibold text-white">{title}</h2>
      {children}
    </section>
  );
}

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-medium text-zinc-400">
        {label}{hint && <span className="ml-1 text-zinc-600">({hint})</span>}
      </label>
      {children}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
  );
}
