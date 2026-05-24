# 🚀 IntelliJudge — Complete Deployment Guide

**Stack**: Vercel (frontend) · Render (backend) · Neon (database) — **100% Free**

---

## 📋 Overview

```
┌─────────────────────────────────────────────────────────┐
│  User Browser                                           │
│  https://your-app.vercel.app                           │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS
┌──────────────────▼──────────────────────────────────────┐
│  Vercel  (Next.js 16 — Frontend)                        │
│  • Serves the React UI                                  │
│  • Calls backend API with JWT token                     │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTPS + Authorization: Bearer <token>
┌──────────────────▼──────────────────────────────────────┐
│  Render  (FastAPI — Backend)                            │
│  • REST API routes                                      │
│  • AI reconstruction (Groq), OCR (EasyOCR)              │
│  • Code execution (Piston API)                          │
└──────────────────┬──────────────────────────────────────┘
                   │ asyncpg (TLS)
┌──────────────────▼──────────────────────────────────────┐
│  Neon PostgreSQL  (Database)                            │
│  • users / problems / test_cases / submissions          │
└─────────────────────────────────────────────────────────┘

     External APIs (called by backend):
     • Groq API   — AI problem reconstruction & hints
     • Cloudinary — Screenshot image CDN
     • Piston API — Free sandboxed code execution
```

> **⚠️ Render Free Tier Note**
> Free web services on Render **spin down after 15 minutes of inactivity**.
> The first request after sleep triggers a cold start (~30–60 seconds).
> This is normal and expected on the free tier.

---

## 🧰 Accounts You Need (all free)

| Service | Purpose | Sign-up |
|---|---|---|
| **GitHub** | Host your code | github.com |
| **Vercel** | Frontend hosting | vercel.com |
| **Render** | Backend hosting | render.com |
| **Neon** | PostgreSQL database | neon.tech |
| **Cloudinary** | Screenshot image storage | cloudinary.com |
| **Groq** | Free AI API | console.groq.com |

---

## Step 1 — Set Up Neon PostgreSQL Database

### 1.1 Create the database

1. Go to **[neon.tech](https://neon.tech)** → Sign up with GitHub
2. Click **"New Project"**
   - Project name: `intellijudge`
   - Database name: `intellijudge`
   - Region: pick the one closest to you
3. Click **"Create Project"**

### 1.2 Copy the connection string

1. In your Neon project → **"Connection Details"**
2. In the dropdown, select **"asyncpg"** (not the default psycopg2)
3. Copy the full URL — it looks like:
   ```
   postgresql+asyncpg://user:password@ep-cool-name.us-east-1.neon.tech/intellijudge?sslmode=require
   ```
4. **Save it** — you will paste it into Render as `DATABASE_URL`

---

## Step 2 — Deploy Backend to Render

### 2.1 Create a Render account

Go to **[render.com](https://render.com)** → **"Get Started for Free"** → sign in with GitHub.

### 2.2 Create a new Web Service

1. In Render dashboard → click **"New +"** → **"Web Service"**
2. Select **"Build and deploy from a Git repository"**
3. Connect your GitHub account if not already connected
4. Find and select the **IntelliJudge** repository → click **"Connect"**

### 2.3 Configure the service

Fill in the form:

| Field | Value |
|---|---|
| **Name** | `intellijudge-backend` |
| **Region** | Oregon (US West) or Frankfurt (EU) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Docker` |
| **Dockerfile Path** | `./Dockerfile` (Render looks inside Root Directory) |
| **Plan** | `Free` |

> **Important**: Set **Root Directory** to `backend` — this tells Render to use
> `backend/Dockerfile` and `backend/requirements.txt` automatically.

### 2.4 Add environment variables

Scroll down to **"Environment Variables"** and add each one:

```
APP_NAME                 IntelliJudge
APP_VERSION              0.1.0
DEBUG                    False
GROQ_MODEL               llama-3.3-70b-versatile
GROQ_BASE_URL            https://api.groq.com/openai/v1
DATABASE_URL             postgresql+asyncpg://...    ← from Neon Step 1
JWT_SECRET               <generate below>
GROQ_API_KEY             gsk_...                    ← from console.groq.com
CLOUDINARY_CLOUD_NAME    your-cloud-name            ← from Cloudinary dashboard
CLOUDINARY_API_KEY       your-api-key
CLOUDINARY_API_SECRET    your-api-secret
CORS_ORIGINS             ["https://your-app.vercel.app"]   ← update after Vercel deploy
```

**Generate JWT_SECRET** (run this in your terminal):
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Get Cloudinary credentials**:
- Sign in at [cloudinary.com](https://cloudinary.com) → Dashboard → Account Details

**Get Groq API key**:
- Sign in at [console.groq.com](https://console.groq.com) → API Keys → Create new key

### 2.5 Deploy

Click **"Create Web Service"**. Render will:
1. Clone your repository
2. Build the Docker image (first build takes ~10–15 min because EasyOCR/PyTorch is large)
3. Start the container
4. Run your health check at `/health`

Watch the **Logs** tab — you should eventually see:
```
🚀 IntelliJudge v0.1.0 starting...
✅ Database connection verified
✅ EasyOCR model ready
```

### 2.6 Save your backend URL

Once deployed, Render gives you a URL like:
```
https://intellijudge-backend.onrender.com
```
**Copy this URL** — you need it for Vercel.

### 2.7 Verify the backend

Open your browser and visit:
```
https://intellijudge-backend.onrender.com/health
```

You should see:
```json
{
  "success": true,
  "data": {
    "app": "IntelliJudge",
    "version": "0.1.0",
    "debug": false,
    "database": "connected",
    "timestamp": "..."
  }
}
```

If `database` says `unreachable`, double-check your `DATABASE_URL` value in Render.

---

## Step 3 — Deploy Frontend to Vercel

### 3.1 Create Vercel account

Go to **[vercel.com](https://vercel.com)** → **"Sign Up"** → sign in with GitHub.

### 3.2 Import the project

1. Click **"Add New..."** → **"Project"**
2. Find your IntelliJudge repository → click **"Import"**

### 3.3 Configure the project

| Field | Value |
|---|---|
| **Framework Preset** | Next.js (auto-detected) |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` (default) |
| **Output Directory** | `.next` (default) |
| **Install Command** | `npm install` (default) |

### 3.4 Add the backend URL

Under **"Environment Variables"**, add:

| Name | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://intellijudge-backend.onrender.com/api` |

Replace the URL with your actual Render backend URL from Step 2.6.

### 3.5 Deploy

Click **"Deploy"**. Vercel builds and deploys in ~2–3 minutes.

You'll get a URL like:
```
https://intellijudge.vercel.app
```

---

## Step 4 — Update CORS on the Backend

After Vercel gives you the frontend URL, you need to tell the backend to allow it.

1. In **Render dashboard** → your `intellijudge-backend` service → **"Environment"**
2. Find `CORS_ORIGINS` → click the pencil icon to edit
3. Update the value:
   ```
   ["https://intellijudge.vercel.app"]
   ```
   Replace with your actual Vercel URL.
4. Click **"Save Changes"** — Render redeploys automatically.

---

## Step 5 — Run Database Migrations

The database tables need to be created before the app works.

### Option A — Render One-off Job (recommended)

1. In Render dashboard → **"New +"** → **"Job"**
2. Connect the same repository
3. Root Directory: `backend`
4. Build Command: *(leave empty)*
5. Command: `alembic upgrade head`
6. Add the same `DATABASE_URL` environment variable
7. Click **"Create Job"** → it runs once and creates all tables

### Option B — Run locally against Neon

```bash
cd backend
source venv/bin/activate
export DATABASE_URL="postgresql+asyncpg://user:password@host/intellijudge?sslmode=require"
alembic upgrade head
```

---

## Step 6 — End-to-End Test

Open your Vercel frontend URL and test the full flow:

1. **Register** — visit `/register`, create a new account
2. **Login** — visit `/login`, sign in
3. **Dashboard** — should load with empty problems list
4. **Upload** — go to `/upload`, drag-and-drop a screenshot of a coding problem
5. **Problem** — OCR + AI reconstruction should create the problem
6. **Code** — write a solution in the Monaco editor, click **Run** then **Submit**
7. **Analytics** — visit `/analytics` to see your stats

### Quick API test from terminal

```bash
# Replace with your actual Render URL
BACKEND=https://intellijudge-backend.onrender.com

# Health check
curl $BACKEND/health

# Register a user
curl -X POST $BACKEND/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test123!"}'
```

---

## 🚨 Troubleshooting

### "CORS error" in browser console

The backend doesn't have your Vercel URL in its allowed origins.

**Fix**: In Render environment variables, set:
```
CORS_ORIGINS = ["https://your-actual-vercel-url.vercel.app"]
```
Then wait for Render to redeploy (~1 minute).

### Backend not responding / 502 Bad Gateway

The free-tier service has spun down (15 min inactivity).

**Fix**: The first request wakes it up. Wait 30–60 seconds and try again. Subsequent requests are fast.

**Keep-alive tip**: Use a free cron service like [cron-job.org](https://cron-job.org) to ping `https://your-backend.onrender.com/health` every 14 minutes to prevent spin-down.

### "Database: unreachable" in health check

`DATABASE_URL` is wrong or missing in Render.

**Fix**:
1. Go to Neon → Connection Details → select **asyncpg** → copy the full URL
2. Paste it as `DATABASE_URL` in Render environment variables
3. Make sure there are no extra spaces or line breaks

### Build fails with OOM error

EasyOCR/PyTorch installation can be memory-intensive during the build.

**Fix**: Trigger a manual redeploy in Render — builds can occasionally fail on memory spikes. Usually succeeds on retry.

### "Tables don't exist" — database errors on first use

Migrations haven't been run yet.

**Fix**: Follow Step 5 above to run `alembic upgrade head`.

### Groq API errors

**Fix**: Check that `GROQ_API_KEY` is set correctly in Render (no leading/trailing spaces). Generate a fresh key at [console.groq.com](https://console.groq.com) if needed.

---

## 🔄 Continuous Deployment

After initial setup, every `git push origin main` automatically:
- Rebuilds and redeploys the **Vercel** frontend (~2 min)
- Rebuilds and redeploys the **Render** backend (~5–10 min for Docker)

```bash
# Your everyday workflow
git add .
git commit -m "feat: add something cool"
git push origin main
# Both platforms auto-deploy → done
```

---

## 📋 Environment Variables Reference

### Backend (set in Render dashboard)

| Variable | Example Value | Where to Get It |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Neon → Connection Details (asyncpg) |
| `JWT_SECRET` | 64-char random hex | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `GROQ_API_KEY` | `gsk_...` | console.groq.com |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Fixed value |
| `GROQ_BASE_URL` | `https://api.groq.com/openai/v1` | Fixed value |
| `CLOUDINARY_CLOUD_NAME` | `mycloud` | Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | `123456789` | Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | `abc123...` | Cloudinary dashboard |
| `CORS_ORIGINS` | `["https://your-app.vercel.app"]` | Your Vercel URL |
| `DEBUG` | `False` | Fixed value |

### Frontend (set in Vercel dashboard)

| Variable | Value |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-backend.onrender.com/api` |

---

## 📚 Useful Links

| Resource | URL |
|---|---|
| Render Docs | render.com/docs |
| Render Blueprint spec | render.com/docs/blueprint-spec |
| Neon Docs | neon.tech/docs |
| Vercel Docs | vercel.com/docs |
| Groq Console | console.groq.com |
| Cloudinary Docs | cloudinary.com/documentation |
| FastAPI Deployment | fastapi.tiangolo.com/deployment |

---

## 🎯 Your Production URLs (fill in after deploying)

```
Frontend (Vercel):   https://_____________________.vercel.app
Backend (Render):    https://_____________________.onrender.com
API Docs (Swagger):  https://_____________________.onrender.com/docs
Database (Neon):     neon.tech dashboard (private)
```

---

*Last updated: 2026-05-25 | Stack: Vercel + Render + Neon — 100% Free*
