# FindShare interview package

**Audience:** hiring managers, interviewers, and you preparing a 10–15 minute walkthrough.

**Honesty rule:** only claim what this table says is Implemented or Tested. Everything else is documented intent.

## Accurate one-sentence summary

FindShare is an invitation-only social product-discovery platform where users share reviews, ratings, recommendations, images, prices, and shopping information across consumer-product categories. It includes secure media uploads, AI-assisted moderation, human review, and production-style AWS infrastructure managed with Terraform, EKS, Helm, and GitHub Actions.

**What that sentence means today:** the product concept, local application, publication gates, and infrastructure *roadmap* exist. Image uploads, YOLO, human moderation, Terraform, EKS, Helm, and GitHub deploy-to-AWS are **not implemented yet**.

## Claim vs evidence

| Talking point | Say this | Do not say this |
| --- | --- | --- |
| Phase 1 local app | Implemented and tested locally | “Production is live on AWS” |
| Invite-only registration | Default `invite_only`, cap 10, seed code for local demo | “We have 10 real beta testers” unless that is actually true |
| AuthZ | JWT `sub` loads the user from PostgreSQL; client `role` is ignored | “We use Cognito in this demo” |
| Publication gate | Only `published` reviews appear in feed, search, and public profiles (enforced in API queries) | “Moderation classifiers are running” |
| Images | Upload path is disabled (`image_uploads_enabled=false`) | “S3 quarantine is in this demo” |
| Ads | Placeholder provider flag exists; live ads are off | “We generate ad revenue” |
| Scale / cost | [scaling-roadmap.md](scaling-roadmap.md) and [cost-model.md](cost-model.md) are planning docs | Any RPS, MAU, or dollar figure as a measured result |
| AWS / EKS | Diagrams and runbooks are roadmap | “The cluster is deployed” |

Status labels used in this repo: Implemented, Tested, Deployed, Estimated, Mocked, Deferred, Roadmap only. Definitions: [implementation-plan.md](implementation-plan.md).

## What to open first

1. This file
2. [interview-demo.md](interview-demo.md) — timed script
3. [architecture.md](architecture.md) — local vs future diagrams
4. [api-contracts.md](api-contracts.md)
5. [data-model.md](data-model.md)
6. [threat-model.md](threat-model.md)
7. Running app: http://localhost:3000 (or `:3001` if 3000 is taken)

## Local demo credentials (development only)

Demonstration data, not real people.

| Role | Username | Password |
| --- | --- | --- |
| admin | `admin` | `FindShareAdmin!dev` |
| moderator | `moderator` | `FindShareMod!dev` |
| demo reviewer | `demo_reviewer` | `FindShareDemo!dev` |

Invitation code for new local accounts: `FINDSHARE-DEV-INVITE`.

Change these before any shared or beta environment.

## Repository map for interviewers

```
apps/web                 Next.js + TypeScript consumer UI
apps/admin               Stub only — Phase 3 human-review dashboard
services/api             FastAPI, SQLAlchemy, Alembic, Pytest
services/*-worker        Placeholders — Phase 3
infrastructure/          Terraform and Helm READMEs — Phases 4–6
docs/                    Architecture, contracts, runbooks, roadmaps
docker-compose.yml       Web, API, PostgreSQL, Redis
```

Identity is never taken from a client-supplied user id or role. The access token subject is a user UUID; each request loads role and status from the database.

## Tests you can run live

```bash
cd services/api && pytest -q
cd apps/web && npm test
```

Last recorded local run (2026-08-21): **35 pytest passed**, **2 vitest passed**, Alembic `001_initial` applied on Compose PostgreSQL, feed returned only published demonstration reviews. See [implementation-plan.md](implementation-plan.md).

## Likely questions and honest answers

**Why invitation-only?** Stage 1 is private development; Stage 2 is a 5–10 person interview beta. Defaults are `registration_mode=invite_only` and `maximum_active_users=10`. Registration, uploads, comments, and ads are kill-switchable.

**Where is authorization enforced?** FastAPI dependencies (`get_current_user`, `require_verified_user`) plus service-layer ownership checks. Unpublished reviews 404 for other users. List/feed/search queries filter `state = published`.

**How do you prevent duplicate products?** Normalized name + brand unique constraint, plus a 409 on create. Administrator merge is deferred.

**Is YOLO providing safety?** No. YOLO is an object detector. Image-safety, OCR, text classification, and human review are separate adapters planned for Phase 3. Phase 1 has no image path.

**Can I see Kubernetes?** Not in this increment. Helm and EKS are specified in [eks-deployment.md](eks-deployment.md) as an optional, destroyable interview environment. Do not imply a live cluster.

**Cost and scale?** Planning scenarios in [scaling-roadmap.md](scaling-roadmap.md). No load-test results have been recorded.

## Features deliberately not in Phase 1

Likes, comments, follows, collections, brands/retailers as tables, presigned uploads, MinIO, SQS workers, Cognito, S3, CloudFront, WAF, EKS, live advertising, payments, retailer scraping.

## Next implementation phase

Phase 2: category-specific attributes, brands, retailers, user-submitted prices, helpful votes, likes, comments, follows, collections, comparisons, reports.
