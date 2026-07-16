from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job import JobDescription, ResumeJobAnalysis, AISuggestion
from app.models.resume import Resume

router = APIRouter()


class JobCreateRequest(BaseModel):
    title: str
    company_name: Optional[str] = None
    job_description: Optional[str] = None
    responsibilities: list[str] = []
    required_qualifications: list[str] = []
    preferred_qualifications: list[str] = []
    technical_requirements: list[str] = []
    behavioral_competencies: list[str] = []
    keywords: list[str] = []
    industry: Optional[str] = None
    seniority_level: Optional[str] = None
    language: str = "en"
    location: Optional[str] = None
    employment_model: Optional[str] = None
    additional_instructions: Optional[str] = None


class JobSummaryResponse(BaseModel):
    id: str
    title: str
    company_name: Optional[str]
    industry: Optional[str]
    seniority_level: Optional[str]
    language: str
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[JobSummaryResponse])
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobDescription).where(JobDescription.user_id == user.id)
        .order_by(JobDescription.updated_at.desc())
    )
    jobs = result.scalars().all()
    return [
        JobSummaryResponse(
            id=str(j.id),
            title=j.title,
            company_name=j.company_name,
            industry=j.industry,
            seniority_level=j.seniority_level,
            language=j.language,
            created_at=j.created_at.isoformat(),
        )
        for j in jobs
    ]


@router.post("", response_model=JobSummaryResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    request: JobCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job = JobDescription(
        user_id=user.id,
        title=request.title,
        company_name=request.company_name,
        job_description=request.job_description,
        responsibilities=request.responsibilities,
        required_qualifications=request.required_qualifications,
        preferred_qualifications=request.preferred_qualifications,
        technical_requirements=request.technical_requirements,
        behavioral_competencies=request.behavioral_competencies,
        keywords=request.keywords,
        industry=request.industry,
        seniority_level=request.seniority_level,
        language=request.language,
        location=request.location,
        employment_model=request.employment_model,
        additional_instructions=request.additional_instructions,
    )
    db.add(job)
    await db.flush()
    return JobSummaryResponse(
        id=str(job.id),
        title=job.title,
        company_name=job.company_name,
        industry=job.industry,
        seniority_level=job.seniority_level,
        language=job.language,
        created_at=job.created_at.isoformat(),
    )


@router.get("/{job_id}", response_model=JobCreateRequest)
async def get_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobDescription).where(JobDescription.id == job_id, JobDescription.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobCreateRequest(
        title=job.title,
        company_name=job.company_name,
        job_description=job.job_description,
        responsibilities=job.responsibilities,
        required_qualifications=job.required_qualifications,
        preferred_qualifications=job.preferred_qualifications,
        technical_requirements=job.technical_requirements,
        behavioral_competencies=job.behavioral_competencies,
        keywords=job.keywords,
        industry=job.industry,
        seniority_level=job.seniority_level,
        language=job.language,
        location=job.location,
        employment_model=job.employment_model,
        additional_instructions=job.additional_instructions,
    )


@router.post("/{job_id}/analyze")
async def analyze_job(
    job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobDescription).where(JobDescription.id == job_id, JobDescription.user_id == user.id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Analysis queued", "job_id": job_id}
