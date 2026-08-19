# Interview demonstration (10–15 minutes)

**Status:** Phase 1 can demonstrate the local application only. Terraform, ECR, EKS, CloudWatch, HPA, and budget dry-runs are **Deferred** — skip those beats until they exist.

Accurate summary:

> FindShare is an invitation-only social product-discovery platform where users share reviews, ratings, recommendations, images, prices, and shopping information across consumer-product categories. It includes secure media uploads, AI-assisted moderation, human review, and production-style AWS infrastructure managed with Terraform, EKS, Helm, and GitHub Actions.

## Phase 1 script (local)

1. Product concept and this architecture (1 min)
2. `docker compose up` — web + API + PostgreSQL + Redis (1 min)
3. Invitation-only registration with `FINDSHARE-DEV-INVITE` (1 min)
4. Sign in as `demo_reviewer` (30 s)
5. Browse data-driven categories and the seeded feed (1 min)
6. Open a product; note user-content and (if food/fitness/beauty) health notices (1 min)
7. Create a text review with rating, pros, cons; publish; see it in the feed (2 min)
8. Search by product, brand, or keyword (1 min)
9. Show unpublished draft does not appear in feed (1 min)
10. Profile edit; attempt to patch another user (API 403) (1 min)
11. Point at tests: `pytest` rating + publication filters (1 min)
12. Scaling/monetization docs as **planning**, not results (1 min)

Skip AWS, quarantine, YOLO, HPA, and ads until those phases are implemented.
