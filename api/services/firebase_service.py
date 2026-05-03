"""
LokMat API — Firebase Auth service.

Verifies Firebase ID tokens using the Firebase Admin SDK.
Falls back to disabled state when SDK is not configured (local dev).

Per GEMINI.md: Firebase Auth for Google OAuth 2.0 sign-in;
ID token verification on every request.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

_firebase_app = None
_firebase_available = False


def _init_firebase() -> bool:
    """
    Initialize Firebase Admin SDK.

    Returns True if successfully initialised, False if SDK not configured.
    Designed to fail gracefully so local dev (JWT mode) still works.
    """
    global _firebase_app, _firebase_available

    try:
        import firebase_admin  # type: ignore
        from firebase_admin import credentials

        from api.config import settings

        if firebase_admin._apps:  # Already initialised
            _firebase_available = True
            return True

        # In production: use Application Default Credentials (Cloud Run SA)
        # In dev: falls back gracefully if no credentials are set
        try:
            cred = credentials.ApplicationDefault()
            _firebase_app = firebase_admin.initialize_app(cred, {
                "projectId": settings.gcp_project_id,
            })
            _firebase_available = True
            logger.info(
                "Firebase Admin SDK initialised",
                extra={"project_id": settings.gcp_project_id},
            )
            return True
        except Exception as cred_err:
            logger.warning(
                "Firebase credentials not available — running in JWT-only mode",
                extra={"error": str(cred_err)},
            )
            _firebase_available = False
            return False

    except ImportError:
        logger.warning("firebase-admin not installed — Firebase Auth disabled")
        _firebase_available = False
        return False


# Attempt initialisation at module load
_init_firebase()


async def verify_firebase_token(id_token: str) -> dict[str, Any] | None:
    """
    Verify a Firebase ID token and return the decoded claims.

    Args:
        id_token: Firebase ID token from the frontend (Google OAuth).

    Returns:
        Decoded token claims dict if valid, None otherwise.
        Claims include: uid, email, phone_number, name, etc.
    """
    if not _firebase_available:
        logger.warning("Firebase not available — token verification skipped")
        return None

    try:
        from firebase_admin import auth as firebase_auth

        decoded = firebase_auth.verify_id_token(id_token, check_revoked=True)
        logger.info(
            "Firebase token verified",
            extra={"uid": decoded.get("uid"), "provider": decoded.get("firebase", {}).get("sign_in_provider")},
        )
        return decoded  # type: ignore



    except Exception as e:
        logger.warning("Firebase token verification failed", extra={"error": str(e)})
        return None


def is_firebase_enabled() -> bool:
    """Return True if Firebase Admin SDK is available and initialised."""
    return _firebase_available
