"use client";

import { useRef, useState } from "react";

interface DropZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  maxSizeMB?: number;
}

const ALLOWED_TYPES = [
  "image/jpeg",
  "image/png",
  "image/gif",
  "image/bmp",
  "image/webp",
  "image/tiff",
];

export default function DropZone({
  onFileSelect,
  disabled = false,
  maxSizeMB = 10,
}: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [selected, setSelected] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  function validate(file: File): string | null {
    if (!ALLOWED_TYPES.includes(file.type))
      return "Unsupported file type. Use JPEG, PNG, GIF, BMP, WEBP or TIFF.";
    if (file.size > maxSizeMB * 1024 * 1024)
      return `File exceeds ${maxSizeMB} MB limit.`;
    return null;
  }

  function accept(file: File) {
    const err = validate(file);
    if (err) {
      setError(err);
      return;
    }
    setError(null);
    setSelected(file);
    onFileSelect(file);
  }

  function onDragOver(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  }

  function onDragLeave() {
    setIsDragging(false);
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;
    const file = e.dataTransfer.files[0];
    if (file) accept(file);
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) accept(file);
    // Reset so the same file can be re-selected after an error
    e.target.value = "";
  }

  const containerClass = [
    "relative flex flex-col items-center justify-center gap-4 rounded-2xl border-2 border-dashed p-12 text-center transition-all",
    disabled
      ? "cursor-not-allowed border-zinc-800 bg-zinc-900/40 opacity-60"
      : isDragging
      ? "cursor-copy border-violet-500 bg-violet-500/10 scale-[1.01]"
      : selected
      ? "cursor-pointer border-emerald-500/50 bg-emerald-500/5 hover:border-emerald-500/70"
      : "cursor-pointer border-zinc-700 bg-zinc-900 hover:border-zinc-500 hover:bg-zinc-900/80",
  ].join(" ");

  return (
    <div
      className={containerClass}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={() => !disabled && inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ALLOWED_TYPES.join(",")}
        className="sr-only"
        onChange={onInputChange}
        disabled={disabled}
      />

      {selected ? (
        <>
          <div className="text-5xl">✅</div>
          <div>
            <p className="font-semibold text-emerald-400">{selected.name}</p>
            <p className="mt-1 text-sm text-zinc-500">
              {(selected.size / 1024 / 1024).toFixed(2)} MB &mdash; click to change
            </p>
          </div>
        </>
      ) : (
        <>
          <div className="text-5xl">{isDragging ? "📂" : "📸"}</div>
          <div>
            <p className="text-base font-semibold text-zinc-200">
              {isDragging ? "Drop it here" : "Drag & drop your screenshot"}
            </p>
            <p className="mt-1 text-sm text-zinc-500">
              or click to browse &mdash; JPEG, PNG, GIF, BMP, WEBP up to {maxSizeMB}&nbsp;MB
            </p>
          </div>
        </>
      )}

      {error && (
        <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-400">
          {error}
        </p>
      )}
    </div>
  );
}
