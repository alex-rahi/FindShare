# Architecture

**Status:** Phase 1 local architecture is **Implemented**. Beta and EKS diagrams are **Roadmap only** until Terraform/Helm are applied.

## Local architecture (Phase 1 — implemented)

```mermaid
flowchart LR
  U[Developer browser] --> W[Next.js web :3000]
  W -->|rewrite /api/*| A[FastAPI :8000]
  A --> PG[(PostgreSQL)]
  A --> RD[(Redis)]
```

Compose services in Phase 1: `web`, `api`, `postgres`, `redis`.

MinIO, LocalStack, image/moderation/notification workers, and the admin dashboard are **Deferred** to Phase 3+. They appear in the target local architecture below.

## Target local architecture (Phase 3+ — deferred)

```mermaid
flowchart LR
  U[User] --> W[Next.js web]
  U --> AD[Next.js admin]
  W --> A[FastAPI]
  AD --> A
  A --> PG[(PostgreSQL)]
  A --> RD[(Redis)]
  A --> Q[MinIO quarantine]
  A --> LS[LocalStack SQS]
  LS --> IW[image-worker]
  LS --> MW[moderation-worker]
  LS --> NW[notification-worker]
  IW --> Q
  MW --> PG
  IW --> P[MinIO published]
```

## Invitation-only beta architecture (Phase 5 — roadmap only)

```mermaid
flowchart LR
  User --> R53[Route 53]
  R53 --> CF[CloudFront + WAF]
  CF --> ALB[ALB / HTTPS]
  ALB --> WEB[Next.js]
  ALB --> API[FastAPI]
  API --> COG[Cognito]
  API --> RDS[(RDS PostgreSQL)]
  API --> REDIS[(Redis)]
  API --> SQ[S3 quarantine]
  API --> Q[SQS]
  Q --> MW[moderation worker]
  MW --> SP[S3 published]
  SP --> CF
```

Not deployed. Creating this environment is optional and should be destroyed after demonstrations.

## EKS interview architecture (Phase 6 — roadmap only)

```mermaid
flowchart TB
  subgraph vpc [VPC]
    subgraph public [Public subnets]
      ALB[ALB Ingress]
    end
    subgraph app [Private app subnets]
      API[API pods + HPA]
      WEB[Web pods + HPA]
      IW[image-worker]
      MW[moderation-worker]
      NW[notification-worker]
    end
    subgraph data [Isolated data subnets]
      RDS[(RDS PostgreSQL)]
      REDIS[(Redis)]
    end
  end
  CF[CloudFront + WAF] --> ALB
  ALB --> API
  ALB --> WEB
  API --> RDS
  API --> REDIS
  API --> S3Q[S3 quarantine]
  API --> SQS[SQS]
  SQS --> IW
  SQS --> MW
  MW --> S3P[S3 published]
```

Independently deployable and destroyable. No live cluster exists in Phase 1.

## Auth model (Phase 1)

Local JWT provider. Access token `sub` is the user UUID. Each request loads the user from PostgreSQL. Role and status come from the database, not the token payload and not the client. Logout records the JWT `jti` in Redis until expiry. Cognito replaces this provider in Phase 4 behind the same application interface.

## Publication boundary (all phases)

Unpublished reviews must not appear in feed, search, public profiles, or public API list endpoints. Enforced in API queries, not in the frontend.
