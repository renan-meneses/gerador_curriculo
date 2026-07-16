from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.resume import Resume, ResumeVersion
from app.models.template import Template

router = APIRouter()


class PersonalInfoSchema(BaseModel):
    full_name: str
    professional_title: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    website_url: Optional[str] = None


class ResumeCreateRequest(BaseModel):
    title: str
    target_job_title: Optional[str] = None
    target_company: Optional[str] = None
    locale: str = "en"
    personal_info: Optional[PersonalInfoSchema] = None


class ResumeSummaryResponse(BaseModel):
    id: str
    title: str
    target_job_title: Optional[str]
    target_company: Optional[str]
    locale: str
    is_archived: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ResumeDetailResponse(BaseModel):
    id: str
    title: str
    target_job_title: Optional[str]
    target_company: Optional[str]
    locale: str
    is_archived: bool
    source: Optional[str]
    created_at: str
    updated_at: str
    version_count: int

    class Config:
        from_attributes = True


@router.get("", response_model=list[ResumeSummaryResponse])
async def list_resumes(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.user_id == user.id, Resume.is_archived == False)
        .order_by(Resume.updated_at.desc())
    )
    resumes = result.scalars().all()
    return [
        ResumeSummaryResponse(
            id=str(r.id),
            title=r.title,
            target_job_title=r.target_job_title,
            target_company=r.target_company,
            locale=r.locale,
            is_archived=r.is_archived,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )
        for r in resumes
    ]


@router.post("", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_resume(
    request: ResumeCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = Resume(
        user_id=user.id,
        title=request.title,
        target_job_title=request.target_job_title,
        target_company=request.target_company,
        locale=request.locale,
    )
    db.add(resume)
    await db.flush()
    return ResumeDetailResponse(
        id=str(resume.id),
        title=resume.title,
        target_job_title=resume.target_job_title,
        target_company=resume.target_company,
        locale=resume.locale,
        is_archived=resume.is_archived,
        source=resume.source,
        created_at=resume.created_at.isoformat(),
        updated_at=resume.updated_at.isoformat(),
        version_count=0,
    )


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
async def get_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    version_result = await db.execute(
        select(ResumeVersion).where(ResumeVersion.resume_id == resume.id)
    )
    version_count = len(version_result.scalars().all())
    return ResumeDetailResponse(
        id=str(resume.id),
        title=resume.title,
        target_job_title=resume.target_job_title,
        target_company=resume.target_company,
        locale=resume.locale,
        is_archived=resume.is_archived,
        source=resume.source,
        created_at=resume.created_at.isoformat(),
        updated_at=resume.updated_at.isoformat(),
        version_count=version_count,
    )


@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    await db.delete(resume)
    return {"message": "Resume deleted"}


@router.post("/{resume_id}/duplicate", response_model=ResumeDetailResponse)
async def duplicate_resume(
    resume_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    original = result.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Resume not found")
    new_resume = Resume(
        user_id=user.id,
        title=f"{original.title} (Copy)",
        target_job_title=original.target_job_title,
        target_company=original.target_company,
        locale=original.locale,
        parent_resume_id=original.id,
    )
    db.add(new_resume)
    await db.flush()
    return ResumeDetailResponse(
        id=str(new_resume.id),
        title=new_resume.title,
        target_job_title=new_resume.target_job_title,
        target_company=new_resume.target_company,
        locale=new_resume.locale,
        is_archived=new_resume.is_archived,
        source=new_resume.source,
        created_at=new_resume.created_at.isoformat(),
        updated_at=new_resume.updated_at.isoformat(),
        version_count=0,
    )
