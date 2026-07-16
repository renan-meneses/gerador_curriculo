from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "resume_builder",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    task_soft_time_limit=540,
    worker_max_tasks_per_child=200,
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def export_resume_task(self, export_id: str):
    from app.services.document_export import DocumentExportService
    service = DocumentExportService()
    return service.process_export(export_id)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_import_task(self, import_id: str):
    from app.importers.markdown_importer import MarkdownImporter
    from app.importers.linkedin_importer import LinkedInImporter
    from app.models.import_export import ImportRecord
    from app.core.database import async_session_factory
    from sqlalchemy import select

    async def _process():
        async with async_session_factory() as db:
            result = await db.execute(
                select(ImportRecord).where(ImportRecord.id == import_id)
            )
            record = result.scalar_one_or_none()
            if not record:
                return {"error": "Import not found"}
            if record.import_type == "markdown":
                importer = MarkdownImporter()
            elif record.import_type == "linkedin":
                importer = LinkedInImporter()
            else:
                return {"error": f"Unknown import type: {record.import_type}"}
            result = await importer.process(record, db)
            return result

    import asyncio
    return asyncio.run(_process())


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def analyze_resume_job_task(self, analysis_id: str):
    from app.services.ai_service import ai_service
    from app.models.job import ResumeJobAnalysis, JobDescription
    from app.models.resume import Resume
    from app.core.database import async_session_factory
    from sqlalchemy import select
    import json

    async def _analyze():
        async with async_session_factory() as db:
            result = await db.execute(
                select(ResumeJobAnalysis).where(ResumeJobAnalysis.id == analysis_id)
            )
            analysis = result.scalar_one_or_none()
            if not analysis:
                return {"error": "Analysis not found"}
            resume_result = await db.execute(
                select(Resume).where(Resume.id == analysis.resume_id)
            )
            resume = resume_result.scalar_one_or_none()
            job_result = await db.execute(
                select(JobDescription).where(JobDescription.id == analysis.job_id)
            )
            job = job_result.scalar_one_or_none()
            if not resume or not job:
                return {"error": "Resume or job not found"}
            resume_data = _build_resume_dict(resume)
            job_data = {
                "title": job.title,
                "company": job.company_name,
                "required_qualifications": job.required_qualifications,
                "preferred_qualifications": job.preferred_qualifications,
                "technical_requirements": job.technical_requirements,
                "keywords": job.keywords,
                "responsibilities": job.responsibilities,
            }
            ai_response = ai_service.analyze_resume_job(resume_data, job_data)
            if ai_response.success and ai_response.parsed:
                analysis.analysis_data = ai_response.parsed
                analysis.overall_score = ai_response.parsed.get("match_score")
                analysis.matched_requirements = ai_response.parsed.get("matched_requirements", [])
                analysis.missing_requirements = ai_response.parsed.get("missing_requirements", [])
                analysis.matched_keywords = ai_response.parsed.get("matched_keywords", [])
                analysis.missing_keywords = ai_response.parsed.get("missing_keywords", [])
                analysis.recommended_changes = ai_response.parsed.get("recommended_changes", [])
                await db.flush()
                return {"status": "completed", "analysis_id": analysis_id}
            return {"status": "failed", "error": ai_response.error}

    import asyncio
    return asyncio.run(_analyze())


def _build_resume_dict(resume) -> dict:
    data = {
        "personal_information": {},
        "summary": "",
        "experiences": [],
        "education": [],
        "skills": [],
        "certifications": [],
        "projects": [],
        "languages": [],
    }
    if resume.personal_info:
        pi = resume.personal_info
        data["personal_information"] = {
            "full_name": pi.full_name,
            "professional_title": pi.professional_title,
            "email": pi.email,
        }
    if hasattr(resume, "summaries") and resume.summaries:
        data["summary"] = resume.summaries[0].original_text or resume.summaries[0].ai_optimized_text or ""
    for exp in resume.experiences:
        data["experiences"].append({
            "company": exp.company,
            "position": exp.position,
            "start_date": str(exp.start_date) if exp.start_date else None,
            "end_date": str(exp.end_date) if exp.end_date else None,
            "is_current": exp.is_current,
            "technologies": exp.technologies,
            "keywords": exp.keywords,
            "achievements": exp.achievements,
        })
    for edu in resume.education_records:
        data["education"].append({
            "institution": edu.institution,
            "degree": edu.degree,
            "field_of_study": edu.field_of_study,
        })
    for skill in resume.skills:
        data["skills"].append({
            "skill_name": skill.skill_name,
            "category": skill.category,
            "proficiency": skill.proficiency,
        })
    for cert in resume.certifications:
        data["certifications"].append({
            "name": cert.name,
            "issuer": cert.issuer,
        })
    for proj in resume.projects:
        data["projects"].append({
            "name": proj.name,
            "technologies": proj.technologies,
        })
    for lang in resume.languages:
        data["languages"].append({
            "language": lang.language,
            "proficiency": lang.proficiency,
        })
    return data
