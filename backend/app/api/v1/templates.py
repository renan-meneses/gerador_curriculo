from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.template import Template, TemplateVersion

router = APIRouter()


class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    page_size: str = "A4"
    supported_sections: list[str] = []
    is_shared: bool = False


class TemplateResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    version: str
    author: Optional[str]
    is_built_in: bool
    is_shared: bool
    page_size: str
    category: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.get("", response_model=list[TemplateResponse])
async def list_templates(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Template).where(
            (Template.user_id == user.id) | (Template.is_built_in == True) | (Template.is_shared == True)
        ).order_by(Template.name)
    )
    templates = result.scalars().all()
    return [
        TemplateResponse(
            id=str(t.id),
            name=t.name,
            description=t.description,
            version=t.version,
            author=t.author,
            is_built_in=t.is_built_in,
            is_shared=t.is_shared,
            page_size=t.page_size,
            category=t.category,
            created_at=t.created_at.isoformat(),
        )
        for t in templates
    ]


@router.post("", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    request: TemplateCreateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    template = Template(
        user_id=user.id,
        name=request.name,
        description=request.description,
        page_size=request.page_size,
        supported_sections=request.supported_sections,
        is_shared=request.is_shared,
    )
    db.add(template)
    await db.flush()
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        version=template.version,
        author=template.author,
        is_built_in=template.is_built_in,
        is_shared=template.is_shared,
        page_size=template.page_size,
        category=template.category,
        created_at=template.created_at.isoformat(),
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Template).where(Template.id == template_id))
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if not template.is_built_in and not template.is_shared and template.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return TemplateResponse(
        id=str(template.id),
        name=template.name,
        description=template.description,
        version=template.version,
        author=template.author,
        is_built_in=template.is_built_in,
        is_shared=template.is_shared,
        page_size=template.page_size,
        category=template.category,
        created_at=template.created_at.isoformat(),
    )


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Template).where(Template.id == template_id, Template.user_id == user.id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned")
    await db.delete(template)
    return {"message": "Template deleted"}
