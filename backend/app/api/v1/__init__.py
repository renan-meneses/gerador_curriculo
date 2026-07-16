from fastapi import APIRouter
from app.api.v1 import auth, resumes, jobs, templates, imports, exports, ai

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["Resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Job Descriptions"])
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(imports.router, prefix="/imports", tags=["Imports"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
api_router.include_router(ai.router, prefix="/ai-suggestions", tags=["AI Suggestions"])
