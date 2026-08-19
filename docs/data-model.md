# Data model

**Status:** Phase 1 tables are **Implemented**. Remaining entities are **Deferred** (schema planned, not migrated).

## Phase 1 entity-relationship diagram

```mermaid
erDiagram
  USER ||--|| PROFILE : has
  USER ||--o{ INVITATION_CODE : creates
  USER ||--o{ PRODUCT : creates
  USER ||--o{ REVIEW : writes
  USER ||--o{ AUDIT_EVENT : records
  CATEGORY ||--o{ SUBCATEGORY : contains
  CATEGORY ||--o{ PRODUCT : classifies
  SUBCATEGORY ||--o{ PRODUCT : classifies
  PRODUCT ||--o{ REVIEW : receives
  BETA_CONFIGURATION ||--o| USER : constrains

  USER {
    uuid id PK
    string email UK
    string username UK
    string password_hash
    string role
    string status
    timestamptz email_verified_at
    int version
  }

  PROFILE {
    uuid id PK
    uuid user_id FK
    string display_name
    string biography
    json interests
  }

  INVITATION_CODE {
    uuid id PK
    string code UK
    int max_uses
    int use_count
    timestamptz expires_at
    timestamptz revoked_at
  }

  BETA_CONFIGURATION {
    int id PK
    string registration_mode
    int maximum_active_users
    int reviews_per_user
    boolean registration_enabled
    boolean maintenance_mode
  }

  CATEGORY {
    uuid id PK
    string slug UK
    string name
    boolean requires_health_notice
  }

  SUBCATEGORY {
    uuid id PK
    uuid category_id FK
    string slug
    string name
  }

  PRODUCT {
    uuid id PK
    string name
    string normalized_name
    string brand_name
    string status
    uuid created_by_user_id FK
    int version
  }

  REVIEW {
    uuid id PK
    uuid product_id FK
    uuid author_id FK
    string title
    text body
    int overall_rating
    string state
    string review_kind
    int version
  }

  AUDIT_EVENT {
    uuid id PK
    uuid actor_id FK
    string action
    string resource_type
    json metadata
  }
```

## Planned full model (deferred)

User, Profile, InvitationCode, BetaConfiguration, Category, Subcategory, CategoryAttribute, Brand, Product, ProductVariant, ProductAttributeValue, ProductImage, Retailer, RetailerLocation, ProductListing, ProductPrice, Review, ReviewRating, ReviewImage, ReviewDisclosure, ReviewComparison, HelpfulVote, Like, Comment, Follow, Block, Collection, CollectionItem, Notification, Report, ModerationJob, ModerationFinding, ReviewCase, ReviewDecision, Appeal, PolicyVersion, FeatureFlag, AdPlacement, MockAdEvent, AuditEvent, CostAssumption, ScalingTestResult.

Phase 1 uses `brand_name` on Product rather than a Brand table. Category-specific attribute definitions arrive in Phase 2.

## Constraints (Phase 1)

- Unique email and username on `users`
- Unique category slug; unique `(category_id, slug)` on subcategories
- Unique `(normalized_name, lower(brand_name))` among non-archived products
- Review `overall_rating` between 1 and 5
- Review `state` in `draft | pending_moderation | needs_review | published | rejected | archived | deleted`
- User `role` in `user | moderator | admin`
- Optimistic `version` columns on User, Product, Review
- Foreign keys with restrict/cascade as appropriate (reviews restrict product delete; profile cascades with user)

## Duplicate products

`normalized_name` lowercases, strips punctuation, and collapses whitespace. Administrators can merge products in a later phase; Phase 1 rejects exact brand+normalized-name duplicates at create time.
