# SkillPath

> Open-source, AI-powered resume analysis, career coaching, and skill gap identification platform.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## Overview

SkillPath is a full-stack SaaS platform that transforms static resume reviews into data-driven career coaching. It parses PDF/DOCX resumes, evaluates skills against real-time industry demands, and generates personalized learning roadmaps using NLP and Generative AI.

This is a community project — contributions are welcome. See [Contributing](#contributing) to get started.

### Who It's For

| Audience | Use Case |
|----------|----------|
| **Job Seekers** | Improve resume, identify skill gaps, prepare for interviews |
| **Career Changers** | Plan transition path into tech roles |
| **Recruiters** | Evaluate candidate fit against job requirements |
| **Hiring Managers** | Understand market trends and skill demands |

---

## Features

### Resume Analysis
- Multi-format parsing (PDF, DOCX) with magic-byte validation
- 22 predefined target roles (Data Science, Web Development, DevOps, Cloud Engineering, AI/ML, Cybersecurity, Mobile Development, and 15 more)
- Skills classified as **required** (6 per role) and **nice-to-have** (9 per role)
- Resume score breakdown across 5 dimensions with weighted scoring
- Required skills weighted 2.4x in match score calculation

### AI-Powered Career Coaching
- 4-phase learning roadmap generation (Gemini / OpenAI-compatible + regex fallback)
- Interactive roadmap progress tracking with skill-level checkpoints
- Actionable learning recommendations per skill gap
- Course suggestions from Coursera and Udemy with platform-branded thumbnails

### Career Toolkit
- **Mock Interview** — Practice mode (static questions) + AI mode (dynamic, LLM-generated)
- **Job Matches** — Market-aligned job suggestions with role fit scores
- **Resume Rewrite** — Rewrites experience bullets with stronger action/outcome framing
- **JD Comparator** — Keyword coverage analysis against job descriptions
- **Project Optimizer** — Portfolio project recommendations based on skill gaps
- **Team Ranking** — Rank multiple candidates with unified scoring

### User Dashboard
- Historical analysis tracking with score progression charts
- Skill trends visualization (learned vs. missing over time)
- Roadmap progress persistence across sessions
- Account settings with password change and self-deletion

### Market Intelligence
- Skill demand trends by role (area, bar, and pie charts)
- Salary ranges and job posting trends
- Workplace distribution (remote/hybrid/onsite)
- Regional market comparisons

### Admin Panel
- **Dashboard** — Total users, resumes analyzed, average scores, upload trends
- **User Management** — Search, role toggle, activate/deactivate accounts
- **Resume Logs** — Paginated resume detail view with delete
- **Feedback** — Sentiment analysis (positive/negative/neutral ratio), color-coded ratings, distribution chart
- **Courses** — CRUD for course recommendations per role
- **Job Roles** — Read-only predefined roles with inline course management
- **Market Data** — Role-specific skill demand, salary trends, workforce distribution
- **AI Monitoring** — Analysis cache management, API usage tracking
- **Audit Logs** — Full activity audit trail
- **Data Export** — CSV export for any table
- **Taxonomy** — Skills, roadmaps, role configs, video resources management

---

## Tech Stack

### Frontend

Managed with **Bun** (install, dev server, build, lint).

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
| Python | 3.9+ | Runtime |
| FastAPI | 0.115+ | Web framework |
| Uvicorn | — | ASGI server |
| SQLite / PostgreSQL | — | Database (dual support via `DATABASE_URL`) |
| SQLAlchemy | 2.0+ | ORM + schema definitions |
| Alembic | 1.13+ | Database migrations |
| psycopg2-binary | 2.9+ | PostgreSQL adapter (optional) |
| PyJWT | 2.10+ | JWT token management |
| bcrypt | 4.2+ | Password hashing |
| Google Generative AI | 0.8+ | Gemini API (optional) |
| PyMuPDF | 1.24+ | PDF parsing |
| python-docx | 1.1+ | DOCX parsing |
| defusedxml | 0.7+ | Safe XML parsing |
| httpx | 0.28+ | Async HTTP client (course scraping) |
| beautifulsoup4 | 4.12+ | HTML parsing |
| pytest | 8.0+ | Test framework |

### AI Providers

SkillPath uses an **ordered fallback chain** (`AI_PROVIDERS`, default `gemini,openai`). If the first provider has no key, the next is tried; if no provider is configured, a fully local parser handles analysis.

| Provider | Config | Notes |
|----------|--------|-------|
| **Google Gemini** | `GEMINI_API_KEY` | Primary: analysis, roadmap generation, interview questions |
| **OpenAI-compatible** | `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL` | Works with OpenAI, Groq, Together, OpenRouter, or local Ollama |
| **Local fallback** | none | Deterministic regex parser (no LLM required) |

Example — Groq as the AI provider:
```env
AI_PROVIDERS=openai,gemini
OPENAI_API_KEY=your_groq_key
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_MODEL=llama-3.3-70b-versatile
```

---

## Project Structure

```
skillpath.ai/
├── api/                            # Backend (FastAPI)
│   ├── main.py                     # App entry, middleware, CORS, router registration
│   ├── database.py                 # DB connections, init, migrations entry
│   ├── models.py                   # SQLAlchemy table definitions (38 tables)
│   ├── db_compat.py                # SQLite/PostgreSQL compatibility layer
│   ├── alembic/                    # Database migrations
│   │   └── versions/               # Migration scripts
│   ├── auth.py                     # JWT creation/validation, auth dependencies
│   ├── security.py                 # Password hashing (bcrypt)
│   ├── exceptions.py               # Error handling
│   ├── extractor.py                # Resume text extraction (PDF/DOCX/Gemini)
│   ├── ai_provider.py              # Gemini + OpenAI-compatible provider chain
│   ├── resume_parser.py            # Local fallback resume parsing
│   ├── resume_patterns.py          # Regex/keyword patterns for parsing
│   ├── career_services.py          # Resume scoring, skill analysis
│   ├── skill_matching.py           # Skill matching helpers
│   ├── job_hunt_services.py        # Job matching, JD comparison
│   ├── roadmap_services.py         # Roadmap generation logic
│   ├── skills_taxonomy.py          # Skill taxonomy data
│   ├── i18n.py                     # Translation support
│   ├── trends.py                   # Trend analysis helpers
│   ├── courses.py                  # Course recommendation logic
│   ├── course_data.py              # Course/roadmap/field data
│   ├── seed_data.py                # In-memory caches + loaders/getters
│   ├── seeders.py                  # DB seeding functions
│   ├── seed_content.py             # Default seed content
│   ├── seed_defaults.py            # Default roles/roadmaps data
│   ├── market_data.py              # Market trend data + cache
│   ├── email_service.py            # SMTP delivery (OTP, password reset)
│   ├── mock_interview.py           # Static interview questions
│   ├── mock_interview_ai.py        # AI-generated interview sessions
│   ├── course_scraper.py           # Coursera scraping, Udemy fallback
│   ├── scraper.py                  # Market data simulation
│   ├── requirements.txt            # Python dependencies
│   ├── routes/
│   │   ├── admin.py                # Admin CRUD, audit, export, taxonomy
│   │   ├── auth.py                 # Register, login, logout, refresh, password
│   │   ├── user.py                 # Profile, preferences, history, analysis
│   │   ├── analysis.py             # Resume analysis pipeline
│   │   ├── jobs.py                 # Job matches, interview, JD compare
│   │   ├── sharing.py              # Public report sharing
│   │   ├── misc.py                 # Feedback, billing, notifications, i18n
│   │   └── health.py               # Health check
│   ├── data/
│   │   └── mock_questions.json     # Static interview questions
│   └── llm/
│
├── frontend/                       # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.tsx                 # Routes (lazy-loaded)
│   │   ├── main.tsx                # Entry point
│   │   ├── types/
│   │   │   └── index.ts            # Shared TypeScript interfaces
│   │   ├── pages/                  # Landing, Analyzer, AnalysisResult, Admin, ...
│   │   ├── components/             # Feature-scoped component modules
│   │   │   ├── analyzer/           # Resume upload + analysis UI
│   │   │   ├── results/            # Analysis results (score, gaps, roadmap)
│   │   │   ├── sidebar/            # App shell navigation
│   │   │   ├── trends/             # Market trend charts
│   │   │   ├── auth/               # Login/register modal
│   │   │   ├── admin/              # Admin panels
│   │   │   ├── landing/            # Landing page sections
│   │   │   ├── interview/          # Mock interview UI
│   │   │   ├── profile/            # Profile + skill trends
│   │   │   ├── settings/           # Account settings
│   │   │   └── analysis/           # Shared analysis components
│   │   ├── context/
│   │   │   └── AuthContext.tsx     # Auth state management
│   │   ├── services/
│   │   │   └── api.ts              # Axios instance + interceptors
│   │   └── styles/
│   │       ├── theme.css           # Design tokens + global styles
│   │       └── animations.css      # Keyframe animations
│   ├── tsconfig.json
│   └── package.json
│
├── api/tests/                      # Backend test suite (pytest)
│   ├── conftest.py                 # Test env isolation (temp DB, no SMTP)
│   ├── test_integration.py         # API integration tests
│   ├── test_features.py            # Unit tests for core services
│   └── test_security_fixes.py      # Security regression tests
├── setup.sh                        # Cross-platform setup script
├── run.js                          # Cross-platform helper to run venv Python commands
├── dev.js                          # Starts backend + frontend together
├── pytest.ini                      # Pytest configuration
├── alembic.ini                     # Alembic migration configuration
├── docker-compose.yml              # PostgreSQL service for local development
├── bun.lock                        # Bun lockfile (committed, used with --frozen-lockfile)
├── package.json                    # Root scripts (setup, dev, build) — run with Bun
├── .env.example                    # Environment variable template
└── venvapp/                        # Python virtual environment (local only)
```

---

## Getting Started

### Prerequisites

- **Bun** v1.3+ ([install](https://bun.sh)) — used for all frontend install/dev/build/lint
- **Python** v3.9+ — `bun run setup` auto-creates a venv at `venvapp/` (Windows needs the `py` launcher from the official Python installer)
- **AI API key** (optional — app works without it using local regex parsing)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Theani7/skillpath.git
cd skillpath
git lfs install

# One-time setup (creates venv, installs Python + frontend dependencies, creates .env)
bun run setup

# Start both backend and frontend
bun run dev
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Bun Scripts

| Command | Description |
|---------|-------------|
| `bun run setup` | One-time setup: creates venv, installs Python + frontend dependencies |
| `bun run dev` | Starts backend + frontend in parallel |
| `bun run dev:backend` | Starts only the backend server |
| `bun run dev:frontend` | Starts only the frontend dev server |
| `bun run build` | Production build of the frontend |
| `bun run lint` | Run ESLint on frontend code |

### Environment Variables

Create a `.env` file in the project root (or copy `.env.example`):

```env
# Required for AI features
GEMINI_API_KEY=your_gemini_api_key_here

# Security (required in production)
JWT_SECRET_KEY=at-least-32-random-characters-please

# Database: leave DATABASE_URL empty to use SQLite (DB_FILE above).
# For PostgreSQL, set DATABASE_URL and leave DB_FILE empty.
# Format: postgresql://user:password@host:5432/dbname
# DATABASE_URL=postgresql://skillpath:skillpath@localhost:5432/skillpath
DB_FILE=api/cv.db

# CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Environment
ENV=development

# Admin account (auto-created on first boot if both set)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_me_in_production
```

Optional:

```env
# Alternative AI provider (OpenAI-compatible: OpenAI, Groq, Together, OpenRouter, Ollama)
AI_PROVIDERS=gemini,openai
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Email delivery (OTP verification + password reset)
# Gmail works with a Google App Password (16 chars, 2-Step Verification required)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=you@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_NAME=SkillPath
SMTP_STARTTLS=false

# Market data provider
MARKET_DATA_PROVIDER=theirstack
THEIRSTACK_API_KEY=your_key
RATE_LIMIT_PER_MINUTE=120
```

> **Email verification**: Registration sends a 6-digit OTP by email before login is allowed. SMTP must be configured for this to work — without it, registration and password reset return 503.

### Manual Setup

<details>
<summary>Manual setup instructions</summary>

#### Backend

```bash
python3 -m venv venvapp
source venvapp/bin/activate          # macOS/Linux
# venvapp\Scripts\activate           # Windows
pip install -r api/requirements.txt
uvicorn api.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
bun install
bun run dev
```

</details>

---

## Running Tests

The backend ships with a pytest suite (73 tests: API integration, unit, and security regressions):

```bash
source venvapp/bin/activate
python -m pytest -q
```

Test environment notes:
- `api/tests/conftest.py` forces a **temporary database** and disables SMTP/Gemini, so tests are deterministic regardless of your local `.env` (they never touch `api/cv.db` or send real emails).
- CI runs the same suite on Python 3.11 in `.github/workflows/ci.yml`.

---

## CI/CD

GitHub Actions (`.github/workflows/ci.yml`) runs on every push/PR:

- **Frontend** — installs with `bun install --frozen-lockfile`, then `bun run lint` and `bun run build`.
- **Backend** — `python -m pytest api/tests` against Python 3.11.


---

## API Reference

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create new user account (email OTP verification) | No |
| POST | `/api/auth/verify-email` | Verify email with 6-digit OTP | No |
| POST | `/api/auth/resend-otp` | Resend email verification OTP | No |
| POST | `/api/auth/login` | Authenticate with username or email (returns httpOnly cookies) | No |
| POST | `/api/auth/logout` | Invalidate refresh token | Yes |
| POST | `/api/auth/refresh` | Rotate refresh token | Cookie |
| POST | `/api/auth/change-password` | Change password | Yes |
| POST | `/api/auth/request-password-reset` | Request reset (emails 6-digit OTP) | No |
| POST | `/api/auth/verify-reset-otp` | Verify password reset OTP | No |
| POST | `/api/auth/reset-password` | Set new password with verified OTP | No |
| GET | `/api/auth/me` | Get current user profile | Cookie |
| GET | `/api/auth/check-username/{username}` | Check username availability | No |

### Analysis

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/analyze` | Upload and analyze resume | Yes |
| GET | `/api/user/latest-analysis` | Get most recent analysis | Yes |
| GET | `/api/user/history` | Get analysis history | Yes |
| DELETE | `/api/user/analysis/{analysis_id}` | Delete specific analysis | Yes |

### Career Toolkit

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/jobs/matches` | Get job match suggestions | Optional |
| POST | `/api/interview/copilot` | Generate interview questions | Optional |
| POST | `/api/interview/simulate` | Run simulated interview | Optional |
| POST | `/api/rewrite-resume` | Rewrite experience bullets | Optional |
| POST | `/api/jd/compare` | Compare resume against JD | Optional |
| POST | `/api/projects/recommend` | Get project recommendations | Optional |
| POST | `/api/team/rank-candidates` | Rank multiple candidates | Optional |

### Mock Interview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/mock-interview` | List available roles | No |
| GET | `/api/mock-interview/{role}` | Get questions for role | No |
| POST | `/api/mock-interview/start` | Start AI interview session | Yes |
| POST | `/api/mock-interview/answer` | Submit answer, get feedback | Yes |
| GET | `/api/mock-interview/session/{session_id}` | Get session transcript | Yes |
| POST | `/api/mock-interview/finish/{session_id}` | End session, get evaluation | Yes |

### User

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/user/profile` | Get user profile | Yes |
| PUT | `/api/user/profile` | Update profile | Yes |
| GET | `/api/user/preferences` | Get preferences | Yes |
| PUT | `/api/user/preferences` | Update preferences | Yes |
| GET | `/api/user/skill-trends` | Get skill trend data | Yes |
| GET | `/api/user/roadmap-progress` | Get roadmap progress | Yes |
| PUT | `/api/user/roadmap-progress` | Update roadmap progress | Yes |
| POST | `/api/user/contact-support` | Send support message | Yes |
| DELETE | `/api/user/account` | Delete account + all data | Yes |

### Report Sharing

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/reports/share` | Generate public share link for an analysis | Yes |
| GET | `/api/reports/my-shares` | List your shared reports | Yes |
| GET | `/api/reports/share/{token}` | Public shared report (no login) | No |
| DELETE | `/api/reports/share/{token}` | Revoke share link | Yes |

### Admin

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/admin/users` | List users + resume logs | Admin |
| GET | `/api/admin/users/{analysis_id}` | Analysis detail | Admin |
| DELETE | `/api/admin/users/{user_id}` | Delete user + data | Admin |
| GET | `/api/admin/registered-users` | Registered users (paginated) | Admin |
| PATCH | `/api/admin/registered-users/{user_id}/role` | Toggle admin role | Admin |
| PATCH | `/api/admin/registered-users/{user_id}/status` | Activate/deactivate user | Admin |
| DELETE | `/api/admin/registered-users/{user_id}` | Delete user | Admin |
| GET | `/api/admin/feedback` | List feedback (paginated) | Admin |
| GET | `/api/admin/feedback/stats` | Feedback sentiment stats | Admin |
| DELETE | `/api/admin/feedback/{feedback_id}` | Delete feedback | Admin |
| GET | `/api/admin/courses` | List all courses | Admin |
| POST | `/api/admin/courses` | Add course | Admin |
| PATCH | `/api/admin/courses/{course_id}` | Update course | Admin |
| DELETE | `/api/admin/courses/{course_id}` | Delete course | Admin |
| GET | `/api/admin/job-roles` | List job roles | Admin |
| POST | `/api/admin/job-roles` | Add job role | Admin |
| PATCH | `/api/admin/job-roles/{role_id}` | Update job role | Admin |
| PATCH | `/api/admin/job-roles/{role_id}/status` | Toggle role active/inactive | Admin |
| DELETE | `/api/admin/job-roles/{role_id}` | Delete job role | Admin |
| GET | `/api/admin/job-roles/{role_id}/roadmaps` | List role roadmaps | Admin |
| POST | `/api/admin/job-roles/{role_id}/roadmaps` | Add roadmap | Admin |
| POST | `/api/admin/job-roles/{role_id}/roadmaps/ai-generate` | AI-generate roadmap | Admin |
| POST | `/api/admin/job-roles/{role_id}/roadmaps/bulk` | Bulk add roadmaps | Admin |
| DELETE | `/api/admin/roadmaps/{roadmap_id}` | Delete roadmap | Admin |
| GET | `/api/admin/roadmap-templates` | Roadmap templates | Admin |
| GET | `/api/admin/analytics` | Platform analytics | Admin |
| GET | `/api/admin/analytics/uploads-over-time` | Upload trend data | Admin |
| GET | `/api/admin/analytics/skill-gaps` | Skill gap distribution | Admin |
| GET | `/api/admin/analytics/role-distribution` | Role distribution data | Admin |
| GET | `/api/admin/analytics/user-growth` | User growth data | Admin |
| GET | `/api/admin/api-usage` | API usage stats | Admin |
| GET | `/api/admin/quality-metrics` | Analysis quality metrics | Admin |
| GET | `/api/admin/audit-logs` | Activity audit trail | Admin |
| GET | `/api/admin/analysis-cache` | Cached analyses | Admin |
| DELETE | `/api/admin/analysis-cache/{content_hash}/{target_role}` | Invalidate cache entry | Admin |
| GET | `/api/admin/export/{table_name}` | Export table as CSV | Admin |
| GET | `/api/admin/taxonomy/overview` | Taxonomy overview | Admin |
| GET | `/api/admin/taxonomy/skills` | Skill taxonomy | Admin |
| GET | `/api/admin/taxonomy/roadmaps` | Roadmap taxonomy | Admin |
| GET | `/api/admin/taxonomy/role-configs` | Role configs | Admin |
| GET | `/api/admin/taxonomy/video-resources` | Video resources | Admin |
| POST | `/api/admin/scrape-courses` | Scrape courses for a role | Admin |
| POST | `/api/admin/trigger-scrape` | Trigger market data scrape | Admin |
| GET | `/api/admin/scrape-fields` | Scrapeable fields | Admin |
| GET | `/api/admin/scrape-status/{job_id}` | Scrape job status | Admin |
| POST | `/api/admin/reset-password` | Reset a user's password | Admin |

### Billing & Notifications

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/billing/plans` | Available plans | No |
| GET | `/api/billing/subscription` | Current user subscription | Yes |
| POST | `/api/billing/subscribe` | Subscribe to a plan | Yes |
| GET | `/api/notifications` | List notifications | Yes |
| POST | `/api/notifications` | Create notification | Yes |
| POST | `/api/notifications/{notification_id}/send` | Send notification | Yes |

### Public

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/health` | Health check | No |
| GET | `/api/job-roles` | List active job roles | No |
| GET | `/api/trends/status` | Market trends status | No |
| POST | `/api/feedback` | Submit feedback | Yes |

---

## Database

Dual support: **SQLite** (`api/cv.db`) for local development or **PostgreSQL** (via `DATABASE_URL`) for production. A `docker-compose.yml` is included for running PostgreSQL locally. Schema defined in SQLAlchemy (`api/models.py`) with **Alembic migrations** auto-applied on boot. 38 tables:

| Table | Purpose |
|-------|---------|
| `users` | User accounts with roles (admin/user) |
| `user_data` | Resume analysis history + full analysis JSON |
| `refresh_tokens` | SHA-256 hashed refresh JWTs |
| `job_roles` | 22 predefined career roles |
| `job_role_skills` | 330 skills (6 required + 9 nice-to-have per role) |
| `career_roadmaps` | 22 role-specific career roadmaps |
| `roadmap_steps` | 88 roadmap steps with resources |
| `courses` | 66 course recommendations (Coursera/Udemy) |
| `skill_recommendations` | 167 skill-specific learning recommendations |
| `learning_resources` | 54 curated learning resources |
| `learning_actions` | 81 actionable learning steps |
| `video_resources` | 186 video tutorials by skill |
| `skill_difficulty` | Difficulty ratings for 94 skills |
| `analysis_cache` | Cached analysis results (7-day TTL) |
| `audit_logs` | Admin activity audit trail |
| `request_logs` | API request logging |

### Seeding

On first boot, the database is automatically seeded with:
- 22 job roles with 15 skills each (6 required + 9 nice-to-have)
- 22 career roadmaps with 4 steps each
- 66 courses from Coursera/Udemy
- Skill recommendations, learning resources, video tutorials, and difficulty ratings

---

## Security

| Feature | Implementation |
|---------|---------------|
| **Authentication** | httpOnly cookies (`skillpath_access`, `skillpath_refresh`) with `SameSite=Strict` |
| **JWT** | HS256, 30-min access + 30-day refresh tokens |
| **Token Rotation** | Refresh tokens are SHA-256 hashed in DB, rotated on every refresh |
| **Password Hashing** | bcrypt (direct usage, no passlib) |
| **Account Deactivation** | `is_active` flag enforced at login + all auth dependencies |
| **File Validation** | Magic-byte checking (`%PDF`, `PK\x03\x04`), not just extension |
| **Input Validation** | Pydantic models with `max_length` and pattern constraints |
| **Rate Limiting** | IP-based bucketing (relaxed in dev: 1000/min, strict in prod: 120/min) |
| **CORS** | Restricted to configured origins |
| **Admin Protection** | Role-based route exclusion (`excludedRoles` prop) |
| **Email Verification** | 6-digit OTP required before login (hashed in DB, expiry + attempt limits) |

### Reporting a Vulnerability

Found a security issue? **Do not open a public issue.** Email the maintainers or open a private report — we'll acknowledge within 48 hours and coordinate a fix before disclosure.

---

## Architecture Decisions

| Decision | Rationale |
|----------|-----------|
| SQLite + PostgreSQL dual support | SQLite for zero-config local dev, PostgreSQL for production (via `DATABASE_URL`) |
| Alembic migrations | Schema versioned in SQLAlchemy, auto-applied on boot |
| httpOnly cookies over localStorage JWT | Prevents XSS token theft |
| SHA-256 hashed refresh tokens | Database stores hashes, not raw tokens |
| Two-tier parsing (AI + regex fallback) | Works offline when no AI key is configured |
| Magic-byte file validation | Prevents malicious file uploads via renamed extensions |
| In-memory cache for market data | Avoids repeated AI/DB calls |
| Required vs nice-to-have skill weighting | Required skills weighted 2.4x in match score |
| AI provider fallback chain | `gemini,openai` — one key is enough; local parser as last resort |
| `run.js` cross-platform helper | Resolves the venv Python binary across macOS/Windows/Linux so `bun run dev:backend` works everywhere |
| Bun for frontend tooling | `bun install` / `bun run dev` / `bun run build` replace npm for speed and a single lockfile |

---

## Development

### Code Conventions

- Group related changes into logical commits
- Push when feature/fix is complete, not after every small change
- Follow title case for UI text (e.g., "Log in", "Sign up")
- Use design tokens from `tokens.css` and `theme.css`
- No comments unless asked

### Key Patterns

- **Backend routing**: Split across `api/routes/` modules, included in `main.py`
- **Frontend routes**: Lazy-loaded in `App.tsx` via `React.lazy`
- **Component structure**: Feature-scoped directories under `frontend/src/components/` (e.g., `analyzer/`, `results/`, `sidebar/`) with barrel `index.js` files
- **State management**: React Context (`AuthContext`) + local component state
- **API calls**: Centralized Axios instance with 401 interceptor
- **Database**: `sqlite3.Row` via `get_db_connection()`, WAL mode + foreign keys
- **Caching**: In-memory dict caches loaded from DB on startup

---

## Contributing

Contributions are what make the open-source community amazing. Any contribution you make is **greatly appreciated**!

### Ways to Contribute

- 🐛 **Report bugs** — open an issue with steps to reproduce
- 💡 **Suggest features** — describe the problem it solves, not just the solution
- 📝 **Improve docs** — typos, examples, diagrams
- 🧪 **Add tests** — see [Running Tests](#running-tests)
- 🔧 **Fix issues** — look for issues tagged `good first issue` or `help wanted`

### Getting Started

1. **Fork** the repository and create your branch: `git checkout -b feature/amazing-feature`
2. Make your changes — keep them focused and follow the [code conventions](#code-conventions)
3. **Test locally** — `python -m pytest -q` (backend) and `bun run lint` + `bun run build` (frontend)
4. Commit with a clear message: `git commit -m "feat: add amazing feature"`
5. **Push** and open a Pull Request

### Pull Request Checklist

- [ ] Tests pass (`python -m pytest -q`)
- [ ] Frontend builds clean (`bun run build`) and lints (`bun run lint`)
- [ ] No new dependencies without a good reason
- [ ] No secrets/keys committed (`.env` is gitignored)
- [ ] Update docs if behavior changed (README, AGENTS.md)

### Code of Conduct

Be respectful and inclusive. Harassment or hate speech is not tolerated — this project follows the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.html). Report violations to the maintainers.

---

## Community & Support

- **Issues** — Bug reports and feature requests: https://github.com/Theani7/skillpath/issues
- **Discussions** — Questions and ideas: https://github.com/Theani7/skillpath/discussions
- **Security** — Private vulnerability reports: email the maintainers (see [Security](#security))

If this project helped you, consider giving it a ⭐ — it helps others find it.

---

## Roadmap

- [x] Core resume analysis with AI providers + regex fallback
- [x] Learning roadmaps, skill gap analysis, career coaching
- [x] Mock interviews (static + AI), JD comparison, team ranking
- [x] Admin panel with analytics, audit, and data export
- [x] Email verification (OTP) and password reset
- [x] PostgreSQL support for production scaling (dual SQLite/PostgreSQL via `DATABASE_URL`)
- [x] TypeScript migration (frontend fully typed, strict mode)
- [x] Alembic schema migrations (versioned, auto-applied)
- [ ] Docker deployment (backend + frontend containers)
- [ ] i18n beyond English (structure exists in `api/i18n.py`)
- [ ] OAuth login (Google/GitHub)

*Have an idea? Open a discussion — roadmap is community-driven.*

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.
