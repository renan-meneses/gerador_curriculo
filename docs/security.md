# Security

## Authentication

- Password hashing via bcrypt (passlib)
- JWT access tokens (15min default) + refresh tokens (7 days)
- Token rotation on refresh
- Secure, HttpOnly cookies for production
- Rate limiting on auth endpoints (60/min default)
- Account lockout after 5 failed attempts (15min)

## Authorization

- Role-based access control (user, template_designer, support, admin)
- Ownership validation for every resource
- No insecure direct object references (IDOR)
- Admin-only endpoints for user management

## Input Validation

- Pydantic schemas on all API endpoints
- Zod validation on frontend forms
- File type and MIME type validation
- Maximum file size limits (10MB default)
- ZIP bomb protection
- Path traversal prevention

## Output Security

- HTML sanitization (bleach) on template content
- Content Security Policy headers
- CORS restricted to configured origins
- No sensitive data in error messages

## Data Protection

- Encryption in transit (TLS via reverse proxy)
- Encryption at rest (database-level encryption)
- Secrets managed via environment variables
- No API keys exposed to browser
- Sensitive fields redacted from logs

## Template Security

Templates are treated as untrusted content:

1. ZIP extraction validates file paths
2. HTML is sanitized (scripts, event handlers removed)
3. CSS is sanitized
4. External resource loading blocked
5. No JavaScript execution
6. Sandboxed preview rendering
7. File type whitelist (.html, .css, .json, .png, .jpg, .svg)
8. Maximum file count (50) and size (5MB)

## Dependency Security

- Regular dependency scanning via `pip audit` and `npm audit`
- Container image scanning in CI/CD
- Dependencies pinned in lock files
- Automated updates via Dependabot/Renovate

## Audit Logging

All sensitive operations are logged:
- Authentication events
- Resource access
- AI processing
- Data export/import
- Template upload
- Admin actions

Logs exclude personal resume content.
