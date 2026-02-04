# PromptGuard - AI-Powered Security Gateway

A sophisticated prompt injection detection system that uses machine learning and rule-based analysis to secure AI interactions.

## 🎯 Features

- **Real-time Threat Detection**: Analyzes user prompts for security threats
- **Multi-layer Security**: Combines ML models with lexical analysis
- **Beautiful UI**: Modern React interface with dark mode support
- **Markdown Support**: AI responses rendered with proper formatting
- **Secure API**: Production-ready Flask backend with CORS support
- **Fast Analysis**: <200ms latency for threat detection

## 📋 Prerequisites

### For Development
- Python 3.11+
- Node.js 18+
- npm or bun

### For Deployment
- Render.com account (backend)
- Vercel.com account (frontend)
- Google API key (for Gemini)

## 🚀 Quick Start

### Development Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd promptguard

# Backend setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# Start backend (from project root)
python api_server.py

# Frontend setup (in another terminal)
cd frontend
npm install
npm run dev

# Frontend will be available at http://localhost:8081
# API will be available at http://localhost:5000
```

### Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 📁 Project Structure

```
promptguard/
├── api_server.py           # Flask API server
├── safe_llm.py             # ML-based threat detection
├── requirements.txt        # Python dependencies
├── Procfile                # Render deployment config
├── render.yaml             # Render service config
├── start.sh                # Production startup script
├── DEPLOYMENT.md           # Deployment guide
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── pages/          # Page components
    │   ├── lib/            # Utilities
    │   └── index.css       # Styles
    ├── package.json        # Node dependencies
    ├── vite.config.ts      # Vite configuration
    ├── vercel.json         # Vercel deployment config
    ├── .env.example        # Frontend env template
    └── .gitignore          # Frontend git ignore
```

## 🔐 Security Features

### Input Analysis
- **ML-based Detection**: Uses ProtectAI DeBERTa model for accurate classification
- **Lexical Analysis**: Pattern matching for common injection techniques
- **Adaptive Learning**: Learns from blocked attempts
- **Benign Intent Detection**: Reduces false positives

### Risk Scoring
- **ML Risk**: 0.0-1.0 (ML model confidence)
- **Lexical Risk**: Pattern-based threat score
- **Benign Offset**: Reduces risk for clearly benign prompts
- **Final Risk**: Aggregated score (ML + Lexical - Benign)

## 📊 API Endpoints

### Health Check
```
GET /api/health
```
Returns server status

### Analyze Prompt
```
POST /api/analyze
Content-Type: application/json

{
  "prompt": "Your prompt here"
}
```

Response:
```json
{
  "status": "approved|blocked",
  "prompt": "echoed prompt",
  "analysis": {
    "risk": 0.0,
    "ml_score": 0.0,
    "lexical_risk": 0.0,
    "benign_offset": 0.0,
    "adaptive_phrases": 0
  },
  "response": "AI generated response",
  "analysisTime": 123
}
```

### Risk Analysis Only
```
POST /api/analyze/risk
```
Returns risk metrics without AI response

### Batch Analysis
```
POST /api/analyze/batch
Content-Type: application/json

{
  "prompts": ["prompt1", "prompt2"]
}
```

## 🛠️ Technology Stack

### Backend
- **Flask**: Web framework
- **Transformers**: HuggingFace ML models
- **Google Generative AI**: Gemini API
- **CORS**: Cross-origin resource sharing
- **Gunicorn**: Production WSGI server

### Frontend
- **React**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Framer Motion**: Animations
- **React Router**: Navigation
- **React Markdown**: Markdown rendering
- **Radix UI**: Component library

## 📝 Environment Variables

### Backend
```
GOOGLE_API_KEY=your_api_key
FLASK_ENV=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Frontend
```
VITE_API_URL=https://your-backend.onrender.com/api
```

## 🧪 Testing

### Backend
```bash
python -m py_compile api_server.py safe_llm.py
python test_responses.py
```

### Frontend
```bash
cd frontend
npm run test
npm run build  # Production build
```

## 📈 Performance

- **Threat Analysis**: <200ms average
- **API Response**: <2s (including AI generation)
- **Frontend Build**: 2s optimized build
- **Bundle Size**: ~640KB (gzipped: ~200KB)

## 🐛 Troubleshooting

### API Connection Issues
- Check CORS settings in backend environment
- Verify API URL in frontend .env
- Ensure both services are running

### Model Loading
- First request loads the ML model (~200MB)
- This is cached for subsequent requests
- On Render free tier, may timeout first request

### Google API Quota
- Free tier has daily limits
- Monitor usage in Google Cloud Console
- Upgrade for production use

## 📚 Documentation

- [Deployment Guide](./DEPLOYMENT.md) - Detailed deployment steps
- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Feature overview
- [Architecture Guide](./ARCHITECTURE.md) - System architecture

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details

## 📞 Support

For issues and questions:
1. Check existing documentation
2. Review GitHub issues
3. Create a new issue with details

## 🔮 Roadmap

- [ ] User authentication
- [ ] Response history
- [ ] Custom threat rules
- [ ] Admin dashboard
- [ ] Rate limiting
- [ ] Webhook notifications
- [ ] Analytics dashboard

## ⚠️ Important Notes

- **API Keys**: Never commit `.env` files
- **Free Tier**: Render free tier has cold starts after 15 minutes
- **Quotas**: Monitor Google API usage
- **CORS**: Update ALLOWED_ORIGINS after frontend deployment

## 🎉 Ready to Deploy?

Follow the [Deployment Guide](./DEPLOYMENT.md) to deploy to Render and Vercel in minutes!
