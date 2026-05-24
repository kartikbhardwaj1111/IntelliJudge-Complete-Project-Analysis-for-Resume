# ✅ Phase 1 — Backend Foundation — Testing Guide

---

## 📌 What Was Built

| # | File | What It Does |
|---|------|-------------|
| 1 | `backend/app/main.py` | FastAPI app entry point — creates the server, adds CORS, exception handlers, and 2 routes (`/` and `/health`) |
| 2 | `backend/app/config.py` | Loads environment variables from `.env` into a typed Python class using pydantic-settings |
| 3 | `backend/app/utils/exceptions.py` | Standard JSON response format (`success`, `message`, `data`, `errors`) + custom exception classes (404, 401, 409, 400) |
| 4 | `backend/.env` | Your local env vars (app name, port, CORS origins) |
| 5 | `backend/.env.example` | Template showing all env vars needed across all phases |
| 6 | `backend/requirements.txt` | Python dependencies — only Phase 1 deps active, future phases commented |
| 7 | `backend/app/**/__init__.py` | Package init files for models, routes, schemas, services, utils |
| 8 | `.gitignore` | Ignores venv, __pycache__, .env, node_modules, etc. |

### Project Structure Created
```
compilor project/
├── .gitignore
├── backend/
│   ├── .env                          # Your local environment vars
│   ├── .env.example                  # Template for all phases
│   ├── requirements.txt              # Python dependencies
│   ├── venv/                         # Python virtual environment
│   └── app/
│       ├── __init__.py
│       ├── main.py                   # ⭐ FastAPI app (the main file)
│       ├── config.py                 # ⭐ Settings from .env
│       ├── utils/
│       │   ├── __init__.py
│       │   └── exceptions.py         # ⭐ Standard response helpers
│       ├── models/
│       │   └── __init__.py           # (Phase 2)
│       ├── schemas/
│       │   └── __init__.py           # (Phase 3)
│       ├── routes/
│       │   └── __init__.py           # (Phase 3)
│       └── services/
│           └── __init__.py           # (Phase 4)
```

---

## 🚀 How to Start the Server

```bash
# Step 1: Open terminal, go to backend folder
cd "/Users/kartikbhardwaj/Desktop/compilor project/backend"

# Step 2: Activate the virtual environment
source venv/bin/activate

# Step 3: Start the server (with auto-reload for development)
uvicorn app.main:app --reload --port 8000
```

You should see:
```
🚀 IntelliJudge v0.1.0 starting...
📄 Swagger docs: http://0.0.0.0:8000/docs
🔧 Debug mode: True
INFO:     Application startup complete.
```

---

## 🧪 Testing with Thunder Client

### Test 1: Health Check

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://localhost:8000/health` |
| **Headers** | None required |
| **Body** | None |

**Expected Response** (Status: `200 OK`):
```json
{
    "success": true,
    "message": "IntelliJudge API is running",
    "data": {
        "app": "IntelliJudge",
        "version": "0.1.0",
        "debug": true,
        "timestamp": "2026-05-09T..."
    }
}
```

✅ **Pass if**: `success` is `true` and `data.app` is `"IntelliJudge"`

---

### Test 2: Root Endpoint

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://localhost:8000/` |
| **Headers** | None required |
| **Body** | None |

**Expected Response** (Status: `200 OK`):
```json
{
    "success": true,
    "message": "Welcome to IntelliJudge! Visit /docs for API documentation.",
    "data": {
        "docs": "/docs",
        "health": "/health"
    }
}
```

✅ **Pass if**: `success` is `true` and `data.docs` is `"/docs"`

---

### Test 3: Swagger UI (Browser)

| Field | Value |
|-------|-------|
| **Open in browser** | `http://localhost:8000/docs` |

✅ **Pass if**: You see the Swagger UI page with "IntelliJudge" title and both endpoints listed

---

### Test 4: Invalid Route (404 test)

| Field | Value |
|-------|-------|
| **Method** | `GET` |
| **URL** | `http://localhost:8000/api/nonexistent` |

**Expected Response** (Status: `404`):
```json
{
    "detail": "Not Found"
}
```

✅ **Pass if**: Returns 404 status (this is default FastAPI behavior, we'll customize it later)

---

## 🖥️ Testing with curl (Terminal)

If you prefer terminal over Thunder Client:

```bash
# Test 1: Health check
curl -s http://localhost:8000/health | python3 -m json.tool

# Test 2: Root endpoint
curl -s http://localhost:8000/ | python3 -m json.tool

# Test 3: Check response headers (verify CORS is working)
curl -s -I http://localhost:8000/health

# Test 4: Invalid route
curl -s http://localhost:8000/api/nonexistent | python3 -m json.tool
```

---

## ✅ Phase 1 Checklist

| # | Check | Status |
|---|-------|:---:|
| 1 | Server starts without errors | ⬜ |
| 2 | `GET /health` returns success JSON | ⬜ |
| 3 | `GET /` returns welcome message | ⬜ |
| 4 | Swagger UI loads at `/docs` | ⬜ |
| 5 | Invalid route returns 404 | ⬜ |

**Once all 5 checks pass → Phase 1 is complete! Say "Let's start Phase 2" to continue.**
