import uuid
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from app.models.base import TimestampMixin, UUIDMixin


class Template(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "templates"

    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    author: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_built_in: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    page_size: Mapped[str] = mapped_column(String(10), default="A4", nullable=False)
    supported_sections: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    fonts: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    variables: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preview_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user = relationship("User", back_populates="templates")
    versions = relationship("TemplateVersion", back_populates="template", cascade="all, delete-orphan")


class TemplateVersion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "template_versions"

    template_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("templates.id"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    html_content: Mapped[str] = mapped_column(Text, nullable=False)
    css_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    assets: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    template = relationship("Template", back_populates="versions")
