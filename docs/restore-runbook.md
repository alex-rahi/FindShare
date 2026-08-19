# Restore runbook

**Status:** Documented procedure. Restore testing is **Deferred**. No production database exists.

## Local PostgreSQL

```bash
docker compose exec postgres pg_dump -U findshare findshare > backup.sql
docker compose exec -T postgres psql -U findshare findshare < backup.sql
```

## Planned AWS

- RDS automated backups and point-in-time recovery
- Test restores in a nonproduction account
- Never restore over production without an incident commander
- After restore, pause publication until moderation workers catch up

A moderation outage must pause publication. Restored unpublished objects stay unpublished.
