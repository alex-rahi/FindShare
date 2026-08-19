# Testing strategy

**Status:** Phase 1 unit and API tests are **Implemented**. Playwright, k6, upload, and moderation-path tests are **Deferred**.

## Phase 1

- Unit: rating aggregation, product-name normalization, invitation/beta limits (service-level), password hashing
- API: register/login, invite enforcement, max-user limit, ownership, product CRUD, review CRUD, feed/search publication filter, account deletion
- Frontend: Vitest for rating display and disclaimer rendering

## Later phases (not run, not claimed)

- Upload: valid, oversized, false MIME, malformed, expired presign, wrong key, quota, disabled uploads
- Moderation: safe/prohibited/ambiguous/conflict, worker failure/timeout, duplicate event, human approve/reject, appeal
- Playwright happy path and rejected-image path
- k6: feed, search, product detail, review create, HPA — **document actual results only**

Unpublished content must be asserted absent from feed, search, profiles, and public API responses in every phase that adds a new read path.
