# API Reference

Base URL: `/api/v1`

## Authentication

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGci..."
}
```

## Resumes

### List Resumes
```http
GET /resumes
Authorization: Bearer <token>
```

### Create Resume
```http
POST /resumes
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Software Engineer Resume",
  "target_job_title": "Senior Software Engineer",
  "target_company": "Tech Corp",
  "locale": "en"
}
```

### Get Resume
```http
GET /resumes/{resume_id}
Authorization: Bearer <token>
```

### Delete Resume
```http
DELETE /resumes/{resume_id}
Authorization: Bearer <token>
```

### Duplicate Resume
```http
POST /resumes/{resume_id}/duplicate
Authorization: Bearer <token>
```

## Job Descriptions

### List Jobs
```http
GET /jobs
Authorization: Bearer <token>
```

### Create Job
```http
POST /jobs
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "company_name": "Tech Corp",
  "job_description": "We are looking for...",
  "required_qualifications": ["Python", "5+ years experience"],
  "preferred_qualifications": ["Kubernetes", "AWS"]
}
```

### Analyze Job
```http
POST /jobs/{job_id}/analyze
Authorization: Bearer <token>
```

## Templates

### List Templates
```http
GET /templates
Authorization: Bearer <token>
```

### Create Template
```http
POST /templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Template",
  "description": "Custom template",
  "page_size": "A4",
  "supported_sections": ["personalInformation", "summary"]
}
```

## Imports

### Import LinkedIn
```http
POST /imports/linkedin
Authorization: Bearer <token>
Content-Type: application/json

{
  "linkedin_data": "Pasted LinkedIn profile content"
}
```

### Import Markdown
```http
POST /imports/markdown
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: resume.md
```

### Import Status
```http
GET /imports/{import_id}/status
Authorization: Bearer <token>
```

## Exports

### Export PDF
```http
POST /exports/pdf
Authorization: Bearer <token>
Content-Type: application/json

{
  "resume_id": "uuid",
  "template_id": "uuid",
  "options": {}
}
```

### Export Status
```http
GET /exports/{export_id}/status
Authorization: Bearer <token>
```

## AI Suggestions

### List Suggestions
```http
GET /ai-suggestions/{analysis_id}
Authorization: Bearer <token>
```

### Accept Suggestion
```http
POST /ai-suggestions/{suggestion_id}/accept
Authorization: Bearer <token>
```

### Reject Suggestion
```http
POST /ai-suggestions/{suggestion_id}/reject
Authorization: Bearer <token>
```

## Error Responses

All errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable error message",
    "details": [],
    "correlationId": "uuid"
  }
}
```

## Health Check

```http
GET /health
```

Response: `{"status": "healthy", "version": "1.0.0"}`
