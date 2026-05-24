import Link from "next/link";

const FEATURES = [
  {
    icon: "📸",
    title: "Screenshot → Problem",
    desc: "Upload any coding question screenshot. Our OCR pipeline extracts the text instantly.",
  },
  {
    icon: "🤖",
    title: "AI Reconstruction",
    desc: "Google Gemini reads the raw text and rebuilds a clean, structured problem statement — title, examples, constraints, all of it.",
  },
  {
    icon: "💻",
    title: "Browser Code Editor",
    desc: "Solve the problem in our Monaco-powered editor. C++, Java, Python, and JavaScript all supported.",
  },
  {
    icon: "⚡",
    title: "Instant Execution",
    desc: "Code runs against real test cases via Judge0. Get a verdict — Accepted, Wrong Answer, TLE — in seconds.",
  },
  {
    icon: "💡",
    title: "AI Hints & Feedback",
    desc: "Stuck? Ask for a progressive hint. Submitted wrong? Get targeted feedback without spoiling the solution.",
  },
  {
    icon: "📊",
    title: "Track Your Progress",
    desc: "Dashboard shows your solved problems, accuracy by topic, and submission history over time.",
  },
];

const STEPS = [
  { step: "01", title: "Upload Screenshot", desc: "Drag and drop the image of your unsolved problem." },
  { step: "02", title: "AI Reconstructs It", desc: "Gemini turns the OCR output into a proper problem statement in seconds." },
  { step: "03", title: "Write Your Solution", desc: "Use the Monaco editor with syntax highlighting and multi-language support." },
  { step: "04", title: "Submit & Get Verdict", desc: "Judge0 runs your code against test cases and tells you if you passed." },
];

export default function LandingPage() {
  return (
    <div className="flex flex-col">
      {/* Hero */}
      <section className="flex flex-col items-center justify-center gap-6 px-4 py-28 text-center sm:py-36">
        <span className="inline-flex items-center gap-2 rounded-full border border-violet-500/30 bg-violet-500/10 px-4 py-1.5 text-sm font-medium text-violet-300">
          <span className="h-1.5 w-1.5 rounded-full bg-violet-400" />
          AI-Powered Coding Practice
        </span>

        <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-white sm:text-6xl">
          Never lose a{" "}
          <span className="bg-linear-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">
            coding problem
          </span>{" "}
          again
        </h1>

        <p className="max-w-xl text-lg text-zinc-400">
          Upload a screenshot, let AI rebuild the full problem statement, then
          solve it in your browser with instant test-case feedback.
        </p>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Link
            href="/register"
            className="rounded-lg bg-violet-600 px-6 py-3 text-base font-semibold text-white transition-colors hover:bg-violet-500"
          >
            Get started free →
          </Link>
          <Link
            href="/login"
            className="rounded-lg border border-zinc-700 px-6 py-3 text-base font-semibold text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
          >
            Sign in
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="border-y border-zinc-800 bg-zinc-900/50 px-4 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-12 text-center text-3xl font-bold text-white">
            How it works
          </h2>
          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map(({ step, title, desc }) => (
              <div key={step} className="flex flex-col gap-3">
                <span className="text-4xl font-black text-violet-500/40">
                  {step}
                </span>
                <h3 className="font-semibold text-white">{title}</h3>
                <p className="text-sm text-zinc-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-4 py-20">
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-12 text-center text-3xl font-bold text-white">
            Everything you need to practice
          </h2>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {FEATURES.map(({ icon, title, desc }) => (
              <div
                key={title}
                className="rounded-xl border border-zinc-800 bg-zinc-900 p-6 transition-colors hover:border-zinc-700"
              >
                <div className="mb-3 text-2xl">{icon}</div>
                <h3 className="mb-2 font-semibold text-white">{title}</h3>
                <p className="text-sm text-zinc-400">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-zinc-800 px-4 py-20 text-center">
        <h2 className="mb-4 text-3xl font-bold text-white">
          Ready to start practicing?
        </h2>
        <p className="mb-8 text-zinc-400">
          Free to use. No credit card required.
        </p>
        <Link
          href="/register"
          className="inline-flex rounded-lg bg-violet-600 px-8 py-3 text-base font-semibold text-white transition-colors hover:bg-violet-500"
        >
          Create your account →
        </Link>
      </section>
    </div>
  );
}
