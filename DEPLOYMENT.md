# Deployment Guide

## Prerequisites
- GitHub account
- Render account (for backend)
- Vercel account (for frontend)
- Google API Key for Gemini

## Backend Deployment (Render)

### 1. Prepare Repository
Ensure these files are in your repository:
- `render.yaml` - Render deployment configuration
- `Procfile` - Process file for Render
- `requirements.txt` - Python dependencies
- `api_server.py` - Main application file
- `.env.example` - Environment variables template

### 2. Deploy to Render
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** → **Blueprint**
3. Connect your GitHub repository
4. Render will detect `render.yaml` automatically
5. Set the following environment variables in Render dashboard:
   - `GOOGLE_API_KEY` - Your Google Gemini API key
   - `ALLOWED_ORIGINS` - Your Vercel frontend URL (e.g., `https://your-app.vercel.app`)
   - Other variables are pre-configured in `render.yaml`

### 3. Verify Deployment
- Wait for build to complete (~5-10 minutes)
- Check logs for any errors
- Visit your Render URL: `https://promptguard-api.onrender.com/api/health`
- Should return: `{"status":"operational","version":"1.0.0","gateway":"PromptGuard - Secure AI Gateway"}`

## Frontend Deployment (Vercel)

### 1. Prepare Repository
Ensure these files are in `frontend/` directory:
- `vercel.json` - Vercel deployment configuration
- `package.json` - Dependencies and build scripts
- `.env.example` - Environment variables template

### 2. Deploy to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **Add New...** → **Project**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build` (auto-detected)
   - **Output Directory:** `dist` (auto-detected)

### 3. Set Environment Variables
In Vercel project settings → Environment Variables:
- `VITE_API_URL` = `https://promptguard-api.onrender.com/api`
  (Replace with your actual Render backend URL)

### 4. Deploy
- Click **Deploy**
- Wait for build to complete (~2-3 minutes)
- Visit your Vercel URL

### 5. Update Backend CORS
After deployment, update Render environment variables:
- Go to Render dashboard → Your service → Environment
- Update `ALLOWED_ORIGINS` to include your Vercel URL:
  ```
  https://your-app.vercel.app,https://promptguard.vercel.app
  ```
- Save and redeploy

## Post-Deployment

### 1. Test the Application
1. Open your Vercel frontend URL
2. Check header for **Connected** status (green indicator)
3. Try analyzing a text prompt
4. Try uploading a PDF file
5. Verify Vigil analysis appears

### 2. Monitor
- **Backend logs:** Render dashboard → Logs
- **Frontend logs:** Vercel dashboard → Deployments → Function Logs
- **Backend health:** `https://your-backend.onrender.com/api/health`

## Troubleshooting

### Backend Issues
- **502 Bad Gateway:** Service is starting (wait 1-2 minutes on free tier)
- **CORS errors:** Update `ALLOWED_ORIGINS` in Render environment variables
- **Module not found:** Check `requirements.txt` has all dependencies
- **Build fails:** Check Python version is 3.11.0 in `render.yaml`

### Frontend Issues
- **API connection failed:** Verify `VITE_API_URL` is correct
- **404 on routes:** Vercel should handle this with SPA routing automatically
- **Build fails:** Run `npm install` and `npm run build` locally to test

### Common Issues
- **Free tier sleep:** Render free tier sleeps after 15 minutes of inactivity
  - First request after sleep takes ~30 seconds
  - Frontend shows "Offline" then "Connected"
- **CORS errors:** Ensure backend `ALLOWED_ORIGINS` includes frontend URL
- **Upload fails:** Check `MAX_UPLOAD_SIZE` environment variable

## Environment Variables Reference

### Backend (.env)
```env
GOOGLE_API_KEY=your_google_api_key_here
FLASK_ENV=production
PORT=5000
ALLOWED_ORIGINS=https://your-app.vercel.app
MAX_UPLOAD_SIZE=26214400
```

### Frontend (.env)
```env
VITE_API_URL=https://promptguard-api.onrender.com/api
```

## Updating After Deployment

### Backend Updates
1. Push changes to GitHub
2. Render auto-deploys from main branch
3. Check deployment logs

### Frontend Updates
1. Push changes to GitHub
2. Vercel auto-deploys from main branch
3. Preview deployments available for pull requests

## Custom Domains (Optional)

### Backend (Render)
1. Render dashboard → Settings → Custom Domain
2. Add your domain
3. Configure DNS records as shown

### Frontend (Vercel)
1. Vercel dashboard → Settings → Domains
2. Add your domain
3. Configure DNS records as shown
4. Update `ALLOWED_ORIGINS` in backend with new domain

## Security Checklist
- ✅ `GOOGLE_API_KEY` stored in environment variables (not in code)
- ✅ CORS configured with specific origins (not `*`)
- ✅ HTTPS enforced on both frontend and backend
- ✅ File upload size limits configured
- ✅ `.env` files in `.gitignore`
- ✅ Environment-specific configurations separated

## Support
- Backend issues: Check Render logs
- Frontend issues: Check Vercel logs and browser console
- API issues: Test `/api/health` endpoint directly
