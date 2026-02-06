# Firebase Authentication Integration

Firebase authentication has been successfully integrated into the PromptGuard application!

## 🎉 What's Been Added

### Frontend (React + TypeScript)
- ✅ Firebase SDK installed and configured
- ✅ Authentication context with hooks
- ✅ Login page with email/password and Google authentication
- ✅ Signup page with user registration
- ✅ Forgot password page with password reset
- ✅ Protected routes (requires authentication)
- ✅ User profile menu in header with logout
- ✅ Automatic token inclusion in API requests

### Backend (FastAPI + Python)
- ✅ Firebase Admin SDK installed
- ✅ Token verification middleware
- ✅ Optional and required authentication decorators
- ✅ User context available in API endpoints
- ✅ Firebase initialization on startup

## 📁 New Files Created

### Frontend
- `src/lib/firebase.ts` - Firebase configuration
- `src/contexts/AuthContext.tsx` - Authentication context provider
- `src/components/ProtectedRoute.tsx` - Route protection component
- `src/pages/Login.tsx` - Login page
- `src/pages/Signup.tsx` - Signup page
- `src/pages/ForgotPassword.tsx` - Password reset page

### Backend
- `promptguard/auth/firebase_auth.py` - Firebase authentication middleware
- `promptguard/auth/__init__.py` - Auth module exports

### Configuration
- `frontend/.env.example` - Updated with Firebase config
- `.env.example` - Updated with Firebase service account path
- `FIREBASE_AUTH_SETUP.md` - Complete setup guide

## 🚀 Next Steps

### 1. Set Up Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Authentication (Email/Password and Google)
4. Get your web app configuration

### 2. Configure Frontend
```bash
cd frontend
cp .env.example .env
# Edit .env and add your Firebase config values
```

### 3. Configure Backend
1. Download service account key from Firebase Console
2. Create `.env` in the root directory
3. Set `FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json`

### 4. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 5. Test the Integration
```bash
# Start backend
python run.py

# Start frontend (in another terminal)
cd frontend
npm run dev
```

Visit `http://localhost:5173` - you'll be redirected to login!

## 🔐 Security Features

- **Token-based authentication** - Secure JWT tokens from Firebase
- **Protected routes** - Automatic redirect to login for unauthenticated users
- **Password reset** - Built-in forgot password functionality
- **Google Sign-in** - One-click authentication with Google
- **Automatic token refresh** - Seamless user experience
- **Backend token verification** - All API requests validated
- **User context** - Access user info in all API endpoints

## 📖 Documentation

See `FIREBASE_AUTH_SETUP.md` for detailed setup instructions, including:
- Step-by-step Firebase configuration
- Environment variable setup
- Adding authentication to API endpoints
- Deployment instructions
- Troubleshooting guide

## 🎨 UI Components

The authentication UI uses your existing shadcn/ui components:
- Cards for page layout
- Forms with validation
- Buttons with loading states
- Alerts for errors and messages
- Dropdown menu for user profile
- Avatar for user display

## 🔧 Customization

### Make Authentication Optional
To make specific routes public, remove the `<ProtectedRoute>` wrapper in `App.tsx`.

### Add More Auth Methods
Enable additional providers (GitHub, Facebook, etc.) in Firebase Console and add buttons in Login/Signup pages.

### Customize User Profile
Extend `FirebaseUser` class in `firebase_auth.py` to include custom claims and additional user data.

## ⚠️ Important Notes

1. **Never commit `.env` files** - They contain sensitive configuration
2. **Secure service account keys** - Add `serviceAccountKey.json` to `.gitignore`
3. **Configure CORS** - Update allowed origins for production
4. **Enable email verification** - Recommended for production use
5. **Set password policies** - Configure in Firebase Console

## 📝 Modified Files

- `frontend/package.json` - Added firebase dependency
- `frontend/src/App.tsx` - Added auth provider and routes
- `frontend/src/components/Header.tsx` - Added user menu
- `frontend/src/lib/apiService.ts` - Added token to requests
- `promptguard/api/main.py` - Added Firebase initialization
- `requirements.txt` - Added firebase-admin
- `requirements_updated.txt` - Added firebase-admin

Enjoy your secure, authenticated PromptGuard application! 🚀🔐
