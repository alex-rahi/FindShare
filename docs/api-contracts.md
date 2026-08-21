# API contracts (Phase 1)

**Status:** These contracts are **Implemented** by `services/api`. Later-phase endpoints are listed as **Deferred**.

Base path: `/api/v1`  
Auth: `Authorization: Bearer <access_token>` or httpOnly `access_token` cookie  
Identity is always loaded from the database using the JWT `sub`. Client-supplied `user_id` or `role` fields are ignored.

Pagination: `limit` (default 20, max 50) and `offset`.

Error shape:

```json
{ "detail": "Human-readable message", "code": "INVITE_REQUIRED" }
```

## Health

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `/health` | No | Liveness |
| GET | `/ready` | No | PostgreSQL + Redis ping |

## Auth

| Method | Path | Auth | Body / query |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | No | email, username, password, invitation_code |
| POST | `/api/v1/auth/login` | No | email_or_username, password |
| POST | `/api/v1/auth/logout` | Yes | — |
| POST | `/api/v1/auth/refresh` | Refresh cookie/token | — |
| POST | `/api/v1/auth/verify-email` | No | token |
| POST | `/api/v1/auth/password-reset/request` | No | email |
| POST | `/api/v1/auth/password-reset/confirm` | No | token, new_password |
| GET | `/api/v1/auth/me` | Yes | — |

Register is invitation-only by default (`REGISTRATION_MODE=invite_only`, `MAXIMUM_ACTIVE_USERS=10`). Open registration is a configurable alternative. Reaching `maximum_active_users` returns `BETA_FULL`. Invalid or missing codes return `INVITE_REQUIRED` or `INVALID_INVITE`.

Email verification and password-reset tokens are stored in Redis and **logged in local development only** (never emailed in Phase 1). Tokens are not written to application logs in any other environment.

## Profiles

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/users/{username}` | No (public fields only) |
| PATCH | `/api/v1/profiles/me` | Owner |
| DELETE | `/api/v1/users/me` | Owner |

Public user payload includes username, display name, biography, interests, and **published** reviews only.

## Categories

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/categories` | No |
| GET | `/api/v1/categories/{slug}` | No |

## Products

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/products` | No | query: category, q, limit, offset |
| GET | `/api/v1/products/{id}` | No |
| POST | `/api/v1/products` | Yes |
| PATCH | `/api/v1/products/{id}` | Owner or admin |

Product create/update fields: name, description, category_id, subcategory_id, brand_name, model_version, website_url, typical_price_min, typical_price_max, currency, release_year.

Typical price range is user-supplied catalog metadata, not a live retailer price. Do not treat it as real-time.

## Reviews

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/reviews` | No | query: product_id, author, state=published for anonymous |
| GET | `/api/v1/reviews/{id}` | Drafts: owner only |
| POST | `/api/v1/reviews` | Yes |
| PATCH | `/api/v1/reviews/{id}` | Owner |
| POST | `/api/v1/reviews/{id}/publish` | Owner |
| POST | `/api/v1/reviews/{id}/archive` | Owner |
| DELETE | `/api/v1/reviews/{id}` | Owner (soft delete) |
| GET | `/api/v1/me/reviews` | Owner (includes drafts) |

Create fields: product_id, title, body, overall_rating (1–5), pros[], cons[], recommended, review_kind, length_of_ownership, usage_context, purchase_date, publish (bool).

`review_kind`: `personal | recommendation | first_impression | long_term | comparison | question`

Unpublished reviews never appear in list endpoints for other users.

## Feed and search

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/feed` | No | sort=`recent\|popular\|highest_rated`, category, min_rating |
| GET | `/api/v1/search` | No | q, type=`all\|product\|review\|user` |

Phase 1 `popular` orders published reviews by `overall_rating` desc, then `published_at` desc (no engagement graph yet).

## Beta status

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/beta/status` | No | registration_mode, seats remaining, maintenance_mode |

## Notices

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/api/v1/meta/notices` | No | Standard product, health, and price disclaimers |
| GET | `/api/v1/meta/flags` | No | Kill switches (uploads, comments, ads) — Phase 1 values are all off except registration |

## Deferred endpoints (not in Phase 1)

Uploads, comments, likes, follows, collections, reports, moderation cases, appeals, ads, admin invitation CRUD, feature flags, brands/retailers/listings.
