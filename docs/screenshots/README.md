# Screenshots

Local Phase 1 UI captured from Docker Compose. Seeded reviews and products are demonstration data, not real commercial listings.

| File | Screen |
| --- | --- |
| [01-feed.png](01-feed.png) | Public snap feed of a published review |
| [02-sign-in.png](02-sign-in.png) | Sign in (seeded local accounts) |
| [03-register.png](03-register.png) | Invitation-only registration |
| [04-products.png](04-products.png) | Shop catalog with category filter |
| [05-product-detail.png](05-product-detail.png) | Product detail, rating, and price notice |
| [06-review.png](06-review.png) | Published text review |
| [07-search.png](07-search.png) | Search for product, brand, or keyword |
| [08-feed-signed-in.png](08-feed-signed-in.png) | Feed after signing in as `demo_reviewer` |
| [09-profile.png](09-profile.png) | Profile edit |
| [10-write-review.png](10-write-review.png) | Text-only review composer |

Regenerate (app must already be running):

```bash
cd scripts && npm install puppeteer-core
BASE_URL=http://localhost:3001 API_URL=http://localhost:8001 node capture-screenshots.mjs
```

Do not treat these images as production traffic, live retailer prices, or measured scale.
