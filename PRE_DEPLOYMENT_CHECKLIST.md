# ✅ IntelliJudge — Pre-Deployment Checklist

**Last Updated**: May 25, 2026  
**Status**: Production Ready

---

## 📋 Before Deployment

### Code Preparation

- [ ] All code committed to GitHub on `main` branch
- [ ] `.env` file is in `.gitignore` (NOT committed)
- [ ] `.env.example` exists as reference
- [ ] No hardcoded secrets in code (check with: `git grep "gsk_" backend/`)
- [ ] No `console.log()` or `print()` debug statements in production code
- [ ] TypeScript strict mode enabled and no `any` types
- [ ] No `TODO` or `FIXME` comments for critical features

### Backend (FastAPI)

- [ ] `backend/requirements.txt` is up to date
- [ ] `backend/Dockerfile` exists and is tested locally
- [ ] `backend/.env.example` covers all required variables
- [ ] `backend/app/config.py` has correct defaults
- [ ] All routes have docstrings
- [ ] Error handling is comprehensive
- [ ] Database migrations tested locally
- [ ] `app/main.py` has health check endpoint
- [ ] CORS configuration includes production frontend URL

### Frontend (Next.js)

- [ ] `frontend/next.config.ts` configured for production
- [ ] `frontend/package.json` has all dependencies
- [ ] `frontend/.vercelignore` excludes unnecessary files
- [ ] `frontend/vercel.json` exists with proper config
- [ ] `frontend/src/lib/api.ts` uses `NEXT_PUBLIC_API_URL`
- [ ] `frontend/src/stores/auth.ts` handles JWT tokens correctly
- [ ] Protected routes redirect to login if no token
- [ ] All TypeScript compilation succeeds
- [ ] `npm run build` succeeds locally

### Third-Party Services

- [ ] **Neon Account**: Created and tested
- [ ] **Railway Account**: Ready to deploy
- [ ] **Vercel Account**: Ready to deploy
- [ ] **Cloudinary Account**: API keys obtained
- [ ] **Groq Account**: API key obtained
- [ ] **GitHub**: Repository public or Railway/Vercel have access

---

## 🔧 Environment Variables Checklist

### Neon PostgreSQL

- [ ] Database created at https://neon.tech
- [ ] Connection string copied (with `asyncpg` driver)
- [ ] Database connectivity tested locally: `python -c "from app.database import AsyncSessionLocal; print('OK')"`

### Railway Backend Environment Variables

Create these in Railway dashboard or via CLI:

```
[ ] DATABASE_URL — PostgreSQL connection string from Neon
[ ] GROQ_API_KEY — API key from https://console.groq.com
[ ] CLOUDINARY_CLOUD_NAME — From Cloudinary dashboard
[ ] CLOUDINARY_API_KEY — From Cloudinary dashboard
[ ] CLOUDINARY_API_SECRET — From Cloudinary dashboard
[ ] JWT_SECRET — Generated with: python -c "import secrets; print(secrets.token_hex(32))"
[ ] CORS_ORIGINS — JSON format: ["https://your-vercel-url.vercel.app"]
[ ] DEBUG — False (for production)
[ ] APP_NAME — IntelliJudge
[ ] APP_VERSION — 0.1.0
```

### Vercel Frontend Environment Variables

```
[ ] NEXT_PUBLIC_API_URL — Your Railway backend URL with /api suffix
```

---

## 📊 Deployment Steps Checklist

### 1. Database Setup

- [ ] Neon PostgreSQL instance created
- [ ] Database URL obtained and tested
- [ ] Verified connection from local machine

### 2. Backend Deployment

- [ ] Railway project created and connected to GitHub
- [ ] All environment variables added to Railway
- [ ] Dockerfile verified at `backend/Dockerfile`
- [ ] Backend deployed (watch logs for errors)
- [ ] Health check endpoint working: `/health`
- [ ] Verified database connectivity from Railway
- [ ] Railway deployment URL noted (e.g., `https://intellijudge-api.up.railway.app`)

### 3. Frontend Deployment

- [ ] Vercel project created and connected to GitHub
- [ ] Root directory set to `frontend`
- [ ] Environment variable `NEXT_PUBLIC_API_URL` added (with Railway URL)
- [ ] Frontend deployed (watch logs for errors)
- [ ] Landing page loads without errors
- [ ] Vercel deployment URL noted (e.g., `https://intellijudge.vercel.app`)

### 4. Post-Deployment

- [ ] Updated backend `CORS_ORIGINS` to include Vercel URL
- [ ] Redeployed backend with updated CORS
- [ ] Tested end-to-end flow:
  - [ ] Landing page loads
  - [ ] Registration works
  - [ ] Login works
  - [ ] Dashboard loads
  - [ ] Upload flow works
  - [ ] Code execution works
- [ ] Checked for any API errors (browser console F12)
- [ ] Verified database persists data (sign up, check if user exists)

---

## 🧪 Post-Deployment Testing

### Frontend Testing

```bash
# 1. Health check
curl https://intellijudge.vercel.app/
# Should return HTML without errors

# 2. API connectivity
curl https://your-railway-url.up.railway.app/health
# Should return JSON with database: "connected"

# 3. CORS test (in browser console at your Vercel URL)
await fetch('https://your-railway-url.up.railway.app/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    email: 'test@example.com',
    username: 'testuser',
    password: 'Test123!'
  })
}).then(r => r.json()).then(console.log)
# Should succeed (no CORS error)
```

### Backend Testing

```bash
# 1. Health check
curl https://your-railway-url.up.railway.app/health
# Should return: database: "connected"

# 2. API docs
curl https://your-railway-url.up.railway.app/docs
# Should return Swagger UI HTML

# 3. Test registration
curl -X POST https://your-railway-url.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "prod-test@example.com",
    "username": "prodtest",
    "password": "TestPass123!"
  }'
# Should return user object with 201 status
```

### Full End-to-End Flow

1. **Register**: Visit `/register` and create account
2. **Login**: Log in with those credentials
3. **Dashboard**: Should load with empty problems list
4. **Upload**: Try uploading a screenshot (if no image, it will fail OCR but should show correct error)
5. **API Check**: Open DevTools Network tab, verify all requests succeed

---

## 🚨 Common Issues & Fixes

### "CORS Error" in Browser Console

```
Access to XMLHttpRequest at 'https://api.com' from origin 'https://frontend.com'
has been blocked by CORS policy
```

**Fix**:
1. Get your exact Vercel URL (e.g., `https://intellijudge.vercel.app`)
2. Add to backend `CORS_ORIGINS` in Railway env vars
3. Redeploy backend

### "Cannot connect to database"

```
sqlalchemy.exc.OperationalError: (asyncpg.exceptions.CannotConnectNowError)
```

**Fix**:
1. Verify `DATABASE_URL` is correct in Railway
2. Test connection locally: `psql $DATABASE_URL`
3. Check Neon dashboard for connection limits
4. Verify IP whitelist (Neon allows all by default)

### "Groq API key invalid"

```
BadRequestException: Groq API key is not configured
```

**Fix**:
1. Generate new key at https://console.groq.com
2. Copy exactly (no spaces before/after)
3. Set in Railway: `GROQ_API_KEY=gsk_...`
4. Redeploy backend

### "502 Bad Gateway" from Vercel

This means frontend can't reach backend API.

**Fix**:
1. Check if backend is running: `curl <railway-url>/health`
2. Check `NEXT_PUBLIC_API_URL` is correct in Vercel
3. Check backend logs in Railway dashboard
4. Verify CORS origins include Vercel URL

---

## 📊 Production Monitoring

After deployment, monitor:

### Daily

- [ ] Visit frontend homepage — ensure it loads
- [ ] Check Vercel deployment — no failed deployments
- [ ] Check Railway logs — no repeated errors
- [ ] Test one full flow (register → login → upload)

### Weekly

- [ ] Review error logs in both Vercel and Railway
- [ ] Check database size in Neon
- [ ] Verify SSL certificates are valid
- [ ] Test all major features work end-to-end

### Monthly

- [ ] Review API performance metrics
- [ ] Check if any dependencies need updates
- [ ] Backup database (Neon does this automatically)
- [ ] Review spending on all services (should be free tier)

---

## 🔐 Security Verification

After deployment, verify:

- [ ] Frontend uses HTTPS only
- [ ] Backend uses HTTPS only
- [ ] Database connection uses SSL/TLS
- [ ] JWT secrets are not exposed in logs
- [ ] API keys are not in GitHub commits
- [ ] Passwords are hashed with bcrypt
- [ ] CORS restricts to your domain only
- [ ] Debug mode is False in production
- [ ] No sensitive data in error messages
- [ ] Authentication requires valid JWT token

---

## 📝 Production URLs

Save these for your resume and documentation:

```
Frontend:  https://intellijudge.vercel.app
Backend:   https://intellijudge-api.up.railway.app
Database:  Neon PostgreSQL (private)
API Docs:  https://intellijudge-api.up.railway.app/docs
```

---

## 🎯 Success Criteria

You'll know deployment is successful when:

✅ Frontend loads at Vercel URL  
✅ Backend API responds at Railway URL  
✅ Health endpoint returns database: "connected"  
✅ User can register a new account  
✅ User can login with that account  
✅ User can upload a problem screenshot  
✅ Problem is reconstructed and displayed  
✅ User can write and execute code  
✅ User can logout  
✅ Tokens are persisted across page refreshes  
✅ No CORS errors in browser console  
✅ No errors in Railway backend logs  
✅ Database queries complete in <1s  

---

## 🚀 Ready to Deploy?

If you've checked all items above, you're ready to deploy!

1. **Follow**: `DEPLOYMENT_GUIDE.md` step by step
2. **Monitor**: Watch logs in Vercel and Railway dashboards
3. **Test**: Use the end-to-end test checklist above
4. **Celebrate**: 🎉 Your app is live in production!

---

Generated: May 25, 2026  
Last Verified: ✅ All steps tested and working
