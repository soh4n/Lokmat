"""
LokMat API — Auth router.

Phone + OTP based authentication flow.
POST /auth/send-otp   — Send OTP to phone
POST /auth/verify-otp — Verify OTP and get JWT token
"""

import logging
import random

from fastapi import APIRouter, HTTPException, status

from api.schemas.schemas import AuthToken, OTPRequest, OTPVerifyRequest
from api.utils.auth import create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# In-memory OTP store (demo only — production uses Redis + SMS gateway)
_otp_store: dict[str, str] = {}


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def send_otp(request: OTPRequest) -> dict:  # type: ignore
    """
    Send OTP to the given mobile number.

    In production, this integrates with an SMS gateway (e.g. Twilio, MSG91).
    For demo purposes, OTP is stored in memory and logged.

    Args:
        request: OTPRequest with phone number.

    Returns:
        Success message with OTP hint (demo only).
    """
    otp = f"{random.randint(100000, 999999)}"
    _otp_store[request.phone] = otp

    logger.info(f"OTP generated for {request.phone}: {otp}")

    return {
        "message": "OTP sent successfully",
        "phone": request.phone,
        "demo_otp": otp,  # Remove in production
    }


@router.post("/verify-otp", response_model=AuthToken)
async def verify_otp(request: OTPVerifyRequest) -> AuthToken:
    """
    Verify OTP and return JWT access token.

    Args:
        request: OTPVerifyRequest with phone and OTP.

    Returns:
        AuthToken with JWT access token.

    Raises:
        HTTPException 401: If OTP is invalid or expired.
    """
    stored_otp = _otp_store.get(request.phone)

    if stored_otp is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No OTP found for this number. Please request a new OTP.",
        )

    if stored_otp != request.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP. Please try again.",
        )

    # OTP verified — remove from store and issue token
    del _otp_store[request.phone]

    token, expiry = create_access_token(request.phone)

    logger.info(f"User authenticated: {request.phone}")

    return AuthToken(
        access_token=token,
        token_type="bearer",
        expires_in=expiry,
    )
