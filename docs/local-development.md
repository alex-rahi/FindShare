# Local development

**Status:** Implemented for Phase 1.

## Prerequisites

- Docker and Docker Compose
- Optional: Python 3.12 and Node.js 22 for running tests on the host

## Start

```bash
cp .env.example .env
docker compose up --build
```

Wait until `api` and `web` are healthy.

| Service | URL |
| --- | --- |
| Web | http://localhost:3000 |
| API | http://localhost:8000 |
| OpenAPI | http://localhost:8000/docs |
| PostgreSQL | localhost:5432 |
| Redis | localhost:6379 |

## Seeded accounts

Demonstration data only. Change passwords before any shared environment.

- Admin: `admin` / `FindShareAdmin!dev`
- Moderator: `moderator` / `FindShareMod!dev`
- Demo reviewer: `demo_reviewer` / `FindShareDemo!dev`
- Invite code: `FINDSHARE-DEV-INVITE`

Email verification tokens for newly registered users are printed by the API process in `APP_ENV=local` only.

## Tests without Docker

API tests use an in-memory SQLite database and do not require Compose:

```bash
cd services/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Web:

```bash
cd apps/web
npm install
npm test
```

`docker compose up --build` remains the one-command local stack. The first run pulls PostgreSQL, Redis, Python, and Node images from the internet.

Or run the same tests inside Compose after the stack is up:

```bash
docker compose exec api pytest -q
docker compose exec web npm test
```

## Migrations

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic revision -m "message"
```

## Reset local data

```bash
docker compose down -v
docker compose up --build
```

## What is not in the local Phase 1 stack

MinIO, LocalStack, workers, admin dashboard, Cognito, and image uploads. See [implementation-plan.md](implementation-plan.md).
