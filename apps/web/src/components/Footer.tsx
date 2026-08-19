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
    <footer className="mt-16 border-t border-slate-200 bg-white px-4 py-10 text-sm text-slate-600">
      <div className="mx-auto max-w-5xl space-y-3">
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
