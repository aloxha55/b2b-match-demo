# Investment Readiness Platform (Monorepo)

This repository contains a full-stack MVP for an **Investment Readiness Platform**:

- `web/`: Next.js (TypeScript) frontend
- `api/`: FastAPI (Python) backend
- Postgres database
- Docker Compose local development stack

## Features (MVP)

- User signup/login (email + password)
- Company profile management (name, sector, country, size)
- Multi-step investment readiness questionnaire
- Results page with total score (0–100), section scores, and recommendations
- Admin dashboard listing all companies and assessments

> The first user who signs up is automatically an admin user.

---

## Tech Stack

- Frontend: Next.js 14 + TypeScript
- Backend: FastAPI + SQLAlchemy + JWT auth
- Database: PostgreSQL 16
- Local runtime: Docker Compose

---

## Project Structure

```text
.
├── api/
│   ├── app/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── scoring.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env(.example)
├── web/
│   ├── app/
│   │   ├── admin/page.tsx
│   │   ├── assessment/page.tsx
│   │   ├── login/page.tsx
│   │   ├── profile/page.tsx
│   │   ├── results/page.tsx
│   │   ├── signup/page.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── lib/api.ts
│   ├── Dockerfile
│   ├── package.json
│   └── .env(.example)
└── docker-compose.yml
```

---

## Run Locally (Windows, Docker Desktop)

### Prerequisites

1. Install **Docker Desktop for Windows**.
2. Ensure Docker Desktop is running.
3. Open PowerShell in the repository root.

### 1) Configure env files

Env files are already scaffolded. If needed:

```powershell
Copy-Item .\api\.env.example .\api\.env
Copy-Item .\web\.env.example .\web\.env
```

### 2) Build and start all services

```powershell
docker compose up --build
```

Services:

- Web app: http://localhost:3000
- API docs: http://localhost:8000/docs
- Postgres: localhost:5432

### 3) Stop services

```powershell
docker compose down
```

To also remove database volume:

```powershell
docker compose down -v
```

---

## Basic Usage Flow

1. Open `http://localhost:3000`.
2. Sign up (first account becomes admin).
3. Fill out company profile.
4. Complete the assessment.
5. View results and recommendations.
6. If admin, open `/admin` to review all companies and assessments.

---

## API Endpoints (high-level)

- `POST /auth/signup`
- `POST /auth/login`
- `GET /users/me`
- `GET /company/profile`
- `PUT /company/profile`
- `POST /assessments`
- `GET /assessments/latest`
- `GET /admin/companies` (admin)
- `GET /admin/assessments` (admin)

---

## Notes

- This MVP uses JWT bearer tokens stored in browser localStorage.
- Database schema is auto-created on API startup.
- Keep secrets and production settings in environment variables for deployment.
