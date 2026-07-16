import pytest
from app.services.scoring import (
    ResumeScoringEngine,
    normalize_text,
    calculate_skill_match,
    calculate_keyword_coverage,
)


class TestNormalizeText:
    def test_basic(self):
        assert normalize_text("Python, Java, and C++") == "python java and c"


class TestSkillMatch:
    def test_full_match(self):
        req_score, pref_score, matched, missing = calculate_skill_match(
            ["Python", "JavaScript", "Docker"],
            ["Python", "JavaScript"],
            ["Kubernetes"],
        )
        assert req_score == 100.0
        assert "Python" in matched
        assert "JavaScript" in matched

    def test_partial_match(self):
        req_score, pref_score, matched, missing = calculate_skill_match(
            ["Python"],
            ["Python", "JavaScript", "Docker"],
            [],
        )
        assert req_score == pytest.approx(33.33, rel=0.1)
        assert "Python" in matched
        assert "JavaScript" in missing

    def test_no_match(self):
        req_score, pref_score, matched, missing = calculate_skill_match(
            ["Python"],
            ["Go", "Rust"],
            [],
        )
        assert req_score == 0.0
        assert len(missing) == 2


class TestKeywordCoverage:
    def test_full_coverage(self):
        coverage, matched, missing = calculate_keyword_coverage(
            "Experienced Python developer with Django and PostgreSQL skills",
            ["Python", "Django", "PostgreSQL"],
        )
        assert coverage == 100.0
        assert len(matched) == 3
        assert len(missing) == 0

    def test_partial_coverage(self):
        coverage, matched, missing = calculate_keyword_coverage(
            "Python developer",
            ["Python", "Django", "PostgreSQL", "AWS"],
        )
        assert coverage == 25.0
        assert len(matched) == 1
        assert len(missing) == 3


class TestScoringEngine:
    def test_deterministic_scoring(self):
        engine = ResumeScoringEngine()
        score = engine.score(
            resume_data={
                "skills": [{"skill_name": "Python"}, {"skill_name": "Docker"}],
                "experiences": [],
                "personal_information": {"full_name": "Test User"},
                "summary": "A Python developer",
            },
            job_data={
                "required_qualifications": ["Python", "Docker"],
                "preferred_qualifications": [],
                "technical_requirements": ["Python"],
                "keywords": ["Python", "Docker"],
            },
        )
        assert score.required_match == 100.0
        assert score.technical_match == 100.0
        assert score.ats_keyword_coverage == 100.0
        assert score.overall > 0

    def test_empty_resume(self):
        engine = ResumeScoringEngine()
        score = engine.score(
            resume_data={
                "skills": [],
                "experiences": [],
                "personal_information": {},
                "summary": "",
            },
            job_data={
                "required_qualifications": ["Python"],
                "preferred_qualifications": ["AWS"],
                "technical_requirements": ["Docker"],
                "keywords": ["Python", "AWS"],
            },
        )
        assert score.required_match == 0.0
        assert score.overall == 0.0
