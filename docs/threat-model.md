# Threat model (Phase 1 scope)

**Status:** Documented. Controls listed as Implemented apply to Phase 1 only.

## Assets

- Account credentials and JWTs
- User profiles and unpublished drafts
- Product and review content
- Invitation codes
- Audit events

## Trust boundaries

- Browser → Next.js
- Next.js rewrite → FastAPI
- FastAPI → PostgreSQL / Redis
- Untrusted client JSON

## Abuses and mitigations

| Threat | Mitigation | Status |
| --- | --- | --- |
| Privilege escalation via client role | Ignore client role; load user from DB | Implemented |
| IDOR on profiles/reviews | Owner checks in services | Implemented |
| Credential stuffing | Redis rate limit on login/register | Implemented |
| JWT reuse after logout | `jti` denylist in Redis | Implemented |
| Unpublished content leak | Query filters `state=published` | Implemented |
| Secret commit | `.gitignore`, no real `.env` | Implemented |
| XSS via review body | Store as text; React escaping | Implemented |
| SQL injection | SQLAlchemy bound parameters | Implemented |
| Public image access | No upload path in Phase 1 | Deferred to Phase 3 |
| Prompt injection into classifiers | N/A until Phase 3 | Deferred |
| Presigned URL leakage in logs | No presign in Phase 1 | Deferred |
| Dependency / container vulns | CI scanning in later phases | Deferred |

## MFA

Moderators and administrators are MFA-ready in the data model (role exists; Cognito MFA in Phase 4). Phase 1 local JWT does **not** enforce MFA. **Deferred.**
