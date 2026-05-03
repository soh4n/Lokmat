"""
LokMat API — Voter profile router.

CRUD operations for voter profiles.
All routes require authentication.

POST   /voter/profile — Create or update voter profile
GET    /voter/profile — Get current user's voter profile
"""

import logging
from datetime import UTC, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas.schemas import VoterProfileCreate, VoterProfileResponse
from api.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voter", tags=["Voter Profile"])

# In-memory store (demo — production uses Cloud SQL)
_profiles: dict[str, dict] = {}


@router.post("/profile", response_model=VoterProfileResponse)
async def create_or_update_profile(
    profile: VoterProfileCreate,
    phone: str = Depends(get_current_user),
) -> VoterProfileResponse:
    """
    Create or update the voter profile for the authenticated user.

    Args:
        profile: Voter profile data.
        phone:   Authenticated user's phone number.

    Returns:
        Complete voter profile with metadata.
    """
    now = datetime.now(UTC)
    existing = _profiles.get(phone)

    profile_data = {
        "id": existing["id"] if existing else str(uuid4()),
        "phone": phone,
        **profile.model_dump(),
        "profile_complete": True,
        "created_at": existing["created_at"] if existing else now,
        "updated_at": now,
    }

    _profiles[phone] = profile_data
    logger.info(f"Profile {'updated' if existing else 'created'} for {phone}")

    return VoterProfileResponse(**profile_data)


@router.get("/profile", response_model=VoterProfileResponse)
async def get_profile(
    phone: str = Depends(get_current_user),
) -> VoterProfileResponse:
    """
    Get the voter profile for the authenticated user.

    Args:
        phone: Authenticated user's phone number.

    Returns:
        Voter profile data.

    Raises:
        HTTPException 404: If no profile exists.
    """
    profile = _profiles.get(phone)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please create your profile first.",
        )
    return VoterProfileResponse(**profile)
