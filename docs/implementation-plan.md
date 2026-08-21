# FindShare implementation plan

**Status labels used everywhere in this repository**

| Label | Meaning |
| --- | --- |
| Implemented | Code exists in this repo for the described behavior |
| Tested | Automated tests exist and have been run for that behavior |
| Deployed | Actually provisioned in a real environment (never claimed without evidence) |
| Estimated | Planning figure; not measured |
| Mocked | Harmless stand-in (moderation, ads, prices) |
| Deferred | Specified, not built yet |
| Roadmap only | Future planning; not an implementation commitment |

## Product summary

FindShare is an invitation-only social product-discovery platform where users share reviews, ratings, recommendations, images, prices, and shopping information across consumer-product categories. It includes secure media uploads, AI-assisted moderation, human review, and production-style AWS infrastructure managed with Terraform, EKS, Helm, and GitHub Actions.

Phase 1 is the local foundation only. Image uploads, AWS, EKS, live ads, and growth architecture are not implemented.

## Current repository inspection

FindShare is a monorepo at this workspace. Valid Phase 1 work is preserved: Compose stack, FastAPI, Next.js web, JWT auth, catalog, text reviews, feed, search, seed data, and docs.

This increment completes Phase 1 against the product spec: invite-only defaults, missing web flows (search, public profiles, password reset, invitation registration), publication-gate tests, and Docker verification. Later phases are not started.

## Implementation-status table

| Area | Phase | Status |
| --- | --- | --- |
| Monorepo structure | 1 | Implemented |
| Docker Compose (web, API, PostgreSQL, Redis) | 1 | Implemented and started locally this session |
| FastAPI + SQLAlchemy + Alembic | 1 | Implemented |
| Next.js web app (feed, auth, products, reviews, search, profiles) | 1 | Implemented |
| Local JWT authentication | 1 | Implemented |
| Profiles, categories, products, text reviews, ratings | 1 | Implemented |
| Basic feed and search | 1 | Implemented |
| Invitation-only registration + configurable cap | 1 | Implemented (defaults: `invite_only`, max 10) |
| Unit and API tests | 1 | Tested this session |
| Brands, retailers, user-submitted prices | 2 | Deferred |
| Likes, helpful votes, comments, follows, collections, reports | 2 | Deferred |
| Presigned uploads, MinIO, image workers | 3 | Deferred |
| YOLO / image-safety / OCR adapters | 3 | Deferred |
| Human-review dashboard | 3 | Deferred |
| Terraform, Cognito, S3, SQS, RDS, ECR | 4 | Deferred |
| CloudFront, WAF, invitation beta hosting | 5 | Deferred |
| EKS, Helm, HPA, load testing | 6 | Deferred |
| Public MVP, live ads, retailer APIs, premium | 7 | Roadmap only |

## Phase acceptance criteria

### Phase 1 — Local foundation (this increment)

**In scope:** monorepo, Compose, Next.js web, FastAPI, PostgreSQL, Redis, local JWT, profiles, data-driven categories, products, text-only reviews, ratings, basic feed, search, unit and API tests, seed data, docs.

**Acceptance criteria**

1. `docker compose up --build` starts web, API, PostgreSQL, and Redis with health checks.
2. Alembic migrations apply on API start. Seed creates admin, moderator, and labeled demonstration data.
3. Registration requires a valid invitation code when `registration_mode=invite_only` (the default). Open registration is a configurable alternative, not the Stage 1 default.
4. Sign-in issues a JWT; identity and role are loaded from the database, never from client-supplied role fields.
5. Users can view/update their own profile and cannot update another user's profile.
6. Categories are served from the database, not hardcoded in frontend components.
7. Authenticated, email-verified users can create products and text-only reviews with 1–5 ratings.
8. Only reviews in `PUBLISHED` state appear in the feed, search, and public profiles.
9. Search matches product name/brand, review title/body, and usernames (not email addresses).
10. API tests cover rating aggregation, product-name normalization, invitation enforcement, quotas, and ownership authorization.
11. No image upload path is exposed. No AWS resources are required.

**Deferred from Phase 1:** images, MinIO, LocalStack, workers, admin dashboard UI, social graph, first-class brand/retailer tables, ads, Terraform, EKS.

### Phase 2 — Social shopping features

Category attributes, brands, retailers, user-submitted prices, helpful votes, likes, comments, follows, collections, comparisons, reports.

### Phase 3 — Secure media and moderation

Quarantine bucket, presigned uploads, validation, metadata strip, mock moderation + adapter interfaces, publication gate, human-review dashboard, appeals.

### Phase 4 — Private AWS staging

Terraform for VPC, Cognito, S3, SQS, RDS, ECR, CloudWatch, KMS, GitHub Actions OIDC, budget notifications. **Not deployed until someone actually applies Terraform.**

### Phase 5 — Invitation-only beta

5–10 user cap, quotas, kill switches, HTTPS, WAF, CloudFront, placeholder ads, smoke/e2e tests.

### Phase 6 — Production-style EKS demonstration

Optional EKS + Helm. Load-test results recorded only if k6 is actually run.

### Phase 7 — Roadmap only

Public MVP, growth architecture, authorized retailer APIs, live advertising, affiliates, premium, recommendations, multi-account/multi-region, DR.

## External dependencies

| Dependency | Phase 1 use | Later |
| --- | --- | --- |
| PostgreSQL 16 | Primary datastore | RDS |
| Redis 7 | Rate limit, token blacklist, email/reset tokens | ElastiCache |
| Next.js / React / Tailwind | Web UI | Admin UI |
| FastAPI / SQLAlchemy / Alembic / Pydantic | API | Workers |
| PyJWT / bcrypt | Local auth | Cognito in Phase 4 |
| Docker / Compose | Local runtime | ECR / EKS |
| MinIO | Unused | Phase 3 quarantine/published |
| LocalStack | Unused | Phase 3 SQS emulation |
| Pillow, YOLO, OCR, image-safety | Unused | Phase 3 adapters |
| Playwright, k6 | Unused | Phases 5–6 |
| Terraform, Helm, GitHub Actions AWS | Unused | Phases 4–6 |

## Deferred features (explicit)

- Image and video uploads
- YOLO, image-safety, OCR, live classifiers
- Human moderation UI
- Likes, comments, follows, collections, reports
- Brands/retailers/price submissions as first-class tables
- Cognito, S3, SQS, CloudFront, WAF, EKS
- Live advertising networks and affiliate tracking
- Payment processing / checkout (never in first release)
- Retailer scraping (never without authorization)
- Fabricated scale, cost, or revenue results

## Environment variables

See [../.env.example](../.env.example). Required for Phase 1: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`.

Stage 1 defaults: `REGISTRATION_MODE=invite_only`, `MAXIMUM_ACTIVE_USERS=10`, `IMAGE_UPLOADS_ENABLED=false`, `LIVE_ADVERTISING_ENABLED=false`.

## Diagrams

- Entity-relationship: [data-model.md](data-model.md)
- API contracts: [api-contracts.md](api-contracts.md)
- Review / media / moderation states: [moderation-pipeline.md](moderation-pipeline.md)
- Local, beta, and EKS architecture: [architecture.md](architecture.md)

## Session test results

Recorded 2026-08-21 after this Phase 1 increment. These are actual command results, not estimates.

| Check | Result |
| --- | --- |
| `pytest -q` in `services/api` (in-memory SQLite) | **35 passed** |
| `ruff check app tests` | All checks passed |
| `npm test` in `apps/web` (Vitest) | **2 passed** (1 file) |
| Alembic on Compose PostgreSQL | `Running upgrade  -> 001_initial` succeeded |
| `GET /health` | `{"status":"ok","service":"findshare-api","phase":1,"env":"local"}` |
| `GET /ready` | `{"status":"ready"}` |
| `GET /api/v1/beta/status` | `registration_mode=invite_only`, `maximum_active_users=10`, `active_users=3`, `seats_remaining=7` |
| `GET /api/v1/feed` | 2 published demonstration reviews; draft title absent |
| `GET /api/v1/meta/flags` | image uploads, comments, live ads all `false` |
| Web `GET /` | HTTP 200 |
| Categories via web `/api` rewrite | 12 data-driven categories |

Compose on this machine used alternate **host** ports `3001` / `8001` / `5433` / `6380` because another local stack already bound 3000, 8000, 5432, and 6379. Default Compose ports remain 3000/8000/5432/6379. No AWS, EKS, or load-test results exist.
