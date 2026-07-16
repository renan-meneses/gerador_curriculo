import uuid
from datetime import date, datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Resume(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    target_job_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    target_company: Mapped[str | None] = mapped_column(String(200), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_resume_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    original_markdown: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="resumes")
    versions = relationship("ResumeVersion", back_populates="resume", cascade="all, delete-orphan")
    personal_info = relationship("PersonalInformation", back_populates="resume", uselist=False, cascade="all, delete-orphan")
    summaries = relationship("ProfessionalSummary", back_populates="resume", cascade="all, delete-orphan")
    experiences = relationship("WorkExperience", back_populates="resume", cascade="all, delete-orphan")
    education_records = relationship("EducationRecord", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
    languages = relationship("Language", back_populates="resume", cascade="all, delete-orphan")
    custom_sections = relationship("CustomSection", back_populates="resume", cascade="all, delete-orphan")


class ResumeVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_versions"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    target_job_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("job_descriptions.id"), nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=True)
    snapshot_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_prompt_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resume = relationship("Resume", back_populates="versions")


class PersonalInformation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "personal_information"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    professional_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    resume = relationship("Resume", back_populates="personal_info")


class ProfessionalSummary(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "professional_summaries"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    original_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_optimized_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_specific_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version_label: Mapped[str | None] = mapped_column(String(50), nullable=True)

    resume = relationship("Resume", back_populates="summaries")


class WorkExperience(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "work_experiences"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    position: Mapped[str] = mapped_column(String(200), nullable=False)
    employment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsibilities: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    achievements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    technologies: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    quantified_results: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    keywords: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    approval_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="experiences")


class EducationRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "education_records"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    institution: Mapped[str] = mapped_column(String(200), nullable=False)
    degree: Mapped[str | None] = mapped_column(String(200), nullable=True)
    field_of_study: Mapped[str | None] = mapped_column(String(200), nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    gpa: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="education_records")


class ResumeSkill(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "resume_skills"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    proficiency: Mapped[str | None] = mapped_column(String(30), nullable=True)
    years_of_experience: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_used_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="skills")


class Certification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "certifications"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    issuer: Mapped[str | None] = mapped_column(String(200), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    credential_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credential_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="certifications")


class Project(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "projects"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    role: Mapped[str | None] = mapped_column(String(100), nullable=True)
    technologies: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    repository_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    achievements: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="projects")


class Language(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "languages"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[str | None] = mapped_column(String(30), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="languages")


class CustomSection(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "custom_sections"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False, index=True)
    section_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    resume = relationship("Resume", back_populates="custom_sections")
