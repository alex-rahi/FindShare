# Rollback runbook

**Status:** Phase 1 local rollback is **Implemented** (Compose recreate). Helm/EKS rollback is **Deferred**.

## Local

```bash
docker compose down
git checkout -- .
docker compose up --build
```

Database: restore from a logical dump if you created one (`scripts/backup-db.sh` in a later phase). Phase 1 data is disposable (`docker compose down -v`).

## Planned (Phase 6)

- Helm: `helm rollback <release> <revision>`
- Images: redeploy previous immutable ECR tag
- Never roll forward with unpublished media promotion
- Record the actual command output when a rollback is performed; do not invent success
