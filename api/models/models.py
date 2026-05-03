"""
LokMat API — SQLAlchemy ORM models.

Defines the database schema for users, sessions, messages, and audit logs.
Per GEMINI.md: persistent storage via Cloud SQL (PostgreSQL).
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class User(Base):
    """Registered voter user."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    phone = Column(String(15), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    full_name_hi = Column(String(200), default="")
    epic_no = Column(String(10), unique=True, nullable=False, index=True)
    dob = Column(String(10), nullable=False)
    gender = Column(Enum("male", "female", "other", name="gender_enum"), nullable=False)
    father_name = Column(String(200), default="")
    address = Column(String(500), default="")
    state = Column(String(100), nullable=False)
    constituency = Column(String(200), default="")
    part_no = Column(String(20), default="")
    serial_no = Column(String(20), default="")
    profile_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")


class ChatSession(Base):
    """AI chat session for context tracking."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), default="Election Query")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    """Individual message in a chat session."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    role = Column(Enum("user", "assistant", name="role_enum"), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(20), default="query")
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(50), default="gemini-2.5-flash")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    session = relationship("ChatSession", back_populates="messages")


class AuditLog(Base):
    """Audit trail for all significant actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_phone = Column(String(15), nullable=True)
    action = Column(String(100), nullable=False)
    detail = Column(Text, default="")
    intent = Column(String(20), default="")
    model = Column(String(50), default="")
    tokens = Column(Integer, default=0)
    latency_ms = Column(Integer, default=0)
    status = Column(String(20), default="success")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
