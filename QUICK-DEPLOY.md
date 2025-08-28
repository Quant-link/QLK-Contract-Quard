# 🚀 ContractQuard Quick Deployment Guide

## Prerequisites
- GitHub repository pushed to main branch
- Vercel account (free tier works)
- Railway account (free tier works)
- Domain name (optional)

## 🔥 STEP 1: Deploy Backend to Railway

1. **Go to Railway.app and login**
2. **Create New Project → Deploy from GitHub repo**
3. **Select your ContractQuard repository**
4. **Railway will auto-detect the railway.toml and deploy**

5. **Set Environment Variables in Railway Dashboard:**
   ```env
   HUGGINGFACE_API_KEY=your_huggingface_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_URL=sqlite:///./contractquard.db
   SECRET_KEY=your_production_secret_key_here
   ENVIRONMENT=production
   DEBUG=false
   CORS_ORIGINS=https://your-domain.com
   ```

6. **Note your Railway URL** (e.g., `https://contractquard-backend.railway.app`)

## 🔥 STEP 2: Deploy Frontend to Vercel

1. **Go to Vercel.com and login**
2. **Import Project → GitHub → Select ContractQuard repo**
3. **Configure Project:**
   - Framework Preset: Vite
   - Root Directory: `web/frontend`
   - Build Command: `npm run vercel-build`
   - Output Directory: `dist`

4. **Set Environment Variables in Vercel:**
   ```env
   VITE_API_BASE_URL=https://your-railway-backend-url.railway.app
   VITE_WS_URL=wss://your-railway-backend-url.railway.app/ws
   VITE_APP_NAME=ContractQuard
   VITE_APP_VERSION=0.1.0
   ```

5. **Deploy and note your Vercel URL**

## 🔥 STEP 3: Connect Custom Domain (Optional)

1. **In Vercel Dashboard:**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update Railway Environment:**
   ```env
   CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
   ```

## 🔥 STEP 4: Verify Deployment

Run the verification script:
```bash
export FRONTEND_URL=https://your-domain.com
export BACKEND_URL=https://your-railway-backend.railway.app
./scripts/verify-deployment.sh
```

## 🎯 Quick Links After Deployment

- **Frontend**: https://your-domain.com
- **Backend API**: https://your-railway-backend.railway.app/api/docs
- **Health Check**: https://your-railway-backend.railway.app/api/health

## 🔧 Troubleshooting

### Common Issues:

1. **Build Fails on Vercel:**
   - Check Node.js version (should be 18+)
   - Verify all dependencies are in package.json

2. **CORS Errors:**
   - Ensure CORS_ORIGINS includes your frontend domain
   - Check both HTTP and HTTPS variants

3. **API Not Connecting:**
   - Verify VITE_API_BASE_URL points to Railway URL
   - Check Railway service is running

### Debug Commands:
```bash
# Test frontend build locally
cd web/frontend
npm run build-production
npm run preview

# Test backend locally
cd web/backend
python -m uvicorn main:app --reload

# Test API
curl https://your-railway-backend.railway.app/api/health
```

## 🎉 Success!

Your ContractQuard application is now live and ready for production use!

- ✅ Frontend deployed on Vercel with CDN
- ✅ Backend deployed on Railway with auto-scaling
- ✅ HTTPS enabled on both services
- ✅ Security headers configured
- ✅ Environment variables secured
- ✅ Custom domain connected (if configured)

## 📊 Next Steps

1. Set up monitoring and alerting
2. Configure backup procedures
3. Set up CI/CD for automatic deployments
4. Monitor performance and optimize as needed
5. Set up error tracking (Sentry recommended)
