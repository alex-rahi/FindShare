/**
 * Capture demonstration screenshots from a running local FindShare web app.
 * Usage: BASE_URL=http://localhost:3001 API_URL=http://localhost:8001 node scripts/capture-screenshots.mjs
 */
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import puppeteer from "puppeteer-core";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const OUT = join(ROOT, "docs", "screenshots");
const BASE = process.env.BASE_URL || "http://localhost:3001";
const API = process.env.API_URL || "http://localhost:8001";
const CHROME =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const DESKTOP = { width: 1100, height: 900, deviceScaleFactor: 2 };
const PHONE = { width: 390, height: 844, deviceScaleFactor: 2 };

async function shot(page, name, fullPage = false) {
  const path = join(OUT, name);
  await page.screenshot({ path, type: "png", fullPage });
  console.log("wrote", path);
}

async function hideDevChrome(page) {
  await page.addStyleTag({
    content: "nextjs-portal, [data-next-badge], #__next-build-watcher { display: none !important; }",
  });
}

async function goto(page, path) {
  await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded", timeout: 30000 });
  await hideDevChrome(page);
  await new Promise((r) => setTimeout(r, 400));
}

async function waitText(page, needle, timeout = 15000) {
  await page.waitForFunction(
    (text) => document.body && document.body.innerText.includes(text),
    { timeout },
    needle,
  );
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
  const page = await browser.newPage();
  page.setDefaultTimeout(25000);

  try {
    await page.setViewport(PHONE);
    await goto(page, "/");
    await waitText(page, "Quiet enough");
    await shot(page, "01-feed.png");

    await page.setViewport(DESKTOP);
    await goto(page, "/login");
    await waitText(page, "Sign in");
    await shot(page, "02-sign-in.png");

    await goto(page, "/register");
    await waitText(page, "Invitation-only");
    await shot(page, "03-register.png");

    await goto(page, "/products");
    await waitText(page, "QuietLine");
    await shot(page, "04-products.png", true);

    await goto(page, `/products/${productId}`);
    await waitText(page, "QuietLine Over-Ear Headphones");
    await shot(page, "05-product-detail.png", true);

    await goto(page, `/reviews/${reviewId}`);
    await waitText(page, "Quiet enough for a noisy office");
    await shot(page, "06-review.png", true);

    await goto(page, "/search");
    await waitText(page, "Search");
    await page.locator("form input.field").fill("Quiet");
    await page.locator("form button.btn").click();
    await new Promise((r) => setTimeout(r, 1500));
    const bodyText = await page.evaluate(() => document.body.innerText);
    if (!bodyText.includes("Harbor") && !bodyText.includes("Quiet enough")) {
      await shot(page, "07-search.png", true);
      throw new Error(`search did not return results:\n${bodyText.slice(0, 800)}`);
    }
    await shot(page, "07-search.png", true);

    await page.setViewport(PHONE);
    await goto(page, "/");
    await page.evaluate((value) => {
      window.localStorage.setItem("findshare.token", value);
    }, token);
    await goto(page, "/");
    await waitText(page, "Quiet enough");
    await waitText(page, "Sign out");
    await shot(page, "08-feed-signed-in.png");

    await page.setViewport(DESKTOP);
    await goto(page, "/me");
    await waitText(page, "Your reviews");
    await shot(page, "09-profile.png", true);

    await goto(page, "/reviews/new");
    await waitText(page, "Write a review");
    await shot(page, "10-write-review.png", true);

    await writeFile(
      join(OUT, "README.md"),
      [
        "# Screenshots",
        "",
        "Captured from the local Phase 1 Docker Compose app. Seeded content is demonstration data, not real reviews or products.",
        "",
        "Regenerate (app must already be running):",
        "",
        "```bash",
        "cd scripts && npm install puppeteer-core",
        "BASE_URL=http://localhost:3001 API_URL=http://localhost:8001 node capture-screenshots.mjs",
        "```",
        "",
      ].join("\n"),
    );
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
