# Interview demonstration (10–15 minutes)

**Status:** Phase 1 can demonstrate the **local** application. Terraform, ECR, EKS, CloudWatch, HPA, and budget dry-runs are **Deferred** — skip those beats until they exist.

Use [interview-package.md](interview-package.md) for talking points, claim-vs-evidence, and likely questions.

Accurate summary (say this out loud):

> FindShare is an invitation-only social product-discovery platform where users share reviews, ratings, recommendations, images, prices, and shopping information across consumer-product categories. It includes secure media uploads, AI-assisted moderation, human review, and production-style AWS infrastructure managed with Terraform, EKS, Helm, and GitHub Actions.

Then immediately qualify: “Today I am showing Phase 1: the local foundation. Media moderation and AWS are designed and documented, not running in this demo.”

## Before the call

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:3000
- API docs: http://localhost:8000/docs

If those ports are busy: `WEB_HOST_PORT=3001 API_HOST_PORT=8001 docker compose up --build`.

Confirm `GET /api/v1/beta/status` shows `registration_mode=invite_only` and `seats_remaining > 0`.

## Timed script (Phase 1)

| Min | Beat | What to show |
| --- | --- | --- |
| 0–1 | Product and architecture | [architecture.md](architecture.md) local diagram. Name the later AWS/EKS boxes as roadmap. |
| 1–2 | Compose | Four healthy services: web, API, PostgreSQL, Redis. Open `/health` and `/ready`. |
| 2–3 | Invitation-only access | Register page requires `FINDSHARE-DEV-INVITE`. Mention the 10-user cap and waitlist message when full. |
| 3–4 | Sign in | `demo_reviewer` / `FindShareDemo!dev`. Point out seeded data is labeled demonstration data. |
| 4–5 | Feed | Snap feed of **published** reviews only. Toggle For you / Recent. |
| 5–6 | Catalog | Shop → categories come from the API, not hardcoded UI. Open a fitness/food/beauty product and read the health notice. |
| 6–8 | Create + publish | Write a text review (rating, kind, pros/cons). Save draft → it is absent from the feed → Publish → it appears. |
| 8–9 | Search and profile | Search a product/brand/username. Open a public profile; drafts are not listed. |
| 9–10 | Authorization | From another account (or curl without the author’s token) a draft returns 404; patching someone else’s review returns 403. Role in a JSON body is ignored. |
| 10–11 | Tests | `pytest -q` covers ratings, invites, quotas, publication filters. Mention 35 passed on the last recorded run — do not inflate. |
| 11–12 | GitHub | Repo layout, GitHub Actions CI (lint/tests), `.env.example` with no secrets. |
| 12–14 | Roadmap only | [scaling-roadmap.md](scaling-roadmap.md), [cost-model.md](cost-model.md), [eks-deployment.md](eks-deployment.md). Label every figure **estimated / not measured**. |
| 14–15 | Close | Recap: invitation-only social reviews, fail-closed publication, Compose + tests today; secure uploads and EKS next. |

## Optional API beats (if there is extra time)

```bash
# Draft must not appear
curl -s http://localhost:8000/api/v1/feed | python3 -m json.tool

# Client cannot self-promote
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@example.com","username":"attacker","password":"TestUser1!ok","invitation_code":"FINDSHARE-DEV-INVITE","role":"admin"}'
```

The created user role will be `user`.

## Skip until implemented

- S3 quarantine and presigned uploads
- YOLO / image-safety / OCR
- Human-review dashboard
- Terraform apply, ECR images, EKS, Helm rollback
- CloudWatch dashboards, HPA, budget dry-run
- Placeholder ads as if they were revenue
- k6 or any fabricated load-test numbers
