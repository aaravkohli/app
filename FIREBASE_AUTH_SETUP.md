# Firebase Authentication Setup Guide

## Overview
Firebase Authentication has been integrated into the PromptGuard application, providing secure user authentication for both the frontend and backend.

## Frontend Setup

### 1. Install Dependencies
Firebase SDK is already added to the frontend dependencies.

### 2. Configure Firebase
Create a `.env` file in the `frontend` folder based on `.env.example`:

```bash
cd frontend
cp .env.example .env
```

Update the Firebase configuration values in `.env`:
```env
VITE_FIREBASE_API_KEY=your_api_key_here
VITE_FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### 3. Get Firebase Configuration
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select an existing one
3. Click on the web icon (</>) to add a web app
4. Copy the configuration values to your `.env` file

### 4. Enable Authentication Methods
In Firebase Console:
1. Go to Authentication → Sign-in method
2. Enable "Email/Password" provider
3. (Optional) Enable "Google" provider for Google Sign-in

## Backend Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This includes `firebase-admin` for token verification.

### 2. Create Firebase Service Account
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file securely (e.g., `serviceAccountKey.json`)
4. **IMPORTANT**: Add this file to `.gitignore` - never commit it to version control

### 3. Configure Backend
Create a `.env` file in the root folder:

```env
FIREBASE_SERVICE_ACCOUNT_PATH=/path/to/serviceAccountKey.json
```

**For production (e.g., Render, Heroku):**
Set the service account JSON content as an environment variable or use secure file storage.

## Features Included

### Frontend
- **Login Page** (`/login`) - Email/password and Google authentication
- **Signup Page** (`/signup`) - User registration with email/password or Google
- **Protected Routes** - Main app requires authentication
- **User Profile Menu** - Shows user info and logout option in header
- **Auth Context** - Global authentication state management
- **Token Management** - Automatic token refresh and inclusion in API requests

### Backend
- **Firebase Token Verification** - Validates Firebase ID tokens
- **Optional Authentication** - Routes can require or optionally accept auth
- **User Context** - Access authenticated user info in API endpoints
- **Secure API Calls** - All authenticated requests include user information

## Usage

### Protecting Routes (Frontend)
Routes are automatically protected. The main app (`/`) requires authentication.

### Adding Auth to Backend Endpoints
For required authentication:
```python
from fastapi import Depends
from promptguard.auth import verify_firebase_token, FirebaseUser

@app.post("/api/protected")
async def protected_endpoint(
    user: FirebaseUser = Depends(verify_firebase_token)
):
    # user.uid, user.email, user.name available
    return {"message": f"Hello {user.email}"}
```

For optional authentication:
```python
from promptguard.auth import optional_firebase_auth, FirebaseUser

@app.post("/api/optional")
async def optional_endpoint(
    user: Optional[FirebaseUser] = Depends(optional_firebase_auth)
):
    if user:
        return {"message": f"Authenticated as {user.email}"}
    return {"message": "Anonymous access"}
```

## Testing

### Local Development
1. Start the backend: `python run.py`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173`
4. You'll be redirected to `/login`
5. Create an account or sign in

### Testing Authentication
- Try accessing the main page - you should be redirected to login
- Sign up with a new account
- Log out and log back in
- Test Google Sign-in (if enabled)

## Security Notes

1. **Never commit** service account keys or Firebase config with real values
2. Use environment variables for all sensitive configuration
3. Enable email verification in Firebase Console for production
4. Set up password policies in Firebase Console
5. Configure authorized domains in Firebase Console
6. Use Firebase Security Rules to protect backend resources

## Deployment

### Frontend (Vercel/Netlify)
Add Firebase environment variables in the hosting platform's settings.

### Backend (Render/Heroku)
1. Add `FIREBASE_SERVICE_ACCOUNT_PATH` or set service account JSON as env variable
2. Ensure `firebase-admin` is in `requirements.txt`
3. Configure CORS to allow your frontend domain

## Troubleshooting

**"No authorization token provided"**
- Ensure user is logged in
- Check that token is included in API requests

**"Invalid token"**
- Token may have expired - frontend should refresh automatically
- Verify Firebase configuration matches between frontend and backend

**"Firebase Admin SDK initialization failed"**
- Check that service account path is correct
- Verify service account JSON is valid
- Ensure proper permissions on the service account file
