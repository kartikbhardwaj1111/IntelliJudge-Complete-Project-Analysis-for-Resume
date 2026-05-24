#!/bin/bash
# IntelliJudge — Quick Deployment Setup Script
# 
# This script helps you generate required secrets and configuration values
# for deploying to production.
# 
# Usage: bash deploy-setup.sh

set -e

echo "🚀 IntelliJudge — Deployment Configuration Generator"
echo "======================================================="
echo ""

# Generate JWT Secret
echo "🔐 Generating JWT_SECRET..."
JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "JWT_SECRET=$JWT_SECRET"
echo ""

# Ask user for values
echo "📝 Enter your configuration values:"
echo ""

read -p "Enter NEON DATABASE_URL (from neon.tech dashboard): " DATABASE_URL
echo ""

read -p "Enter GROQ_API_KEY (from console.groq.com): " GROQ_API_KEY
echo ""

read -p "Enter CLOUDINARY_CLOUD_NAME: " CLOUDINARY_CLOUD_NAME
echo ""

read -p "Enter CLOUDINARY_API_KEY: " CLOUDINARY_API_KEY
echo ""

read -sp "Enter CLOUDINARY_API_SECRET: " CLOUDINARY_API_SECRET
echo ""
echo ""

read -p "Enter your VERCEL frontend URL (e.g., https://intellijudge.vercel.app): " VERCEL_URL
echo ""

# Create .env for backend
echo "📝 Creating backend/.env file..."
cat > backend/.env << EOF
# IntelliJudge — Backend Environment Variables
# Generated: $(date)

APP_NAME=IntelliJudge
APP_VERSION=0.1.0
DEBUG=False

HOST=0.0.0.0
PORT=8000

CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000", "$VERCEL_URL"]

DATABASE_URL=$DATABASE_URL

JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=24

CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET

GROQ_API_KEY=$GROQ_API_KEY
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1

JUDGE0_API_KEY=
JUDGE0_API_URL=https://judge0-ce.p.rapidapi.com
EOF

echo "✅ Created backend/.env"
echo ""

# Create Railway environment variables export
echo "📋 Railway Environment Variables:"
echo "=================================="
echo ""
echo "Copy these to Railway dashboard (Settings → Variables):"
echo ""
echo "DATABASE_URL"
echo "$DATABASE_URL"
echo ""
echo "GROQ_API_KEY"
echo "$GROQ_API_KEY"
echo ""
echo "CLOUDINARY_CLOUD_NAME"
echo "$CLOUDINARY_CLOUD_NAME"
echo ""
echo "CLOUDINARY_API_KEY"
echo "$CLOUDINARY_API_KEY"
echo ""
echo "CLOUDINARY_API_SECRET"
echo "$CLOUDINARY_API_SECRET"
echo ""
echo "JWT_SECRET"
echo "$JWT_SECRET"
echo ""
echo "CORS_ORIGINS"
echo "[\"$VERCEL_URL\"]"
echo ""
echo "=================================="
echo ""

# Create Vercel environment variables export
echo "📋 Vercel Environment Variables:"
echo "================================"
echo ""
echo "When deploying to Vercel, add this to project settings (Environment Variables):"
echo ""
echo "NEXT_PUBLIC_API_URL=<YOUR_RAILWAY_URL>/api"
echo ""
echo "Note: Replace <YOUR_RAILWAY_URL> with your Railway deployment URL"
echo "      You'll get this after deploying to Railway"
echo ""

# Create setup instructions file
cat > SETUP_INSTRUCTIONS.md << EOF
# Deployment Setup — Next Steps

## 1. Backend (Railway)

1. Go to https://railway.app
2. Connect your GitHub repository
3. In project settings, add these variables:

\`\`\`
DATABASE_URL=$DATABASE_URL
GROQ_API_KEY=$GROQ_API_KEY
CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET
JWT_SECRET=$JWT_SECRET
CORS_ORIGINS=["$VERCEL_URL"]
DEBUG=False
APP_NAME=IntelliJudge
APP_VERSION=0.1.0
\`\`\`

4. Deploy the backend
5. Copy the deployment URL (e.g., https://intellijudge-api.up.railway.app)

## 2. Frontend (Vercel)

1. Go to https://vercel.com
2. Connect your GitHub repository
3. Select 'frontend' as the root directory
4. Add environment variables:
   - NEXT_PUBLIC_API_URL=<RAILWAY_URL>/api

5. Deploy the frontend
6. Save your Vercel URL (e.g., https://intellijudge.vercel.app)

## 3. Update Backend CORS

1. Update CORS_ORIGINS in backend app/config.py or Railway env vars
2. Redeploy backend

## 4. Test

Visit your Vercel URL and test the full flow:
- Register a new account
- Login
- Upload a problem screenshot
- Submit code

Enjoy! 🎉
EOF

echo "✅ Created SETUP_INSTRUCTIONS.md"
echo ""
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "1. Review backend/.env (should be in .gitignore)"
echo "2. Read SETUP_INSTRUCTIONS.md"
echo "3. Follow the deployment guide: DEPLOYMENT_GUIDE.md"
echo ""
