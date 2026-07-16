import uuid
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class JobDescription(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "job_descriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    job_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    required_qualifications: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    preferred_qualifications: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    technical_requirements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    behavioral_competencies: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)
    seniority_level: Mapped[str | None] = mapped_column(String(50), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employment_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    additional_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_requirements: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    user = relationship("User", back_populates="job_descriptions")
    analyses = relationship("ResumeJobAnalysis", back_populates="job_description", cascade="all, delete-orphan")


class ResumeJobAnalysis(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_job_analyses"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=False, index=True)
    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    required_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    technical_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    experience_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    education_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    ats_keyword_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_requirements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    missing_requirements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    matched_keywords: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    missing_keywords: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    recommended_changes: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    weak_sections: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    unsupported_claims: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    analysis_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    ai_model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ai_prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    resume = relationship("Resume")
    job_description = relationship("JobDescription", back_populates="analyses")
    suggestions = relationship("AISuggestion", back_populates="analysis", cascade="all, delete-orphan")


class AISuggestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_suggestions"

    analysis_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resume_job_analyses.id"), nullable=False, index=True)
    section: Mapped[str] = mapped_column(String(50), nullable=False)
    field: Mapped[str | None] = mapped_column(String(100), nullable=True)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_requirement: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    user_edited_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    analysis = relationship("ResumeJobAnalysis", back_populates="suggestions")
