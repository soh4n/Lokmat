"""
LokMat API — Pydantic schemas for request/response validation.

All API contracts defined here. No raw dicts in routers.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

# --- Auth Schemas ---

class OTPRequest(BaseModel):
    """Request to send OTP to a mobile number."""
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$", description="Indian mobile number with +91 prefix")


class OTPVerifyRequest(BaseModel):
    """Request to verify OTP and get auth token."""
    phone: str = Field(..., pattern=r"^\+91[6-9]\d{9}$")
    otp: str = Field(..., min_length=6, max_length=6)


class AuthToken(BaseModel):
    """JWT auth token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# --- User / Voter Profile Schemas ---

class Gender(str, Enum):
    """Gender enum for voter profile."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class VoterProfileCreate(BaseModel):
    """Request to create/update voter profile."""
    full_name: str = Field(..., min_length=2, max_length=200)
    full_name_hi: str = Field(default="", max_length=200)
    epic_no: str = Field(..., min_length=10, max_length=10, description="EPIC Voter ID number")
    dob: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    gender: Gender
    father_name: str = Field(default="", max_length=200)
    address: str = Field(default="", max_length=500)
    state: str = Field(..., min_length=2, max_length=100)
    constituency: str = Field(default="", max_length=200)
    part_no: str = Field(default="", max_length=20)
    serial_no: str = Field(default="", max_length=20)

    @field_validator("epic_no")
    @classmethod
    def validate_epic(cls, v: str) -> str:
        """Validate EPIC format: 3 uppercase letters + 7 digits."""
        v = v.upper()
        if not (v[:3].isalpha() and v[3:].isdigit()):
            raise ValueError("EPIC must be 3 letters followed by 7 digits (e.g. ABC1234567)")
        return v


class VoterProfileResponse(BaseModel):
    """Voter profile response with metadata."""
    id: str
    phone: str
    full_name: str
    full_name_hi: str
    epic_no: str
    dob: str
    gender: Gender
    father_name: str
    address: str
    state: str
    constituency: str
    part_no: str
    serial_no: str
    profile_complete: bool
    created_at: datetime
    updated_at: datetime


# --- Chat Schemas ---

class IntentType(str, Enum):
    """Classification of user intent for routing."""
    QUERY = "query"
    ACTION = "action"
    CLARIFY = "clarify"
    OUT_OF_SCOPE = "out_of_scope"


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=5000)


class ChatRequest(BaseModel):
    """Request to send a message to the AI assistant."""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="")
    history: list[ChatMessage] = Field(default_factory=list, max_length=20)


class ChatResponse(BaseModel):
    """AI assistant response."""
    model_config = {"protected_namespaces": ()}

    message: str
    intent: IntentType
    session_id: str
    suggestions: list[str] = Field(default_factory=list)
    is_fallback: bool = False
    model_used: str = "gemini-2.5-flash"
    tokens_used: int = 0


# --- Health ---

class HealthResponse(BaseModel):
    """Health check response for all services."""
    status: str
    db: str = "unknown"
    gemini: str
    redis: str = "unknown"
    version: str
