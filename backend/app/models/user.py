import uuid
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    google_id: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)
    linkedin_id: Mapped[str | None] = mapped_column(String(200), nullable=True, unique=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    ai_consent_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_consent_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    data_export_requested: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    job_descriptions = relationship("JobDescription", back_populates="user", cascade="all, delete-orphan")
    templates = relationship("Template", back_populates="user", cascade="all, delete-orphan")
    imports = relationship("ImportRecord", back_populates="user", cascade="all, delete-orphan")
    exports = relationship("ExportRecord", back_populates="user", cascade="all, delete-orphan")
    ai_usage = relationship("AIUsageRecord", back_populates="user", cascade="all, delete-orphan")
