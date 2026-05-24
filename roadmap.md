# 🗺️ IntelliJudge — Learning Roadmap

## Backend-First, Step-by-Step

> **Philosophy**: Build the entire backend API first, test it with Swagger/Postman, then build the frontend to consume it. This way you learn one thing at a time without context-switching.

---

## Overview

```
Phase 1  ➜  Phase 2  ➜  Phase 3  ➜  Phase 4  ➜  Phase 5
Backend     Database     Auth        OCR          AI Recon
Setup       & ORM        System      Pipeline     Engine
 (BE)        (BE)         (BE)        (BE)         (BE)

Phase 6  ➜  Phase 7  ➜  Phase 8  ➜  Phase 9  ➜  Phase 10
Frontend    Full-Stack   Compiler    AI Smart     Deploy &
Foundation  Integration  + Verdicts  Features     Polish
 (FE)       (FE+BE)      (FE+BE)    (FE+BE)      (ALL)
```

---

## Phase 1 — Backend Foundation

> **Goal**: A running FastAPI server with health check + proper project structure

### 🎓 What You'll Learn
- Python virtual environments & dependency management
- FastAPI basics — decorators, routes, request/response
- Pydantic for settings management
- CORS middleware
- API documentation (Swagger UI auto-generated)

### 📝 Tasks (in order)

| # | Task | File to Create |
|---|------|---------------|
| 1.1 | Create project folder structure | `backend/app/` tree |
| 1.2 | Set up Python venv + install FastAPI, uvicorn | `requirements.txt` |
| 1.3 | Create FastAPI app entry point | `app/main.py` |
| 1.4 | Add environment config with pydantic-settings | `app/config.py` |
| 1.5 | Add CORS middleware | `app/main.py` |
| 1.6 | Create `.env.example` with all vars | `.env.example` |
| 1.7 | Build `GET /health` endpoint | `app/main.py` |
| 1.8 | Create standard response format utility | `app/utils/exceptions.py` |

### ✅ Deliverable
```bash
uvicorn app.main:app --reload
# Visit http://localhost:8000/docs → Swagger UI shows /health endpoint
# GET /health returns {"success": true, "message": "IntelliJudge API is running"}
```

### 📂 Files Created
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app + /health route
│   ├── config.py            # Settings class with env vars
│   └── utils/
│       ├── __init__.py
│       └── exceptions.py    # Standard response helpers
├── .env.example
├── .env
└── requirements.txt
```

---

## Phase 2 — Database & ORM

> **Goal**: PostgreSQL connected, User model created, migrations working

### 🎓 What You'll Learn
- PostgreSQL setup (local or Neon cloud)
- SQLAlchemy async ORM — models, sessions, engine
- Alembic for database migrations
- UUID primary keys
- Async/await patterns in Python

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 2.1 | Set up PostgreSQL database (Neon or local) | — |
| 2.2 | Install SQLAlchemy, asyncpg, Alembic | `requirements.txt` |
| 2.3 | Create async database connection | `app/database.py` |
| 2.4 | Create base model class | `app/models/__init__.py` |
| 2.5 | Create User model | `app/models/user.py` |
| 2.6 | Initialize Alembic | `app/migrations/` |
| 2.7 | Generate first migration for users table | `migrations/versions/` |
| 2.8 | Run migration → verify table exists | — |

### ✅ Deliverable
```bash
alembic upgrade head
# Connect to PostgreSQL → "users" table exists with correct columns
```

### 🗄️ Schema Created
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## Phase 3 — Authentication System

> **Goal**: Register, login, and protect routes with JWT tokens

### 🎓 What You'll Learn
- Password hashing with bcrypt (why plain text is dangerous)
- JWT tokens — how they work, encoding/decoding
- Pydantic schemas for request validation
- FastAPI dependency injection (`Depends()`)
- Protected routes pattern
- HTTP status codes (201 Created, 401 Unauthorized, 409 Conflict)

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 3.1 | Install bcrypt, python-jose | `requirements.txt` |
| 3.2 | Create password hashing utility | `app/utils/hashing.py` |
| 3.3 | Create JWT encode/decode utility | `app/utils/jwt.py` |
| 3.4 | Create User Pydantic schemas (request + response) | `app/schemas/user.py` |
| 3.5 | Create auth service (register, login logic) | `app/services/auth_service.py` |
| 3.6 | Build `POST /api/auth/register` | `app/routes/auth.py` |
| 3.7 | Build `POST /api/auth/login` | `app/routes/auth.py` |
| 3.8 | Build `get_current_user` dependency | `app/utils/jwt.py` |
| 3.9 | Build `GET /api/auth/me` (protected) | `app/routes/auth.py` |
| 3.10 | Test all 3 endpoints in Swagger UI | — |

### ✅ Deliverable
```
POST /api/auth/register → creates user, returns JWT
POST /api/auth/login → validates credentials, returns JWT  
GET /api/auth/me → returns user profile (requires Bearer token)
Calling /me without token → 401 Unauthorized
```

### 🧪 Test Scenarios
1. Register with valid email/username/password → 201
2. Register with duplicate email → 409
3. Login with correct password → 200 + token
4. Login with wrong password → 401
5. Access `/me` with valid token → 200 + user data
6. Access `/me` without token → 401

---

## Phase 4 — OCR Pipeline (Backend)

> **Goal**: Upload image → store in Cloudinary → extract text with EasyOCR

### 🎓 What You'll Learn
- File upload handling in FastAPI (`UploadFile`)
- Cloudinary SDK — upload, URL generation
- EasyOCR library — image to text
- Image processing basics (PIL/Pillow)
- Async file I/O

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 4.1 | Install cloudinary, easyocr, Pillow | `requirements.txt` |
| 4.2 | Create Cloudinary upload helper | `app/services/ocr_service.py` |
| 4.3 | Create EasyOCR text extraction function | `app/services/ocr_service.py` |
| 4.4 | Build OCR text cleanup function | `app/services/ocr_service.py` |
| 4.5 | Create upload schemas | `app/schemas/upload.py` |
| 4.6 | Build `POST /api/upload/screenshot` | `app/routes/upload.py` |
| 4.7 | Build `GET /api/upload/{id}/ocr-result` | `app/routes/upload.py` |
| 4.8 | Test with real screenshot images | — |

### ✅ Deliverable
```
POST /api/upload/screenshot (multipart form) 
→ Image stored in Cloudinary
→ OCR text extracted and returned
→ Test with a real coding question screenshot
```

---

## Phase 5 — AI Problem Reconstruction (Backend)

> **Goal**: OCR text → Gemini AI → structured coding problem with examples

### 🎓 What You'll Learn
- Google Gemini API — `@google/generative-ai` Python SDK
- Prompt engineering for structured output
- JSON parsing from AI responses
- Problem and TestCase database models
- CRUD operations pattern (Create, Read, Update, Delete)

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 5.1 | Install google-generativeai | `requirements.txt` |
| 5.2 | Create Gemini client wrapper | `app/services/ai_service.py` |
| 5.3 | Design reconstruction prompt | `app/services/ai_service.py` |
| 5.4 | Create Problem model + migration | `app/models/problem.py` |
| 5.5 | Create Problem schemas | `app/schemas/problem.py` |
| 5.6 | Build `POST /api/problems/reconstruct` | `app/routes/problems.py` |
| 5.7 | Build problem CRUD routes (list, get, update, delete) | `app/routes/problems.py` |
| 5.8 | Create TestCase model + migration | `app/models/test_case.py` |
| 5.9 | Build AI test case generation | `app/services/ai_service.py` |
| 5.10 | Build `POST /api/problems/{id}/generate-tests` | `app/routes/problems.py` |
| 5.11 | End-to-end test: screenshot → OCR → reconstruct → test cases | — |

### ✅ Deliverable
```
Full backend pipeline working:
Screenshot upload → OCR extraction → AI reconstruction → Structured problem in DB
AI-generated test cases (sample, edge, hidden) stored in DB
All endpoints testable via Swagger UI
```

### 🎯 Milestone: Backend MVP Complete!
At this point your entire backend API is functional. You can test everything via Swagger UI at `http://localhost:8000/docs` before writing a single line of frontend code.

---

## Phase 6 — Frontend Foundation

> **Goal**: Next.js app with auth pages, layout, and API client

### 🎓 What You'll Learn
- Next.js 15 App Router (file-based routing)
- TypeScript with React
- Tailwind CSS v4 setup and utility classes
- Component architecture
- API client with fetch/axios
- JWT token storage and management
- Zustand for global state
- Protected route pattern (redirect if not logged in)

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 6.1 | Initialize Next.js 15 + TypeScript + Tailwind | `frontend/` |
| 6.2 | Create shared TypeScript types | `src/types/` |
| 6.3 | Build API client (fetch wrapper with auth header) | `src/lib/api.ts` |
| 6.4 | Set up Zustand auth store | `src/stores/auth.ts` |
| 6.5 | Build base layout (navbar, sidebar) | `src/components/layout/` |
| 6.6 | Build Landing page (hero section) | `src/app/page.tsx` |
| 6.7 | Build Register page | `src/app/(auth)/register/page.tsx` |
| 6.8 | Build Login page | `src/app/(auth)/login/page.tsx` |
| 6.9 | Add auth middleware (redirect if not logged in) | `src/middleware.ts` |
| 6.10 | Build empty Dashboard page (protected) | `src/app/dashboard/page.tsx` |
| 6.11 | Test: Register → Login → See dashboard → Logout flow | — |

### ✅ Deliverable
```
Working auth flow:
Landing page → Register → Login → Dashboard (protected)
JWT stored in localStorage, sent in API headers
Redirect to /login if not authenticated
```

---

## Phase 7 — Full-Stack Integration (Upload + Problems)

> **Goal**: Connect upload UI and problem display to the backend APIs built in Phases 4-5

### 🎓 What You'll Learn
- File upload from React (drag-and-drop)
- Loading states and progress indicators
- Displaying structured data from API
- Dynamic routes in Next.js (`/problem/[id]`)
- Editable forms (user can correct AI output)

### 📝 Tasks

| # | Task | File |
|---|------|------|
| 7.1 | Build drag-and-drop upload component | `src/components/upload/` |
| 7.2 | Build Upload page (upload → show OCR → trigger reconstruct) | `src/app/upload/page.tsx` |
| 7.3 | Build Problem card component | `src/components/problem/` |
| 7.4 | Build Dashboard: show user's problems list | `src/app/dashboard/page.tsx` |
| 7.5 | Build Problem detail page | `src/app/problem/[id]/page.tsx` |
| 7.6 | Add "Edit Problem" capability | `src/app/problem/[id]/page.tsx` |
| 7.7 | Add "Generate Test Cases" button | `src/app/problem/[id]/page.tsx` |
| 7.8 | Display test cases on problem page | `src/components/problem/` |
| 7.9 | End-to-end test: Upload screenshot → see reconstructed problem | — |

### ✅ Deliverable
```
Full upload-to-problem flow:
Upload screenshot → See OCR text → AI reconstructs problem 
→ Problem appears in dashboard → Click to view details + test cases
```

---

## Phase 8 — Compiler Engine + Verdict System

> **Goal**: Monaco code editor + Judge0 execution + test case validation

### 🎓 What You'll Learn
- Monaco Editor integration in React
- Judge0 API — submit code, poll results
- Polling pattern (submit → wait → check status → get result)
- Submission model and database storage
- Verdict computation logic
- Output comparison/validation

### 📝 Backend Tasks

| # | Task | File |
|---|------|------|
| 8.1 | Install httpx for Judge0 API calls | `requirements.txt` |
| 8.2 | Create compiler service (submit, poll, result) | `app/services/compiler_service.py` |
| 8.3 | Create validation service (compare outputs) | `app/services/validation_service.py` |
| 8.4 | Create Submission model + migration | `app/models/submission.py` |
| 8.5 | Create Submission schemas | `app/schemas/submission.py` |
| 8.6 | Build `POST /api/submissions/run` (custom input) | `app/routes/submissions.py` |
| 8.7 | Build `POST /api/submissions/submit` (run all test cases) | `app/routes/submissions.py` |
| 8.8 | Implement verdict computation (CE > RE > TLE > MLE > WA > AC) | `app/services/validation_service.py` |

### 📝 Frontend Tasks

| # | Task | File |
|---|------|------|
| 8.9 | Integrate Monaco Editor component | `src/components/editor/` |
| 8.10 | Add language selector (C++, Java, Python, JS) | `src/components/editor/` |
| 8.11 | Add code templates per language | `src/lib/templates.ts` |
| 8.12 | Build Run button + custom input panel | `src/app/problem/[id]/page.tsx` |
| 8.13 | Build output panel (stdout, stderr, time, memory) | `src/components/editor/` |
| 8.14 | Build Submit button + test case results display | `src/app/problem/[id]/page.tsx` |
| 8.15 | Show per-test-case pass/fail indicators | `src/components/problem/` |

### ✅ Deliverable
```
Full coding experience:
View problem → Write code in Monaco → Run with custom input → See output
Submit → Code runs against all test cases → Get verdict (AC/WA/TLE/RE/CE)
Per-test-case results shown with pass/fail indicators
```

### 🎯 Milestone: Core Product Complete!
At this point IntelliJudge is fully functional end-to-end. Everything after this is enhancement.

---

## Phase 9 — AI Smart Features

> **Goal**: AI feedback on wrong answers, hints, edge case analysis

### 🎓 What You'll Learn
- Advanced prompt engineering
- Progressive disclosure UX pattern (Hint 1 → Hint 2 → Hint 3)
- Rate limiting implementation
- Complexity analysis concepts

### 📝 Tasks

| # | Task |
|---|------|
| 9.1 | Build AI feedback service (analyze failed submissions) |
| 9.2 | Build `POST /api/ai/feedback` endpoint |
| 9.3 | Build hint generation (progressive, not full solutions) |
| 9.4 | Build `POST /api/ai/hints` endpoint |
| 9.5 | Build edge case detection |
| 9.6 | Build `POST /api/ai/edge-cases` endpoint |
| 9.7 | Build optimization suggestions |
| 9.8 | Add rate limiting on AI endpoints |
| 9.9 | Build AI feedback panel in frontend (shows on wrong answer) |
| 9.10 | Add "Get Hint" button in problem page |
| 9.11 | Display edge case warnings |

### ✅ Deliverable
```
Submit wrong answer → "Get Feedback" button appears → AI explains what went wrong
"Get Hint" gives progressive hints without spoiling the solution
Edge case warnings highlight tricky inputs
```

---

## Phase 10 — Analytics Dashboard + Deployment

> **Goal**: Progress tracking + production deployment

### 🎓 What You'll Learn
- SQL aggregation queries (GROUP BY, COUNT, AVG)
- Charting libraries (Recharts / Chart.js)
- Docker basics + Dockerfile
- Vercel deployment (frontend)
- Railway deployment (backend)
- Environment variable management in production

### 📝 Tasks

| # | Task |
|---|------|
| 10.1 | Build analytics aggregation queries (backend) |
| 10.2 | Build analytics API endpoints (overview, topics, trends) |
| 10.3 | Build Dashboard page with summary stats cards |
| 10.4 | Add topic-wise accuracy radar chart |
| 10.5 | Add difficulty distribution pie chart |
| 10.6 | Add performance trend line chart |
| 10.7 | Add submission history table with pagination |
| 10.8 | Create Dockerfile for backend |
| 10.9 | Deploy backend to Railway |
| 10.10 | Deploy frontend to Vercel |
| 10.11 | Set up Neon PostgreSQL for production |
| 10.12 | Final end-to-end testing in production |

### ✅ Deliverable
```
Analytics dashboard with charts showing progress
Fully deployed and accessible via public URLs
```

---

## 📊 Timeline Summary

| Phase | Focus | Type | Effort |
|-------|-------|------|--------|
| **Phase 1** | Backend Foundation | 🟦 BE | ~1-2 hrs |
| **Phase 2** | Database & ORM | 🟦 BE | ~2 hrs |
| **Phase 3** | Auth System | 🟦 BE | ~2-3 hrs |
| **Phase 4** | OCR Pipeline | 🟦 BE | ~2-3 hrs |
| **Phase 5** | AI Reconstruction | 🟦 BE | ~3-4 hrs |
| **Phase 6** | Frontend Foundation | 🟩 FE | ~3-4 hrs |
| **Phase 7** | Full-Stack Integration | 🟨 BOTH | ~3-4 hrs |
| **Phase 8** | Compiler + Verdicts | 🟨 BOTH | ~4-5 hrs |
| **Phase 9** | AI Smart Features | 🟨 BOTH | ~3 hrs |
| **Phase 10** | Analytics + Deploy | 🟨 BOTH | ~4 hrs |

> **Total estimated**: ~28-34 hours of focused work

---

## 🏁 How to Use This Roadmap

1. **Start with Phase 1** — I'll guide you through every file
2. **Don't skip phases** — each one builds on the previous
3. **Test before moving on** — every phase has a clear deliverable to verify
4. **Ask me to start any phase** — just say "Let's start Phase X" and I'll write the code step by step

> **Ready to begin?** Say **"Let's start Phase 1"** and I'll scaffold the entire backend foundation for you, explaining every line as we go.
