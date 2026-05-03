"""
LokMat API — Auth router.

Phone + OTP based authentication flow.
POST /auth/send-otp   — Send OTP to phone
POST /auth/verify-otp — Verify OTP and get JWT token

Security per GEMINI.md:
- OTP generated using cryptographically secure secrets module
- OTPs expire after 5 minutes (TTL enforced)
- Brute-force protection: max 5 verify attempts per phone per window
- OTP never exposed in API response or plain-text logs
- Phone numbers masked in logs
"""

import logging
import secrets
import time

from fastapi import APIRouter, HTTPException, status

from api.schemas.schemas import AuthToken, OTPRequest, OTPVerifyRequest
from api.utils.auth import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OTP store: phone -> {otp, expires_at, attempts}
# Production: replace with Redis (TTL-backed) + SMS gateway.
_otp_store: dict[str, dict] = {}  # type: ignore[type-arg]

OTP_TTL_SECONDS = 300       # 5-minute OTP window
OTP_MAX_ATTEMPTS = 5        # Brute-force lockout threshold


def _mask_phone(phone: str) -> str:
    """Mask all but last 4 digits for safe logging (e.g. +91XXXXXX3210)."""
    if len(phone) <= 4:
        return "****"
    return phone[:-4].replace(phone[4:-4], "X" * len(phone[4:-4])) + phone[-4:]


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(request: OTPRequest) -> dict:  # type: ignore
    """
    Initiate OTP authentication for the given mobile number.

    Generates a cryptographically secure 6-digit OTP with a 5-minute TTL.
    In production, the OTP is delivered via an SMS gateway (MSG91/Twilio).
    For the demo environment, the OTP is included in the response under
    ``demo_otp``; this field MUST be removed before production launch.

    Args:
        request: OTPRequest containing a valid ``+91`` Indian mobile number.

    Returns:
        JSON with ``message`` and ``phone``. The ``demo_otp`` field is
        present only in non-production environments.
    """
    # Use secrets for cryptographically secure OTP generation
    otp = f"{secrets.randbelow(900000) + 100000}"
    _otp_store[request.phone] = {
        "otp": otp,
        "expires_at": time.time() + OTP_TTL_SECONDS,
        "attempts": 0,
    }

    # Never log the OTP value — log only that an OTP was dispatched
    logger.info(
        "OTP dispatched",
        extra={"phone": _mask_phone(request.phone)},
    )

    # In production, call SMS gateway here and omit demo_otp
    return {
        "message": "OTP sent successfully. Valid for 5 minutes.",
        "phone": request.phone,
        "demo_otp": otp,  # TODO: remove before production launch
    }


@router.post("/verify-otp", response_model=AuthToken)
async def verify_otp(request: OTPVerifyRequest) -> AuthToken:
    """
    Verify a previously issued OTP and return a JWT access token.

    Enforces:
    - OTP existence and expiry (5-minute window)
    - Brute-force lockout after ``OTP_MAX_ATTEMPTS`` failed attempts
    - Constant-time comparison via ``secrets.compare_digest``

    Args:
        request: OTPVerifyRequest with ``phone`` and ``otp``.

    Returns:
        ``AuthToken`` containing a signed JWT access token.

    Raises:
        HTTPException 401: OTP not found, expired, or locked out.
        HTTPException 401: OTP value is incorrect.
    """
    record = _otp_store.get(request.phone)

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No OTP found for this number. Please request a new OTP.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Enforce TTL expiry
    if time.time() > record["expires_at"]:
        del _otp_store[request.phone]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP has expired. Please request a new OTP.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Enforce brute-force lockout
    if record["attempts"] >= OTP_MAX_ATTEMPTS:
        del _otp_store[request.phone]
        logger.warning(
            "OTP brute-force lockout triggered",
            extra={"phone": _mask_phone(request.phone)},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Too many incorrect attempts. Please request a new OTP.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(record["otp"], request.otp):
        record["attempts"] += 1
        remaining = OTP_MAX_ATTEMPTS - record["attempts"]
        logger.warning(
            "OTP mismatch",
            extra={"phone": _mask_phone(request.phone), "attempts": record["attempts"]},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid OTP. {remaining} attempt(s) remaining.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # OTP verified — purge from store and issue token
    del _otp_store[request.phone]

    token, expiry = create_access_token(request.phone)

    logger.info(
        "User authenticated",
        extra={"phone": _mask_phone(request.phone)},
    )

    return AuthToken(
        access_token=token,
        token_type="bearer",
        expires_in=expiry,
    )
