"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth";

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuthStore();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-zinc-950/90 backdrop-blur supports-[backdrop-filter]:bg-zinc-950/60">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Brand */}
        <Link
          href="/"
          className="flex items-center gap-2 font-bold text-white"
        >
          <span className="text-violet-400">⚡</span>
          <span>IntelliJudge</span>
        </Link>

        {/* Nav links */}
        <nav className="hidden items-center gap-6 text-sm text-zinc-400 sm:flex">
          {isAuthenticated && (
            <>
              <Link
                href="/dashboard"
                className="transition-colors hover:text-white"
              >
                Dashboard
              </Link>
              <Link
                href="/analytics"
                className="transition-colors hover:text-white"
              >
                Analytics
              </Link>
              <Link
                href="/upload"
                className="transition-colors hover:text-white"
              >
                Upload
              </Link>
            </>
          )}
        </nav>

        {/* Auth actions */}
        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <span className="hidden text-sm text-zinc-400 sm:block">
                {user?.username}
              </span>
              <button
                onClick={handleLogout}
                className="rounded-md border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition-colors hover:border-zinc-500 hover:text-white"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="text-sm text-zinc-400 transition-colors hover:text-white"
              >
                Sign in
              </Link>
              <Link
                href="/register"
                className="rounded-md bg-violet-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-violet-500"
              >
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
