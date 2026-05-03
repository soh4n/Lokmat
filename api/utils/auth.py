"""
LokMat API — Authentication utilities.

Supports two auth modes:
1. Firebase Admin SDK (production) — verifies Firebase ID tokens
2. Local JWT (development) — simple HMAC-signed JWTs

Mode is controlled by FIREBASE_AUTH_ENABLED in config.
"""

import logging
from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from api.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()

# Firebase Admin SDK — lazy initialized
_firebase_app = None


def _init_firebase() -> None:
    """Initialize Firebase Admin SDK on first use."""
    global _firebase_app
    if _firebase_app is not None:
        return

    try:
        # In production: uses Application Default Credentials (ADC)
        # Cloud Run automatically provides the service account credentials
        import firebase_admin
        from firebase_admin import credentials
        if settings.testing:
            raise Exception("Testing mode, skipping ADC")
        cred = credentials.ApplicationDefault()
        _firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": settings.gcp_project_id,
        })
        logger.info(
            "Firebase Admin SDK initialized",
            extra={"project_id": settings.gcp_project_id},
        )
    except Exception as e:
        logger.error(f"Firebase Admin SDK initialization failed: {e}")
        raise


# --- Token Creation (Local JWT mode) ---

def create_access_token(phone: str) -> tuple[str, int]:
    """
    Create a JWT access token for the given phone number.

    Args:
        phone: Verified phone number (e.g. +919876543210).

    Returns:
        Tuple of (token_string, expiry_seconds).
    """
    expires_delta = timedelta(minutes=settings.jwt_expiry_minutes)
    expire = datetime.now(UTC) + expires_delta

    payload = {
        "sub": phone,
        "exp": expire,
        "iat": datetime.now(UTC),
        "iss": "lokmat-api",
    }

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


# --- Token Verification ---

def verify_token(token: str) -> str | None:
    """
    Verify a token and return the user identifier.

    In Firebase mode: verifies Firebase ID token, returns Firebase UID.
    In local mode: verifies HMAC JWT, returns phone number.

    Args:
        token: Token string (Firebase ID token or local JWT).

    Returns:
        User identifier string if valid, None if invalid/expired.
    """
    if settings.firebase_auth_enabled:
        return _verify_firebase_token(token)
    return _verify_local_jwt(token)


def _verify_firebase_token(token: str) -> str | None:
    """
    Verify a Firebase ID token using Firebase Admin SDK.

    Returns the Firebase UID as the user identifier.
    """
    try:
        _init_firebase()
        from firebase_admin import auth

        decoded = auth.verify_id_token(token, check_revoked=True)
        uid = decoded.get("uid")
        phone = decoded.get("phone_number")
        logger.info(
            "Firebase token verified",
            extra={"uid": uid, "phone": phone},
        )
        # Return phone if available, else UID
        return cast(str | None, phone or uid)
    except Exception as e:
        logger.warning(
            "Firebase token verification failed",
            extra={"error": str(e)},
        )
        return None


def _verify_local_jwt(token: str) -> str | None:
    """
    Verify a locally-issued HMAC JWT token.

    Returns the phone number (subject claim).
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        phone: str | None = payload.get("sub")
        if phone is None:
            return None
        return phone
    except JWTError as e:
        logger.warning("Token verification failed", extra={"error": str(e)})
        return None


# --- FastAPI Dependency ---

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    FastAPI dependency — extracts and verifies the current user from JWT/Firebase token.

    Args:
        credentials: Bearer token from Authorization header.

    Returns:
        User identifier (phone number or Firebase UID).

    Raises:
        HTTPException 401: If token is missing, invalid, or expired.
    """
    user_id = verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
