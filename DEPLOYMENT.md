# ContractQuard Deployment Guide

## Production Deployment

This guide covers deploying ContractQuard to production using Vercel (frontend) and Railway (backend).

### Prerequisites

- Node.js 18+ and npm
- Git repository access
- Vercel account
- Railway account
- Domain name (optional)

## Backend Deployment (Railway)

### 1. Deploy to Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Deploy from project root:**
   ```bash
   railway deploy
   ```

4. **Set Environment Variables in Railway Dashboard:**
   ```env
   HUGGINGFACE_API_KEY=your_huggingface_api_key
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=sqlite:///./contractquard.db
   SECRET_KEY=your_production_secret_key_here
   CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
   ENVIRONMENT=production
   DEBUG=false
   API_TIMEOUT=30
   MAX_FILE_SIZE_MB=10
   LOG_LEVEL=INFO
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

5. **Note your Railway URL** (e.g., `https://contractquard-backend.railway.app`)

## Frontend Deployment (Vercel)

### 1. Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Deploy from frontend directory:**
   ```bash
   cd web/frontend
   vercel
   ```

3. **Set Environment Variables in Vercel Dashboard:**
   ```env
   VITE_API_BASE_URL=https://your-railway-backend-url.railway.app
   VITE_WS_URL=wss://your-railway-backend-url.railway.app/ws
   VITE_APP_NAME=ContractQuard
   VITE_APP_VERSION=0.1.0
   VITE_MAX_FILE_SIZE_MB=10
   ```

### 2. Configure Custom Domain

1. **Add Domain in Vercel Dashboard:**
   - Go to your project settings
   - Add your custom domain
   - Follow DNS configuration instructions

2. **Update Backend CORS:**
   - Add your domain to Railway environment variables:
   ```env
   CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
   ```

## Testing Deployment

### Health Checks

```bash
# Backend health check
curl https://your-backend-url.railway.app/api/health

# Frontend accessibility
curl https://your-domain.com

# API functionality test
curl -X POST https://your-backend-url.railway.app/api/analyze \
  -F "file=@test.sol"
```

### Performance Testing

```bash
# Load test (install artillery first: npm install -g artillery)
artillery quick --count 10 --num 5 https://your-domain.com
```

## Monitoring

### Logs

- **Railway**: View logs in Railway dashboard
- **Vercel**: View function logs in Vercel dashboard

### Uptime Monitoring

Set up monitoring with:
- UptimeRobot
- Pingdom
- StatusCake

## Troubleshooting

### Common Issues

1. **CORS Errors:**
   - Verify CORS_ORIGINS includes your frontend domain
   - Check both HTTP and HTTPS variants

2. **API Connection Issues:**
   - Verify VITE_API_BASE_URL points to correct Railway URL
   - Check Railway service is running

3. **Build Failures:**
   - Check Node.js version compatibility
   - Verify all dependencies are installed

### Debug Commands

```bash
# Check frontend build locally
cd web/frontend
npm run build
npm run preview

# Check backend locally
cd web/backend
python -m uvicorn main:app --reload

# Test API endpoints
curl -X GET http://localhost:8000/api/health
```

## Security Checklist

- [ ] Environment variables set correctly
- [ ] CORS origins configured properly
- [ ] HTTPS enabled on both frontend and backend
- [ ] Security headers configured
- [ ] API keys secured and not exposed
- [ ] Database access restricted
- [ ] File upload limits configured

## Performance Optimization

- [ ] Frontend assets minified and compressed
- [ ] CDN configured for static assets
- [ ] Database queries optimized
- [ ] Caching implemented where appropriate
- [ ] Error tracking configured

## Backup and Recovery

- [ ] Database backup strategy implemented
- [ ] Environment variables documented
- [ ] Deployment rollback procedure tested
- [ ] Monitoring and alerting configured
