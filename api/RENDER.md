# Render + Neon Deployment Guide (free tier)

Backend: Render free web service. Database: Neon free Postgres.
The Flutter APK and web frontend both talk to this deployment.

> `api/database.py` runs `init_db()` on import — all tables and seed data
> are created automatically on first boot against an empty Neon database.

## 1. Create the Neon database

1. Sign up at [neon.tech](https://neon.tech) (free tier: 0.5 GB storage, autosuspend).
2. Create a project (e.g. `skillpath`).
3. Copy the **Pooled connection string** (channel binding disabled):
   ```
   postgresql://user:pass@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require
   ```
   Use the `-pooler` host — Render's free instance shares few connections and
   the app pool is capped via `DB_POOL_MAX=10` (see `render.yaml`).

## 2. Deploy the backend on Render

1. Push this repo to GitHub (already done).
2. [render.com](https://render.com) → **New → Blueprint** → select the repo.
   Render reads `render.yaml` from the root.
3. Fill the prompted secrets:
   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Neon pooled connection string from step 1 |
   | `ADMIN_USERNAME` | your admin username |
   | `ADMIN_PASSWORD` | strong password (weak values fail production validation) |
   | `GEMINI_API_KEY` | your Google AI Studio key |
4. **Apply** — build takes ~5 min (spaCy model download included; if it is
   skipped the parser falls back to regex-only, still functional).

`JWT_SECRET_KEY` is generated automatically by Render.

### First boot verification

- `https://<service>.onrender.com/api/health` → `{"status": "ok", ...}`
- Register a user; log in; upload a resume.

## 3. Point the Flutter app at it

```bash
cd mobile && flutter build apk --release \
  --dart-define=API_BASE_URL=https://<service>.onrender.com
```

The native app is not subject to CORS — no extra backend config needed.
Add your web frontend's origin to `CORS_ORIGINS` (comma-separated) in the
Render dashboard only when you host the React frontend.

## 4. Email OTP (required for registration in production)

`ENV=production` disables the `debug_otp` dev shortcut: without SMTP,
**registration and password reset return 503**. Add to Render env vars:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=you@gmail.com
SMTP_PASSWORD=<16-char Google App Password>   # myaccount.google.com/apppasswords
SMTP_FROM_NAME=SkillPath
SMTP_STARTTLS=false
```

## Free-tier caveats

- **Render sleeps** the service after ~15 min idle; the first request after
  sleep takes ~30-60 s. The Flutter app's 20 s connect timeout can trip on a
  cold start — retry once.
- **Neon autosuspends** the database; first query after suspend adds latency.
- Free instances have 512 MB RAM — the blueprint pins 1 gthread worker
  accordingly. Do not raise `--workers` without upgrading the plan.
