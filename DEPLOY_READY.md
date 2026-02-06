# 🚀 Ready for Production Deployment

## Backend → Render

### Quick Deploy
1. Push to GitHub: `git push origin main`
2. Go to https://dashboard.render.com/
3. New → Blueprint → Connect GitHub repo
4. Set `GOOGLE_API_KEY` in environment variables
5. Deploy!

**Backend URL:** `https://promptguard-api.onrender.com`

### Test Backend
```bash
curl https://promptguard-api.onrender.com/api/health
```

---

## Frontend → Vercel

### Quick Deploy
1. Go to https://vercel.com/dashboard
2. New Project → Import from GitHub
3. Root Directory: `frontend`
4. Add env var: `VITE_API_URL=https://promptguard-api.onrender.com/api`
5. Deploy!

**Frontend URL:** `https://your-app.vercel.app`

### Update CORS
After Vercel deployment, update Render `ALLOWED_ORIGINS`:
```
https://your-app.vercel.app
```

---

## Files Ready ✅

### Backend
- ✅ `render.yaml` - Render config
- ✅ `Procfile` - Gunicorn command  
- ✅ `requirements.txt` - PyPDF2, python-docx added
- ✅ `api_server.py` - File upload + Vigil
- ✅ `.env.example` - Env template

### Frontend
- ✅ `vercel.json` - Vercel config
- ✅ Connection indicator
- ✅ File upload with reset
- ✅ `.env.example` - Env template

---

## Environment Variables

### Render (Backend)
```
GOOGLE_API_KEY=<your-key>
ALLOWED_ORIGINS=https://your-app.vercel.app
```

### Vercel (Frontend)
```
VITE_API_URL=https://promptguard-api.onrender.com/api
```

---

## Test After Deployment

1. Check connection indicator (green = connected)
2. Test text analysis
3. Upload PDF file
4. Verify Vigil scanners appear

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed guide.
