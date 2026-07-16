import re
import logging
from typing import Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MatchScore:
    overall: float = 0.0
    required_match: float = 0.0
    preferred_match: float = 0.0
    technical_match: float = 0.0
    experience_match: float = 0.0
    education_match: float = 0.0
    ats_keyword_coverage: float = 0.0
    matched_requirements: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)
    matched_keywords: list[str] = field(default_factory=list)
    missing_keywords: list[str] = field(default_factory=list)


def normalize_text(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower().strip())


def extract_keywords(text: str) -> set[str]:
    words = normalize_text(text).split()
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "shall", "can", "need",
        "able", "about", "into", "over", "after", "before", "between", "under",
        "above", "below", "up", "down", "out", "off", "just", "also", "very",
        "too", "really", "quite", "some", "any", "all", "both", "each", "few",
        "more", "most", "other", "such", "only", "own", "same", "so", "than",
        "too", "very", "just", "because", "using", "used", "including",
    }
    return {w for w in words if len(w) > 1 and w not in stop_words}


def calculate_skill_match(
    resume_skills: list[str],
    required_skills: list[str],
    preferred_skills: list[str],
) -> tuple[float, float, list[str], list[str]]:
    resume_normalized = {normalize_text(s) for s in resume_skills}
    required_normalized = {normalize_text(s) for s in required_skills}
    preferred_normalized = {normalize_text(s) for s in preferred_skills}

    matched_required = [s for s in required_skills if normalize_text(s) in resume_normalized]
    missing_required = [s for s in required_skills if normalize_text(s) not in resume_normalized]

    matched_preferred = [s for s in preferred_skills if normalize_text(s) in resume_normalized]

    required_score = len(matched_required) / max(len(required_skills), 1) * 100
    preferred_score = len(matched_preferred) / max(len(preferred_skills), 1) * 100

    return required_score, preferred_score, matched_required, missing_required


def calculate_keyword_coverage(
    resume_text: str, job_keywords: list[str]
) -> tuple[float, list[str], list[str]]:
    resume_tokens = extract_keywords(resume_text)
    matched = []
    missing = []
    for kw in job_keywords:
        kw_tokens = extract_keywords(kw)
        if kw_tokens and kw_tokens.issubset(resume_tokens):
            matched.append(kw)
        else:
            missing.append(kw)
    coverage = len(matched) / max(len(job_keywords), 1) * 100
    return coverage, matched, missing


def calculate_experience_match(
    total_years: float, required_years: float
) -> float:
    if total_years >= required_years:
        return 100.0
    if required_years > 0:
        return (total_years / required_years) * 100
    return 100.0


class ResumeScoringEngine:
    REQUIRED_WEIGHT = 0.35
    PREFERRED_WEIGHT = 0.15
    TECHNICAL_WEIGHT = 0.20
    EXPERIENCE_WEIGHT = 0.15
    EDUCATION_WEIGHT = 0.05
    ATS_WEIGHT = 0.10

    def score(
        self,
        resume_data: dict[str, Any],
        job_data: dict[str, Any],
    ) -> MatchScore:
        resume_skills = [
            s.get("skill_name", "") for s in resume_data.get("skills", [])
        ]
        required_quals = job_data.get("required_qualifications", [])
        preferred_quals = job_data.get("preferred_qualifications", [])
        tech_reqs = job_data.get("technical_requirements", [])
        job_keywords = job_data.get("keywords", [])

        req_match, pref_match, matched_req, missing_req = calculate_skill_match(
            resume_skills, required_quals, preferred_quals
        )

        tech_match, _, _ = calculate_skill_match(
            resume_skills, tech_reqs, []
        )

        resume_text = " ".join(
            [
                resume_data.get("personal_information", {}).get("full_name", ""),
                resume_data.get("summary", "") or "",
            ]
            + [
                f"{e.get('company', '')} {e.get('position', '')} {' '.join(e.get('technologies', []))} {' '.join(e.get('keywords', []))}"
                for e in resume_data.get("experiences", [])
            ]
        )

        ats_coverage, matched_kws, missing_kws = calculate_keyword_coverage(
            resume_text, job_keywords
        )

        experience_score = calculate_experience_match(
            total_years=sum(
                _calculate_experience_duration(e) for e in resume_data.get("experiences", [])
            ),
            required_years=_extract_required_years(required_quals),
        )

        overall = (
            req_match * self.REQUIRED_WEIGHT
            + pref_match * self.PREFERRED_WEIGHT
            + tech_match * self.TECHNICAL_WEIGHT
            + experience_score * self.EXPERIENCE_WEIGHT
            + ats_coverage * self.ATS_WEIGHT
        )

        return MatchScore(
            overall=round(overall, 1),
            required_match=round(req_match, 1),
            preferred_match=round(pref_match, 1),
            technical_match=round(tech_match, 1),
            experience_match=round(experience_score, 1),
            education_match=0.0,
            ats_keyword_coverage=round(ats_coverage, 1),
            matched_requirements=matched_req,
            missing_requirements=missing_req,
            matched_keywords=matched_kws,
            missing_keywords=missing_kws,
        )


def _calculate_experience_duration(experience: dict) -> float:
    from datetime import date
    start = experience.get("start_date")
    end = experience.get("end_date")
    if not start:
        return 0
    try:
        start_date = date.fromisoformat(start) if isinstance(start, str) else start
        end_date = date.fromisoformat(end) if isinstance(end, str) else (end or date.today())
        delta = end_date - start_date
        return max(0, delta.days / 365.25)
    except (ValueError, TypeError):
        return 0


def _extract_required_years(qualifications: list[str]) -> float:
    for q in qualifications:
        match = re.search(r"(\d+)\+?\s*years?", q, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0


scoring_engine = ResumeScoringEngine()
