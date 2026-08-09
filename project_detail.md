# SkillPath.ai — Complete Technical Documentation

> **Version:** 2.1
> **Last Updated:** 2026-08-08
> **Status:** MVP — see Section 5.6 (no migrations) and Section 9 (unauthenticated
> AI interview routes) for the two known gaps before production.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Database Schema](#5-database-schema)
6. [Resume Parsing Pipeline](#6-resume-parsing-pipeline)
7. [Scoring & Matching Algorithms](#7-scoring--matching-algorithms)
8. [Authentication & Security](#8-authentication--security)
9. [API Reference](#9-api-reference)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Configuration & Environment](#11-configuration--environment)
12. [Algorithms Deep Dive](#12-algorithms-deep-dive)
13. [Testing](#13-testing)
14. [Deployment](#14-deployment)

---

## 1. Project Overview

SkillPath is a full-stack SaaS platform that analyzes resumes using NLP and Generative AI to provide career coaching, skill gap analysis, and learning roadmaps.

### Core Value Proposition
- **Resume Analysis:** Parse PDF/DOCX resumes and extract structured data
- **Skill Gap Analysis:** Compare candidate skills against role requirements
- **Career Coaching:** Generate personalized learning roadmaps
- **Job Matching:** Match candidates to market opportunities
- **Mock Interviews:** AI-powered interview practice

### Target Audience
| Audience | Use Case |
|----------|----------|
| Job Seekers | Improve resume, identify skill gaps, prepare for interviews |
| Career Changers | Plan transition path into tech roles |
| Recruiters | Evaluate candidate fit against job requirements |
| Hiring Managers | Understand market trends and skill demands |

---

## 2. Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                   │
│  TypeScript | React Router | Recharts | Framer Motion | Lucide  │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (httpOnly cookies)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Uvicorn)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Auth Layer  │  │ Middleware  │  │ Route Handlers          │  │
│  │ JWT/bcrypt  │  │ Rate Limit  │  │ /auth /analysis /admin  │  │
│  └─────────────┘  │ CORS        │  │ /user /jobs /sharing    │  │
│                   │ Security    │  └─────────────────────────┘  │
│                   └─────────────┘                               │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Service Layer                              ││
│  │ resume_parser | career_services | skill_matching | roadmap  ││
│  │ extractor | ai_provider | parser_enhancements | market_data ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ PostgreSQL │  │ Gemini API │  │ OpenAI-    │
     │ (psycopg2) │  │ (Google)   │  │ Compatible │
     └────────────┘  └────────────┘  └────────────┘
```

### Data Flow (Resume Analysis)

```
User Uploads Resume
       │
       ▼
┌──────────────────┐
│ Magic Byte Check │ ← Validates %PDF or PK\x03\x04
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Text Extraction  │ ← PyMuPDF (PDF) / python-docx (DOCX)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────┐
│              Parsing Decision Tree                │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │ Tier 1: Local Regex Parser (always runs)    │ │
│  │   → spaCy NER + rapidfuzz + dateutil        │ │
│  │   → Confidence score (0-100)                │ │
│  └─────────────────────────────────────────────┘ │
│                      │                            │
│                      ▼                            │
│  ┌─────────────────────────────────────────────┐ │
│  │ Tier 2: AI Provider (if key configured)     │ │
│  │   → Gemini (if GEMINI_API_KEY)              │ │
│  │   → OpenAI-compatible (if OPENAI_API_KEY)   │ │
│  └─────────────────────────────────────────────┘ │
│                      │                            │
│                      ▼                            │
│  ┌─────────────────────────────────────────────┐ │
│  │ Fallback: Local regex result                │ │
│  └─────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ Score Computation│ ← Weighted breakdown (100 pts)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Cache & Respond  │ ← (content_hash, target_role) → 7-day TTL
└──────────────────┘
```

---

## 3. Tech Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.x | UI framework |
| TypeScript | 5.x | Type-safe JavaScript |
| Vite | 7.x | Build tool and dev server |
| React Router DOM | 7.x | Client-side routing |
| Recharts | — | Data visualization (area, bar, pie, radar charts) |
| Framer Motion | — | Animations and transitions |
| Lucide React | — | Icon library |
| Axios | — | HTTP client |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.9+ | Runtime (CI matrix: 3.9, 3.11, 3.12) |
| FastAPI | 0.115+ | Web framework |
| Uvicorn | 0.32+ | ASGI server |
| PostgreSQL | 16 | Database — **required**, no SQLite fallback |
| psycopg2-binary | 2.9+ | PostgreSQL adapter with `ThreadedConnectionPool` |
| PyJWT | 2.10+ | JWT token management |
| bcrypt | 4.2+ | Password hashing |
| Google Generative AI | 0.8+ | Gemini API (optional) |
| PyMuPDF | 1.24+ | PDF parsing |
| python-docx | 1.1+ | DOCX parsing |
| defusedxml | 0.7+ | Safe XML parsing |
| spacy | 3.7+ | Named entity recognition |
| rapidfuzz | 3.9+ | Fuzzy string matching |
| python-dateutil | 2.9+ | Flexible date parsing |
| httpx | 0.28+ | Async HTTP client |
| beautifulsoup4 | 4.12+ | HTML parsing |
| pytest | 8.0+ | Test framework |

### AI Providers

| Provider | Config | Notes |
|----------|--------|-------|
| **Google Gemini** | `GEMINI_API_KEY` | Primary: analysis, roadmap generation, interview questions |
| **OpenAI-compatible** | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` | Works with OpenAI, Groq, Together, OpenRouter, or local Ollama |
| **Local fallback** | none | Enhanced regex + spaCy NER parser (no LLM required) |

---

## 4. Project Structure

```
skillpath.ai/
├── api/                                # Backend (FastAPI)
│   ├── main.py                         # App entry, middleware, CORS, router registration
│   ├── database.py                     # Connection pool + init_db() (all 38 CREATE TABLE stmts)
│   ├── auth.py                         # JWT creation/validation, auth dependencies
│   ├── security.py                     # Password hashing (bcrypt)
│   ├── exceptions.py                   # Custom exceptions
│   ├── extractor.py                    # Resume text extraction (PDF/DOCX/Gemini)
│   ├── resume_parser.py                # Local fallback resume parsing
│   ├── parser_enhancements.py          # spaCy + rapidfuzz + dateutil enhancements
│   ├── resume_patterns.py              # Regex/keyword patterns for parsing
│   ├── career_services.py              # Resume scoring, skill analysis, candidate ranking
│   ├── skill_matching.py               # Skill matching, JD comparison, gap prioritisation
│   ├── roadmap_services.py             # Roadmap generation, project recommendations
│   ├── ai_provider.py                  # Gemini + OpenAI-compatible provider chain
│   ├── email_service.py                # SMTP delivery (OTP, password reset)
│   ├── mock_interview.py               # Static interview questions
│   ├── mock_interview_ai.py            # AI-generated interview sessions
│   ├── course_scraper.py               # Coursera scraping, Udemy fallback
│   ├── scraper.py                      # Market data simulation
│   ├── market_data.py                  # Market trend data + cache
│   ├── courses.py                      # Course recommendation logic
│   ├── course_data.py                  # Course/roadmap/field data
│   ├── seed_data.py                    # In-memory caches + loaders/getters
│   ├── seeders.py                      # DB seeding functions
│   ├── seed_content.py                 # Default seed content
│   ├── seed_defaults.py                # Default roles/roadmaps data
│   ├── skills_taxonomy.py              # Skill taxonomy data
│   ├── i18n.py                         # Translation support
│   ├── trends.py                       # Trend analysis helpers
│   ├── requirements.txt                # Python dependencies
│   ├── routes/
│   │   ├── admin.py                    # Admin CRUD, audit, export, taxonomy
│   │   ├── auth.py                     # Register, login, logout, refresh, password
│   │   ├── user.py                     # Profile, preferences, history, analysis
│   │   ├── analysis.py                 # Resume analysis pipeline
│   │   ├── jobs.py                     # Job matches, interview, JD compare
│   │   ├── sharing.py                  # Public report sharing
│   │   ├── misc.py                     # Feedback, billing, notifications, i18n
│   │   └── health.py                   # Health check
│   ├── data/
│   │   └── mock_questions.json         # Static interview questions
│   └── tests/                          # Backend test suite (pytest)
│       ├── conftest.py                 # Test env isolation (temp DB, no SMTP)
│       ├── test_integration.py         # API integration tests
│       ├── test_features.py            # Unit tests for core services
│       └── test_security_fixes.py      # Security regression tests
│
├── frontend/                           # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.tsx                     # Routes (lazy-loaded)
│   │   ├── main.tsx                    # Entry point
│   │   ├── types/
│   │   │   └── index.ts                # Shared TypeScript interfaces
│   │   ├── pages/                      # Landing, Analyzer, AnalysisResult, Admin, ...
│   │   ├── components/                 # Feature-scoped component modules
│   │   │   ├── analyzer/               # Resume upload + analysis UI
│   │   │   ├── results/                # Analysis results (score, gaps, roadmap)
│   │   │   ├── sidebar/                # App shell navigation
│   │   │   ├── trends/                 # Market trend charts
│   │   │   ├── auth/                   # Login/register modal
│   │   │   ├── admin/                  # Admin panels
│   │   │   ├── landing/                # Landing page sections
│   │   │   ├── interview/              # Mock interview UI
│   │   │   ├── profile/                # Profile + skill trends
│   │   │   ├── settings/               # Account settings
│   │   │   └── analysis/               # Shared analysis components
│   │   ├── context/
│   │   │   └── AuthContext.tsx         # Auth state management
│   │   ├── services/
│   │   │   ├── api.ts                  # Axios instance + interceptors
│   │   │   └── env.ts                  # Environment config
│   │   └── styles/
│   │       ├── theme.css               # Design tokens + global styles
│   │       └── animations.css          # Keyframe animations
│   ├── src/test/
│   │   ├── setup.ts                    # jsdom setup (matchMedia, scrollIntoView stubs)
│   │   └── apiContract.test.ts         # Greps Python routes to catch field-name drift
│   ├── e2e/                            # Playwright specs (auth, analyzer, admin, interview)
│   │   └── fixtures.ts                 # Network-layer /api/** stubs (no backend needed)
│   ├── playwright.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── .github/workflows/ci.yml            # CI: frontend, e2e, backend matrix, analysis, release
├── docker-compose.yml                  # Postgres 16 + backend + frontend
├── Dockerfile.backend / Dockerfile.frontend
├── pytest.ini                          # Pytest configuration
├── package.json                        # Root scripts (setup, dev, build)
├── .env.example                        # Environment variable template
└── venvapp/                            # Python virtual environment (local only)
```

> **Note:** `alembic.ini` exists at the repo root but is **not wired up** — there is no
> `alembic/` directory and Alembic is not in `requirements.txt`. Schema is created by
> `init_db()` in `database.py`, which runs at import time (`database.py:753`).
> See [Section 5.6](#56-schema-management) for the implications.

---

## 5. Database Schema

### 5.1 Overview

- **Engine:** PostgreSQL 16 only. `DATABASE_URL` is **required** — `_get_pool()` raises
  `RuntimeError` if it is unset. There is no SQLite fallback and no dialect
  compatibility layer.
- **Source of truth:** `api/database.py`, function `init_db()` (lines 155–614).
  All 38 tables are created there with `CREATE TABLE IF NOT EXISTS`.
- **Access pattern:** `psycopg2` `ThreadedConnectionPool` with `RealDictCursor`,
  so every row behaves like a dict.
- **Table count:** 38.

### 5.2 Entity Relationship Diagram

Only tables with real foreign keys are shown. Reference/lookup tables
(Section 5.5) are standalone and joined by string value, not by key.

```mermaid
erDiagram
    users ||--o| user_profiles       : "has one"
    users ||--o| user_preferences    : "has one"
    users ||--o| subscriptions       : "has one"
    users ||--o{ notifications       : "receives"
    users ||--o{ user_roadmap_progress : "tracks"
    users ||--o{ refresh_tokens      : "holds (by user_id, no FK)"
    users ||--o{ user_data           : "uploads (by user_id, no FK)"
    user_data ||--o{ shared_reports  : "shared as (by analysis_id, no FK)"

    job_roles ||--o{ job_role_skills : "requires"
    job_roles ||--o{ career_roadmaps : "has"
    career_roadmaps ||--o{ roadmap_steps : "contains"

    skill_categories ||--o{ skills   : "groups"

    users {
        bigserial id PK
        varchar username UK
        varchar email UK
        varchar hashed_password
        text role "CHECK admin|user"
        int is_active
        int email_verified
    }
    user_data {
        bigserial ID PK
        int user_id "default -1 = anonymous"
        varchar content_hash
        varchar resume_score
        text analysis_data "full JSON"
        varchar target_role
    }
    job_roles {
        bigserial id PK
        varchar title
        varchar category
        int is_active
    }
    job_role_skills {
        bigserial id PK
        int job_role_id FK
        varchar skill_name
        int is_required "1 = core, scores 2x"
    }
    career_roadmaps {
        bigserial id PK
        int job_role_id FK
        varchar title
        int duration_weeks
    }
    roadmap_steps {
        bigserial id PK
        int roadmap_id FK
        int step_number
        text skills
    }
    skill_categories {
        bigserial id PK
        varchar name UK
    }
    skills {
        bigserial id PK
        int category_id FK
        varchar name
    }
```

**Two things the diagram makes visible:**

1. **`user_data` has no foreign key to `users`.** It stores `user_id INTEGER DEFAULT -1`,
   where `-1` means anonymous. This is deliberate — analyses survive account deletion —
   but it also means deleting a user leaves orphaned rows that no cascade cleans up.
2. **`refresh_tokens`, `password_reset_tokens` and `shared_reports` also lack FKs.**
   They reference `user_id` by value only, so expired rows are cleaned by application
   code, not by the database.

### 5.3 Cascade behaviour (data deletion)

Seven tables declare `ON DELETE CASCADE`, so `DELETE FROM users` cleans them
automatically. Everything else must be deleted explicitly.

| Cascades automatically | Must be deleted by application code |
|---|---|
| `user_profiles` | `user_data` (no FK, `user_id` default −1) |
| `user_preferences` | `refresh_tokens` (no FK) |
| `subscriptions` | `password_reset_tokens` (no FK) |
| `notifications` | `shared_reports` (no FK) |
| `user_roadmap_progress` | `otp_codes` (keyed by email, not user_id) |
| `skills` (via `skill_categories`) | `login_attempts` (keyed by username) |
| `job_role_skills`, `career_roadmaps`, `roadmap_steps` (via `job_roles`) | `audit_logs` (retained intentionally) |

### 5.4 Core tables

#### Users & Authentication

| # | Table | Primary Key | Type | Notes |
|---|-------|-------------|------|-------|
| 1 | `users` | `id` | BIGSERIAL | `username`, `email` UNIQUE; `CHECK role IN ('admin','user')` |
| 2 | `user_profiles` | `user_id` | INTEGER | FK → users, CASCADE. Note the column is `current_job_role`, **not** `current_role` (reserved word in Postgres) |
| 3 | `user_preferences` | `user_id` | INTEGER | FK → users, CASCADE |
| 4 | `refresh_tokens` | `token` | VARCHAR(64) | SHA-256 hash of the JWT, never the raw token |
| 5 | `password_reset_tokens` | `token` | VARCHAR(128) | `used` flag enforces single use |
| 6 | `otp_codes` | `id` | BIGSERIAL | `code_hash` SHA-256; `attempts` caps brute force |
| 7 | `login_attempts` | `username` | VARCHAR(100) | `locked_until` epoch drives lockout |
| 8 | `subscriptions` | `user_id` | INTEGER | FK → users, CASCADE. Schema only — no billing integration yet |

#### Resume Analysis

| # | Table | Primary Key | Type | Notes |
|---|-------|-------------|------|-------|
| 9 | `user_data` | `ID` | BIGSERIAL | Uppercase `ID`, and quoted mixed-case columns (`"Name"`, `"Email_ID"`, `"Predicted_Field"`). Postgres folds unquoted identifiers to lowercase, so API responses return `id` — this caused a production bug in the admin tables |
| 10 | `analysis_cache` | `(content_hash, target_role)` | VARCHAR(64), VARCHAR(200) | **Composite PK** — the same resume for a different role is a different result. `expires_at` gives a 7-day TTL |
| 11 | `shared_reports` | `id` | BIGSERIAL | `token` UNIQUE; `expires_at` + `is_public` gate access |
| 12 | `user_feedback` | `ID` | BIGSERIAL | `CHECK feed_score BETWEEN 1 AND 5` |

#### Job Roles & Skills

| # | Table | Primary Key | Type | Notes |
|---|-------|-------------|------|-------|
| 13 | `job_roles` | `id` | BIGSERIAL | Admin-managed; `is_active` soft-deletes |
| 14 | `job_role_skills` | `id` | BIGSERIAL | FK → job_roles, CASCADE. `is_required` drives the 2× score weighting |
| 15 | `skill_categories` | `id` | BIGSERIAL | `name` UNIQUE |
| 16 | `skills` | `id` | BIGSERIAL | FK → skill_categories, CASCADE. UNIQUE `(category_id, name)` |

#### Roadmaps & Progress

| # | Table | Primary Key | Type | Notes |
|---|-------|-------------|------|-------|
| 17 | `career_roadmaps` | `id` | BIGSERIAL | FK → job_roles, CASCADE |
| 18 | `roadmap_steps` | `id` | BIGSERIAL | FK → career_roadmaps, CASCADE |
| 19 | `user_roadmap_progress` | `id` | BIGSERIAL | FK → users, CASCADE. Has both a table constraint and a partial unique index using `COALESCE(analysis_id, -1)`, because SQL `UNIQUE` treats NULLs as distinct and would otherwise allow duplicate rows |

#### Operations

| # | Table | Primary Key | Type | Notes |
|---|-------|-------------|------|-------|
| 20 | `rate_limits` | `key` | VARCHAR(100) | Key is `ip:minute`; incremented via atomic `ON CONFLICT ... RETURNING count` |
| 21 | `request_logs` | `id` | BIGSERIAL | Written by a background batch consumer, never inline |
| 22 | `audit_logs` | `id` | BIGSERIAL | Admin action trail; deliberately survives user deletion |
| 23 | `notifications` | `id` | BIGSERIAL | FK → users, CASCADE |
| 24 | `courses` | `id` | BIGSERIAL | Course catalogue with rating, price, platform |
| 25 | `market_trends_cache` | `field` | VARCHAR(200) | External market API payload, keyed by field |

### 5.5 Reference / lookup tables

These hold seed data that drives parsing and recommendations. They have no
foreign keys — they are joined by string value (`field_name`, `skill_name`,
`role_key`), which is why `skill_aliases` exists to normalise spelling first.

| # | Table | Primary Key | Unique Constraint | Purpose |
|---|-------|-------------|-------------------|---------|
| 26 | `skill_aliases` | `id` | `alias` | "JS" → "JavaScript". Column is `canonical_skill` |
| 27 | `role_synonyms` | `id` | `role_key` | Role name → categories. Columns are `role_key`, `categories` |
| 28 | `field_keywords` | `id` | `(field_name, keyword)` | Weighted keywords for field prediction |
| 29 | `skill_difficulty` | `id` | `skill_name` | Level 1–3, orders roadmap phases |
| 30 | `skill_clusters` | `id` | `(cluster_name, skill_name)` | Related-skill grouping |
| 31 | `skill_recommendations` | `id` | `(field_name, skill_name)` | Suggested skills per field |
| 32 | `roadmap_templates` | `id` | `(field_name, step_number)` | Default roadmap steps per field |
| 33 | `learning_actions` | `id` | `(skill_name, action_text)` | "Do this" items per skill |
| 34 | `learning_resources` | `id` | `(skill_name, title)` | Links and articles per skill |
| 35 | `video_resources` | `id` | `(field_name, video_type, url)` | Video tutorials per field |
| 36 | `industry_trends` | `id` | `(field_name, trend_type)` | Trend payloads per field |
| 37 | `market_role_aliases` | `id` | `alias` | Job-board title → internal field |
| 38 | `role_configs` | `id` | `role_key` | Project types, interview focus, key tools |

### 5.6 Schema management

There are **no migrations**. `init_db()` runs on import (`database.py:753`) and
creates any missing table via `CREATE TABLE IF NOT EXISTS`.

A helper for additive column changes exists — `_ensure_column(cursor, table, col,
typedef, default)` at `database.py:132-154`. It checks `information_schema.columns`
and issues `ALTER TABLE ADD COLUMN` when the column is absent, and validates the
table name against an `ALLOWED_TABLES` whitelist to prevent SQL injection through
the identifier. It currently has **no production call sites** — it is exercised only
by `test_security_fixes.py`, so it is available for the next additive change rather
than in active use.

**What this handles:** new tables, and new columns if `_ensure_column` is called.

**What it does not handle:** changing a column type, renaming, dropping,
backfilling data, or rolling anything back. With 38 tables that is a real
constraint — `alembic.ini` is present at the repo root but unused, which
suggests migrations were started and never finished. Adopting Alembic is the
recommended next step before any destructive schema change.

### 5.7 Integrity guards

Beyond primary and foreign keys:

| Guard | Where | Purpose |
|-------|-------|---------|
| `CHECK role IN ('admin','user')` | `users` | Invalid roles rejected by the database |
| `CHECK feed_score BETWEEN 1 AND 5` | `user_feedback` | Rating bounds |
| `trg_ensure_admin_remains` | `users`, `database.py:618-638` | `CONSTRAINT TRIGGER ... DEFERRABLE INITIALLY DEFERRED` on `AFTER DELETE OR UPDATE OF role`. Raises if no admin would remain. Deferred so it evaluates at commit, allowing a legitimate admin swap inside one transaction. The application checks this too, but that guard has been bypassed before |
| `idx_roadmap_progress_unique` | `user_roadmap_progress` | `COALESCE(analysis_id, -1)` closes the NULL-duplicate hole |

---

## 6. Resume Parsing Pipeline

### 6.1 File Upload & Validation

**Endpoint:** `POST /api/analyze`

**Validation Steps:**
1. File size check (max 5MB)
2. Magic byte validation:
   - PDF: `%PDF` (hex: `25 50 44 46`)
   - DOCX: `PK\x03\x04` (hex: `50 4B 03 04`)
3. Extension is NOT trusted — only magic bytes determine file type
4. DOCX requires a second check: `PK\x03\x04` is the generic ZIP signature shared by
   xlsx, pptx, jar and plain .zip, so the archive is opened and must contain both
   `[Content_Types].xml` and `word/document.xml` to qualify

**Code Location:** `api/routes/analysis.py:52-69` (`_detect_filetype`), called at line 83

### 6.2 Text Extraction

**PDF Extraction** (`api/extractor.py:14-22`):
```python
doc = fitz.open(pdf_path)
text = ""
for page in doc:
    text += page.get_text() + "\n"
```

**DOCX Extraction** (`api/extractor.py:27-38`):
```python
doc = docx.Document(docx_path)
text = ""
for para in doc.paragraphs:
    if para.text:
        text += para.text + "\n"
```

### 6.3 Local Regex Parser (Tier 1)

**File:** `api/resume_parser.py` (499 lines)

**Always runs first** — produces a confidence score that determines if AI is needed.

#### Step-by-Step Process:

**1. Section Detection** (`_detect_section`)
- Strips leading bullets (•, ·, -, *, ▪) and trailing punctuation
- Word-boundary matches against 40+ header variants
- Canonical order: summary → experience → education → skills → projects → certifications → languages → awards
- Max header length: 40 characters

**Section Header Variants:**
```python
SECTION_HEADERS = {
    "experience": ["experience", "work experience", "professional experience",
                   "work history", "employment", "employment history",
                   "professional background", "career history", "relevant experience"],
    "education": ["education", "academic", "academic background",
                  "qualifications", "education & training", "university"],
    "skills": ["skills", "technical skills", "technical stack",
               "core competencies", "competencies", "technologies",
               "skills & tools", "key skills", "areas of expertise"],
    "projects": ["projects", "personal projects", "academic projects",
                 "portfolio", "selected projects", "notable projects"],
    "summary": ["summary", "profile", "objective", "about me",
                "professional summary", "career objective", "about", "overview"],
    "certifications": ["certifications", "certificates", "licenses",
                       "professional certifications", "credentials"],
    "languages": ["languages", "language skills", "spoken languages"],
    "awards": ["awards", "honors", "achievements", "recognition", "publications"],
}
```

**2. Entity Extraction**
- Email: `[\w.+-]+@[\w.-]+\.\w+`
- LinkedIn: `linkedin\.com/in/[\w-]+`
- GitHub: `github\.com/[\w-]+`
- Phone: 10-15 digits, prefers `+` or parens

**3. Skill Extraction** (`extract_skills_fuzzy` in `parser_enhancements.py`)
- Uses **rapidfuzz** with `fuzz.WRatio` scorer
- Threshold: 85% similarity
- Generates 1-3 grams from text tokens
- Matches against full skill taxonomy
- Catches variants: "JS" → "JavaScript", "k8s" → "Kubernetes"

**4. Skill Inference** (`infer_implicit_skills`)
- Expands found skills using inference graph
- Example: "React" → ["javascript", "html", "css", "jsx", "typescript"]
- 60+ technology mappings across all domains

**5. Name Detection** (`_detect_name`)
- Primary: spaCy NER (PERSON entity) on first 10 lines
- Fallback: 2-4 Title-Case words, no digits, no noise

**6. Experience Parsing** (`_parse_experience_blocks`)
- Date-range detection using regex + dateutil
- Scans backwards from date line for title/company headers
- Scans forwards for bullet points
- Stops bullets at next title-like line

**7. Education Parsing** (`_parse_education_blocks`)
- Degree keyword matching (PhD, MBA, MS, BS, etc.)
- Year extraction: `\b(?:19|20)\d{2}\b`
- Institution = remaining text after removing degree/year

**8. Company Extraction** (`extract_companies_spacy`)
- spaCy ORG entities
- Filters out false positives (university, college, etc.)

**9. Match Score** (`_compute_local_match_score`)
```
score = 20 + (required_matched × 12) + (nice_matched × 5)
range: 20-95
```

**10. Confidence Scoring**
```
+20 for name found
+20 for email found
+5 for phone found
+25 for 5+ skills found
+15 for experience blocks found
+10 for education blocks found
+5 for summary found
max: 100
```

**11. Roadmap Generation** (`generate_personalized_roadmap`)
- Groups missing skills into phases
- Estimates duration based on difficulty
- Generates action items per skill
- Adds career prep phase

### 6.4 AI Provider Chain (Tier 2)

**File:** `api/ai_provider.py`

**Provider Order** (from `AI_PROVIDERS` env, default: `gemini,openai`):

1. **GeminiProvider** (`gemini-2.0-flash`, set at `ai_provider.py:32`)
   - Uses `google.generativeai`
   - Structured JSON output with schema enforcement
   - Default temperature: 0.2 for JSON, 0.7 for chat

2. **OpenAICompatibleProvider**
   - Uses `httpx` for HTTP calls
   - Works with any OpenAI-API-compatible endpoint
   - Configurable model, base URL

**Prompt Construction** (`extractor.py:57-80`):
- Target role instruction
- Strict JSON schema enforcement
- Requests: name, email, skills, education, experience, experience_blocks, education_blocks, missing_skills, match_score, roadmap

**Fallback:** If both providers fail or return empty → use local regex result

### 6.5 Caching

**Cache Key:** `(content_hash, target_role)`
- `content_hash` = SHA-256 of `f"{_CACHE_VERSION}:"` + file bytes. Bumping
  `_CACHE_VERSION` (`analysis.py:30`, currently **3**) invalidates every entry at once,
  which is how scoring changes are rolled out without a manual purge.
- `target_role` = requested role (or None)

**TTL:** 7 days

**Storage:** `analysis_cache` table

**Invalidation:** Automatic on expiry, manual via admin panel

---

## 7. Scoring & Matching Algorithms

### 7.1 Resume Score Breakdown

**Total: 100 points**

| Category | Max Points | Criteria |
|----------|-----------|----------|
| Summary | 15 | Present if >30 chars |
| Education | 15 | Present if any education found |
| Experience | 35 | Entry count (8) + bullet count (8) + avg bullets (6) + action verbs (6) + metrics (7) |
| Skills | 25 | Role-aware: required skills count 2x |
| Contact Info | 10 | Email (5) + phone (5) |

**Experience Scoring Detail:**
```python
# Entry count (max 8)
if entries >= 3: 8 pts
elif entries == 2: 6 pts
elif entries == 1: 3 pts

# Bullet count (max 8)
if bullets >= 6: 8 pts
elif bullets >= 3: 6 pts
elif bullets >= 1: 3 pts

# Avg bullets per entry (max 6)
if avg >= 3: 6 pts
elif avg >= 2: 4 pts
elif avg >= 1: 2 pts

# Action verbs (max 6)
if verb_count >= 5: 6 pts
elif verb_count >= 3: 4 pts
elif verb_count >= 1: 2 pts

# Metrics/quantified impact (max 7)
if metric_count >= 3: 7 pts
elif metric_count >= 2: 5 pts
elif metric_count >= 1: 3 pts
```

**Skills Scoring:**
- Required skills matched: 2 points each
- Nice-to-have skills matched: 1 point each
- Max: 25 points

### 7.2 Match Score

**Formula:**
```
match_score = 20 + (required_matched × 12) + (nice_matched × 5)
range: 20-95
```

### 7.3 Job Candidate Ranking

**Formula:**
```
rank_score = (resume_score × 0.5) + (match_score × 0.45) - (missing_count × 1.5)
```

### 7.4 Skill Gap Prioritization

**Factors:**
1. **Category count:** Skills in more role categories score higher
2. **Foundational bonus:** Skills that are prerequisites for other missing skills
3. **Adjacent-skill bonus:** Skills related to already-found skills

### 7.5 Field Prediction

**Algorithm:** Weighted keyword matching
- Designation matches: 3x weight
- Exact skill matches: 2x weight
- Partial skill matches: 1x weight
- Objective/summary matches: 1x weight
- Minimum threshold: 3 points

---

## 8. Authentication & Security

### 8.1 JWT Token System

**Access Token:**
- Algorithm: HS256
- Expiry: 30 minutes
- Storage: httpOnly cookie (`skillpath_access`)
- Claims: `exp`, `type="access"`, `jti`

**Refresh Token:**
- Algorithm: HS256
- Expiry: 30 days
- Storage: httpOnly cookie (`skillpath_refresh`)
- DB: SHA-256 hash stored in `refresh_tokens` table
- Rotation: New token issued on every refresh, old one deleted

**Cookie Settings:**
- `httpOnly: true` (not accessible via JavaScript)
- `secure: true` in production
- `SameSite: lax` in development, `strict` in production
- `path: /`

### 8.2 Password Security

**Hashing:** bcrypt with 12 rounds
**Truncation:** 72-byte limit enforced (bcrypt max)
**Verification:** `bcrypt.checkpw()`

### 8.3 OTP Verification

**Registration Flow:**
1. User registers → account created with `email_verified=0`
2. 6-digit OTP generated, hashed (SHA-256), stored in `otp_codes`
3. OTP sent via SMTP email
4. User enters OTP → verified → `email_verified=1`

**Password Reset Flow:**
1. User requests reset → 6-digit OTP sent to email
2. User enters OTP → verified → reset_token issued
3. User sets new password with reset_token

**OTP Constraints:**
- Length: 6 digits
- TTL: 10 minutes
- Max attempts: 5
- Resend cooldown: 60s (prod) / 5s (dev)

### 8.4 Login Lockout

- Max attempts: 5
- Lockout duration: 15 min (prod) / disabled (dev)
- Tracked in `login_attempts` table

### 8.5 Rate Limiting

**Global Rate Limit:**
- Production: 120 requests/minute/IP
- Development: 1000 requests/minute/IP
- Bucket key: `ip:minute`

**Auth Endpoint Rate Limit:**
- Production: 20 requests/minute/IP
- Development: 1000 requests/minute/IP

**Cleanup:** Every 5 minutes, expired buckets deleted

### 8.6 Security Headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self';
  style-src 'self' 'unsafe-inline'; img-src 'self' data: https:;
  font-src 'self' data:; connect-src 'self' https:;
  frame-ancestors 'none'; base-uri 'self';
```

### 8.7 CORS

- Configurable via `CORS_ORIGINS` env var
- Default: `http://localhost:5173,http://127.0.0.1:5173`
- Wildcard `*` prohibited in production
- Credentials allowed (for cookies)

---

## 9. API Reference

### Authentication Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create account (sends OTP) | No |
| POST | `/api/auth/verify-email` | Verify email with OTP | No |
| POST | `/api/auth/resend-otp` | Resend verification OTP | No |
| POST | `/api/auth/resend-verification` | Resend from login screen | No |
| GET | `/api/auth/check-username/{username}` | Check username availability | No |
| POST | `/api/auth/login` | Login (username or email) | No |
| POST | `/api/auth/logout` | Logout | Yes |
| GET | `/api/auth/me` | Get current user | Cookie |
| POST | `/api/auth/refresh` | Rotate refresh token | Cookie |
| POST | `/api/auth/request-password-reset` | Request reset OTP | No |
| POST | `/api/auth/verify-reset-otp` | Verify reset OTP | No |
| POST | `/api/auth/reset-password` | Set new password | No |
| POST | `/api/auth/change-password` | Change password | Yes |

### Analysis Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/analyze` | Upload & analyze resume | Yes |
| GET | `/api/user/latest-analysis` | Get latest analysis | Yes |
| GET | `/api/user/history` | Get analysis history | Yes |
| DELETE | `/api/user/history` | Delete all history | Yes |
| DELETE | `/api/user/analysis/{id}` | Delete single analysis | Yes |

### Career Toolkit Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/jobs/matches` | Job match suggestions | Optional |
| POST | `/api/interview/copilot` | Interview questions | Optional |
| POST | `/api/interview/simulate` | AI interview turn | Optional |
| POST | `/api/rewrite-resume` | Rewrite resume bullets | Optional |
| POST | `/api/jd/compare` | Compare resume to JD | Optional |
| POST | `/api/projects/recommend` | Project recommendations | Optional |
| POST | `/api/team/rank-candidates` | Rank candidates | Optional |

### Mock Interview Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/mock-interview` | List roles | No |
| GET | `/api/mock-interview/{role}` | Get questions | No |
| POST | `/api/mock-interview/start` | Start AI interview | **No** ⚠️ |
| POST | `/api/mock-interview/answer` | Submit answer | **No** ⚠️ |
| GET | `/api/mock-interview/session/{id}` | Get session | **No** ⚠️ |
| POST | `/api/mock-interview/finish/{id}` | End session | **No** ⚠️ |

> ⚠️ **Known gap:** the AI interview routes in `api/mock_interview_ai.py` declare no
> `Depends(get_current_user)` and the router has no dependency, so they are
> **publicly reachable** and each call spends AI provider quota. Sessions are also held
> in a module-level `_sessions = {}` dict (`mock_interview_ai.py:45`), so they are lost
> on restart and not shared across workers. Both should be fixed before production.

### User Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/PUT | `/api/user/profile` | Get/update profile | Yes |
| GET/PUT | `/api/user/preferences` | Get/update preferences | Yes |
| GET | `/api/user/skill-trends` | Skill trends | Yes |
| GET/PUT | `/api/user/roadmap-progress` | Roadmap progress | Yes |
| DELETE | `/api/user/account` | Delete account | Yes |
| POST | `/api/user/contact-support` | Support request | Yes |

### Sharing Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/reports/share` | Create share link | Yes |
| GET | `/api/reports/share/{token}` | View shared report | No |
| DELETE | `/api/reports/share/{token}` | Revoke share | Yes |
| GET | `/api/reports/my-shares` | List my shares | Yes |

### Admin Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/admin/users` | Resume logs | Admin |
| GET | `/api/admin/users/{id}` | Analysis detail | Admin |
| DELETE | `/api/admin/users/{id}` | Delete user data | Admin |
| GET | `/api/admin/registered-users` | List users | Admin |
| PATCH | `/api/admin/registered-users/{id}/role` | Change role | Admin |
| PATCH | `/api/admin/registered-users/{id}/status` | Activate/deactivate | Admin |
| DELETE | `/api/admin/registered-users/{id}` | Delete user | Admin |
| GET/POST/PATCH/DELETE | `/api/admin/courses` | Course CRUD | Admin |
| GET/POST/PATCH/DELETE | `/api/admin/job-roles` | Job role CRUD | Admin |
| GET/POST/DELETE | `/api/admin/job-roles/{id}/roadmaps` | Roadmap CRUD | Admin |
| GET | `/api/admin/feedback` | Feedback list | Admin |
| GET | `/api/admin/feedback/stats` | Feedback stats | Admin |
| DELETE | `/api/admin/feedback/{id}` | Delete feedback | Admin |
| GET | `/api/admin/analytics` | Platform analytics | Admin |
| GET | `/api/admin/quality-metrics` | Quality metrics | Admin |
| GET | `/api/admin/audit-logs` | Audit trail | Admin |
| GET/DELETE | `/api/admin/analysis-cache` | Cache management | Admin |
| GET | `/api/admin/api-usage` | API usage stats | Admin |
| GET | `/api/admin/export/{table}` | CSV export | Admin |
| POST | `/api/admin/scrape-courses` | Scrape courses | Admin |
| POST | `/api/admin/trigger-scrape` | Trigger market scrape | Admin |

### Public Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/health` | Health check | No |
| GET | `/api/job-roles` | List active roles | No |
| GET | `/api/trends/status` | Scraper status | No |
| POST | `/api/feedback` | Submit feedback | Yes |
| GET | `/api/billing/plans` | Billing plans | No |
| GET | `/api/notifications` | List notifications | Yes |

---

## 10. Frontend Architecture

### 10.1 Technology Stack

- **Framework:** React 19 with TypeScript
- **Build Tool:** Vite 7
- **Routing:** React Router DOM 7 (lazy-loaded routes)
- **State:** React Context (AuthContext) + local component state
- **HTTP Client:** Axios with interceptors
- **Charts:** Recharts
- **Icons:** Lucide React
- **Animations:** Framer Motion

### 10.2 Routing Structure

```
/                       → Landing (public)
/shared/:token          → SharedReport (public)
/app                    → Analyzer (authenticated)
/analysis               → AnalysisResult (authenticated)
/settings               → Settings (authenticated)
/profile                → Profile (authenticated)
/admin                  → Admin Dashboard (admin only)
/admin/dashboard        → Admin Dashboard
/admin/resumes          → Resume Logs
/admin/users            → User Management
/admin/feedback         → Feedback Management
/admin/courses          → Course Management
/admin/job-roles        → Job Role Management
/admin/ai-monitoring    → AI Monitoring
/mock-interview         → Mock Interview (authenticated)
```

### 10.3 Authentication Flow

**AuthContext** (`context/AuthContext.tsx`):
- Reads `/api/auth/me` on mount
- Caches profile in localStorage (`skillpath_profile`)
- Provides: `user`, `loading`, `login()`, `logout()`, `updateUser()`
- Axios interceptor handles 401 → redirects to login

**Login Flow:**
1. User submits credentials → POST `/api/auth/login`
2. Server sets httpOnly cookies (access + refresh)
3. Client calls `/api/auth/me` to get user profile
4. Profile cached in localStorage

**Token Refresh:**
- Access token expires after 30 min
- Refresh token valid for 30 days
- POST `/api/auth/refresh` rotates refresh token
- Automatic via cookie (no client-side token management)

### 10.4 Key Components

**AuthModal** (`components/AuthModal.tsx`):
- Login / Register tabs
- Email OTP verification flow
- Password reset flow
- "Username or email" login field

**Sidebar** (`components/Sidebar.tsx`):
- Collapsible (persisted to localStorage)
- Role-based sections (admin vs user)
- Navigation groups: Analyze / Track / Manage

**ErrorBoundary** (`components/ErrorBoundary.tsx`):
- Class-based error boundary
- Recovery UI with reset button
- Logs errors via componentDidCatch

**ProtectedRoute** (`components/ProtectedRoute.tsx`):
- Route guard with role-based access
- `allowedRoles` / `excludedRoles` props

### 10.5 State Management

**Local Storage Keys:**
- `skillpath_profile` — Cached user profile
- `skillpath_sidebar_collapsed` — Sidebar state

**API Service** (`services/api.ts`):
- Axios instance with `withCredentials: true`
- Response interceptor: 401 → logout handler
- `registerLogoutHandler(fn)` for custom 401 handling

---

## 11. Configuration & Environment

### 11.1 Required Environment Variables

```env
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here

# Security (required in production)
JWT_SECRET_KEY=at-least-32-random-characters-please

# Database
DB_FILE=api/cv.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Environment
ENV=development
```

### 11.2 Optional Environment Variables

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Admin account (auto-created on first boot)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me_in_production

# AI Provider Chain
AI_PROVIDERS=gemini,openai
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=you@gmail.com
SMTP_PASSWORD=xxxx_xxxx_xxxx_xxxx
SMTP_FROM_NAME=SkillPath
SMTP_STARTTLS=false

# Rate Limiting
RATE_LIMIT_PER_MINUTE=120

# Market Data
MARKET_DATA_PROVIDER=theirstack
THEIRSTACK_API_KEY=your_key
```

### 11.3 Environment-Specific Behavior

| Behavior | Development | Production |
|----------|-------------|------------|
| JWT Secret | Random per-process | Required from env |
| Rate Limit | 1000/min | 120/min |
| Auth Rate Limit | 1000/min | 20/min |
| Login Lockout | Disabled | 15 min |
| OTP Resend Cooldown | 5s | 60s |
| Cookie Secure | false | true |
| Cookie SameSite | lax | strict |
| CORS Wildcard | Allowed | Prohibited |
| Admin Password | Any | Must not be default |

---

## 12. Algorithms Deep Dive

### 12.1 Skill Inference Graph

**File:** `api/parser_enhancements.py`

**Concept:** When a skill is found, infer related skills that the candidate likely knows.

**Coverage:**
- Frontend frameworks (React, Angular, Vue, Svelte)
- Backend frameworks (Flask, Django, Express, Spring)
- Languages (JavaScript, Python, Java, Go, Rust)
- Databases (PostgreSQL, MongoDB, Redis)
- Cloud platforms (AWS, GCP, Azure)
- DevOps tools (Docker, Kubernetes, Terraform)
- ML/Data tools (TensorFlow, PyTorch, Spark)
- Mobile development (Flutter, React Native)
- Testing frameworks (Jest, Pytest, Selenium)
- APIs & protocols (GraphQL, REST, gRPC)

**Example Mappings:**
```
"react" → ["javascript", "html", "css", "jsx", "typescript"]
"flask" → ["python", "rest api", "web development"]
"kubernetes" → ["containerization", "devops", "infrastructure", "orchestration"]
"tensorflow" → ["python", "machine learning", "deep learning", "neural networks"]
```

### 12.2 Fuzzy Skill Matching

**Library:** rapidfuzz (`fuzz.WRatio`)

**Process:**
1. Tokenize text into words (1-3 grams)
2. For each token, find best match in skill taxonomy
3. Score using Weighted Ratio (WRatio)
4. Threshold: 85% similarity
5. Title-case results for consistency

**Noise Filter:**
- Single letters (c, r, go)
- Generic computing terms (cpu, gpu, ram)
- Protocols (tcp, udp, ip, ftp)
- Media formats (png, jpg, mp3)

### 12.3 Date Parsing

**Library:** python-dateutil + custom regex

**Supported Formats:**
- "Jan 2020 - Present"
- "January 2020 – December 2023"
- "2020 - 2023"
- "01/2020 - 12/2023"
- "since 2019"
- "March 2021 – current"

**Process:**
1. Quick check: must contain date-like component (month name, year, etc.)
2. Try precompiled regex patterns (most specific first)
3. Fallback: dateutil parser on month-name-containing text
4. Normalize output: "Jan 2020", "Present"

### 12.4 Experience Block Parsing

**Algorithm:**
1. Find all lines containing date ranges
2. For each date line:
   - Scan backwards: collect header lines (non-bullet, <100 chars)
   - Scan forwards: collect bullet lines until next date or title
3. Extract title/company from headers or same-line content
4. Merge: prefer explicit headers, fall back to same-line extraction

**Header Line Rules:**
- No bullet prefix
- Less than 100 characters
- No blank lines between headers
- 2+ headers: first = title, second = company
- 1 header: try "at/@/-" separator

**Bullet Line Rules:**
- Starts with bullet character OR indented text
- Stops at next date line
- Stops at next title-like line (short, title case, title keyword)

### 12.5 Roadmap Generation

**Algorithm:**
1. Get missing skills for target role
2. Prioritize by: category count, foundational bonus, adjacent-skill bonus
3. Group related skills into phases (by cluster)
4. Estimate duration based on difficulty:
   - Easy (≤1.3): 1 week per skill
   - Medium (≤2.3): 2 weeks per skill
   - Hard (>2.3): 3 weeks per skill
5. Generate action items per skill
6. Add career prep phase (interview prep, portfolio)

**Phase Structure:**
```python
{
    "step": 1,
    "title": "Fundamentals",
    "duration": "2 weeks",
    "skills": ["skill1", "skill2"],
    "action_items": ["Learn X", "Build Y", "Read Z"],
    "resources": [{"title": "...", "url": "..."}],
    "difficulty": "Fundamentals"
}
```

---

## 13. Testing

### 13.1 Test Suite Overview

**Total: 131 tests across three layers.**

| Layer | Count | Framework | Location |
|-------|-------|-----------|----------|
| Backend | 75 | pytest 8.0+ | `api/tests/` |
| Frontend unit | 40 | Vitest + React Testing Library (jsdom) | `frontend/src/**/*.test.tsx` |
| End-to-end | 16 | Playwright (chromium) | `frontend/e2e/` |

### 13.2 Test Files

**Backend** (`api/tests/`):

| File | Tests | Focus |
|------|-------|-------|
| `test_integration.py` | 36 | API endpoints, auth flows |
| `test_features.py` | 29 | Resume parser, scoring, skill matching |
| `test_security_fixes.py` | 10 | Security regression tests |

**Frontend** (`frontend/src/`):

| File | Focus |
|------|-------|
| `test/apiContract.test.ts` | Reads the Python route files and asserts frontend field names still match the backend. Exists because two production bugs came from drift the type checker cannot see across HTTP: admin tables keyed on `ID` when Postgres returns `id`, and `current_role` vs `current_job_role` |
| `pages/Analyzer.test.tsx` | Upload, drag-drop, error handling |
| `context/AuthContext.test.tsx` | Session bootstrap and 401 handling |
| `components/interview/AiInterviewMode.test.tsx` | Question rendering, failure recovery |
| `components/admin/DataTable.test.tsx` | Admin table rendering |
| `components/profile/HistoryList.test.tsx` | Analysis history |
| `components/ErrorBoundary.test.tsx` | Render-error recovery |
| `services/api.test.ts` | Axios interceptor behaviour |

**E2E** (`frontend/e2e/`): `auth.spec.ts`, `analyzer.spec.ts`, `admin.spec.ts`,
`interview.spec.ts`. All `/api/**` calls are stubbed at the network layer via
`fixtures.ts`, so no backend or database is required.

### 13.3 Test Environment

**Backend** (`conftest.py`):
- PostgreSQL test database via `TEST_DATABASE_URL`
  (default `postgresql://postgres@localhost:5432/skillpath_test`)
- SMTP disabled (no real emails)
- AI provider keys disabled
- ENV=development

```bash
createdb skillpath_test
python -m pytest api/tests/      # from the repo root
```

**Frontend:**
```bash
cd frontend
npm test              # 40 unit tests
npm run test:e2e      # 16 Playwright tests
```

**Isolation:**
- Each test class gets fresh database state
- Rate limits cleared between tests
- Shared test client with `raise_server_exceptions=False`

### 13.4 Key Test Cases

**Parser Tests:**
- Name detection (spaCy + regex fallback)
- Experience block structure (title, company, dates, bullets)
- Education block structure (degree, institution, year)
- Skill extraction (taxonomy + fuzzy matching)
- Skill inference graph
- Section header variants
- Confidence scoring

**Integration Tests:**
- Registration + OTP verification flow
- Login (username + email)
- Login blocked until email verified
- Password reset flow
- Rate limiting (429 responses)
- Resend OTP cooldown

**Security Tests:**
- Password hashing/verification
- JWT token creation/validation
- Token refresh rotation
- OTP attempt limits
- Login lockout

---

## 14. Deployment

### 14.1 Backend Deployment

```bash
# Activate virtual environment
source venvapp/bin/activate

# Install dependencies
pip install -r api/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Tables are created by init_db() on import - no migration step
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 14.2 Frontend Deployment

```bash
cd frontend
npm install
npm run build
# Serve dist/ with any static file server
```

### 14.3 Environment Setup

**Production Checklist:**
- [ ] Set `ENV=production`
- [ ] Set `JWT_SECRET_KEY` (32+ random chars)
- [ ] Set `DATABASE_URL` for PostgreSQL
- [ ] Set `CORS_ORIGINS` (no wildcard)
- [ ] Set `ADMIN_PASSWORD` (strong)
- [ ] Configure SMTP for email
- [ ] Set AI provider API keys
- [ ] Run `python -m spacy download en_core_web_sm`

### 14.4 Docker Support

**docker-compose.yml** defines three services:
- `db` — PostgreSQL 16 Alpine with a `pg_isready` health check and a named volume
- `backend` — built from `Dockerfile.backend`, waits for `db` to be healthy,
  health-checked on `/api/health`
- `frontend` — built from `Dockerfile.frontend`

```bash
docker compose up -d          # full stack
docker compose up -d db       # database only, run the app locally
DATABASE_URL=postgresql://skillpath:skillpath@localhost:5432/skillpath
```

### 14.5 Continuous Integration

`.github/workflows/ci.yml` defines five jobs:

| Job | What it runs |
|-----|--------------|
| `frontend` | ESLint, `tsc --noEmit`, 40 Vitest tests, build |
| `e2e` | Build, then 16 Playwright tests (chromium, cached browsers) |
| `backend` | 75 pytest tests against a Postgres service container, matrix 3.9 / 3.11 / 3.12 |
| `analysis` | Static analysis |
| `release` | Artifact packaging and GitHub release |

---

## Appendix A: Skill Taxonomy

**8 Categories, 116+ Skills:**

| Category | Count | Examples |
|----------|-------|----------|
| Programming Languages | 20 | Python, JavaScript, Java, Go, Rust, C# |
| Web Frameworks | 17 | React, Angular, Django, Flask, Express |
| Databases | 14 | PostgreSQL, MongoDB, Redis, Cassandra |
| Cloud & DevOps | 18 | AWS, Docker, Kubernetes, Terraform |
| Data Science & AI | 15 | TensorFlow, PyTorch, Pandas, Spark |
| Mobile Development | 8 | Flutter, React Native, Swift, Kotlin |
| Soft Skills | 10 | Leadership, Communication, Teamwork |
| Other Technical | 14 | Git, GraphQL, REST, Microservices |

## Appendix B: Role Configurations

**22 predefined roles**, seeded from `api/seed_defaults.py`:

| Constant | Type | Entries |
|----------|------|---------|
| `DEFAULT_ROLES` | list | 22 |
| `DEFAULT_ROLE_SKILLS` | dict | 22 |
| `DEFAULT_ROADMAPS` | dict | 22 |
| `CORE_SKILLS_BY_ROLE` | dict | 8 |

Covering backend, frontend, full stack, data science/analysis/engineering,
DevOps, cloud, SRE, mobile, ML/AI, security, QA, product, engineering
management, UI/UX and technical writing.

**Each role has:** a skill list split into required and nice-to-have
(`job_role_skills.is_required`), a multi-phase roadmap, project suggestions
and interview focus areas.

---

*This document covers every technical aspect of the SkillPath.ai platform. For questions or updates, refer to the source code directly.*
