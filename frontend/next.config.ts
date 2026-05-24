/**
 * Vercel Next.js Configuration
 * 
 * This configuration optimizes the frontend for Vercel deployment
 * with proper image optimization, redirects, and headers.
 */

import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* ── Image Optimization ────────────────────────────────────── */

  images: {
    remotePatterns: [
      { protocol: "http", hostname: "localhost" },
      { protocol: "https", hostname: "res.cloudinary.com" },
    ],
    formats: ["image/avif", "image/webp"],
  },

  /* ── Headers for Security & Performance ────────────────────── */
  
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Prevent clickjacking
          {
            key: "X-Frame-Options",
            value: "SAMEORIGIN",
          },
          // Disable MIME type sniffing
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          // Enable XSS protection
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
          // Referrer policy
          {
            key: "Referrer-Policy",
            value: "strict-origin-when-cross-origin",
          },
          // Cache control for static assets
          {
            key: "Cache-Control",
            value: "public, max-age=3600, must-revalidate",
          },
        ],
      },
    ];
  },

  /* ── Redirects & Rewrites ──────────────────────────────────── */
  
  async redirects() {
    return [
      // Redirect /index to root
      {
        source: "/index",
        destination: "/",
        permanent: true,
      },
    ];
  },

  /* ── Environment Variables in Build ────────────────────────── */
  
  env: {
    // NEXT_PUBLIC_* variables are exposed to the browser
    // Set these in Vercel project settings
    NEXT_PUBLIC_APP_VERSION: "0.1.0",
  },

  /* ── Experimental Features ──────────────────────────────────– */
  
  experimental: {
    // Enable optimized package imports
    optimizePackageImports: ["recharts"],
  },
};

export default nextConfig;
