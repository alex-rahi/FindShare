# Cost model

**Status:** Estimated / roadmap only. No AWS bill has been measured for FindShare.

Illustrative **non-measured** beta sketch (destroy after demo):

- NAT, RDS, and ALB dominate a tiny EKS demo
- Prefer ECS/Fargate or a single-node shutdown for 5–10 users
- S3 and CloudFront should be near-zero without media
- Budget alerts at 50/70/80/90% are planned; live scale-down actions require `BUDGET_LIVE_ACTIONS_ENABLED=true` and default to `BUDGET_DRY_RUN=true`

Never publish unmoderated media to save cost. Never auto-delete the production database. Never disable security logging to reduce cost.

Replace this document with actual line items after a real `terraform apply`.
