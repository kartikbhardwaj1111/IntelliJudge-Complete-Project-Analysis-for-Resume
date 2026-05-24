<div align="center">

![IntelliJudge — AI-Powered Coding Question Recovery & Practice](assets/banner.png)

# IntelliJudge

### 🧠 AI-Powered Coding Question Recovery & Practice Platform

[![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-886FBF?style=for-the-badge&logo=googlegemini&logoColor=fff)](https://ai.google.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

**Recover coding questions from screenshots. Reconstruct. Practice. Master.**

*Built for students, interview candidates, and competitive programmers who want to revisit unsolved problems from exams, contests, and coding rounds.*

[Features](#-features) · [How It Works](#-how-it-works) · [Architecture](#-architecture) · [Getting Started](#-getting-started) · [API Reference](#-api-reference) · [Contributing](#-contributing)

</div>

---

## 🎯 The Problem

Every competitive programmer and interview candidate knows this pain:

> 💭 You encounter a challenging coding question during an online assessment or interview. Time runs out. Later, all you have is a **screenshot** — and there's no way to reconstruct the full problem, generate test cases, or set up a proper environment to practice.

**IntelliJudge eliminates this problem entirely.**

Upload a screenshot → Get a fully reconstructed problem → Code, compile, test, and get AI-driven feedback — all in one platform.

---

## ✨ How It Works

![IntelliJudge Workflow](assets/workflow.png)

| Step | Action | What Happens |
|:---:|---|---|
| **1** | 📸 **Upload Screenshot** | Drag-and-drop or upload a screenshot of any coding question |
| **2** | 🔍 **OCR Extraction** | EasyOCR extracts raw text from the image with AI-powered cleanup |
| **3** | 🤖 **AI Reconstruction** | Google Gemini reconstructs the full problem statement — title, constraints, examples, tags, difficulty |
| **4** | 💻 **Code & Judge** | Write solutions in Monaco Editor, run against test cases via Judge0, get instant verdicts + AI feedback |

---

## 🚀 Features

### Core Platform

| Feature | Description |
|---|---|
| **🖼️ Screenshot → Problem** | Upload a screenshot from any coding exam and get a fully structured problem with title, description, I/O format, constraints, and examples |
| **🔍 Smart OCR Pipeline** | EasyOCR extraction with AI-powered text cleanup — handles messy exam screenshots, rotated text, and multi-column layouts |
| **🤖 AI Reconstruction** | Google Gemini transforms raw OCR text into a structured JSON problem with difficulty classification and topic tagging |
| **📝 Monaco Code Editor** | VS Code-powered editor with syntax highlighting, IntelliSense, and language-specific templates for C++, Java, Python, and JavaScript |
| **⚡ Live Compilation** | Sandboxed code execution via Judge0 API with real-time status tracking (queued → processing → done) |
| **🧪 Auto Test Cases** | AI-generated test cases including sample, hidden, edge, and stress categories |
| **✅ Verdict System** | Full competitive programming verdict support — AC, WA, TLE, MLE, RE, CE — with test-case-level results |
| **💡 AI Feedback** | Get intelligent feedback on wrong answers: what went wrong, missed edge cases, and hints toward the correct approach — without spoiling the solution |
| **📊 Analytics Dashboard** | Track progress with topic-wise accuracy, difficulty distribution, streak tracking, and performance trends |

### Platform Highlights

| Feature | Description |
|---|---|
| **🔐 Secure Auth** | JWT-based stateless authentication with bcrypt password hashing |
| **🌐 Full-Stack Monorepo** | Clean separation of Next.js frontend and FastAPI backend with shared types |
| **☁️ Cloud-Native** | Cloudinary for image hosting, Neon for serverless PostgreSQL, Vercel + Railway for deployment |
| **📱 Responsive Design** | Tailwind CSS v4 powered UI that works across desktop and tablet |
| **🔄 Smart Retry Logic** | Exponential backoff on all API calls for reliability |

---

## 🏗️ Architecture

### System Overview

```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend — Next.js 15"]
        UI["Dashboard UI"]
        Editor["Monaco Editor"]
        Upload["Upload System"]
        Analytics["Analytics View"]
    end

    subgraph Backend["⚙️ Backend — FastAPI"]
        API["API Routes"]
        Auth["Auth Service"]
        OCR["OCR Service"]
        AISvc["AI Service"]
        CompSvc["Compiler Service"]
        ValidSvc["Validation Service"]
    end

    subgraph External["☁️ External Services"]
        Gemini["Google Gemini API"]
        Judge0["Judge0 API"]
        Cloud["Cloudinary"]
    end

    subgraph Data["💾 Data Layer"]
        PG[("PostgreSQL (Neon)")]
    end

    UI --> API
    Editor --> API
    Upload --> API
    Analytics --> API

    API --> Auth
    API --> OCR
    API --> AISvc
    API --> CompSvc
    API --> ValidSvc

    AISvc --> Gemini
    CompSvc --> Judge0
    Upload --> Cloud
    
    Auth --> PG
    OCR --> PG
    AISvc --> PG
    CompSvc --> PG
    ValidSvc --> PG
```

### Data Flow Pipeline

```
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Screenshot  │────▶│  Cloudinary  │────▶│  EasyOCR        │────▶│  Cleaned Text    │
│  Upload      │     │  Storage     │     │  Extraction     │     │  Output          │
└──────────────┘     └──────────────┘     └─────────────────┘     └────────┬─────────┘
                                                                           │
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐             │
│  Analytics   │◀────│  Verdict +   │◀────│  Judge0         │             │
│  Dashboard   │     │  AI Feedback │     │  Execution      │             │
└──────────────┘     └──────────────┘     └────────┬────────┘             │
                                                    │                      │
                     ┌──────────────┐     ┌────────▼────────┐    ┌───────▼──────────┐
                     │  Test Case   │◀────│  Structured     │◀───│  Gemini AI       │
                     │  Generation  │     │  Problem        │    │  Reconstruction  │
                     └──────────────┘     └─────────────────┘    └──────────────────┘
```

### Database Entity Relationship

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
        text ocr_text
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

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | [Next.js 15](https://nextjs.org/) + TypeScript | SSR, app router, UI components |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com/) | Utility-first responsive design |
| **Code Editor** | [Monaco Editor](https://microsoft.github.io/monaco-editor/) | VS Code-like in-browser editing |
| **State Management** | [Zustand](https://github.com/pmndrs/zustand) | Lightweight global state |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) + Python | Async REST API & business logic |
| **ORM** | [SQLAlchemy](https://www.sqlalchemy.org/) + Alembic | Async ORM + database migrations |
| **Database** | [PostgreSQL](https://www.postgresql.org/) (Neon) | Serverless relational datastore |
| **OCR Engine** | [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Screenshot text extraction |
| **AI Engine** | [Google Gemini](https://ai.google.dev/) | Problem reconstruction, hints, feedback |
| **Compiler** | [Judge0 API](https://judge0.com/) | Sandboxed code execution & judging |
| **Image Storage** | [Cloudinary](https://cloudinary.com/) | CDN-backed screenshot hosting |
| **Auth** | JWT + bcrypt | Stateless token-based authentication |

---

## 📁 Project Structure

```
intellijudge/
├── frontend/                        # Next.js 15 application
│   ├── src/
│   │   ├── app/                     # App router pages
│   │   │   ├── (auth)/              #   ├── Login & Register
│   │   │   ├── dashboard/           #   ├── Main dashboard
│   │   │   ├── problem/[id]/        #   ├── Problem view + editor
│   │   │   ├── upload/              #   ├── Screenshot upload
│   │   │   ├── analytics/           #   └── Analytics dashboard
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx             # Landing page
│   │   ├── components/
│   │   │   ├── ui/                  # Reusable UI primitives
│   │   │   ├── editor/              # Monaco editor wrapper
│   │   │   ├── upload/              # Drag-and-drop upload
│   │   │   ├── problem/             # Problem display cards
│   │   │   ├── dashboard/           # Dashboard widgets
│   │   │   └── layout/              # Nav, sidebar, footer
│   │   ├── lib/                     # API client, auth, helpers
│   │   ├── hooks/                   # Custom React hooks
│   │   ├── types/                   # Shared TypeScript types
│   │   └── stores/                  # Zustand state stores
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── backend/                         # FastAPI application
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # Env vars & settings
│   │   ├── database.py              # Async DB connection
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── problem.py
│   │   │   ├── submission.py
│   │   │   └── test_case.py
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── routes/                  # API route handlers
│   │   │   ├── auth.py              #   ├── Register, Login, Profile
│   │   │   ├── problems.py          #   ├── CRUD + AI reconstruct
│   │   │   ├── submissions.py       #   ├── Run & submit code
│   │   │   ├── upload.py            #   ├── Screenshot upload + OCR
│   │   │   └── analytics.py         #   └── Stats & trends
│   │   ├── services/                # Business logic layer
│   │   │   ├── auth_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── ai_service.py
│   │   │   ├── compiler_service.py
│   │   │   ├── validation_service.py
│   │   │   └── analytics_service.py
│   │   ├── utils/                   # JWT, hashing, exceptions
│   │   └── migrations/              # Alembic DB migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml               # Local dev orchestration
├── .gitignore
└── README.md
```

---

## 📦 Getting Started

### Prerequisites

| Requirement | Version | Link |
|---|---|---|
| Node.js | ≥ 18.x | [nodejs.org](https://nodejs.org/) |
| Python | ≥ 3.11 | [python.org](https://www.python.org/) |
| PostgreSQL | ≥ 15 | [postgresql.org](https://www.postgresql.org/) or [Neon](https://neon.tech/) |
| Gemini API Key | Free | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Judge0 API Key | Free tier | [judge0.com](https://judge0.com/) or [RapidAPI](https://rapidapi.com/judge0-official/api/judge0-ce) |
| Cloudinary Account | Free | [cloudinary.com](https://cloudinary.com/) |

### 1. Clone the Repository

```bash
git clone https://github.com/kartikbhardwaj/intellijudge.git
cd intellijudge
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials (see below)

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### 4. Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host/intellijudge

# Authentication
JWT_SECRET=your-super-secret-key-here

# Google Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Judge0 Compiler API
JUDGE0_API_KEY=your-judge0-api-key
JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com

# Cloudinary Image Storage
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### 5. Run with Docker (Alternative)

```bash
docker-compose up --build
```

> **Frontend**: http://localhost:3000  
> **Backend**: http://localhost:8000  
> **API Docs**: http://localhost:8000/docs

---

## 📡 API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/auth/register` | Register new user | ❌ |
| `POST` | `/api/auth/login` | Login, returns JWT | ❌ |
| `GET` | `/api/auth/me` | Get current user profile | ✅ |

### Screenshot Upload & OCR

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/upload/screenshot` | Upload screenshot, run OCR | ✅ |
| `GET` | `/api/upload/{id}/ocr-result` | Get OCR extraction result | ✅ |

### Problems

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/problems/reconstruct` | AI-reconstruct from OCR text | ✅ |
| `GET` | `/api/problems` | List user's problems | ✅ |
| `GET` | `/api/problems/{id}` | Get problem details | ✅ |
| `PUT` | `/api/problems/{id}` | Edit problem | ✅ |
| `DELETE` | `/api/problems/{id}` | Delete problem | ✅ |

### Code Execution

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/submissions/run` | Run code with custom input | ✅ |
| `POST` | `/api/submissions/submit` | Submit for full judging | ✅ |
| `GET` | `/api/submissions/{id}` | Get submission result | ✅ |

### Test Cases

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/problems/{id}/generate-tests` | AI-generate test cases | ✅ |
| `GET` | `/api/problems/{id}/test-cases` | List test cases | ✅ |
| `POST` | `/api/problems/{id}/test-cases` | Add custom test case | ✅ |

### AI Features

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `POST` | `/api/ai/feedback` | AI feedback on wrong answer | ✅ |
| `POST` | `/api/ai/hints` | Progressive hints | ✅ |
| `POST` | `/api/ai/edge-cases` | Edge case analysis | ✅ |
| `POST` | `/api/ai/optimize` | Optimization suggestions | ✅ |

### Analytics

| Method | Endpoint | Description | Auth |
|:---:|---|---|:---:|
| `GET` | `/api/analytics/overview` | Dashboard summary stats | ✅ |
| `GET` | `/api/analytics/topics` | Topic-wise breakdown | ✅ |
| `GET` | `/api/analytics/submissions` | Paginated submission history | ✅ |
| `GET` | `/api/analytics/trends` | Performance over time | ✅ |

---

## ⚖️ Verdict System

IntelliJudge uses a competitive programming-style verdict system:

| Verdict | Code | Description |
|---|:---:|---|
| ✅ **Accepted** | `AC` | Output matches expected for all test cases |
| ❌ **Wrong Answer** | `WA` | Output differs from expected |
| ⏱️ **Time Limit Exceeded** | `TLE` | Execution exceeded time limit |
| 💾 **Memory Limit Exceeded** | `MLE` | Execution exceeded memory limit |
| 💥 **Runtime Error** | `RE` | Crash, segfault, or unhandled exception |
| 🔧 **Compilation Error** | `CE` | Code failed to compile |

**Priority**: `CE > RE > TLE > MLE > WA > AC`

---

## 🌐 Supported Languages

| Language | Version | Judge0 ID |
|---|---|:---:|
| C++ | C++17 | 54 |
| Java | Java 17 | 62 |
| Python | Python 3 | 71 |
| JavaScript | Node.js | 63 |

---

## 🚢 Deployment

| Service | Platform | Notes |
|---|---|---|
| **Frontend** | [Vercel](https://vercel.com/) | Auto-deploy from `main` branch |
| **Backend** | [Railway](https://railway.app/) | Docker container deployment |
| **Database** | [Neon](https://neon.tech/) | Serverless PostgreSQL, auto-scaling |
| **Images** | [Cloudinary](https://cloudinary.com/) | CDN-backed image storage |

---

## 🗺️ Roadmap

| Phase | Status | Description |
|---|:---:|---|
| **Phase 0** — Foundation | 🔴 | Auth, project scaffold, database |
| **Phase 1** — OCR Pipeline | 🔴 | Screenshot upload → text extraction |
| **Phase 2** — AI Reconstruction | 🔴 | OCR text → structured problem |
| **Phase 3** — Compiler Engine | 🟡 | Monaco editor + Judge0 execution |
| **Phase 4** — Test Case System | 🟡 | AI-generated test cases + validation |
| **Phase 5** — AI Features | 🟢 | Feedback, hints, edge case analysis |
| **Phase 6** — Analytics | 🟢 | Dashboard, progress tracking, trends |

> 🔴 = MVP &nbsp; 🟡 = P1 &nbsp; 🟢 = P2

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- **Frontend**: Follow Next.js App Router conventions, use TypeScript strict mode
- **Backend**: Follow FastAPI best practices, use async/await, type all endpoints with Pydantic
- **Database**: Create Alembic migrations for all schema changes
- **Testing**: Write tests for all new service-layer functions

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ by [Kartik Bhardwaj](https://github.com/kartikbhardwaj)**

*If IntelliJudge helped you crack a problem, consider giving it a ⭐!*

</div>
