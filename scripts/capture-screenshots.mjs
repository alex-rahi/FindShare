/**
 * Capture demonstration screenshots from a running local FindShare web app.
 * Usage: BASE_URL=http://localhost:3000 API_URL=http://localhost:8000 node scripts/capture-screenshots.mjs
 */
import { mkdir } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const OUT = join(ROOT, "docs", "screenshots");
const BASE = process.env.BASE_URL || "http://localhost:3000";
const API = process.env.API_URL || "http://localhost:8000";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const DESKTOP = { width: 980, height: 900, deviceScaleFactor: 2 };
const PHONE = { width: 390, height: 844, deviceScaleFactor: 2 };

async function shot(page, name) {
  const path = join(OUT, name);
  await clean(page);
  await new Promise((r) => setTimeout(r, 250));
  await page.screenshot({ path, type: "png", fullPage: false });
  console.log("wrote", path);
}

async function clean(page) {
  await page.evaluate(() => {
    document.querySelectorAll("nextjs-portal").forEach((el) => el.remove());
    const footer = document.querySelector("footer");
    if (footer) footer.style.display = "none";
  });
  await page.addStyleTag({
    content: [
      "nextjs-portal, [data-next-badge], [data-nextjs-dev-indicator] { display: none !important; }",
      "footer { display: none !important; }",
    ].join("\n"),
  });
}

async function goto(page, path) {
  await page.goto(`${BASE}${path}`, { waitUntil: "networkidle2", timeout: 30000 });
  await clean(page);
}

async function waitText(page, needle, timeout = 20000) {
  await page.waitForFunction(
    (text) => document.body && document.body.innerText.includes(text),
    { timeout },
    needle,
  );
}

async function withToken(page, token) {
  await page.goto(BASE, { waitUntil: "domcontentloaded" });
  await page.evaluate((value) => {
    window.localStorage.setItem("findshare.token", value);
  }, token);
}

async function main() {
  await mkdir(OUT, { recursive: true });
  const catalog = await fetch(`${API}/api/v1/products`).then((r) => r.json());
  const feed = await fetch(`${API}/api/v1/feed?sort=recent`).then((r) => r.json());
  const productId = catalog.items?.[0]?.id;
  const reviewId = feed.items?.[0]?.id;
  if (!productId || !reviewId) {
    throw new Error("Seeded products/reviews missing; is the API running with seed data?");
  }

  const login = await fetch(`${API}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email_or_username: "demo_reviewer", password: "FindShareDemo!dev" }),
  }).then((r) => r.json());
  const token = login.tokens?.access_token;
  if (!token) throw new Error("Could not log in demo_reviewer for signed-in screenshots");

  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: true,
    args: ["--hide-scrollbars", "--disable-gpu"],
  });

  try {
    const guest = await browser.newPage();
    guest.setDefaultTimeout(25000);

    await guest.setViewport(PHONE);
    await goto(guest, "/");
    await waitText(guest, "Quiet enough");
    await shot(guest, "01-feed.png");

    await guest.setViewport(DESKTOP);
    await goto(guest, "/login");
    await waitText(guest, "Sign in");
    await shot(guest, "02-sign-in.png");

    await goto(guest, "/register");
    await waitText(guest, "Invitation-only");
    await shot(guest, "03-register.png");

    await goto(guest, "/products");
    await waitText(guest, "QuietLine");
    await shot(guest, "04-products.png");

    await goto(guest, `/products/${productId}`);
    await waitText(guest, "QuietLine Over-Ear Headphones");
    await shot(guest, "05-product-detail.png");

    await goto(guest, `/reviews/${reviewId}`);
    await waitText(guest, "Quiet enough for a noisy office");
    await shot(guest, "06-review.png");

    await goto(guest, "/search");
    await waitText(guest, "Search");
    await guest.locator("form input.field").fill("Quiet");
    await guest.locator("form button.btn").click();
    await waitText(guest, "Harbor Audio");
    await shot(guest, "07-search.png");
    await guest.close();

    const signed = await browser.newPage();
    signed.setDefaultTimeout(25000);
    await signed.setViewport(PHONE);
    await withToken(signed, token);
    await goto(signed, "/");
    await waitText(signed, "Quiet enough");
    await waitText(signed, "Sign out");
    await shot(signed, "08-feed-signed-in.png");

    await signed.setViewport(DESKTOP);
    await goto(signed, "/me");
    await waitText(signed, "@demo_reviewer");
    await waitText(signed, "Quiet enough");
    await shot(signed, "09-profile.png");

    await goto(signed, "/reviews/new");
    await waitText(signed, "Write a review");
    await waitText(signed, "@demo_reviewer");
    await shot(signed, "10-write-review.png");
    await signed.close();
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
