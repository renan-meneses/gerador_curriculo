# AI Integration

## Gemini Service Layer

The AI integration is encapsulated in a dedicated service layer:

- `app/ai/gemini.py` — Core Gemini client with retry logic, schema validation, and token tracking
- `app/ai/prompts/` — Versioned prompt templates for each operation
- `app/services/ai_service.py` — Business logic combining prompts, Gemini calls, and output parsing
- `app/services/scoring.py` — Deterministic scoring engine that complements AI analysis

## Safety Rules

The AI must:

1. Only use information present in user-provided data
2. Never invent qualifications, metrics, dates, or achievements
3. Identify gaps honestly rather than fabricating content
4. Provide traceable changes with original/suggested text and reasoning

## Prompt Structure

Each prompt template includes:

- **Role definition** — Context for the AI model
- **Objective** — Clear task description
- **Input schema** — Expected input format
- **Output schema** — Structured JSON response schema
- **Constraints** — Rules the AI must follow
- **Prohibited behavior** — Explicit restrictions

## Available Operations

| Operation | Prompt File | Description |
|-----------|-------------|-------------|
| Job Extraction | `job_extraction.txt` | Parse job descriptions into structured requirements |
| Resume Analysis | `resume_analysis.txt` | Compare resume against job requirements |
| Summary Rewrite | `summary_rewrite.txt` | Tailor professional summary to target role |
| Experience Rewrite | `experience_rewrite.txt` | Improve achievement bullet points |

## Error Handling

- Exponential backoff with configurable retries (default: 3)
- JSON output validation against schema
- Fallback to deterministic scoring when AI unavailable
- Correlation IDs for request tracking
- Structured logging (no personal data in logs)
- Token usage tracking per request

## Privacy

- No resume content sent to Gemini without explicit user consent
- API key stored only server-side, never exposed to browser
- Configurable model selection
- Token tracking for cost monitoring
