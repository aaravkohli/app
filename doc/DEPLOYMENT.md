# Deployment Guide - PromptGuard

This guide explains how to deploy PromptGuard to production using Render (backend) and Vercel (frontend).

## Prerequisites

1. **Render Account**: https://render.com/
2. **Vercel Account**: https://vercel.com/
3. **GitHub Repository**: Your code must be on GitHub
4. **Google API Key**: For Gemini AI access

## Backend Deployment (Render)

### Step 1: Prepare Environment Variables

The backend requires:
- `GOOGLE_API_KEY` - Your Google Gemini API key
- `FLASK_ENV` - Set to `production`
- `ALLOWED_ORIGINS` - Your Vercel frontend URL (or * for development)

### Step 2: Deploy to Render

1. Go to https://dashboard.render.com/
2. Click "New Web Service"
3. Connect your GitHub repository
4. Configure with these settings:
   - **Name**: `promptguard-api`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api_server:app`
   - **Python Version**: 3.11

5. Add Environment Variables:
   ```
   GOOGLE_API_KEY=your_key_here
   FLASK_ENV=production
   ALLOWED_ORIGINS=https://your-vercel-frontend.vercel.app
   ```

6. Click "Deploy"

### Step 3: Get Your API URL

After deployment, Render will provide a URL like:
```
https://promptguard-api.onrender.com
```

Save this for the frontend deployment.

## Frontend Deployment (Vercel)

### Step 1: Prepare Environment Variables

The frontend requires:
- `VITE_API_URL` - Your Render backend URL

Example:
```
VITE_API_URL=https://promptguard-api.onrender.com/api
```

### Step 2: Update Local Configuration

1. Update `frontend/.env.production`:
```
VITE_API_URL=https://your-render-backend.onrender.com/api
```

2. Push changes to GitHub

### Step 3: Deploy to Vercel

1. Go to https://vercel.com/dashboard
2. Click "New Project"
3. Select your GitHub repository
4. Configure with these settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. Add Environment Variable:
   ```
   VITE_API_URL=https://your-render-backend.onrender.com/api
   ```

6. Click "Deploy"

### Step 4: Get Your Frontend URL

After deployment, Vercel will provide a URL like:
```
https://promptguard.vercel.app
```

### Step 5: Update Backend CORS

Go back to Render dashboard:
1. Select `promptguard-api` service
2. Go to Environment
3. Update `ALLOWED_ORIGINS` to your Vercel URL:
   ```
   https://promptguard.vercel.app
   ```
4. Redeploy

## Testing the Deployment

1. Visit your Vercel frontend URL
2. Test the application:
   - Enter a safe prompt (should be approved)
   - Enter a malicious prompt (should be blocked)
   - Verify proper error handling

## Troubleshooting

### API Connection Issues
- Check CORS settings in Render environment variables
- Verify `VITE_API_URL` in Vercel environment variables
- Check that both services are running

### Model Loading Issues
- First request takes time to load the ML model
- This is normal and cached after first request
- Render free tier may timeout on first request (upgrade if needed)

### Google API Quota
- Free tier has daily limits
- Check your Google Cloud quotas
- Consider upgrading for production use

## Environment Variable Reference

### Backend (.env)
```
GOOGLE_API_KEY=your_google_api_key
FLASK_ENV=production
ALLOWED_ORIGINS=https://your-vercel-frontend.vercel.app
```

### Frontend (.env.production)
```
VITE_API_URL=https://your-render-backend.onrender.com/api
```

## Security Checklist

- [ ] Never commit `.env` files
- [ ] Use `.env.example` for template
- [ ] Rotate API keys periodically
- [ ] Use environment-specific settings
- [ ] Enable HTTPS (automatic on both platforms)
- [ ] Set proper CORS origins
- [ ] Monitor usage and quotas

## Performance Notes

- Render free tier may have cold starts (project sleeps after 15 minutes)
- First request after sleep takes ~30 seconds
- Consider upgrading to paid tier for production
- Vercel has generous free tier without cold starts

## Next Steps

1. Monitor logs in both dashboards
2. Set up error tracking (Sentry, etc.)
3. Configure custom domain (optional)
4. Set up CI/CD for automatic deployments
5. Monitor API usage and costs
