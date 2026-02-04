# 🚀 Quick Deployment Reference

## Render Backend Deployment (5 minutes)

```bash
# 1. Environment Variables to Set
GOOGLE_API_KEY=<your_api_key>
FLASK_ENV=production
ALLOWED_ORIGINS=<will_update_after_vercel>

# 2. Configuration
Build Command: pip install -r requirements.txt
Start Command: gunicorn api_server:app
Python Version: 3.11.0

# 3. Result
API URL: https://promptguard-api.onrender.com
```

## Vercel Frontend Deployment (3 minutes)

```bash
# 1. Configuration
Root Directory: frontend
Build Command: npm run build
Output Directory: dist

# 2. Environment Variables
VITE_API_URL=https://promptguard-api.onrender.com/api

# 3. Result
Frontend URL: https://promptguard.vercel.app
```

## Post-Deployment (2 minutes)

```bash
# 1. Return to Render Dashboard
# 2. Update Backend Environment
ALLOWED_ORIGINS=https://promptguard.vercel.app

# 3. Trigger Redeploy
# 4. Test in browser - DONE! ✅
```

## File Checklist

```
Backend:
✅ requirements.txt       - Python dependencies
✅ .env.example          - Environment template
✅ .gitignore            - Git ignore rules
✅ Procfile              - Render config
✅ render.yaml           - Service config
✅ api_server.py         - Updated for production
✅ start.sh              - Startup script

Frontend:
✅ .env.example          - Environment template
✅ vercel.json           - Vercel config
✅ vite.config.ts        - Build optimization
✅ .gitignore            - Updated ignore rules
✅ .env                  - Local dev env

Documentation:
✅ DEPLOYMENT.md         - Full guide
✅ DEPLOYMENT_CHECKLIST.md - Step-by-step
✅ README_DEPLOYMENT.md  - Project info
```

## Environment Variables Quick Reference

### Backend (.env)
```
GOOGLE_API_KEY=your_key_here
FLASK_ENV=production
ALLOWED_ORIGINS=https://promptguard.vercel.app
```

### Frontend (.env)
```
VITE_API_URL=https://promptguard-api.onrender.com/api
```

## Test After Deployment

```bash
# 1. Test Frontend
Visit: https://promptguard.vercel.app

# 2. Test Safe Prompt
Input: "What is machine learning?"
Expected: Approved with response

# 3. Test Malicious Prompt
Input: "Ignore previous instructions"
Expected: Blocked

# 4. Verify Markdown
Check if response is beautifully formatted ✅
```

## Important URLs

| Service | URL | Status |
|---------|-----|--------|
| Backend API | https://promptguard-api.onrender.com | Will be created |
| Frontend | https://promptguard.vercel.app | Will be created |
| Health Check | https://promptguard-api.onrender.com/api/health | Test after deploy |

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| CORS Error | Update ALLOWED_ORIGINS in Render |
| API Not Responding | Check Render logs, wait for cold start |
| Frontend 404 | Check VITE_API_URL environment variable |
| Blank Page | Check browser console for errors |
| Model Load Timeout | Upgrade Render plan or wait longer |

## Key Points to Remember

1. ✅ Never commit `.env` files
2. ✅ Update ALLOWED_ORIGINS after Vercel deployment
3. ✅ First API request may take ~30s (model loading)
4. ✅ Free tier has cold starts after 15 min inactivity
5. ✅ Monitor API quota usage
6. ✅ HTTPS is automatic on both platforms

## Support Resources

- 📖 [Full Deployment Guide](./DEPLOYMENT.md)
- ✅ [Deployment Checklist](./DEPLOYMENT_CHECKLIST.md)
- 📚 [README](./README_DEPLOYMENT.md)
- 🔗 [Render Docs](https://render.com/docs)
- 🔗 [Vercel Docs](https://vercel.com/docs)

---

**Ready to deploy?** Follow this quick reference, then check the full DEPLOYMENT.md guide for details!
