# Private deployment (Stage 1)

**Status:** Implemented as the Docker Compose local environment. This is not a public host.

Rules for private development:

- Invitation-only registration
- Seeded developer admin account
- Image uploads disabled
- Live advertising disabled
- Mock/placeholder ads disabled until Phase 5
- Unrestricted public registration disabled
- No AWS account required

Run:

```bash
cp .env.example .env
docker compose up --build
```

Bind only to localhost if exposing the Docker daemon on a shared machine. Do not publish Compose ports to the public internet.

Destroy:

```bash
docker compose down -v
```
