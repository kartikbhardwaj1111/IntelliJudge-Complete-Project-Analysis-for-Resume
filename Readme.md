<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,50:8b5cf6,100:06b6d4&height=260&section=header&text=IntelliJudge&fontSize=88&animation=fadeIn&fontColor=ffffff&fontAlignY=42&desc=AI-Powered%20Coding%20Question%20Recovery%20%26%20Practice%20Platform&descAlignY=68&descSize=19" width="100%"/>

<br/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=20&pause=1200&color=6366F1&background=FFFFFF00&center=true&vCenter=true&repeat=true&width=750&height=50&lines=📸+Upload+Screenshot+→+🤖+AI+Reconstructs+Problem;💻+Monaco+Editor+with+Live+Code+Execution;✨+AI+Hints+%26+Feedback+on+Wrong+Answers;📊+Analytics+Dashboard+for+Progress+Tracking;🚀+FastAPI+%2B+Next.js+16+%2B+PostgreSQL+%2B+Groq+AI)](https://github.com/kartikbhardwaj1111/IntelliJudge-Complete-Project-Analysis-for-Resume)

<br/>

[![Next.js](https://img.shields.io/badge/Next.js_16-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)

<br/>

![GitHub repo size](https://img.shields.io/github/repo-size/kartikbhardwaj1111/IntelliJudge-Complete-Project-Analysis-for-Resume?style=flat-square&color=6366f1&label=Repo%20Size)
![GitHub last commit](https://img.shields.io/github/last-commit/kartikbhardwaj1111/IntelliJudge-Complete-Project-Analysis-for-Resume?style=flat-square&color=8b5cf6&label=Last%20Commit)
![GitHub stars](https://img.shields.io/github/stars/kartikbhardwaj1111/IntelliJudge-Complete-Project-Analysis-for-Resume?style=flat-square&color=06b6d4&label=Stars)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

<br/>

[🎯 Features](#-features) · [⚙️ How It Works](#%EF%B8%8F-how-it-works) · [🏗️ Architecture](#%EF%B8%8F-architecture) · [🚀 Getting Started](#-getting-started) · [📡 API Reference](#-api-reference) · [🚢 Deployment](#-deployment)

<br/>

> **Recover coding questions from screenshots. Reconstruct. Practice. Master.**
>
> *Built for students and competitive programmers who want to revisit unsolved problems from exams, contests, and coding rounds.*

</div>

---

## 🎯 The Problem

Every competitive programmer knows this frustration:

```
You're in an online assessment or contest. Time runs out.
Later, all you have is a screenshot of the problem.
No way to reconstruct it. No test cases. No practice environment.
```

**IntelliJudge eliminates this problem entirely.**

```
📸 Upload Screenshot  →  🔍 OCR Extraction  →  🤖 AI Reconstruction  →  💻 Code & Judge  →  📊 Analytics
```

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### 🧠 AI-Powered Core
- **Screenshot → Problem** — Upload any exam screenshot and get a fully structured problem with title, constraints, examples, difficulty, and topic tags
- **Smart OCR Pipeline** — EasyOCR extraction + AI-powered text cleanup handles messy layouts, rotated text, and multi-column screenshots
- **Groq / Llama 3.3 Reconstruction** — Converts raw OCR output into clean structured JSON with auto-classification
- **Auto Test Case Generation** — AI generates sample, hidden, edge, and stress test categories instantly

</td>
<td width="50%" valign="top">

### 💻 Code Execution Engine
- **Monaco Code Editor** — Full VS Code engine in-browser with IntelliSense and language-specific starter templates
- **Piston API Sandbox** — Free, open sandboxed execution for C++, Java, Python, and JavaScript
- **Competitive Verdict System** — AC / WA / TLE / MLE / RE / CE with per-test-case detail and diff view on WA
- **AI Feedback on Wrong Answers** — Targeted hints and missed edge-case analysis without spoiling the solution

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔐 Secure & Scalable
- **JWT + bcrypt Auth** — Stateless token-based authentication with bcrypt password hashing (12 salt rounds)
- **Fully Async** — FastAPI + SQLAlchemy async + asyncpg — zero blocking I/O from endpoint to database
- **Cloud-Native Stack** — Cloudinary CDN for screenshots, Neon serverless PostgreSQL, Vercel + Railway deploy
- **End-to-End Type Safety** — TypeScript strict mode on frontend, Pydantic validation on all backend endpoints

</td>
<td width="50%" valign="top">

### 📊 Analytics & Insights
- **Progress Dashboard** — Topic-wise accuracy, difficulty distribution, and language usage breakdown
- **Submission Trends** — Time-series charts of your solving activity over 7 / 30 / 90 days
- **Performance Metrics** — Success rate, total problems solved, average verdict per language
- **Recharts Visualizations** — Interactive charts: bar, line, pie, and area graphs powered by Recharts

</td>
</tr>
</table>

---

## ⚙️ How It Works

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                         IntelliJudge — Full Pipeline                          ║
╠════════════╦══════════════╦══════════════╦═════════════════╦══════════════════╣
║  📸 Upload ║  🔍 Extract  ║ 🤖 Reconstruct║  💻 Code + Run  ║  📊 Track        ║
╠════════════╬══════════════╬══════════════╬═════════════════╬══════════════════╣
║ Drag-drop  ║  EasyOCR     ║ Groq / Llama ║  Monaco Editor  ║  Analytics       ║
║ screenshot ║  extraction  ║ 3.3 70B →    ║  + Piston API   ║  Dashboard       ║
║ to         ║  + AI text   ║ structured   ║  sandboxed      ║  with charts     ║
║ Cloudinary ║  cleanup     ║ JSON problem ║  execution      ║  & trends        ║
╚════════════╩══════════════╩══════════════╩═════════════════╩══════════════════╝
```

| Step | Action | Technology Used |
|:---:|---|---|
| **1** | 📸 Upload a screenshot of any coding question | Drag-and-drop UI → Cloudinary CDN |
| **2** | 🔍 Extract text from the image with OCR | EasyOCR + AI-powered text cleanup |
| **3** | 🤖 Reconstruct the full problem with AI | Groq API — Llama 3.3 70B |
| **4** | 💻 Write your solution in Monaco Editor | VS Code engine, 4 languages, code templates |
| **5** | ⚡ Execute code against all test cases | Piston API — free sandboxed runner |
| **6** | 💡 Get AI feedback if you get a wrong answer | Groq AI hints, edge-case analysis |
| **7** | 📊 Track your progress over time | Recharts analytics dashboard |

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Frontend — Next.js 16 + TypeScript"]
        Landing["Landing Page"]
        Dashboard["Dashboard"]
        Editor["Monaco Editor"]
        Upload["Upload Flow (3-step)"]
        Analytics["Analytics Dashboard"]
    end

    subgraph API["⚙️ API Layer — FastAPI"]
        AuthR["Auth Routes\n/api/auth"]
        ProbR["Problem Routes\n/api/problems"]
        SubR["Submission Routes\n/api/submissions"]
        UploadR["Upload Routes\n/api/upload"]
        AIR["AI Routes\n/api/ai"]
        AnalR["Analytics Routes\n/api/analytics"]
    end

    subgraph Services["🔧 Service Layer (Business Logic)"]
        AuthSvc["AuthService\nbcrypt + JWT"]
        OCRSvc["OCRService\nEasyOCR"]
        AISvc["AIService\nGroq/Llama"]
        CompSvc["CompilerService\nPiston API"]
        ValSvc["ValidationService\nVerdict Engine"]
        AnasSvc["AnalyticsService\nStats + Trends"]
    end

    subgraph External["☁️ External Services"]
        Groq["Groq API\nLlama 3.3 70B"]
        Piston["Piston API\nSandboxed Execution"]
        Cloudinary["Cloudinary\nImage CDN"]
    end

    subgraph Data["💾 Data Layer — PostgreSQL (Neon)"]
        Users[("users")]
        Problems[("problems")]
        TestCases[("test_cases")]
        Submissions[("submissions")]
    end

    Client -->|HTTP REST| API
    AuthR --> AuthSvc
    ProbR --> AISvc & OCRSvc
    SubR --> CompSvc & ValSvc
    UploadR --> OCRSvc
    AIR --> AISvc
    AnalR --> AnasSvc

    AISvc --> Groq
    CompSvc --> Piston
    OCRSvc --> Cloudinary

    AuthSvc --> Users
    AISvc --> Problems & TestCases
    ValSvc --> Submissions
    AnasSvc --> Submissions & Problems
```

### Database Schema

```mermaid
erDiagram
    USERS ||--o{ PROBLEMS : creates
    USERS ||--o{ SUBMISSIONS : makes
    PROBLEMS ||--o{ TEST_CASES : has
    PROBLEMS ||--o{ SUBMISSIONS : receives

    USERS {
        uuid id PK
        string email UK
        string username UK
        string password_hash
        timestamp created_at
        timestamp updated_at
    }

    PROBLEMS {
        uuid id PK
        uuid user_id FK
        string title
        text description
        text input_format
        text output_format
        jsonb constraints
        jsonb examples
        string difficulty
        jsonb tags
        string screenshot_url
        timestamp created_at
    }

    TEST_CASES {
        uuid id PK
        uuid problem_id FK
        text input
        text expected_output
        string category
        boolean is_visible
        timestamp created_at
    }

    SUBMISSIONS {
        uuid id PK
        uuid user_id FK
        uuid problem_id FK
        string language
        text code
        string verdict
        integer runtime_ms
        integer memory_kb
        integer test_cases_passed
        integer total_test_cases
        jsonb results
        timestamp created_at
    }
```

---

## 🛠️ Tech Stack

<div align="center">

**Frontend**

<img src="https://skillicons.dev/icons?i=nextjs,ts,tailwind,react&theme=dark" />

**Backend & Database**

<img src="https://skillicons.dev/icons?i=python,fastapi,postgresql,docker&theme=dark" />

**Cloud & DevOps**

<img src="https://skillicons.dev/icons?i=vercel,github,vscode,linux&theme=dark" />

</div>

<br/>

| Layer | Technology | Version | Purpose |
|---|---|:---:|---|
| **Frontend Framework** | Next.js | 16 | SSR, App Router, file-based routing |
| **Language (Frontend)** | TypeScript | 5.x | Full type safety across the codebase |
| **Styling** | Tailwind CSS | v4 | Utility-first responsive UI design |
| **Code Editor** | Monaco Editor | 4.7 | VS Code engine — syntax highlighting + IntelliSense |
| **Charts** | Recharts | 3.x | Analytics data visualization |
| **State Management** | Zustand | 5.x | Lightweight global auth + app state |
| **Backend Framework** | FastAPI | 0.115 | Async REST API with auto-generated Swagger docs |
| **Language (Backend)** | Python | 3.11+ | All backend services and AI integrations |
| **ORM** | SQLAlchemy | 2.0 | Async ORM with full type support |
| **Migrations** | Alembic | 1.15 | Version-controlled database schema changes |
| **Database** | PostgreSQL (Neon) | 15+ | Serverless relational datastore with JSONB |
| **OCR Engine** | EasyOCR | 1.7 | Screenshot text extraction (no API key needed) |
| **AI Engine** | Groq / Llama 3.3 | 70B | Problem reconstruction, hints, feedback |
| **Code Execution** | Piston API | v2 | Free, open sandboxed multi-language runner |
| **Image Storage** | Cloudinary | — | CDN-backed screenshot hosting + auto-optimize |
| **Authentication** | JWT + bcrypt | — | Stateless token auth with secure password hashing |
| **Deployment** | Vercel + Railway | — | Frontend on Vercel, backend on Railway (Docker) |

---

## ⚡ Verdict System

<div align="center">

| Verdict | Symbol | Description | Priority |
|:---:|:---:|---|:---:|
| **Accepted** | `✅ AC` | All test cases passed | 6 (lowest) |
| **Wrong Answer** | `❌ WA` | Output differs from expected | 5 |
| **Time Limit Exceeded** | `⏱️ TLE` | Execution exceeded time limit | 4 |
| **Memory Limit Exceeded** | `💾 MLE` | Memory usage exceeded limit | 3 |
| **Runtime Error** | `💥 RE` | Crash, segfault, or unhandled exception | 2 |
| **Compilation Error** | `🔧 CE` | Code failed to compile | 1 (highest) |

**Overall Verdict Priority:** `CE` › `RE` › `TLE` › `MLE` › `WA` › `AC`

*On Compilation Error, remaining test cases are skipped immediately.*

</div>

---

## 🌐 Supported Languages

<div align="center">

<img src="https://skillicons.dev/icons?i=cpp,java,python,js&theme=dark" />

| Language | Runtime | Starter Template |
|---|---|:---:|
| C++ | C++17 | ✅ |
| Java | Java 17 | ✅ |
| Python | Python 3.x | ✅ |
| JavaScript | Node.js | ✅ |

</div>

---

## 📁 Project Structure

```
IntelliJudge/
│
├── 📂 frontend/                         # Next.js 16 application
│   ├── src/
│   │   ├── 📂 app/                      # App Router pages
│   │   │   ├── (auth)/login/            # ├── Login page
│   │   │   ├── (auth)/register/         # ├── Register page
│   │   │   ├── dashboard/               # ├── Problem feed with filters
│   │   │   ├── problem/[id]/            # ├── Problem detail + Monaco editor
│   │   │   ├── upload/                  # ├── 3-step screenshot upload flow
│   │   │   └── analytics/              # └── Progress charts dashboard
│   │   ├── 📂 components/
│   │   │   ├── editor/                  # Monaco editor + I/O output panel
│   │   │   ├── upload/                  # Drag-and-drop DropZone
│   │   │   ├── problem/                 # ProblemCard, TestCaseList, SubmissionResult
│   │   │   ├── ai/                      # HintPanel, FeedbackPanel, EdgeCasePanel
│   │   │   ├── analytics/               # StatsCard, DifficultyChart, TrendChart
│   │   │   └── layout/                  # Navbar
│   │   ├── 📂 lib/                      # API client (fetch wrapper) + code templates
│   │   ├── 📂 stores/                   # Zustand auth store with cookie sync
│   │   └── 📂 types/                    # Shared TypeScript interfaces
│   ├── next.config.ts                   # Image remotePatterns, security headers
│   ├── vercel.json                      # Vercel deployment configuration
│   └── package.json
│
├── 📂 backend/                          # FastAPI application
│   ├── app/
│   │   ├── main.py                      # App entry point, CORS, exception handlers, lifespan
│   │   ├── config.py                    # Pydantic Settings — loads all env vars
│   │   ├── database.py                  # Async SQLAlchemy engine + session factory
│   │   ├── 📂 models/                   # SQLAlchemy ORM table definitions
│   │   │   ├── user.py                  # User model with relationships
│   │   │   ├── problem.py               # Problem model (JSONB fields)
│   │   │   ├── test_case.py             # TestCase model with category enum
│   │   │   └── submission.py            # Submission with JSONB results
│   │   ├── 📂 schemas/                  # Pydantic request / response models
│   │   ├── 📂 routes/                   # API route handlers
│   │   │   ├── auth.py                  # Register, Login, /me
│   │   │   ├── problems.py              # CRUD + AI reconstruct + test case gen
│   │   │   ├── submissions.py           # Run (no-DB) + Submit (full judge)
│   │   │   ├── upload.py                # Screenshot upload → OCR
│   │   │   ├── ai.py                    # Hints, feedback, edge cases, optimize
│   │   │   └── analytics.py            # Overview, topics, trends, history
│   │   ├── 📂 services/                 # Pure business logic (no HTTP concerns)
│   │   │   ├── auth_service.py          # bcrypt hash + JWT sign/verify
│   │   │   ├── ocr_service.py           # EasyOCR reader (cached singleton)
│   │   │   ├── ai_service.py            # Groq client — reconstruct + test-gen
│   │   │   ├── compiler_service.py      # Piston API wrapper + base64 codec
│   │   │   ├── validation_service.py    # Verdict computation + output diff
│   │   │   └── analytics_service.py     # Stats aggregation queries
│   │   ├── 📂 utils/                    # JWT helpers, bcrypt, exceptions, rate limiter
│   │   └── 📂 migrations/              # Alembic version history
│   ├── requirements.txt
│   ├── Dockerfile                       # Multi-stage Railway deploy image
│   └── .env.example
│
├── railway.json                         # Railway backend service configuration
├── judge0-compose.yml                   # Optional local Judge0 Docker setup
└── README.md
```

---

## 📦 Getting Started

### Prerequisites

| Requirement | Version | Get It |
|---|---|---|
| Node.js | ≥ 18.x | [nodejs.org](https://nodejs.org/) |
| Python | ≥ 3.11 | [python.org](https://www.python.org/) |
| PostgreSQL | ≥ 15 | Local or free at [neon.tech](https://neon.tech/) |
| Groq API Key | Free | [console.groq.com](https://console.groq.com/) |
| Cloudinary Account | Free | [cloudinary.com](https://cloudinary.com/) |

### 1 · Clone

```bash
git clone https://github.com/kartikbhardwaj1111/IntelliJudge-Complete-Project-Analysis-for-Resume.git
cd IntelliJudge-Complete-Project-Analysis-for-Resume
```

### 2 · Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# Install all dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Open .env and fill in your credentials (see section below)

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --port 8000
```

> **Backend running at:** `http://localhost:8000`
> **Swagger API docs at:** `http://localhost:8000/docs`

### 3 · Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env.local
# Set: NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Start the development server
npm run dev
```

> **Frontend running at:** `http://localhost:3000`

### 4 · Environment Variables

<details>
<summary><b>📄 backend/.env — click to expand</b></summary>

```env
# Application
APP_NAME=IntelliJudge
APP_VERSION=0.1.0
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000

# CORS (add your frontend URL)
CORS_ORIGINS=["http://localhost:3000"]

# Database — get from Neon or use local PostgreSQL
# Select the "asyncpg" driver in Neon connection details
DATABASE_URL=postgresql+asyncpg://user:password@host/intellijudge

# Auth — generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=your-super-secret-key-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

# Groq AI (free at console.groq.com)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Cloudinary (free at cloudinary.com → Dashboard)
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

</details>

<details>
<summary><b>📄 frontend/.env.local — click to expand</b></summary>

```env
# URL of your running FastAPI backend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

</details>

---

## 📡 API Reference

<details>
<summary><b>🔐 Authentication</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/auth/register` | Register new user | ❌ |
| `POST` | `/api/auth/login` | Login — returns JWT token | ❌ |
| `GET` | `/api/auth/me` | Get current user profile | ✅ |

</details>

<details>
<summary><b>📸 Upload & OCR</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/upload/screenshot` | Upload screenshot → Cloudinary → EasyOCR | ✅ |

</details>

<details>
<summary><b>📝 Problems</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/problems/reconstruct` | AI-reconstruct problem from OCR text | ✅ |
| `GET` | `/api/problems` | List problems (paginated, filter by difficulty/tag/search) | ✅ |
| `GET` | `/api/problems/{id}` | Get full problem with test cases | ✅ |
| `PUT` | `/api/problems/{id}` | Edit problem fields | ✅ |
| `DELETE` | `/api/problems/{id}` | Delete problem | ✅ |
| `POST` | `/api/problems/{id}/generate-tests` | AI-generate test cases | ✅ |
| `GET` | `/api/problems/{id}/test-cases` | List test cases | ✅ |
| `POST` | `/api/problems/{id}/test-cases` | Add custom test case | ✅ |
| `DELETE` | `/api/problems/{id}/test-cases/{tc_id}` | Delete test case | ✅ |

</details>

<details>
<summary><b>⚡ Code Execution</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/submissions/run` | Run code with custom stdin (no DB write) | ✅ |
| `POST` | `/api/submissions/submit` | Submit — judge all test cases + store result | ✅ |
| `GET` | `/api/submissions/{id}` | Get full submission result with per-case verdicts | ✅ |

</details>

<details>
<summary><b>💡 AI Features</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/ai/feedback` | AI feedback on wrong answer submission | ✅ |
| `POST` | `/api/ai/hints` | Progressive hints (level 1 → 3) | ✅ |
| `POST` | `/api/ai/edge-cases` | Edge case analysis for a problem | ✅ |
| `POST` | `/api/ai/optimize` | Complexity optimization suggestions | ✅ |

</details>

<details>
<summary><b>📊 Analytics</b></summary>

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `GET` | `/api/analytics/overview` | Summary stats — total, accepted, rate, streak | ✅ |
| `GET` | `/api/analytics/topics` | Topic-wise accuracy breakdown | ✅ |
| `GET` | `/api/analytics/submissions` | Paginated submission history | ✅ |
| `GET` | `/api/analytics/trends` | Daily submission counts over time | ✅ |

</details>

---

## 🚢 Deployment

<div align="center">

| Service | Platform | Config | Auto-Deploy |
|---|---|---|:---:|
| **Frontend** | [Vercel](https://vercel.com/) | `frontend/vercel.json` | ✅ from `main` |
| **Backend** | [Railway](https://railway.app/) | `railway.json` + `Dockerfile` | ✅ from `main` |
| **Database** | [Neon](https://neon.tech/) | Env var `DATABASE_URL` | — |
| **Images** | [Cloudinary](https://cloudinary.com/) | Env vars | — |

</div>

### Step-by-step

**① Database — Neon (free)**
```
neon.tech → New Project → Connection Details → select "asyncpg" driver → copy URL
```

**② Backend — Railway**
```
railway.app → New Project → Deploy from GitHub →
  Root Directory: backend
  + Add env variables from backend/.env.example
  + Set CORS_ORIGINS to your Vercel URL
Railway auto-detects the Dockerfile and builds
```

**③ Frontend — Vercel**
```
vercel.com → Import from GitHub →
  Root Directory: frontend
  + Add: NEXT_PUBLIC_API_URL = https://your-backend.railway.app/api
Deploy → get your live URL
```

**④ Run migrations**
```bash
# In Railway → your backend service → New Job:
alembic upgrade head
```

---

## 🗺️ Roadmap

<table>
<tr>
<th align="center">Phase</th>
<th>Feature</th>
<th align="center">Status</th>
</tr>
<tr>
<td align="center"><b>Phase 0</b></td>
<td>Project scaffold, auth system, database schema</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 1</b></td>
<td>Screenshot upload → Cloudinary → EasyOCR text extraction</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 2</b></td>
<td>Groq / Llama AI problem reconstruction + test case generation</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 3</b></td>
<td>Monaco Editor integration + Piston API code execution</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 4</b></td>
<td>Verdict system (AC/WA/TLE/MLE/RE/CE) + per-test-case results</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 5</b></td>
<td>AI feedback, progressive hints, edge-case analysis</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 6</b></td>
<td>Analytics dashboard — charts, trends, performance metrics</td>
<td align="center">✅ Complete</td>
</tr>
<tr>
<td align="center"><b>Phase 7</b></td>
<td>Real-time collaboration, leaderboard, mobile app</td>
<td align="center">🔜 Planned</td>
</tr>
</table>

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

**Guidelines:**
- **Backend** — Async/await throughout, type-hint all functions, follow service-layer pattern
- **Frontend** — TypeScript strict mode, no `any`, small reusable components
- **Database** — Always create an Alembic migration for schema changes

---

<div align="center">

### 🧑‍💻 Built by

**[Kartik Bhardwaj](https://github.com/kartikbhardwaj1111)**

*Full-stack platform demonstrating end-to-end engineering:*
*AI/OCR integration · Async APIs · Monaco Editor · Sandboxed code execution · Cloud deployment*

<br/>

*If IntelliJudge helped you crack a problem, consider giving it a ⭐*

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,50:8b5cf6,100:06b6d4&height=120&section=footer" width="100%"/>

</div>
