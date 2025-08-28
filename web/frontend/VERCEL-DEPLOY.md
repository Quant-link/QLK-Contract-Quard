# 🚀 ContractQuard Frontend - Vercel Deployment Guide

## Quick Deploy to Vercel

### 1. Vercel Dashboard Setup

1. Go to [vercel.com](https://vercel.com) and login
2. Click **"New Project"**
3. Import from GitHub: Select your ContractQuard repository
4. Configure project settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `web/frontend`
   - **Build Command**: `npm run vercel-build`
   - **Output Directory**: `dist`

### 2. Environment Variables

Set these environment variables in Vercel dashboard:

```env
VITE_API_BASE_URL=https://qlk-contract-quard-production.up.railway.app
VITE_WS_URL=wss://qlk-contract-quard-production.up.railway.app/ws
VITE_APP_NAME=ContractQuard
VITE_APP_VERSION=0.1.0
VITE_MAX_FILE_SIZE_MB=10
```

### 3. Deploy

Click **"Deploy"** and wait for the build to complete.

**Note**: If you get a vercel.json configuration error, you can use the minimal version:
- Rename `vercel.json` to `vercel-full.json`
- Rename `vercel-minimal.json` to `vercel.json`
- Redeploy

### 4. Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to **"Domains"**
3. Add your custom domain
4. Update DNS records as instructed

## API Connection

✅ **Backend API**: `https://qlk-contract-quard-production.up.railway.app`
✅ **WebSocket**: `wss://qlk-contract-quard-production.up.railway.app/ws`
✅ **CORS**: Pre-configured for Vercel domains

## Testing

After deployment, test these endpoints:

- **Health Check**: `https://your-vercel-domain.vercel.app/api/health`
- **API Docs**: `https://your-vercel-domain.vercel.app/docs`
- **Frontend**: `https://your-vercel-domain.vercel.app`

## Troubleshooting

- **API Connection Issues**: Check environment variables in Vercel dashboard
- **CORS Errors**: Verify your Vercel domain is in the CORS whitelist
- **Build Errors**: Check build logs in Vercel dashboard
