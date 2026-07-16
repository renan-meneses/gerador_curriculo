from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.import_export import ExportRecord

router = APIRouter()


class ExportRequest(BaseModel):
    resume_id: str
    format: str
    template_id: Optional[str] = None
    options: dict = {}


class ExportStatusResponse(BaseModel):
    id: str
    format: str
    status: str
    file_path: Optional[str]
    file_size: Optional[int]
    error_message: Optional[str]
    created_at: str
    completed_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/pdf", status_code=status.HTTP_202_ACCEPTED)
async def export_pdf(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    export_record = ExportRecord(
        user_id=user.id,
        resume_id=request.resume_id,
        template_id=request.template_id,
        format="pdf",
        status="queued",
        options=request.options,
    )
    db.add(export_record)
    await db.flush()
    return {
        "export_id": str(export_record.id),
        "message": "PDF export queued",
        "status": "queued",
    }


@router.post("/docx", status_code=status.HTTP_202_ACCEPTED)
async def export_docx(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    export_record = ExportRecord(
        user_id=user.id,
        resume_id=request.resume_id,
        template_id=request.template_id,
        format="docx",
        status="queued",
        options=request.options,
    )
    db.add(export_record)
    await db.flush()
    return {
        "export_id": str(export_record.id),
        "message": "DOCX export queued",
        "status": "queued",
    }


@router.post("/markdown", status_code=status.HTTP_202_ACCEPTED)
async def export_markdown(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    export_record = ExportRecord(
        user_id=user.id,
        resume_id=request.resume_id,
        format="markdown",
        status="queued",
        options=request.options,
    )
    db.add(export_record)
    await db.flush()
    return {
        "export_id": str(export_record.id),
        "message": "Markdown export queued",
        "status": "queued",
    }


@router.post("/html", status_code=status.HTTP_202_ACCEPTED)
async def export_html(
    request: ExportRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    export_record = ExportRecord(
        user_id=user.id,
        resume_id=request.resume_id,
        template_id=request.template_id,
        format="html",
        status="queued",
        options=request.options,
    )
    db.add(export_record)
    await db.flush()
    return {
        "export_id": str(export_record.id),
        "message": "HTML export queued",
        "status": "queued",
    }


@router.get("/{export_id}/status", response_model=ExportStatusResponse)
async def get_export_status(
    export_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExportRecord).where(ExportRecord.id == export_id, ExportRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Export not found")
    return ExportStatusResponse(
        id=str(record.id),
        format=record.format,
        status=record.status,
        file_path=record.file_path,
        file_size=record.file_size,
        error_message=record.error_message,
        created_at=record.created_at.isoformat(),
        completed_at=record.completed_at.isoformat() if record.completed_at else None,
    )


@router.get("/{export_id}/download")
async def download_export(
    export_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExportRecord).where(ExportRecord.id == export_id, ExportRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Export not found")
    if record.status != "completed":
        raise HTTPException(status_code=400, detail="Export not yet completed")
    if not record.file_path:
        raise HTTPException(status_code=404, detail="Export file not found")
    return {"download_url": record.file_path}
