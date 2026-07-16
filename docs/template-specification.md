# Template Specification

## Package Structure

Custom templates are uploaded as ZIP files with the following structure:

```
template-package.zip
├── template.json        # Required: Template metadata
├── template.html        # Required: HTML template
├── styles.css           # Optional: Template styles
├── preview.png          # Optional: Preview image
├── preview.jpg          # Optional: Alternative preview
└── assets/              # Optional: Additional assets (fonts, icons)
```

## template.json

```json
{
  "name": "Modern Professional",
  "version": "1.0.0",
  "author": "Author Name",
  "description": "Clean, ATS-friendly resume template",
  "supportedSections": [
    "personalInformation",
    "summary",
    "experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "languages"
  ],
  "pageSize": "A4",
  "fonts": ["Inter", "Arial"],
  "variables": {},
  "entryFile": "template.html",
  "styleFile": "styles.css",
  "category": "professional"
}
```

## Template Variables

Access resume data via `{{ resume.<section>.<field> }}`:

```
{{ resume.personalInformation.fullName }}
{{ resume.personalInformation.email }}
{{ resume.personalInformation.phone }}
{{ resume.personalInformation.city }}
{{ resume.personalInformation.state }}
{{ resume.personalInformation.professionalTitle }}
{{ resume.personalInformation.linkedinUrl }}
{{ resume.personalInformation.githubUrl }}
{{ resume.personalInformation.websiteUrl }}
{{ resume.summary }}
```

## Loops

Iterate over list fields:

```html
{% for exp in resume.experiences %}
  <h3>{{ exp.position }} at {{ exp.company }}</h3>
  <p>{{ exp.startDate }} - {% if exp.isCurrent %}Present{% else %}{{ exp.endDate }}{% endif %}</p>
  <ul>
    {% for ach in exp.achievements %}
      <li>{{ ach }}</li>
    {% endfor %}
  </ul>
{% endfor %}
```

## Conditionals

```html
{% if resume.summary %}
  <section id="summary">{{ resume.summary }}</section>
{% endif %}
```

## Supported Section Keys for Loops

| Variable | Type | Fields |
|----------|------|--------|
| `resume.experiences` | list | position, company, startDate, endDate, isCurrent, description, achievements, technologies |
| `resume.education` | list | institution, degree, fieldOfStudy, startDate, endDate, description, gpa |
| `resume.skills` | list | skillName, category, proficiency, yearsOfExperience |
| `resume.certifications` | list | name, issuer, issueDate, expirationDate, credentialId, credentialUrl |
| `resume.projects` | list | name, description, role, technologies, repositoryUrl, liveUrl |
| `resume.languages` | list | language, proficiency |

## Security

Uploaded templates are sandboxed:

- HTML sanitized (scripts, event handlers, and dangerous tags removed)
- CSS sanitized
- No JavaScript execution allowed
- External resource loading blocked
- Path traversal prevented
- File type and MIME type validated
- Maximum file size and count enforced
- ZIP bomb protection

## Built-in Templates

1. **ATS Classic** — Simple, clean layout optimized for ATS parsing
2. **Modern Professional** — Two-column design with sidebar
3. **Technical Engineer** — Focused on technical skills and projects
4. **Executive** — Professional design for senior roles
5. **Minimalist** — Clean, minimal design with ample white space
