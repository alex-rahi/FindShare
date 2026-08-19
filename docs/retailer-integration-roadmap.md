# Retailer integration roadmap

**Status:** Roadmap only. No retailer scraping. No purchase processing.

Future integrations must use authorized APIs behind an adapter interface (`RetailerCatalogAdapter`, `PriceAdapter`). User-submitted prices must remain labeled as user-submitted unless they come from an authorized integration. Display observation date and location. Do not claim real-time prices.

Display: “Prices and availability may vary by retailer, location, product variant, and date. Verify current pricing and availability with the retailer before purchasing.”
