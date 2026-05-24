# 🚀 IntelliJudge — Complete Deployment Guide

**Status**: Production-ready deployment guide for Vercel + Railway + Neon

---

## 📋 Deployment Overview

This guide covers deploying IntelliJudge to production using:

- **Frontend**: Vercel (Next.js hosting)
- **Backend API**: Railway (Python/FastAPI hosting)
- **Database**: Neon (serverless PostgreSQL)
- **Image Storage**: Cloudinary (CDN)

```
┌─────────────────────────────────────────────────────┐
│  User Browser                                       │
│  https://intellijudge.vercel.app                    │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS
┌──────────────────▼──────────────────────────────────┐
│  Vercel (Next.js Frontend)                          │
│  • Static HTML/CSS/JS                               │
│  • API calls to backend                             │
│  • Authentication state (Zustand)                   │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS + JWT Token
┌──────────────────▼──────────────────────────────────┐
│  Railway (FastAPI Backend)                          │
│  • REST API endpoints                               │
│  • Business logic & services                        │
│  • Database queries (SQLAlchemy ORM)                │
└──────────────────┬──────────────────────────────────┘
                   │ SQL (asyncpg)
┌──────────────────▼──────────────────────────────────┐
│  Neon PostgreSQL                                    │
│  • Users table                                      │
│  • Problems table                                   │
│  • Submissions table                                │
│  • Test cases table                                 │
└─────────────────────────────────────────────────────┘

     External APIs (all async):
     • Groq API (LLM)
     • Cloudinary (Image CDN)
     • EasyOCR (text extraction)
```

---

## 🔧 Prerequisites

Before deploying, you'll need:

### 1. GitHub Repository
- [ ] Create a GitHub repo for your project
- [ ] Push your code (`git push origin main`)
- [ ] Make sure `.env` is in `.gitignore` (secrets should never be committed)

### 2. Account Signups
- [ ] Vercel account (free): https://vercel.com
- [ ] Railway account (free): https://railway.app
- [ ] Neon account (free): https://neon.tech
- [ ] Cloudinary account (free): https://cloudinary.com
- [ ] Groq API key (free): https://console.groq.com

### 3. Local Setup
- [ ] Python 3.11+ installed locally
- [ ] Node.js 20+ installed locally
- [ ] Git installed and configured

---

## 🗄️ Step 1: Create PostgreSQL Database on Neon

Neon provides a free serverless PostgreSQL database perfect for this project.

### 1.1 Create a Neon Project

1. Go to https://neon.tech
2. Sign up with GitHub or email
3. Create a new project:
   - **Project name**: `intellijudge`
   - **Database name**: `intellijudge`
   - **Region**: Choose closest to you
4. Click "Create project" and wait for it to initialize

### 1.2 Get the Connection String

1. In Neon dashboard, go to **Connection string**
2. Select **Python** from the dropdown
3. Copy the connection string (it looks like):
   ```
   postgresql+asyncpg://user:password@ep-xxx.us-east-1.neon.tech/intellijudge?sslmode=require
   ```
4. **Save this** — you'll need it for Railway environment variables

### 1.3 Test the Connection Locally

Before deploying, test that the connection works:

```bash
# In the backend directory
export DATABASE_URL="postgresql+asyncpg://..."  # Paste your Neon URL
cd backend
python -c "from app.database import AsyncSessionLocal; print('✅ Database connection OK')"
```

---

## 🚂 Step 2: Deploy Backend to Railway

Railway is a cloud platform that runs Docker containers. We'll deploy the FastAPI backend here.

### 2.1 Prepare Backend Environment Variables

Create a list of all variables needed in production:

```
DATABASE_URL = postgresql+asyncpg://...  (from Neon above)
GROQ_API_KEY = gsk_...  (from https://console.groq.com)
CLOUDINARY_CLOUD_NAME = (from https://cloudinary.com dashboard)
CLOUDINARY_API_KEY = (from Cloudinary dashboard)
CLOUDINARY_API_SECRET = (from Cloudinary dashboard)
JWT_SECRET = (generate: python -c "import secrets; print(secrets.token_hex(32))")
CORS_ORIGINS = ["https://intellijudge.vercel.app"]
DEBUG = False
APP_NAME = IntelliJudge
APP_VERSION = 0.1.0
```

### 2.2 Connect Railway to GitHub

1. Go to https://railway.app
2. Sign in with GitHub
3. Create a new project → "Deploy from GitHub repo"
4. Select your IntelliJudge repository
5. Choose the root directory if prompted

### 2.3 Configure Railway Environment Variables

1. In Railway project dashboard, click **Variables**
2. Add all variables from step 2.1 above
   - Click **+ New Variable** for each one
   - **Name** (left): `DATABASE_URL`
   - **Value** (right): `postgresql+asyncpg://...`

### 2.4 Configure Build Settings

1. In project settings, ensure:
   - **Build** command: (leave empty — Railway auto-detects)
   - **Start** command: (leave empty if Dockerfile exists)
   - Railway should auto-detect the Dockerfile and run it

2. If using Dockerfile:
   - Railway will automatically use `backend/Dockerfile`
   - The Dockerfile contains: `CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4"]`

### 2.5 Deploy & Get Backend URL

1. Railway will automatically deploy when you push to main
2. Wait for deployment to complete (watch the logs)
3. Once deployed, click the deployment and you'll see a URL like:
   ```
   https://intellijudge-api-production.up.railway.app
   ```
4. **Save this URL** — you'll need it for the frontend

### 2.6 Verify Backend is Running

```bash
# From your terminal
curl https://intellijudge-api-production.up.railway.app/health

# You should get:
# {
#   "success": true,
#   "data": {
#     "app": "IntelliJudge",
#     "version": "0.1.0",
#     "debug": false,
#     "database": "connected",
#     "timestamp": "2026-05-25T10:30:00+00:00"
#   }
# }
```

---

## 🎨 Step 3: Deploy Frontend to Vercel

### 3.1 Connect Vercel to GitHub

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New..." → "Project"
4. Select your IntelliJudge repository
5. Configure build settings:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`

### 3.2 Add Environment Variables to Vercel

In the Vercel project settings, add:

**Environment Variables** tab:

1. Click "Add New"
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://intellijudge-api-production.up.railway.app/api` (replace with your Railway URL)
   - **Environments**: Production, Preview, Development
   - Click "Save"

The `NEXT_PUBLIC_` prefix makes it available in the browser (not secret).

### 3.3 Deploy to Vercel

1. Click "Deploy"
2. Vercel will:
   - Checkout your code from GitHub
   - Run `npm install` in the `frontend` directory
   - Run `npm run build`
   - Upload build artifacts to Vercel's CDN
   - Give you a live URL

3. Wait for deployment to complete
4. You'll get a URL like: `https://intellijudge.vercel.app`

### 3.4 Verify Frontend is Running

1. Open https://intellijudge.vercel.app in your browser
2. You should see the landing page
3. Try navigating to `/register` and `/login`
4. Check browser console (F12 → Console) for any API errors

---

## 🔐 Step 4: Update Backend CORS for Vercel Domain

After Vercel deployment, update the backend CORS configuration:

### 4.1 Update backend/app/config.py

The CORS_ORIGINS should include your Vercel URL:

```python
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://intellijudge.vercel.app",  # ← Add your actual Vercel URL
]
```

But Vercel URL can change on each deployment. Better approach: use environment variable.

### 4.2 Alternative: Use Environment Variable

Instead of hardcoding, read from .env:

```python
# In backend/app/config.py
CORS_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Allow additional origins from environment
if env_origins := os.getenv("CORS_ORIGINS"):
    CORS_ORIGINS.extend(json.loads(env_origins))
```

Then in Railway environment variables, add:
```
CORS_ORIGINS = ["https://intellijudge.vercel.app"]
```

### 4.3 Redeploy Backend

1. Push the updated code to GitHub: `git push origin main`
2. Railway will automatically redeploy when you push
3. Or manually trigger in Railway dashboard: **Deploy** → **Redeploy main branch**

---

## 🧪 Step 5: End-to-End Testing

### 5.1 Test Frontend → Backend Connection

```bash
# In browser console (F12):
await fetch('https://intellijudge-api-production.up.railway.app/health')
  .then(r => r.json())
  .then(d => console.log(d))

# Should show database: "connected"
```

### 5.2 Test Registration

1. Visit https://intellijudge.vercel.app/register
2. Fill in email, username, password
3. Click "Register"
4. Should redirect to login page
5. Check Network tab (F12) to see the API request succeeded

### 5.3 Test Login

1. Visit https://intellijudge.vercel.app/login
2. Use credentials from above
3. Click "Login"
4. Should redirect to dashboard
5. Check localStorage (F12 → Application → Local Storage) for JWT token

### 5.4 Test Problem Upload

1. Go to Upload page
2. Try uploading a screenshot of a coding problem
3. Should:
   - Show preview of image
   - Run OCR extraction
   - Call Groq API for reconstruction
   - Save to database
   - Redirect to problem page

---

## 📊 Step 6: Monitor Production

### 6.1 View Logs

**Vercel Logs:**
1. In Vercel dashboard, click your project
2. Go to **Deployments**
3. Click recent deployment → **Logs**
4. Watch real-time logs as requests come in

**Railway Logs:**
1. In Railway dashboard, click your project
2. Select the service (your backend)
3. Click **Logs** tab
4. Watch real-time logs from FastAPI

### 6.2 Set Up Error Tracking (Optional)

Consider adding error tracking for production:

- **Sentry** (https://sentry.io) — tracks backend exceptions
- **LogRocket** (https://logrocket.com) — tracks frontend errors

### 6.3 Monitor Database

Neon dashboard shows:
- Query performance
- Connection count
- Backup history

---

## 🚨 Troubleshooting Common Issues

### Issue: "CORS error" in browser console

**Cause**: Backend doesn't have frontend URL in CORS_ORIGINS

**Fix**:
1. Get your Vercel URL
2. Add to Railway environment variable: `CORS_ORIGINS=["https://your-vercel-url.app"]`
3. Redeploy backend

### Issue: "Cannot connect to database"

**Cause**: DATABASE_URL not set in Railway, or URL is wrong

**Fix**:
1. Test locally: `python -c "from app.database import AsyncSessionLocal; print('OK')"`
2. Check Railway variables: is `DATABASE_URL` set?
3. Copy from Neon again (make sure "asyncpg" driver selected)
4. Redeploy

### Issue: "Groq API key invalid"

**Cause**: GROQ_API_KEY not set or wrong value

**Fix**:
1. Generate new key at https://console.groq.com
2. Copy exactly (no extra spaces)
3. Set in Railway environment variables
4. Redeploy

### Issue: Frontend shows blank page

**Cause**: Build failed or wrong configuration

**Fix**:
1. Check Vercel deployment logs
2. Look for TypeScript errors or build errors
3. Fix and push to GitHub (Vercel redeploys automatically)

### Issue: Code execution not working

**Cause**: Compilers not installed in Docker container

**Fix**:
1. Dockerfile includes: `gcc`, `g++`, `openjdk-17-jdk`, `python3`
2. Make sure Railway is using the Dockerfile
3. Check backend logs for compiler errors
4. Test locally: `g++ --version`, `javac -version`, etc.

---

## 📝 Environment Variables Checklist

### Frontend (.env in Vercel)

```
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app/api
```

### Backend (.env in Railway)

```
DATABASE_URL=postgresql+asyncpg://...
GROQ_API_KEY=gsk_...
CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...
JWT_SECRET=...
CORS_ORIGINS=["https://your-vercel-url.vercel.app"]
DEBUG=False
APP_NAME=IntelliJudge
APP_VERSION=0.1.0
```

---

## 🔄 Continuous Deployment Workflow

After initial deployment, here's the workflow:

```
1. Make code changes locally
   git add .
   git commit -m "Fix: ..."

2. Push to GitHub
   git push origin main

3. Vercel automatically redeploys frontend
   → New build in ~2-3 minutes

4. Railway automatically redeploys backend
   → New image in ~3-5 minutes

5. Monitor logs to ensure no errors

6. Test the feature in production
```

---

## ✅ Deployment Checklist

- [ ] Created Neon PostgreSQL database
- [ ] Saved DATABASE_URL from Neon
- [ ] Set up Railway project connected to GitHub
- [ ] Added all environment variables to Railway
- [ ] Verified backend deployed and `/health` endpoint works
- [ ] Deployed frontend to Vercel
- [ ] Added NEXT_PUBLIC_API_URL to Vercel env vars
- [ ] Updated CORS_ORIGINS in backend config with Vercel URL
- [ ] Tested registration → login → upload flow end-to-end
- [ ] Checked logs for any errors
- [ ] Tested from different browser (not development browser)

---

## 📚 Useful Links

| Resource | Link |
|----------|------|
| Vercel Docs | https://vercel.com/docs |
| Railway Docs | https://docs.railway.app |
| Neon Docs | https://neon.tech/docs |
| FastAPI Deployment | https://fastapi.tiangolo.com/deployment/ |
| Next.js Deployment | https://nextjs.org/docs/app/building-your-application/deploying |
| Cloudinary Docs | https://cloudinary.com/documentation |
| Groq Console | https://console.groq.com |

---

## 🎯 Your Production URLs

Once deployed, save these:

```
Frontend (Vercel):  https://intellijudge.vercel.app
Backend (Railway):  https://intellijudge-api-production.up.railway.app
Database (Neon):    neon.tech dashboard
```

---

**Generated**: May 25, 2026
**Status**: ✅ Ready for Deployment
