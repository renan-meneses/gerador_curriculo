# Resume Builder

AI-powered web application for creating, managing, optimizing, and exporting professional resumes. Import from LinkedIn, use custom templates, tailor resumes to job descriptions with Google Gemini AI, and export to PDF, DOCX, HTML, and Markdown.

## Features

- **LinkedIn Import** — Import professional data via manual paste or LinkedIn data export with review before saving
- **Markdown Import** — Upload or paste Markdown resumes with automatic section mapping
- **Structured Resume Builder** — Create resumes through structured forms with a canonical data model
- **Custom Templates** — Upload, manage, and use custom HTML/CSS templates with sandboxed rendering
- **AI-Powered Optimization** — Google Gemini API integration for resume analysis, job matching, content rewriting, and ATS optimization
- **Deterministic Scoring** — Combined keyword matching and AI analysis for accurate job-match scores
- **Multi-format Export** — PDF (via WeasyPrint), DOCX, Markdown, HTML, and JSON
- **Version Management** — Maintain multiple resume versions for different job applications
- **Privacy & Consent** — Explicit consent for AI processing, data export, and account deletion
- **Internationalization** — English, Portuguese, and Spanish support
- **Accessibility** — WCAG 2.2 AA compliant interface
- **Observability** — Structured logging, metrics, tracing, and health checks

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Browser   │────▶│  Next.js UI  │────▶│  FastAPI    │
│  (React)    │     │  (Frontend)  │     │  (Backend)  │
└─────────────┘     └──────────────┘     ────┬────┬────┘
                                              │    │
                                    ┌─────────┘    └─────────┐
                                    ▼                       ▼
                             ┌────────────┐          ┌────────────┐
                             │ PostgreSQL │          │   Redis    │
                             │ (Primary)  │          │ (Cache/Q)  │
                             └────────────┘          └─────┬──────┘
                                                            │
                                                    ┌──────▼──────┐
                                                    │   Celery    │
                                                    │  (Worker)   │
                                                    └──────┬──────┘
                                                           │
                                              ┌────────────▼────────────┐
                                              │  Google Gemini API     │
                                              │  Document Export       │
                                              │  Template Sandbox      │
                                              └────────────────────────┘
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React, Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, TanStack Query |
| **Backend** | Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 16 with async driver |
| **Cache/Queue** | Redis 7 |
| **AI** | Google Gemini API (gemini-1.5-pro) |
| **Documents** | WeasyPrint (PDF), python-docx (DOCX), Jinja2 (templates) |
| **Workers** | Celery for background jobs |
| **Infrastructure** | Docker, Docker Compose, Kubernetes, GitHub Actions |

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+
- Google Gemini API key (for AI features)

## Local Setup

### 1. Clone and configure

```bash
git clone <repository-url> curriculo_gerador
cd curriculo_gerador

# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your settings (especially GEMINI_API_KEY)
```

### 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Open in browser

- Frontend: http://localhost:3000
- API: http://localhost:8000/api/docs

## Docker Setup

```bash
docker compose up --build
```

## Gemini API Configuration

1. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Set `GEMINI_API_KEY` in `backend/.env`
3. Optionally configure `GEMINI_MODEL` (default: `gemini-1.5-pro`)

## Testing

```bash
# Backend tests
cd backend && python -m pytest tests/ -v --cov=app

# Frontend tests (when configured)
cd frontend && npm test
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Project Structure

```
curriculo_gerador/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes (auth, resumes, jobs, templates, imports, exports, ai)
│   │   ├── core/            # Config, database, security, dependencies
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic (AI, scoring, export, template)
│   │   ├── ai/              # Gemini integration & prompt templates
│   │   ├── importers/       # LinkedIn & Markdown parsers
│   │   ├── exporters/       # Document generation
│   │   ├── templates/       # Built-in resume templates
│   │   └── worker/          # Celery background jobs
│   ├── alembic/             # Database migrations
│   ├── tests/               # Backend test suite
│   └── Dockerfile
├── frontend/
│   └── src/
│       ├── app/             # Next.js pages
│       ├── components/      # React components
│       ├── lib/             # Utilities
│       ├── services/        # API client
│       └── store/           # State management
├── infrastructure/
│   ├── docker/              # Docker configs
│   ├── kubernetes/          # K8s manifests
│   └── monitoring/          # Observability configs
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD
```

## Security

- Password hashing with bcrypt
- JWT tokens with configurable expiration
- CSRF protection via SameSite cookies
- CORS restricted to configured origins
- Input validation on all endpoints
- Template HTML sanitization (no script execution)
- Path traversal protection for file uploads
- Rate limiting on auth endpoints
- SQL injection protection via SQLAlchemy ORM
- Ownership validation for all resources

## Privacy

- Explicit consent for AI data processing
- LinkedIn import consent
- Data export and account deletion
- Configurable data retention
- No resume data used for AI training without consent
- Sensitive data redacted from logs
- Encryption in transit (TLS) and at rest

## License

MIT
