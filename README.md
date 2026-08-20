# FindShare

FindShare is a social product-discovery platform where users share reviews, ratings, recommendations, images, prices, and shopping information across consumer-product categories. It includes secure media uploads, AI-assisted moderation, human review, and production-style AWS infrastructure managed with Terraform, EKS, Helm, and GitHub Actions.

**Current implementation status:** Phase 1 (local foundation) with an open GymTok-style review feed. Later phases are documented, not implemented. See [docs/implementation-plan.md](docs/implementation-plan.md).

| Claim | Status |
| --- | --- |
| Local JWT auth, profiles, products, text reviews, ratings, feed, search | Implemented in Phase 1 |
| Docker Compose local stack | Implemented in Phase 1 |
| Image uploads, YOLO, human moderation | Deferred to Phase 3 |
| AWS, Cognito, EKS, Helm, live ads | Deferred to Phases 4–6 |
| Scale, cost, and revenue numbers | Roadmap / estimated only — not measured |

## Stage 1: private development

Open registration. Image uploads, comments, live ads, and public collections are still disabled in Phase 1.

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000
- API health: http://localhost:8000/health
- OpenAPI: http://localhost:8000/docs

Seeded local accounts (development only, labeled demonstration data):

| Role | Username | Email | Password |
| --- | --- | --- | --- |
| admin | `admin` | `admin@findshare.local` | `FindShareAdmin!dev` |
| moderator | `moderator` | `moderator@findshare.local` | `FindShareMod!dev` |
| demo reviewer | `demo_reviewer` | `demo.reviewer@findshare.local` | `FindShareDemo!dev` |

Invitation codes are optional and unused in open registration.

## Notices

Reviews, ratings, product details, prices, and availability may be submitted by users and may contain errors. FindShare does not independently guarantee product quality, safety, authenticity, suitability, or availability. Verify important product information with the manufacturer or retailer before purchasing or using a product.

User content is not medical, nutritional, health, or safety advice. Consult a qualified professional when appropriate and follow manufacturer instructions and warnings.

Prices and availability may vary by retailer, location, product variant, and date. Verify current pricing and availability with the retailer before purchasing.

Legal templates in `docs/legal/` require qualified legal review before any public release.

## Repository layout

```
apps/web                 Next.js consumer app
apps/admin               Moderator/admin dashboard (Phase 3+)
services/api             FastAPI backend
services/*-worker        Background workers (Phase 3+)
packages/shared-types    Shared TypeScript types
infrastructure/terraform AWS IaC (Phase 4+)
infrastructure/helm      EKS charts (Phase 6)
docs                     Architecture, runbooks, roadmaps
tests                    Integration, e2e, load (later phases)
```

## Tests

```bash
docker compose exec api pytest -q
docker compose exec web npm test
```

Do not treat unrun tests, planned AWS environments, or roadmap scenarios as completed work.

## Documentation

Start with [docs/implementation-plan.md](docs/implementation-plan.md), then [docs/local-development.md](docs/local-development.md) and [docs/api-contracts.md](docs/api-contracts.md).
