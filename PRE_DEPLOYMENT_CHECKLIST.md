# ✅ IntelliJudge — Pre-Deployment Checklist

**Stack**: Vercel · Render · Neon — 100% Free  
**Last Updated**: 2026-05-25

---

## 📋 Before You Deploy

### Code

- [ ] All code committed to `main` branch on GitHub
- [ ] `.env` is in `.gitignore` — confirmed NOT committed
- [ ] `backend/.env.example` covers all required variables
- [ ] No hardcoded API keys in any file (`git grep "gsk_" backend/`)
- [ ] TypeScript strict mode passes: `npm run build` succeeds locally
- [ ] `backend/Dockerfile` exists at `backend/Dockerfile`
- [ ] `render.yaml` exists at the repo root

### Backend (FastAPI)

- [ ] `backend/requirements.txt` is up to date
- [ ] `backend/app/config.py` has sensible defaults
- [ ] All API routes have error handling
- [ ] `GET /health` endpoint returns `{ database: "connected" }` when DB is up
- [ ] CORS config reads from `CORS_ORIGINS` env var

### Frontend (Next.js)

- [ ] `frontend/vercel.json` exists
- [ ] `frontend/src/lib/api.ts` uses `NEXT_PUBLIC_API_URL` (not hardcoded localhost)
- [ ] `npm run build` succeeds from `frontend/` directory

---

## 🔧 Environment Variables Checklist

### Neon PostgreSQL

- [ ] Project created at [neon.tech](https://neon.tech)
- [ ] Connection string copied with **asyncpg** driver selected
- [ ] Starts with `postgresql+asyncpg://`
- [ ] Includes `?sslmode=require`

### Render Backend Variables

Set all of these in Render → Environment:

```
[ ] DATABASE_URL            → postgresql+asyncpg://... (from Neon)
[ ] JWT_SECRET              → 64-char hex (python3 -c "import secrets; print(secrets.token_hex(32))")
[ ] GROQ_API_KEY            → gsk_... (from console.groq.com)
[ ] GROQ_MODEL              → llama-3.3-70b-versatile
[ ] GROQ_BASE_URL           → https://api.groq.com/openai/v1
[ ] CLOUDINARY_CLOUD_NAME   → from cloudinary.com dashboard
[ ] CLOUDINARY_API_KEY      → from cloudinary.com dashboard
[ ] CLOUDINARY_API_SECRET   → from cloudinary.com dashboard
[ ] CORS_ORIGINS            → ["https://your-app.vercel.app"]
[ ] DEBUG                   → False
[ ] APP_NAME                → IntelliJudge
[ ] APP_VERSION             → 0.1.0
```

### Vercel Frontend Variable

```
[ ] NEXT_PUBLIC_API_URL  →  https://your-backend.onrender.com/api
```

---

## 📊 Deployment Steps

### 1 — Database

- [ ] Neon project created and connection string obtained
- [ ] `DATABASE_URL` tested locally:
  ```bash
  cd backend && source venv/bin/activate
  python -c "from app.database import AsyncSessionLocal; print('OK')"
  ```

### 2 — Backend (Render)

- [ ] Render account created and GitHub connected
- [ ] New Web Service created from repo
- [ ] Root Directory set to `backend`
- [ ] Runtime set to `Docker`
- [ ] All environment variables added
- [ ] First deploy completed (watch logs for ✅ messages)
- [ ] `/health` endpoint returns `database: connected`
- [ ] Backend URL saved: `https://_____.onrender.com`

### 3 — Frontend (Vercel)

- [ ] Vercel account created and GitHub connected
- [ ] New project imported from repo
- [ ] Root Directory set to `frontend`
- [ ] `NEXT_PUBLIC_API_URL` added with Render backend URL + `/api`
- [ ] Frontend deployed successfully
- [ ] Frontend URL saved: `https://_____.vercel.app`

### 4 — Wire them together

- [ ] Updated `CORS_ORIGINS` in Render to include Vercel URL
- [ ] Render redeployed after CORS update
- [ ] Ran `alembic upgrade head` to create database tables

### 5 — Post-Deployment Testing

- [ ] Landing page loads
- [ ] Registration works
- [ ] Login works and redirects to dashboard
- [ ] Dashboard loads (empty problems list is fine)
- [ ] Upload flow works (screenshot → OCR → problem)
- [ ] Code editor loads for a problem
- [ ] Run button executes code and shows verdict
- [ ] Analytics page loads
- [ ] No CORS errors in browser DevTools console (F12)
- [ ] No errors in Render logs

---

## 🚨 Common Issues Quick Reference

| Symptom | Most Likely Cause | Fix |
|---|---|---|
| CORS error in browser | Vercel URL missing from `CORS_ORIGINS` | Update env var in Render |
| 502 / no response | Free tier service spun down | Wait 30–60 s for cold start |
| `database: unreachable` | Wrong `DATABASE_URL` | Re-copy asyncpg URL from Neon |
| Build fails / OOM | PyTorch memory spike during install | Retry the deploy |
| `Table doesn't exist` | Migrations not run | Run `alembic upgrade head` |
| Groq errors | Bad `GROQ_API_KEY` | Re-generate key at console.groq.com |

---

## 🎯 Success Criteria

Your deployment is working when:

✅ `https://your-backend.onrender.com/health` → `database: connected`  
✅ Frontend loads at Vercel URL without JS errors  
✅ User can register a new account  
✅ User can log in and see the dashboard  
✅ Screenshot upload creates a problem  
✅ Code editor executes code and returns a verdict  
✅ No CORS errors in browser DevTools  

---

*See `DEPLOYMENT_GUIDE.md` for the full step-by-step guide.*
