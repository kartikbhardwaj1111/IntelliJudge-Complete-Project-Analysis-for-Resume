"use client";

import { useState } from "react";
import Link from "next/link";
import DropZone from "@/components/upload/DropZone";
import { api, ApiError } from "@/lib/api";
import type { Problem, UploadResult } from "@/types";

type Step = "upload" | "review" | "done";

const DIFFICULTY_BADGE: Record<string, string> = {
  easy: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
  medium: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  hard: "bg-red-500/15 text-red-400 border-red-500/30",
};

const STEP_LABELS: Record<Step, string> = {
  upload: "Upload",
  review: "Review OCR",
  done: "Done",
};

const STEPS: Step[] = ["upload", "review", "done"];

export default function UploadPage() {
  const [step, setStep] = useState<Step>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [ocrText, setOcrText] = useState("");
  const [problem, setProblem] = useState<Problem | null>(null);

  const [uploading, setUploading] = useState(false);
  const [reconstructing, setReconstructing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // ── Step 1: upload screenshot → extract OCR ─────────────────────────────
  async function handleUpload() {
    if (!file) return;
    setError(null);
    setUploading(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await api.post<UploadResult>("/upload/screenshot", form);
      setUploadResult(result);
      setOcrText(result.ocr_text);
      setStep("review");
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Upload failed. Please try again."
      );
    } finally {
      setUploading(false);
    }
  }

  // ── Step 2: send OCR text to AI → get structured problem ────────────────
  async function handleReconstruct() {
    if (!uploadResult) return;
    setError(null);
    setReconstructing(true);
    try {
      // If the user edited the OCR text, pass it as an override so Gemini
      // uses the corrected version instead of the stored one.
      const ocr_text_override =
        ocrText.trim() !== uploadResult.ocr_text.trim() ? ocrText : undefined;

      const reconstructed = await api.post<Problem>("/problems/reconstruct", {
        problem_id: uploadResult.problem_id,
        ocr_text_override,
      });
      setProblem(reconstructed);
      setStep("done");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "AI reconstruction failed. Please try again."
      );
    } finally {
      setReconstructing(false);
    }
  }

  // ── Step indicator ───────────────────────────────────────────────────────
  const currentIndex = STEPS.indexOf(step);

  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-10">
      {/* Breadcrumb */}
      <nav className="mb-8 flex items-center gap-2 text-sm text-zinc-500">
        <Link href="/dashboard" className="transition-colors hover:text-zinc-300">
          Dashboard
        </Link>
        <span>/</span>
        <span className="text-zinc-300">Upload Problem</span>
      </nav>

      {/* Step indicator */}
      <div className="mb-10 flex items-center gap-1">
        {STEPS.map((s, i) => {
          const isPast = i < currentIndex;
          const isCurrent = i === currentIndex;
          return (
            <div key={s} className="flex items-center gap-1">
              {i > 0 && (
                <div
                  className={`h-px w-10 transition-colors ${
                    isPast || isCurrent ? "bg-violet-600" : "bg-zinc-800"
                  }`}
                />
              )}
              <div
                className={`flex items-center gap-2 ${
                  isCurrent
                    ? "text-white"
                    : isPast
                    ? "text-violet-400"
                    : "text-zinc-600"
                }`}
              >
                <div
                  className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold transition-colors ${
                    isCurrent
                      ? "bg-violet-600 text-white"
                      : isPast
                      ? "bg-violet-500/20 text-violet-400"
                      : "bg-zinc-800 text-zinc-600"
                  }`}
                >
                  {isPast ? "✓" : i + 1}
                </div>
                <span className="hidden text-sm font-medium sm:block">
                  {STEP_LABELS[s]}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Step 1: Upload ─────────────────────────────────────────────── */}
      {step === "upload" && (
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-xl font-bold text-white">
              Upload a screenshot
            </h1>
            <p className="mt-1 text-sm text-zinc-400">
              Drop a screenshot of any coding problem. AI will extract the text
              and reconstruct the full problem statement for you.
            </p>
          </div>

          <DropZone onFileSelect={setFile} disabled={uploading} />

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="flex items-center justify-center gap-2 rounded-lg bg-violet-600 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {uploading ? (
              <>
                <Spinner />
                <span className="flex flex-col items-center gap-0.5">
                  <span>Uploading &amp; extracting text&hellip;</span>
                  <span className="text-xs font-normal opacity-70">
                    First run loads OCR model (~60s). Subsequent uploads are fast.
                  </span>
                </span>
              </>
            ) : (
              "Upload & Extract Text →"
            )}
          </button>
        </div>
      )}

      {/* ── Step 2: Review OCR ─────────────────────────────────────────── */}
      {step === "review" && uploadResult && (
        <div className="flex flex-col gap-6">
          <div>
            <h1 className="text-xl font-bold text-white">Review extracted text</h1>
            <p className="mt-1 text-sm text-zinc-400">
              OCR extracted{" "}
              <span className="font-medium text-zinc-300">
                {uploadResult.text_length} characters
              </span>
              . Correct any OCR errors before sending to AI.
            </p>
          </div>

          {/* Screenshot preview */}
          {uploadResult.screenshot_url && (
            <div className="overflow-hidden rounded-xl border border-zinc-800">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={uploadResult.screenshot_url}
                alt="Uploaded screenshot"
                className="max-h-72 w-full object-contain bg-zinc-900"
              />
            </div>
          )}

          {/* Editable OCR output */}
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-zinc-300">
              Extracted text{" "}
              <span className="text-zinc-500">(edit if OCR made mistakes)</span>
            </label>
            <textarea
              value={ocrText}
              onChange={(e) => setOcrText(e.target.value)}
              rows={12}
              spellCheck={false}
              className="w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-4 py-3 font-mono text-sm text-zinc-200 placeholder-zinc-600 focus:border-violet-500 focus:outline-none focus:ring-1 focus:ring-violet-500"
              placeholder="OCR text will appear here…"
            />
          </div>

          {error && (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {error}
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => {
                setStep("upload");
                setError(null);
              }}
              disabled={reconstructing}
              className="rounded-lg border border-zinc-700 px-4 py-2.5 text-sm text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white disabled:opacity-50"
            >
              ← Back
            </button>
            <button
              onClick={handleReconstruct}
              disabled={!ocrText.trim() || reconstructing}
              className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-violet-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {reconstructing ? (
                <>
                  <Spinner />
                  AI is analyzing&hellip; (5–10s)
                </>
              ) : (
                "Reconstruct with AI →"
              )}
            </button>
          </div>
        </div>
      )}

      {/* ── Step 3: Done ───────────────────────────────────────────────── */}
      {step === "done" && problem && (
        <div className="flex flex-col items-center gap-6 py-8 text-center">
          <div className="text-6xl">🎉</div>

          <div>
            <h1 className="text-xl font-bold text-white">
              Problem reconstructed!
            </h1>
            <p className="mx-auto mt-2 max-w-sm text-sm text-zinc-400">
              AI parsed your screenshot into a structured problem. You can view
              it, correct any mistakes, and generate test cases.
            </p>
          </div>

          {/* Problem preview card */}
          <div className="w-full rounded-xl border border-zinc-800 bg-zinc-900 p-5 text-left">
            <p className="mb-1 text-xs uppercase tracking-wide text-zinc-500">
              Problem title
            </p>
            <p className="font-semibold text-white">{problem.title}</p>
            {problem.difficulty && (
              <span
                className={`mt-3 inline-block rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize ${
                  DIFFICULTY_BADGE[problem.difficulty] ?? ""
                }`}
              >
                {problem.difficulty}
              </span>
            )}
            {problem.tags && problem.tags.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {problem.tags.slice(0, 5).map((tag) => (
                  <span
                    key={tag}
                    className="rounded-md bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="flex w-full gap-3">
            <Link
              href="/dashboard"
              className="flex-1 rounded-lg border border-zinc-700 px-4 py-2.5 text-center text-sm text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
            >
              Dashboard
            </Link>
            <Link
              href={`/problem/${problem.id}`}
              className="flex-1 rounded-lg bg-violet-600 px-4 py-2.5 text-center text-sm font-semibold text-white transition-colors hover:bg-violet-500"
            >
              View Problem →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg
      className="h-4 w-4 animate-spin"
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
