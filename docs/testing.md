# Testing

## Backend Tests

### Test Structure

```
backend/tests/
├── conftest.py           # Test fixtures and configuration
├── test_auth.py          # Authentication flow tests
├── test_resumes.py       # Resume CRUD and operations
├── test_scoring.py       # Deterministic scoring engine tests
└── test_template_service.py  # Template validation and rendering tests
```

### Running Tests

```bash
# All tests
cd backend && python -m pytest tests/ -v

# With coverage
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Specific test file
python -m pytest tests/test_scoring.py -v

# Specific test
python -m pytest tests/test_scoring.py::TestScoringEngine::test_deterministic_scoring -v
```

### Test Coverage Goals

| Module | Coverage Target |
|--------|----------------|
| Core (config, database, security) | 90%+ |
| Models | 85%+ |
| API Routes | 80%+ |
| Services (scoring, AI, export) | 90%+ |
| Importers | 85%+ |
| Template Service | 90%+ |

## Critical Test Scenarios

1. **Authentication**: Registration, login, token refresh, invalid credentials, duplicate emails
2. **Resume CRUD**: Create, list, get, delete, duplicate, ownership validation
3. **Scoring Engine**: Full match, partial match, no match, empty resume, keyword coverage
4. **Template Security**: Path traversal blocking, script injection prevention, event handler removal
5. **Template Rendering**: Variable substitution, loops, conditionals, nested variables

## Frontend Tests

```bash
cd frontend && npm test
```

## Manual Testing Checklist

- [ ] User registration and login flow
- [ ] Resume creation via form
- [ ] Markdown import with review
- [ ] LinkedIn data import
- [ ] Job description entry
- [ ] Template upload and validation
- [ ] PDF export
- [ ] DOCX export
- [ ] Resume duplication
- [ ] Version management
- [ ] AI analysis (when configured)
- [ ] Accessibility (keyboard nav, screen reader)
- [ ] Responsive layout (mobile/tablet/desktop)
- [ ] Error states and recovery
- [ ] Account deletion
- [ ] Data export
