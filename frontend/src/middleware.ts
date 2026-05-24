/**
 * Next.js Middleware — Auth Route Guard
 *
 * Runs on every request before the page renders (edge runtime).
 * Protects all routes under /dashboard, /upload, /problem by redirecting
 * unauthenticated users to /login.
 *
 * HOW TOKEN DETECTION WORKS:
 *   Zustand persist stores the auth state in localStorage as JSON under the
 *   key "ij-auth". Middleware runs on the server/edge and cannot access
 *   localStorage directly. Instead we check for the presence of the token
 *   in a cookie named "ij_token" that we set from the client after login.
 *
 *   Because this is a learning project and the token is also stored in
 *   localStorage (via tokenStore), we use a lightweight cookie-based
 *   check here. The client sets this cookie in the Zustand store on login.
 */

import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PREFIXES = ["/dashboard", "/upload", "/problem"];
const AUTH_ROUTES = ["/login", "/register"];

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;

  const isProtected = PROTECTED_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  );
  const isAuthRoute = AUTH_ROUTES.some((r) => pathname.startsWith(r));

  // Read token from cookie (set by the client after login)
  const token = req.cookies.get("ij_token")?.value;

  if (isProtected && !token) {
    const loginUrl = new URL("/login", req.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If already logged in, redirect away from auth pages
  if (isAuthRoute && token) {
    return NextResponse.redirect(new URL("/dashboard", req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/upload/:path*",
    "/problem/:path*",
    "/login",
    "/register",
  ],
};
