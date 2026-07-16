import json
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.import_export import ImportRecord

logger = logging.getLogger(__name__)


class LinkedInImporter:
    async def process(self, record: ImportRecord, db: AsyncSession) -> dict:
        raw_data = record.raw_data or {}
        content = raw_data.get("linkedin_data", "") or raw_data.get("file_content", "")

        if not content:
            record.status = "failed"
            record.errors.append("No LinkedIn data provided")
            return {"status": "failed", "errors": record.errors}

        try:
            parsed = json.loads(content) if content.startswith("{") else self._parse_text(content)
        except json.JSONDecodeError:
            parsed = self._parse_text(content)

        record.parsed_data = parsed
        normalized = self._normalize(parsed)
        record.normalized_data = normalized
        record.status = "parsed"
        record.warnings.append("Review all imported data before saving")
        return {"status": "parsed", "sections": list(normalized.keys()), "warnings": record.warnings}

    def _parse_text(self, text: str) -> dict:
        sections = {}
        current_section = "header"
        current_content = []
        section_keywords = {
            "about": ["about", "summary", "professional summary"],
            "experience": ["experience", "work experience", "employment"],
            "education": ["education", "academic"],
            "skills": ["skills", "skill", "top skills"],
            "certifications": ["certifications", "certificates", "licenses"],
            "projects": ["projects"],
            "languages": ["languages"],
            "volunteer": ["volunteer", "volunteering"],
            "publications": ["publications", "published"],
            "courses": ["courses"],
            "honors": ["honors", "awards", "honors & awards"],
        }

        for line in text.split("\n"):
            line_stripped = line.strip()
            matched_section = None
            for section_name, keywords in section_keywords.items():
                for kw in keywords:
                    if line_stripped.lower().startswith(kw) and len(line_stripped) < 40:
                        matched_section = section_name
                        break
                if matched_section:
                    break
            if matched_section:
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = matched_section
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _normalize(self, parsed: dict) -> dict:
        normalized = {}
        section_mapping = {
            "header": "personal_information",
            "about": "summary",
            "experience": "experiences",
            "education": "education",
            "skills": "skills",
            "certifications": "certifications",
            "projects": "projects",
            "languages": "languages",
            "volunteer": "volunteer_experience",
            "publications": "publications",
        }
        for source_key, target_key in section_mapping.items():
            if source_key in parsed:
                normalized[target_key] = parsed[source_key]
        return normalized
