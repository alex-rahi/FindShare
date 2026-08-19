# Privacy and retention

**Status:** Phase 1 implements account deletion (anonymize email/username, mark deleted, hide content). Full media retention jobs are **Deferred**.

Rules:

- Collect only necessary account fields (email, username, password hash, profile)
- Do not log credentials, raw private content, or presigned URLs
- Strip location metadata from uploads (Phase 3)
- Delete temporary processing files (Phase 3)
- Retain moderation findings only as operationally necessary (Phase 3)
- Delete rejected media after the configured appeal period (Phase 3)
- Support legal hold later without bypassing publication gates
- Log retention and deletion events in `audit_events`

Phase 1 account deletion:

- `users.status = deleted`
- email replaced with `deleted+<uuid>@invalid.local`
- username replaced with `deleted_<shortid>`
- password hash rotated to an unusable value
- reviews moved to `deleted` and excluded from public feeds
