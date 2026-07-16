from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.import_export import ImportRecord

router = APIRouter()


class ImportStatusResponse(BaseModel):
    id: str
    import_type: str
    source: str
    status: str
    warnings: list[str]
    errors: list[str]
    created_at: str

    class Config:
        from_attributes = True


class ConfirmImportRequest(BaseModel):
    import_id: str
    selected_sections: list[str] = []
    edits: dict = {}


@router.post("/linkedin")
async def import_linkedin(
    resume_id: Optional[str] = Form(None),
    linkedin_data: str = Form(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    import_record = ImportRecord(
        user_id=user.id,
        import_type="linkedin",
        source="manual",
        status="pending",
        raw_data={"linkedin_data": linkedin_data},
    )
    db.add(import_record)
    await db.flush()
    return {
        "import_id": str(import_record.id),
        "message": "LinkedIn data received, processing...",
        "status": "pending",
    }


@router.post("/linkedin-export")
async def import_linkedin_export(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await file.read()
    import_record = ImportRecord(
        user_id=user.id,
        import_type="linkedin",
        source="export",
        status="processing",
        file_name=file.filename,
        file_size=len(content),
        raw_data={"file_content": content.decode("utf-8")},
    )
    db.add(import_record)
    await db.flush()
    return {
        "import_id": str(import_record.id),
        "message": "LinkedIn export file received, processing...",
        "status": "processing",
    }


@router.post("/markdown")
async def import_markdown(
    file: UploadFile = File(None),
    content: str = Form(None),
    resume_id: Optional[str] = Form(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not file and not content:
        raise HTTPException(status_code=400, detail="Either file or content is required")
    md_content = content or (await file.read()).decode("utf-8")
    import_record = ImportRecord(
        user_id=user.id,
        import_type="markdown",
        source="upload" if file else "paste",
        status="processing",
        file_name=file.filename if file else None,
        file_size=len(md_content),
        raw_data={"content": md_content},
    )
    db.add(import_record)
    await db.flush()
    return {
        "import_id": str(import_record.id),
        "message": "Markdown received, processing...",
        "status": "processing",
    }


@router.get("/{import_id}/status", response_model=ImportStatusResponse)
async def get_import_status(
    import_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImportRecord).where(ImportRecord.id == import_id, ImportRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Import not found")
    return ImportStatusResponse(
        id=str(record.id),
        import_type=record.import_type,
        source=record.source,
        status=record.status,
        warnings=record.warnings,
        errors=record.errors,
        created_at=record.created_at.isoformat(),
    )


@router.post("/{import_id}/confirm")
async def confirm_import(
    import_id: str,
    request: ConfirmImportRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ImportRecord).where(ImportRecord.id == import_id, ImportRecord.user_id == user.id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Import not found")
    record.status = "confirmed"
    record.selected_sections = request.selected_sections
    await db.flush()
    return {"message": "Import confirmed", "import_id": import_id}
