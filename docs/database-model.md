# Database Model

## Entity Relationship Diagram

```mermaid
erDiagram
    users ||--o{ resumes : "has"
    users ||--o{ job_descriptions : "has"
    users ||--o{ templates : "has"
    users ||--o{ imports : "has"
    users ||--o{ exports : "has"
    users ||--o{ api_usage : "records"

    resumes ||--o{ resume_versions : "versioned"
    resumes ||--o| personal_information : "has"
    resumes ||--o{ professional_summaries : "has"
    resumes ||--o{ work_experiences : "has"
    resumes ||--o{ education_records : "has"
    resumes ||--o{ resume_skills : "has"
    resumes ||--o{ certifications : "has"
    resumes ||--o{ projects : "has"
    resumes ||--o{ languages : "has"
    resumes ||--o{ custom_sections : "has"

    resumes ||--o{ resume_job_analyses : "analyzed in"
    job_descriptions ||--o{ resume_job_analyses : "compared with"
    resume_job_analyses ||--o{ ai_suggestions : "generates"

    templates ||--o{ template_versions : "versioned"

    users {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        boolean is_active
        boolean is_verified
        boolean is_admin
        string role
        string google_id UK
        string linkedin_id UK
        string locale
        boolean ai_consent_given
        datetime created_at
        datetime updated_at
        datetime deleted_at
    }

    resumes {
        uuid id PK
        uuid user_id FK
        string title
        string target_job_title
        string target_company
        string locale
        boolean is_archived
        uuid parent_resume_id FK
        string source
        text original_markdown
        datetime created_at
        datetime updated_at
    }

    personal_information {
        uuid id PK
        uuid resume_id FK UK
        string full_name
        string professional_title
        string email
        string phone
        string city
        string state
        string country
        string linkedin_url
        string github_url
        string portfolio_url
    }

    work_experiences {
        uuid id PK
        uuid resume_id FK
        string company
        string position
        string employment_type
        string location
        date start_date
        date end_date
        boolean is_current
        text description
        jsonb achievements
        jsonb technologies
        string approval_status
        int sort_order
    }

    job_descriptions {
        uuid id PK
        uuid user_id FK
        string title
        string company_name
        text job_description
        jsonb required_qualifications
        jsonb preferred_qualifications
        jsonb technical_requirements
        jsonb keywords
        string industry
        string seniority_level
        string language
    }

    resume_job_analyses {
        uuid id PK
        uuid resume_id FK
        uuid job_id FK
        float overall_score
        jsonb matched_requirements
        jsonb missing_requirements
        jsonb recommended_changes
        jsonb unsupported_claims
    }

    ai_suggestions {
        uuid id PK
        uuid analysis_id FK
        string section
        text original_text
        text suggested_text
        text reason
        float confidence
        string status
        text user_edited_text
    }

    templates {
        uuid id PK
        uuid user_id FK
        string name
        string description
        string version
        string author
        boolean is_built_in
        boolean is_shared
        boolean is_default
        string page_size
        jsonb supported_sections
    }
```

## Indexes

- `users.email` (unique)
- `resumes.user_id`
- `resume_versions.resume_id`
- `work_experiences.resume_id`
- `job_descriptions.user_id`
- `resume_job_analyses.resume_id`
- `resume_job_analyses.job_id`
- `templates.user_id`
- `imports.user_id`
- `exports.user_id`
- `ai_suggestions.analysis_id`
- `api_usage.user_id`

## Soft Deletion

Users are soft-deleted via `deleted_at` timestamp to preserve referential integrity. Resume data is cascade-deleted when a user is hard-deleted after the retention period.
