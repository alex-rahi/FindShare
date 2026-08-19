# Incident response

**Status:** Process documented. No production on-call rotation exists.

1. Detect (health, logs, later CloudWatch alarms)
2. Contain (enable `maintenance_mode`, disable registration/uploads)
3. Do not disable security logging to “save cost”
4. Do not publish unmoderated media
5. Preserve audit events
6. Communicate scope honestly (local vs beta vs none)
7. Recover via rollback/restore runbooks
8. Post-incident notes in the repo only with non-secret facts

Phase 1 signals: API `/ready`, Compose health, structured request logs.
