import os
import re
import json
import zipfile
import logging
import hashlib
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

MAX_TEMPLATE_SIZE_MB = 5
MAX_TEMPLATE_FILES = 50
ALLOWED_EXTENSIONS = {".html", ".css", ".json", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", ".md"}

TEMPLATE_VARIABLE_PATTERN = re.compile(r"\{\{\s*resume\.([a-zA-Z0-9_.]+)\s*\}\}")
TEMPLATE_LOOP_PATTERN = re.compile(r"\{\%\s*for\s+(\w+)\s+in\s+resume\.([a-zA-Z0-9_.]+)\s*\%\}(.*?)\{\%\s*endfor\s*%\}", re.DOTALL)

BLOCKED_PATTERNS = [
    r"<script[^>]*>",
    r"javascript\s*:",
    r"on\w+\s*=",
    r"document\.(cookie|domain|location)",
    r"window\.(localStorage|sessionStorage)",
    r"fetch\s*\(",
    r"XMLHttpRequest",
    r"WebSocket",
    r"eval\s*\(",
    r"Function\s*\(",
]


class TemplateValidator:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_package(self, file_path: str) -> bool:
        self.errors = []
        self.warnings = []

        file_size = os.path.getsize(file_path)
        if file_size > MAX_TEMPLATE_SIZE_MB * 1024 * 1024:
            self.errors.append(f"File size exceeds {MAX_TEMPLATE_SIZE_MB}MB limit")
            return False

        try:
            with zipfile.ZipFile(file_path, "r") as zf:
                file_count = len(zf.namelist())
                if file_count > MAX_TEMPLATE_FILES:
                    self.errors.append(f"Too many files: {file_count} (max {MAX_TEMPLATE_FILES})")
                    return False

                has_template_html = False
                has_template_json = False

                for entry in zf.namelist():
                    if not self._validate_entry(entry):
                        self.errors.append(f"Invalid entry: {entry}")
                        return False

                    if entry == "template.html":
                        has_template_html = True
                        content = zf.read(entry).decode("utf-8")
                        self._validate_html(content)
                    elif entry == "template.json":
                        has_template_json = True
                        content = zf.read(entry).decode("utf-8")
                        self._validate_config(content)

                if not has_template_html:
                    self.errors.append("Missing template.html")
                    return False
                if not has_template_json:
                    self.warnings.append("Missing template.json, using defaults")

        except zipfile.BadZipFile:
            self.errors.append("Invalid ZIP file")
            return False

        return len(self.errors) == 0

    def _validate_entry(self, entry: str) -> bool:
        normal = entry.lower()
        if ".." in entry:
            return False
        if normal.startswith("/") or normal.startswith("\\"):
            return False
        ext = os.path.splitext(entry)[1].lower()
        if ext and ext not in ALLOWED_EXTENSIONS:
            self.warnings.append(f"Skipping disallowed file type: {entry}")
            return False
        return True

    def _validate_html(self, content: str):
        for pattern in BLOCKED_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                self.errors.append(f"Blocked pattern found in template: {pattern[:30]}...")

        variables = TEMPLATE_VARIABLE_PATTERN.findall(content)
        if not variables:
            self.warnings.append("No resume variables found in template")

    def _validate_config(self, content: str):
        try:
            config = json.loads(content)
            if not config.get("name"):
                self.warnings.append("Template name not specified in config")
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid template.json: {e}")

    def is_valid(self) -> bool:
        return len(self.errors) == 0


class TemplateRenderer:
    def __init__(self, html_template: str, css_template: Optional[str] = None):
        self.html = html_template
        self.css = css_template or ""

    def render(self, resume_data: dict) -> str:
        html = self.html

        def replace_variable(match):
            path = match.group(1)
            value = self._resolve_path(resume_data, path)
            if value is None:
                return ""
            if isinstance(value, (list, dict)):
                return json.dumps(value, ensure_ascii=False)
            if isinstance(value, bool):
                return str(value).lower()
            return str(value)

        html = TEMPLATE_VARIABLE_PATTERN.sub(replace_variable, html)

        def replace_loop(match):
            var_name = match.group(1)
            list_path = match.group(2)
            loop_content = match.group(3)
            items = self._resolve_path(resume_data, list_path)
            if not isinstance(items, list):
                return ""
            result_parts = []
            for item in items:
                item_html = loop_content
                item_vars = re.findall(r"\{\{\s*" + var_name + r"\.([a-zA-Z0-9_.]+)\s*\}\}", item_html)
                for sub_path in item_vars:
                    placeholder = "{{ " + var_name + "." + sub_path + " }}"
                    value = self._resolve_path(item, sub_path)
                    item_html = item_html.replace(placeholder, str(value or ""))
                result_parts.append(item_html)
            return "".join(result_parts)

        html = TEMPLATE_LOOP_PATTERN.sub(replace_loop, html)

        if self.css:
            style_tag = f"<style>\n{self.css}\n</style>"
            html = html.replace("</head>", f"{style_tag}\n</head>") if "</head>" in html else f"{style_tag}\n{html}"

        return html

    def _resolve_path(self, data: dict, path: str):
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                try:
                    idx = int(part)
                    current = current[idx] if 0 <= idx < len(current) else None
                except ValueError:
                    return None
            else:
                return None
            if current is None:
                return None
        return current


def sanitize_template_html(html: str) -> str:
    import bleach
    allowed_tags = [
        "html", "head", "body", "meta", "title", "style", "link",
        "div", "span", "p", "h1", "h2", "h3", "h4", "h5", "h6",
        "ul", "ol", "li", "dl", "dt", "dd",
        "table", "thead", "tbody", "tr", "th", "td",
        "a", "img", "br", "hr", "strong", "em", "b", "i", "u",
        "small", "sub", "sup", "blockquote", "pre", "code",
        "section", "article", "header", "footer", "main", "nav",
        "figure", "figcaption",
    ]
    allowed_attrs = {
        "*": ["class", "id", "style"],
        "a": ["href", "target", "rel", "title"],
        "img": ["src", "alt", "width", "height"],
        "meta": ["charset", "name", "content"],
        "link": ["href", "rel", "type"],
    }
    cleaned = bleach.clean(
        html,
        tags=allowed_tags,
        attributes=allowed_attrs,
        protocols=["https", "http", "mailto"],
        strip=True,
    )
    return cleaned
