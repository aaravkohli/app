"""
Firebase Authentication Middleware for PromptGuard (FastAPI)
Verifies Firebase ID tokens and extracts user information
"""

import os
from typing import Optional
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import firebase_admin
from firebase_admin import credentials, auth

security = HTTPBearer(auto_error=False)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
        print("✅ Firebase Admin SDK already initialized")
    except ValueError:
        # Initialize with service account or application default credentials
        # For production: Set GOOGLE_APPLICATION_CREDENTIALS environment variable
        # For development: Can use a service account JSON file
        
        cred_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
        if cred_path and os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin SDK initialized with service account")
        else:
            # Use application default credentials or initialize without credentials for testing
            try:
                firebase_admin.initialize_app()
                print("✅ Firebase Admin SDK initialized with default credentials")
            except Exception as e:
                print(f"⚠️ Firebase Admin SDK initialization warning: {str(e)}")
                print("⚠️ Authentication will be available but token verification may fail")

class FirebaseUser:
    """Represents authenticated Firebase user"""
    def __init__(self, uid: str, email: Optional[str], name: Optional[str], email_verified: bool):
        self.uid = uid
        self.email = email
        self.name = name
        self.email_verified = email_verified

async def verify_firebase_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> FirebaseUser:
    """
    Dependency to verify Firebase ID token from Authorization header
    Raises HTTPException if token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="No authorization token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(token)
        
        return FirebaseUser(
            uid=decoded_token['uid'],
            email=decoded_token.get('email'),
            name=decoded_token.get('name'),
            email_verified=decoded_token.get('email_verified', False)
        )
        
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"Token verification error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def optional_firebase_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Optional[FirebaseUser]:
    """
    Optional authentication dependency
    Returns FirebaseUser if token is valid, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        
        return FirebaseUser(
            uid=decoded_token['uid'],
            email=decoded_token.get('email'),
            name=decoded_token.get('name'),
            email_verified=decoded_token.get('email_verified', False)
        )
    except Exception as e:
        print(f"Optional auth failed: {str(e)}")
        return None

