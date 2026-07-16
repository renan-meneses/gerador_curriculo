import re
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.import_export import ImportRecord
from app.models.resume import Resume, PersonalInformation, ProfessionalSummary, WorkExperience
from app.models.resume import EducationRecord, ResumeSkill, Certification, Project, Language

logger = logging.getLogger(__name__)

SECTION_PATTERNS = {
    "summary": re.compile(r"^#{1,2}\s*(professional\s*summary|about|profile|summary)\s*$", re.IGNORECASE),
    "experience": re.compile(r"^#{1,2}\s*(experience|work\s*experience|employment|professional\s*experience|career)\s*$", re.IGNORECASE),
    "education": re.compile(r"^#{1,2}\s*(education|academic|qualifications|academic\s*background)\s*$", re.IGNORECASE),
    "skills": re.compile(r"^#{1,2}\s*(skills|technical\s*skills|competencies|core\s*competencies)\s*$", re.IGNORECASE),
    "certifications": re.compile(r"^#{1,2}\s*(certifications|certificates|professional\s*certifications)\s*$", re.IGNORECASE),
    "projects": re.compile(r"^#{1,2}\s*(projects|personal\s*projects|side\s*projects)\s*$", re.IGNORECASE),
    "languages": re.compile(r"^#{1,2}\s*(languages|language)\s*$", re.IGNORECASE),
    "name": re.compile(r"^#\s+(.+)$", re.MULTILINE),
}


class MarkdownImporter:
    async def process(self, record: ImportRecord, db: AsyncSession) -> dict:
        content = ""
        if record.raw_data:
            content = record.raw_data.get("content", "")
        if not content and record.file_path:
            try:
                with open(record.file_path, "r") as f:
                    content = f.read()
            except FileNotFoundError:
                record.status = "failed"
                record.errors.append("File not found")
                return {"status": "failed", "errors": record.errors}

        parsed = self._parse_markdown(content)
        record.parsed_data = parsed
        record.normalized_data = self._normalize(parsed)
        record.status = "parsed"
        return {"status": "parsed", "sections": list(parsed.keys())}

    def _parse_markdown(self, content: str) -> dict:
        lines = content.split("\n")
        sections = {}
        current_section = "header"
        current_content = []

        name_match = SECTION_PATTERNS["name"].search(content)
        if name_match:
            sections["full_name"] = name_match.group(1).strip()

        for line in lines:
            matched_section = None
            for section_name, pattern in SECTION_PATTERNS.items():
                if section_name == "name":
                    continue
                if pattern.match(line.strip()):
                    matched_section = section_name
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
        if "full_name" in parsed:
            normalized["personal_information"] = {"full_name": parsed["full_name"]}
        if "summary" in parsed:
            normalized["summary"] = parsed["summary"]
        if "experience" in parsed:
            normalized["experiences"] = self._parse_experience_section(parsed["experience"])
        if "education" in parsed:
            normalized["education"] = self._parse_education_section(parsed["education"])
        if "skills" in parsed:
            normalized["skills"] = self._parse_skills_section(parsed["skills"])
        if "certifications" in parsed:
            normalized["certifications"] = self._parse_certifications_section(parsed["certifications"])
        if "projects" in parsed:
            normalized["projects"] = self._parse_projects_section(parsed["projects"])
        if "languages" in parsed:
            normalized["languages"] = self._parse_languages_section(parsed["languages"])
        return normalized

    def _parse_experience_section(self, text: str) -> list[dict]:
        entries = []
        blocks = re.split(r"\n\s*\n", text.strip())
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            entry = {"company": "", "position": "", "description": "", "technologies": [], "achievements": []}
            for i, line in enumerate(lines):
                if i == 0:
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        entry["position"] = parts[0]
                        entry["company"] = parts[1] if len(parts) > 1 else parts[0]
                    elif "," in line:
                        parts = [p.strip() for p in line.split(",", 1)]
                        entry["position"] = parts[0]
                        entry["company"] = parts[1] if len(parts) > 1 else parts[0]
                    else:
                        entry["position"] = line
                elif line.startswith("-") or line.startswith("*"):
                    bullet = line.lstrip("-* ").strip()
                    entry["achievements"].append(bullet)
                else:
                    entry["description"] = (entry["description"] + " " + line).strip()
            entries.append(entry)
        return entries

    def _parse_education_section(self, text: str) -> list[dict]:
        entries = []
        blocks = re.split(r"\n\s*\n", text.strip())
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            entry = {"institution": "", "degree": "", "field_of_study": ""}
            for i, line in enumerate(lines):
                if i == 0:
                    if "|" in line:
                        parts = [p.strip() for p in line.split("|")]
                        entry["institution"] = parts[0]
                        entry["degree"] = parts[1] if len(parts) > 1 else ""
                    elif "," in line:
                        parts = [p.strip() for p in line.split(",", 1)]
                        entry["institution"] = parts[0]
                        entry["degree"] = parts[1] if len(parts) > 1 else ""
                    else:
                        entry["institution"] = line
                else:
                    if not entry["field_of_study"]:
                        entry["field_of_study"] = line
            entries.append(entry)
        return entries

    def _parse_skills_section(self, text: str) -> list[dict]:
        skills = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("-* ").strip()
            if not line:
                continue
            if ":" in line:
                parts = [p.strip() for p in line.split(":", 1)]
                category = parts[0]
                for skill in re.split(r"[,|]", parts[1]):
                    skill = skill.strip()
                    if skill:
                        skills.append({"skill_name": skill, "category": category})
            else:
                for skill in re.split(r"[,|]", line):
                    skill = skill.strip()
                    if skill:
                        skills.append({"skill_name": skill})
        return skills

    def _parse_certifications_section(self, text: str) -> list[dict]:
        certs = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("-* ").strip()
            if not line:
                continue
            certs.append({"name": line})
        return certs

    def _parse_projects_section(self, text: str) -> list[dict]:
        projects = []
        blocks = re.split(r"\n\s*\n", text.strip())
        for block in blocks:
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if not lines:
                continue
            project = {"name": lines[0], "description": "", "technologies": []}
            for line in lines[1:]:
                if line.startswith("-") or line.startswith("*"):
                    project["achievements"] = project.get("achievements", [])
                    project["achievements"].append(line.lstrip("-* ").strip())
                else:
                    project["description"] = (project["description"] + " " + line).strip()
            projects.append(project)
        return projects

    def _parse_languages_section(self, text: str) -> list[dict]:
        languages = []
        for line in text.strip().split("\n"):
            line = line.strip().lstrip("-* ").strip()
            if not line:
                continue
            if ":" in line:
                parts = [p.strip() for p in line.split(":", 1)]
                languages.append({"language": parts[0], "proficiency": parts[1]})
            elif "-" in line:
                parts = [p.strip() for p in line.split("-", 1)]
                languages.append({"language": parts[0], "proficiency": parts[1]})
            else:
                languages.append({"language": line, "proficiency": ""})
        return languages
