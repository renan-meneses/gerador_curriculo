# LinkedIn Import

## Supported Methods

### 1. Manual Paste

Users can copy and paste text from their LinkedIn profile. The importer uses keyword-based section detection to parse:

- About/Summary
- Experience
- Education
- Skills
- Certifications
- Projects
- Languages
- Volunteer experience
- Publications
- Courses

### 2. LinkedIn Data Export

Users can upload their LinkedIn data export (ZIP file containing Profile data in JSON format).

To request your data export:
1. Go to LinkedIn Settings & Privacy
2. Data Privacy > Get a copy of your data
3. Select "Profile" and request archive
4. Download and upload the file

## Import Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Parser
    participant DB

    User->>Frontend: Selects LinkedIn import method
    Frontend->>API: POST /imports/linkedin (data)
    API->>Parser: Parse raw data
    Parser->>API: Structured sections
    API->>DB: Save import record
    API->>Frontend: Return import_id
    Frontend->>API: Poll status
    API->>Frontend: Parsed data ready
    Frontend-->>User: Show sections for review
    User->>Frontend: Select/Edit sections
    Frontend->>API: POST /imports/{id}/confirm
    API->>DB: Create/update resume
    API->>Frontend: Resume updated
```

## Review Process

Before saving, users can:

- View each detected section
- Select/deselect sections to import
- Edit individual fields
- Resolve duplicates with existing data
- Reject incorrect information
- Confirm dates and employment details

## Security & Compliance

- No unauthorized scraping of LinkedIn
- Data export import requires user to provide their own export
- All data reviewed before persisting
- Import consent explicitly requested
- Data can be deleted at any time
