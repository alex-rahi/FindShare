export const NOTICES = {
  general:
    "Reviews, ratings, product details, prices, and availability may be submitted by users and may contain errors. FindShare does not independently guarantee product quality, safety, authenticity, suitability, or availability. Verify important product information with the manufacturer or retailer before purchasing or using a product.",
  pricing:
    "Prices and availability may vary by retailer, location, product variant, and date. Verify current pricing and availability with the retailer before purchasing.",
  health:
    "User content is not medical, nutritional, health, or safety advice. Consult a qualified professional when appropriate and follow manufacturer instructions and warnings.",
};

export function Footer() {
  return (
    <footer className="px-4 pb-24 pt-8 text-sm text-zinc-400">
      <div className="mx-auto max-w-xl space-y-3">
        <p>{NOTICES.general}</p>
        <p>{NOTICES.pricing}</p>
        <p>{NOTICES.health}</p>
        <p className="text-xs">
          Policy templates require qualified legal review before public release. See docs/legal/.
        </p>
      </div>
    </footer>
  );
}
