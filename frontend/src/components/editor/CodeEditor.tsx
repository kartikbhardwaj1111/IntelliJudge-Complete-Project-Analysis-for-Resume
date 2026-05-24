"use client";

import Editor from "@monaco-editor/react";
import type { Language } from "@/types";
import { LANGUAGE_LABELS, MONACO_LANGUAGE } from "@/lib/templates";

interface CodeEditorProps {
  language: Language;
  value: string;
  onChange: (code: string) => void;
  onLanguageChange: (lang: Language) => void;
  readOnly?: boolean;
}

const LANGUAGES: Language[] = ["cpp", "java", "python", "javascript"];

export default function CodeEditor({
  language,
  value,
  onChange,
  onLanguageChange,
  readOnly = false,
}: CodeEditorProps) {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Language selector bar */}
      <div className="flex shrink-0 items-center gap-1 border-b border-zinc-800 bg-zinc-950 px-3 py-2">
        {LANGUAGES.map((lang) => (
          <button
            key={lang}
            onClick={() => onLanguageChange(lang)}
            className={[
              "rounded px-3 py-1 text-xs font-medium transition-colors",
              lang === language
                ? "bg-violet-600 text-white"
                : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200",
            ].join(" ")}
          >
            {LANGUAGE_LABELS[lang]}
          </button>
        ))}
      </div>

      {/* Monaco editor */}
      <div className="min-h-0 flex-1">
        <Editor
          height="100%"
          language={MONACO_LANGUAGE[language]}
          value={value}
          onChange={(v) => onChange(v ?? "")}
          theme="vs-dark"
          options={{
            fontSize: 14,
            fontFamily:
              "var(--font-geist-mono), 'Cascadia Code', 'Fira Code', 'JetBrains Mono', monospace",
            fontLigatures: true,
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            wordWrap: "on",
            readOnly,
            padding: { top: 12, bottom: 12 },
            lineNumbers: "on",
            renderLineHighlight: "line",
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            cursorBlinking: "smooth",
            smoothScrolling: true,
            scrollbar: {
              verticalScrollbarSize: 6,
              horizontalScrollbarSize: 6,
            },
          }}
        />
      </div>
    </div>
  );
}
