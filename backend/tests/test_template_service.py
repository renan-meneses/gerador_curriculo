import pytest
from app.services.template_service import (
    TemplateValidator,
    TemplateRenderer,
    sanitize_template_html,
)


class TestTemplateValidator:
    def test_validate_entry_path_traversal(self):
        validator = TemplateValidator()
        assert not validator._validate_entry("../etc/passwd")
        assert not validator._validate_entry("/etc/passwd")
        assert not validator._validate_entry("foo/../../bar")

    def test_validate_html_blocked_scripts(self):
        validator = TemplateValidator()
        validator._validate_html("<script>alert('xss')</script>")
        assert len(validator.errors) > 0

    def test_validate_html_blocked_onclick(self):
        validator = TemplateValidator()
        validator._validate_html("<div onclick='alert(1)'>Click</div>")
        assert len(validator.errors) > 0


class TestTemplateRenderer:
    def test_render_variable_substitution(self):
        renderer = TemplateRenderer("<h1>{{ resume.personalInformation.fullName }}</h1>")
        result = renderer.render({
            "personalInformation": {"fullName": "John Doe"},
        })
        assert "<h1>John Doe</h1>" in result

    def test_render_missing_variable(self):
        renderer = TemplateRenderer("<p>{{ resume.nonexistent.field }}</p>")
        result = renderer.render({"personalInformation": {}})
        assert "<p></p>" in result

    def test_render_loop(self):
        renderer = TemplateRenderer(
            "{% for exp in resume.experiences %}"
            "<p>{{ exp.position }} at {{ exp.company }}</p>"
            "{% endfor %}"
        )
        result = renderer.render({
            "experiences": [
                {"position": "Engineer", "company": "ACME"},
                {"position": "Manager", "company": "XYZ"},
            ]
        })
        assert "<p>Engineer at ACME</p>" in result
        assert "<p>Manager at XYZ</p>" in result

    def test_render_nested_variables(self):
        renderer = TemplateRenderer("{% for skill in resume.skills %}{{ skill.skillName }},{% endfor %}")
        result = renderer.render({
            "skills": [
                {"skillName": "Python"},
                {"skillName": "JavaScript"},
            ]
        })
        assert "Python,JavaScript," in result


class TestSanitizeHTML:
    def test_removes_scripts(self):
        result = sanitize_template_html("<script>alert('xss')</script><p>Safe</p>")
        assert "<script>" not in result
        assert "<p>Safe</p>" in result

    def test_allows_safe_tags(self):
        result = sanitize_template_html("<h1>Title</h1><p>Content</p><strong>Bold</strong>")
        assert "<h1>Title</h1>" in result
        assert "<strong>Bold</strong>" in result

    def test_removes_event_handlers(self):
        result = sanitize_template_html("<div onclick='evil()'>Click</div>")
        assert "onclick" not in result
