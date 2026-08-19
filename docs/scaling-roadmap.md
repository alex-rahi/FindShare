# Scaling roadmap

**Status:** Roadmap only. These are planning scenarios, not tested capacity.

Do not treat the following as load-test results. No k6 run has been recorded.

## 100–10,000 monthly active users (planning)

Single-region RDS, modest ECS/EKS, Redis cache for feed, CloudFront for web assets, queue workers scaled to near-zero when idle. Cost control: scheduled nonproduction shutdown.

## 10,000–100,000 MAU (planning)

Read replicas, Redis for sessions and hot feed pages, HPA on API/web, queue-depth worker scaling, S3 lifecycle on derivatives, stronger index hygiene.

## 100,000–1,000,000 MAU (planning)

Search moved off primary ILIKE (OpenSearch or equivalent — not selected), connection pooling (RDS Proxy), partitioned audit/moderation tables, multi-AZ workers, CDN for all published media.

## More than 1,000,000 MAU (planning)

Multi-account AWS, possible multi-region read path, dedicated moderation fleet, more aggressive derivative and retention policies. Requires measured data that does not exist yet.

Scale signals (to measure later): MAU, concurrent users, RPS, feed/search latency, images/minute, SQS depth and age, moderation latency, CPU/memory, DB connections, cache hit rate, storage growth, CloudFront traffic, cost per active user / review / image.
