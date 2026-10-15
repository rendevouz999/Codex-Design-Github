import { expect, test } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

test('chromium visual pipeline captures Design Brain evidence', async ({ page }) => {
  await page.setContent(`
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <style>
          :root {
            color-scheme: dark;
            font-family: Inter, Arial, sans-serif;
            background: #101114;
          }
          body {
            margin: 0;
            min-height: 100vh;
            display: grid;
            place-items: center;
            background:
              radial-gradient(circle at 20% 10%, rgba(192, 255, 70, 0.16), transparent 28%),
              linear-gradient(135deg, #101114 0%, #181223 56%, #111316 100%);
            color: #f5f7ee;
          }
          [data-testid="review-surface"] {
            width: min(1120px, calc(100vw - 80px));
            aspect-ratio: 16 / 9;
            border: 1px solid rgba(198, 255, 83, 0.34);
            border-radius: 8px;
            display: grid;
            grid-template-columns: 1.15fr 0.85fr;
            gap: 32px;
            padding: 48px;
            box-sizing: border-box;
            background: rgba(14, 15, 19, 0.82);
          }
          h1 {
            margin: 0;
            font-size: 60px;
            line-height: 0.95;
            letter-spacing: 0;
          }
          p {
            margin: 18px 0 0;
            max-width: 520px;
            color: #cfd3c2;
            font-size: 20px;
            line-height: 1.45;
          }
          .badge {
            display: inline-block;
            margin-bottom: 22px;
            color: #c6ff53;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
          }
          .panel {
            border-left: 3px solid #8d5cf6;
            padding-left: 24px;
            align-self: end;
          }
          .metric {
            color: #c6ff53;
            font-size: 44px;
            font-weight: 800;
          }
        </style>
      </head>
      <body>
        <main data-testid="review-surface">
          <section>
            <span class="badge">Design Brain v2.0.0</span>
            <h1>Presentation QA smoke frame</h1>
            <p>Chromium renders this deterministic frame so the local visual pipeline can prove screenshots and evidence storage are working.</p>
          </section>
          <aside class="panel">
            <div class="metric">16:9</div>
            <p>Evidence is stored in .design-brain/evidence/visual-reviews for review notes, screenshots, scores, and revisions.</p>
          </aside>
        </main>
      </body>
    </html>
  `);

  const surface = page.locator('[data-testid="review-surface"]');
  await expect(surface).toBeVisible();
  const box = await surface.boundingBox();
  expect(box?.width).toBeGreaterThan(1000);
  expect(box?.height).toBeGreaterThan(560);

  const evidenceDir = path.resolve(process.cwd(), '.design-brain', 'evidence', 'visual-reviews');
  await fs.mkdir(evidenceDir, { recursive: true });
  const screenshotPath = path.join(evidenceDir, 'playwright-smoke.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  const screenshot = await fs.stat(screenshotPath);
  expect(screenshot.size).toBeGreaterThan(10000);
});
