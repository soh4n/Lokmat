"""
Unit tests — Pydantic schema validation.

Per GEMINI.md testing requirements:
- Malformed request bodies → 422
- Validates phone format, EPIC format, field lengths
"""

import pytest
from pydantic import ValidationError

from api.schemas.schemas import (
    ChatRequest,
    OTPRequest,
    OTPVerifyRequest,
    VoterProfileCreate,
)


class TestOTPRequest:
    """Tests for OTP request phone validation."""

    def test_valid_phone_accepted(self) -> None:
        req = OTPRequest(phone="+919876543210")
        assert req.phone == "+919876543210"

    def test_invalid_phone_rejected_no_prefix(self) -> None:
        with pytest.raises(ValidationError):
            OTPRequest(phone="9876543210")

    def test_invalid_phone_rejected_wrong_start(self) -> None:
        with pytest.raises(ValidationError):
            OTPRequest(phone="+911234567890")

    def test_invalid_phone_rejected_too_short(self) -> None:
        with pytest.raises(ValidationError):
            OTPRequest(phone="+91987654")

    def test_invalid_phone_rejected_letters(self) -> None:
        with pytest.raises(ValidationError):
            OTPRequest(phone="+91abcdefghij")


class TestOTPVerifyRequest:
    """Tests for OTP verify request validation."""

    def test_valid_otp(self) -> None:
        req = OTPVerifyRequest(phone="+919876543210", otp="123456")
        assert req.otp == "123456"

    def test_otp_too_short(self) -> None:
        with pytest.raises(ValidationError):
            OTPVerifyRequest(phone="+919876543210", otp="123")

    def test_otp_too_long(self) -> None:
        with pytest.raises(ValidationError):
            OTPVerifyRequest(phone="+919876543210", otp="1234567890")


class TestVoterProfileCreate:
    """Tests for voter profile creation schema."""

    def _valid_profile(self, **overrides) -> None:  # type: ignore
        data = {
            "full_name": "Rajesh Kumar",
            "epic_no": "ABC1234567",
            "dob": "1990-05-15",
            "gender": "male",
            "state": "Maharashtra",
        }
        data.update(overrides)
        return VoterProfileCreate(**data)  # type: ignore


    def test_valid_profile(self) -> None:  # type: ignore
        profile = self._valid_profile()  # type: ignore
        assert profile.full_name == "Rajesh Kumar"  # type: ignore
        assert profile.epic_no == "ABC1234567"

    def test_epic_normalized_to_uppercase(self) -> None:  # type: ignore
        profile = self._valid_profile(epic_no="abc1234567")  # type: ignore
        assert profile.epic_no == "ABC1234567"

    def test_invalid_epic_all_numbers(self) -> None:
        with pytest.raises(ValidationError):
            self._valid_profile(epic_no="1234567890")

    def test_invalid_epic_all_letters(self) -> None:
        with pytest.raises(ValidationError):
            self._valid_profile(epic_no="ABCDEFGHIJ")

    def test_name_too_short(self) -> None:
        with pytest.raises(ValidationError):
            self._valid_profile(full_name="R")

    def test_missing_required_state(self) -> None:
        with pytest.raises(ValidationError):  # type: ignore
            VoterProfileCreate(
                full_name="Rajesh",
                epic_no="ABC1234567",
                dob="1990-01-01",  # type: ignore
                gender="male",
                # state missing
            )


class TestChatRequest:
    """Tests for chat request validation."""

    def test_valid_chat(self) -> None:
        req = ChatRequest(message="How to register to vote?")
        assert req.message == "How to register to vote?"
        assert req.history == []

    def test_empty_message_rejected(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_message_too_long(self) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(message="x" * 2001)

    def test_history_with_valid_messages(self) -> None:
        req = ChatRequest(
            message="Follow up question",
            history=[  # type: ignore
                {"role": "user", "content": "Hello"},  # type: ignore
                {"role": "assistant", "content": "Namaste!"},
            ],
        )
        assert len(req.history) == 2
