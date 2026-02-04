# PromptGuard - Complete File Guide

## 📁 Project Structure

### Root Directory Files

#### Core Application Files

| File | Purpose | Status |
|------|---------|--------|
| `safe_llm.py` | Backend security engine with ML threat detection | ✅ Original |
| `api_server.py` | Flask REST API server exposing safe_llm | ✅ NEW |
| `run.py` | Simple test script for backend | ✅ Original |

#### Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Backend environment variables (Google API key) | ✅ NEW |

#### Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `README.md` | Main project documentation | ✅ NEW |
| `QUICK_START.md` | 5-minute setup guide | ✅ NEW |
| `INTEGRATION_GUIDE.md` | Complete technical integration docs | ✅ NEW |
| `IMPLEMENTATION_SUMMARY.md` | What was implemented | ✅ NEW |
| `VERIFICATION_CHECKLIST.md` | Testing and verification guide | ✅ NEW |
| `FILE_GUIDE.md` | This file - complete file guide | ✅ NEW |

#### Testing Files

| File | Purpose | Status |
|------|---------|--------|
| `test_integration.py` | Integration test suite | ✅ NEW |

---

## 📁 Frontend Directory Structure

### `/frontend` - React Application

#### Configuration Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Frontend environment variables (API URL) | ✅ NEW |
| `package.json` | Dependencies and build scripts | ✅ Original |
| `package-lock.json` | Locked dependency versions | ✅ Original |
| `vite.config.ts` | Vite build configuration | ✅ Original |
| `tsconfig.json` | TypeScript configuration | ✅ Original |

#### Source Files: Pages

| File | Purpose | Status |
|------|---------|--------|
| `src/pages/Index.tsx` | Main UI component with user input and results | ✅ UPDATED |

#### Source Files: Components

| File | Purpose | Status |
|------|---------|--------|
| `src/components/PromptInput.tsx` | User input textarea with character count | ✅ Original |
| `src/components/ResultCard.tsx` | Display analysis results (approved/blocked) | ✅ Original |
| `src/components/RiskMeter.tsx` | Visual risk gauge with animation | ✅ Original |
| `src/components/SecurityConfidence.tsx` | Risk metrics breakdown | ✅ Original |
| `src/components/RiskBreakdown.tsx` | Detailed metric display | ✅ Original |
| `src/components/ExamplePrompts.tsx` | Sample prompts for quick testing | ✅ Original |
| `src/components/Header.tsx` | Top navigation header | ✅ Original |
| `src/components/HeroSection.tsx` | Welcome/intro section | ✅ Original |
| `src/components/SecurityBadge.tsx` | Trust and security indicators | ✅ Original |

#### Source Files: Library/Utils

| File | Purpose | Status |
|------|---------|--------|
| `src/lib/apiService.ts` | TypeScript API client for backend communication | ✅ NEW |

#### Source Files: Styling & Config

| File | Purpose | Status |
|------|---------|--------|
| `src/index.css` | Global styles | ✅ Original |
| `src/App.tsx` | Root application component | ✅ Original |
| `src/main.tsx` | Application entry point | ✅ Original |

---

## 📋 File Dependencies

### API Server Chain
```
api_server.py
  ↓ imports
safe_llm.py
  ├── google.generativeai (Gemini LLM)
  └── transformers (ProtectAI model)
```

### Frontend Component Chain
```
Index.tsx (Main Page)
  ├── imports apiService.ts
  ├── uses PromptInput.tsx
  ├── uses ResultCard.tsx
  ├── uses RiskMeter.tsx
  ├── uses SecurityConfidence.tsx
  ├── uses RiskBreakdown.tsx
  └── uses ExamplePrompts.tsx
  
apiService.ts
  └── calls API at http://localhost:5000/api
```

---

## 🔄 Data Flow

### From User to Analysis
```
User Input (Index.tsx)
    ↓
apiService.analyzePrompt()
    ↓
HTTP POST /api/analyze
    ↓
api_server.py receives request
    ↓
safe_llm.py analyzes
    ├── ML threat detection
    ├── Lexical pattern matching
    ├── Risk calculation
    └── LLM response (if approved)
    ↓
API returns JSON response
    ↓
Index.tsx displays results
    ├── Maps to RiskMeter
    ├── Maps to SecurityConfidence
    ├── Maps to ResultCard
    └── Maps to RiskBreakdown
```

---

## 📝 File Descriptions

### Backend Files

#### `safe_llm.py` (Backend Security Engine)
- **Lines:** 204
- **Purpose:** Core ML-based threat detection
- **Key Functions:**
  - `final_risk()` - Calculate overall risk score
  - `call_llm()` - Generate AI response with Gemini
  - `safe_generate()` - Complete analysis pipeline
  - `output_risk()` - Check for leaks in response
- **Models Used:**
  - ProtectAI/deberta-v3 (ML threat detection)
  - Google Generative AI (LLM)
- **Status:** Fully functional, production-ready

#### `api_server.py` (Flask REST API)
- **Lines:** ~300
- **Purpose:** HTTP API wrapper around safe_llm.py
- **Endpoints:**
  1. `GET /api/health` - Health check
  2. `POST /api/analyze` - Full analysis with LLM
  3. `POST /api/analyze/risk` - Risk-only (fast)
  4. `POST /api/analyze/batch` - Multiple prompts
- **Features:**
  - Request validation
  - Error handling
  - CORS support
  - Logging
  - Response formatting
- **Status:** NEW, fully functional

#### `.env` (Backend Configuration)
- **Purpose:** Store sensitive API keys
- **Variables:**
  - `GOOGLE_API_KEY` - Google Generative AI key
- **Status:** NEW, required for operation

#### `test_integration.py` (Integration Tests)
- **Lines:** ~450
- **Purpose:** Automated testing of integration
- **Tests:**
  - Health check
  - Safe prompt analysis
  - Dangerous prompt detection
  - Risk-only analysis
  - Batch analysis
  - Error handling
- **Status:** NEW, comprehensive test suite

### Frontend Files

#### `Index.tsx` (Main Component)
- **Lines:** ~260
- **Purpose:** Main user interface
- **Features:**
  - Prompt input handling
  - API communication via apiService
  - Result display
  - Real-time metrics
  - Error handling
- **Changes Made:**
  - Replaced simulated data with real API calls
  - Updated to use apiService
  - Improved error handling
- **Status:** UPDATED, fully functional

#### `apiService.ts` (Frontend API Client)
- **Lines:** ~150
- **Purpose:** TypeScript wrapper for API communication
- **Methods:**
  - `healthCheck()` - Verify API availability
  - `analyzePrompt(prompt)` - Analyze single prompt
  - `analyzeRiskOnly(prompt)` - Fast risk analysis
  - `analyzeBatch(prompts)` - Batch processing
- **Features:**
  - Type-safe interfaces
  - Error handling
  - Environment variables
  - Request/response mapping
- **Status:** NEW, production-ready

#### `frontend/.env` (Frontend Configuration)
- **Purpose:** Frontend environment variables
- **Variables:**
  - `VITE_API_URL` - API server endpoint
- **Default:** `http://localhost:5000/api`
- **Status:** NEW, required for operation

#### Component Files (UI Components)
- **Purpose:** Reusable React components
- **Files:**
  - `PromptInput.tsx` - User input area
  - `ResultCard.tsx` - Result display card
  - `RiskMeter.tsx` - Visual risk gauge
  - `SecurityConfidence.tsx` - Metrics breakdown
  - `RiskBreakdown.tsx` - Detailed metrics
  - `ExamplePrompts.tsx` - Sample prompts
  - `Header.tsx` - Navigation header
  - `HeroSection.tsx` - Hero section
  - `SecurityBadge.tsx` - Trust indicators
- **Status:** Original, already enhanced with animations

### Documentation Files

#### `README.md` (Main Documentation)
- **Purpose:** Project overview and getting started
- **Sections:**
  - Quick start (5 minutes)
  - Architecture overview
  - API documentation
  - How it works
  - Setup instructions
  - Troubleshooting
- **Status:** NEW, comprehensive

#### `QUICK_START.md` (Quick Start Guide)
- **Purpose:** Get running in 5 minutes
- **Content:**
  - Setup instructions
  - Quick test commands
  - System overview
  - Data flow examples
  - Performance metrics
- **Status:** NEW, easy to follow

#### `INTEGRATION_GUIDE.md` (Technical Reference)
- **Purpose:** Complete integration documentation
- **Content:**
  - Architecture details
  - API endpoints documentation
  - Response schemas
  - Risk calculation
  - Error handling
  - Future enhancements
- **Status:** NEW, comprehensive

#### `IMPLEMENTATION_SUMMARY.md` (What Was Done)
- **Purpose:** Summary of work completed
- **Content:**
  - What was implemented
  - System architecture
  - API endpoints
  - Data flow examples
  - File modifications
  - Performance metrics
- **Status:** NEW, detailed summary

#### `VERIFICATION_CHECKLIST.md` (Testing Guide)
- **Purpose:** Verify integration is working
- **Content:**
  - Pre-flight checklist
  - Startup checklist
  - API testing procedures
  - Frontend testing procedures
  - Performance verification
  - Debugging guide
- **Status:** NEW, comprehensive

#### `FILE_GUIDE.md` (This File)
- **Purpose:** Complete file guide
- **Content:**
  - File structure
  - File dependencies
  - Data flow
  - File descriptions
- **Status:** NEW, complete reference

---

## 🚀 Quick File Reference

### To Start the System
1. **Backend API:** Run `python api_server.py`
2. **Frontend:** Run `cd frontend && npm run dev`

### To Test
- **API Tests:** Run `python test_integration.py`
- **Manual Tests:** Use `curl` commands from documentation
- **Frontend Tests:** Use browser at `http://localhost:5173`

### To Debug
- **API Logs:** Check terminal running `api_server.py`
- **Frontend Logs:** Open DevTools (F12) in browser
- **Network Logs:** Check Network tab in DevTools

### To Configure
- **Backend:** Edit `/Users/aaravkohli/idk/.env`
- **Frontend:** Edit `/Users/aaravkohli/idk/frontend/.env`

### To Understand
1. Start with `README.md` (overview)
2. Read `QUICK_START.md` (setup)
3. Check `INTEGRATION_GUIDE.md` (details)
4. Use `VERIFICATION_CHECKLIST.md` (testing)

---

## 📊 File Statistics

### Code Files
- Backend: ~500 lines (safe_llm.py + api_server.py)
- Frontend: ~2000 lines (React components)
- Total: ~2500 lines of code

### Documentation
- 6 documentation files
- ~4000 lines of documentation
- Comprehensive guides and references

### Configuration
- 2 `.env` files (backend + frontend)
- 5 config files (vite, ts, package, etc.)

---

## ✅ Integration Checklist

Files that need to exist:
- [x] `safe_llm.py` - Backend engine
- [x] `api_server.py` - REST API
- [x] `frontend/src/lib/apiService.ts` - API client
- [x] `frontend/src/pages/Index.tsx` - Updated main component
- [x] `frontend/.env` - API configuration
- [x] `.env` - Backend configuration
- [x] Documentation files

Files that are optional but recommended:
- [x] `test_integration.py` - Integration tests
- [x] `README.md` - Main documentation
- [x] `QUICK_START.md` - Quick start
- [x] All other guide files

---

## 🔧 Modifying Files

### If you need to change...

**API Endpoints?**
- Edit: `api_server.py`
- Restart: `python api_server.py`

**Risk Calculation?**
- Edit: `safe_llm.py` function `final_risk()`
- Restart: Both servers

**Frontend Components?**
- Edit: `src/components/*.tsx`
- Rebuild: Automatic with hot reload

**API URL?**
- Edit: `frontend/.env`
- Restart: Frontend dev server

**Threat Patterns?**
- Edit: `safe_llm.py` patterns
- Restart: API server

---

## 📚 File Navigation

### By Purpose

**User Interface**
- `Index.tsx` - Main page
- `components/*.tsx` - UI components
- `index.css` - Styling

**API Communication**
- `apiService.ts` - Frontend client
- `api_server.py` - Backend server
- Network requests go through port 5000

**Security Analysis**
- `safe_llm.py` - Detection engine
- ML models from Hugging Face
- LLM from Google

**Configuration**
- `.env` - Backend config
- `frontend/.env` - Frontend config
- `package.json` - Dependencies

**Documentation**
- `README.md` - Start here
- `QUICK_START.md` - Fast setup
- `INTEGRATION_GUIDE.md` - Details
- `VERIFICATION_CHECKLIST.md` - Testing

---

## 🎯 File Import Map

```
Index.tsx
├── imports apiService.ts
│   └── calls /api/analyze endpoints
├── imports PromptInput.tsx
├── imports ResultCard.tsx
├── imports RiskMeter.tsx
├── imports SecurityConfidence.tsx
├── imports RiskBreakdown.tsx
└── imports ExamplePrompts.tsx

api_server.py
├── imports safe_llm.py
├── imports flask
└── imports flask_cors

safe_llm.py
├── imports google.generativeai
├── imports transformers
└── imports custom patterns
```

---

## 🚦 Status Summary

### ✅ Complete & Working
- Backend security engine (safe_llm.py)
- REST API server (api_server.py)
- Frontend UI (React components)
- API client (apiService.ts)
- Full integration
- All documentation

### 🟡 Tested & Verified
- Health check endpoint
- Safe prompt analysis
- Dangerous prompt detection
- Risk-only analysis
- Batch analysis
- Frontend build (0 errors)
- Browser display (no console errors)

### 🟢 Ready for Production
- Backend security engine
- API server
- Frontend application
- Error handling
- Type safety
- Documentation

---

## 📞 File Support

If you need help with a file:

1. **Technical issues?** → Check INTEGRATION_GUIDE.md
2. **Setup problems?** → Check QUICK_START.md
3. **Testing?** → Check VERIFICATION_CHECKLIST.md
4. **Code questions?** → Check file comments
5. **Architecture?** → Check IMPLEMENTATION_SUMMARY.md

---

**All files are in place and the integration is complete!** ✅

For the next steps, see [QUICK_START.md](QUICK_START.md)
