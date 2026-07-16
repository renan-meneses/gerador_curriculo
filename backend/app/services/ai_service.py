import os
import json
import logging
from typing import Optional, Any
from app.ai.gemini import gemini_service, GeminiResponse

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "ai", "prompts")


class PromptManager:
    def __init__(self):
        self._cache: dict[str, str] = {}

    def load_prompt(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        filepath = os.path.join(PROMPTS_DIR, f"{name}.txt")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Prompt file not found: {name}.txt")
        with open(filepath, "r") as f:
            prompt = f.read()
        self._cache[name] = prompt
        return prompt

    def get_version(self, name: str) -> str:
        return "1.0.0"


prompt_manager = PromptManager()


class AIService:
    def __init__(self):
        self.gemini = gemini_service
        self.prompts = prompt_manager

    def _format_prompt(self, template: str, **kwargs: Any) -> str:
        return template.format(**kwargs)

    def _get_analysis_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "match_score": {"type": "number"},
                "matched_requirements": {"type": "array", "items": {"type": "string"}},
                "missing_requirements": {"type": "array", "items": {"type": "string"}},
                "matched_keywords": {"type": "array", "items": {"type": "string"}},
                "missing_keywords": {"type": "array", "items": {"type": "string"}},
                "recommended_changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "section": {"type": "string"},
                            "field": {"type": "string"},
                            "original_text": {"type": "string"},
                            "suggested_text": {"type": "string"},
                            "reason": {"type": "string"},
                            "related_requirement": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                    },
                },
                "weak_sections": {"type": "array", "items": {"type": "string"}},
                "unsupported_claims": {"type": "array", "items": {"type": "string"}},
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "match_score", "matched_requirements", "missing_requirements",
                "matched_keywords", "missing_keywords", "recommended_changes",
                "weak_sections", "unsupported_claims", "warnings",
            ],
        }

    def analyze_resume_job(
        self, resume_data: dict, job_data: dict
    ) -> GeminiResponse:
        prompt_template = self.prompts.load_prompt("resume_analysis")
        prompt = self._format_prompt(
            prompt_template,
            resume_data=json.dumps(resume_data, indent=2),
            job_data=json.dumps(job_data, indent=2),
        )
        return self.gemini.generate(prompt, response_schema=self._get_analysis_schema())

    def summarize_job(self, job_description: str) -> GeminiResponse:
        prompt_template = self.prompts.load_prompt("job_extraction")
        prompt = self._format_prompt(job_description=job_description)
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "company": {"type": "string"},
                "responsibilities": {"type": "array", "items": {"type": "string"}},
                "required_qualifications": {"type": "array", "items": {"type": "string"}},
                "preferred_qualifications": {"type": "array", "items": {"type": "string"}},
                "technical_requirements": {"type": "array", "items": {"type": "string"}},
                "behavioral_competencies": {"type": "array", "items": {"type": "string"}},
                "keywords": {"type": "array", "items": {"type": "string"}},
                "seniority_level": {"type": "string"},
            },
            "required": ["title", "responsibilities", "required_qualifications", "preferred_qualifications", "keywords"],
        }
        return self.gemini.generate(prompt, response_schema=schema)

    def rewrite_summary(
        self, original_summary: str, user_profile: dict, job_data: dict
    ) -> GeminiResponse:
        prompt_template = self.prompts.load_prompt("summary_rewrite")
        prompt = self._format_prompt(
            original_summary=original_summary,
            user_profile=json.dumps(user_profile, indent=2),
            job_data=json.dumps(job_data, indent=2),
        )
        schema = {
            "type": "object",
            "properties": {
                "rewritten_summary": {"type": "string"},
                "changes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string"},
                            "related_requirement": {"type": "string"},
                        },
                    },
                },
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["rewritten_summary", "changes", "warnings"],
        }
        return self.gemini.generate(prompt, response_schema=schema)

    def rewrite_experience(
        self, experience_data: dict, job_data: Optional[dict] = None
    ) -> GeminiResponse:
        prompt_template = self.prompts.load_prompt("experience_rewrite")
        prompt = self._format_prompt(
            experience_data=json.dumps(experience_data, indent=2),
            job_data=json.dumps(job_data or {}, indent=2),
        )
        schema = {
            "type": "object",
            "properties": {
                "rewritten_bullets": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original": {"type": "string"},
                            "rewritten": {"type": "string"},
                            "reason": {"type": "string"},
                            "confidence": {"type": "number"},
                        },
                    },
                },
                "warnings": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["rewritten_bullets", "warnings"],
        }
        return self.gemini.generate(prompt, response_schema=schema)


ai_service = AIService()
