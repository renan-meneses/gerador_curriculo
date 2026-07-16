from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.job import AISuggestion, ResumeJobAnalysis
from app.models.resume import Resume

router = APIRouter()


class AISuggestionResponse(BaseModel):
    id: str
    section: str
    field: Optional[str]
    original_text: Optional[str]
    suggested_text: Optional[str]
    reason: Optional[str]
    related_requirement: Optional[str]
    confidence: Optional[float]
    status: str
    analysis_id: str

    class Config:
        from_attributes = True


@router.get("/{analysis_id}", response_model=list[AISuggestionResponse])
async def list_suggestions(
    analysis_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResumeJobAnalysis).where(ResumeJobAnalysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    suggestions_result = await db.execute(
        select(AISuggestion).where(AISuggestion.analysis_id == analysis_id)
        .order_by(AISuggestion.sort_order)
    )
    suggestions = suggestions_result.scalars().all()
    return [
        AISuggestionResponse(
            id=str(s.id),
            section=s.section,
            field=s.field,
            original_text=s.original_text,
            suggested_text=s.suggested_text,
            reason=s.reason,
            related_requirement=s.related_requirement,
            confidence=s.confidence,
            status=s.status,
            analysis_id=str(s.analysis_id),
        )
        for s in suggestions
    ]


@router.post("/{suggestion_id}/accept")
async def accept_suggestion(
    suggestion_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AISuggestion).where(AISuggestion.id == suggestion_id))
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestion.status = "accepted"
    await db.flush()
    return {"message": "Suggestion accepted", "suggestion_id": suggestion_id}


@router.post("/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AISuggestion).where(AISuggestion.id == suggestion_id))
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestion.status = "rejected"
    await db.flush()
    return {"message": "Suggestion rejected", "suggestion_id": suggestion_id}


class EditSuggestionRequest(BaseModel):
    edited_text: str


@router.post("/{suggestion_id}/edit")
async def edit_suggestion(
    suggestion_id: str,
    request: EditSuggestionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(AISuggestion).where(AISuggestion.id == suggestion_id))
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestion.user_edited_text = request.edited_text
    suggestion.status = "edited"
    await db.flush()
    return {"message": "Suggestion edited", "suggestion_id": suggestion_id}
