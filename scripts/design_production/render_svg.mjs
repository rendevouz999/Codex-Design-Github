// Private offline preview adapter. No model-provided script, URL, or filesystem path.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const directory = await fs.realpath(process.argv[2]);
if (!directory.startsWith(path.join(root, 'output') + path.sep)) throw Error('Output boundary violation');
const units = JSON.parse(await fs.readFile(path.join(directory, 'unit-order.json'), 'utf8'));
const browser = await chromium.launch({ headless: true });
const checks = [];
try {
  const context = await browser.newContext({ javaScriptEnabled: false, serviceWorkers: 'block' });
  await context.route('**/*', route => route.abort());
  for (const file of units) {
    if (path.basename(file) !== file || !file.endsWith('.svg')) throw Error('Invalid unit filename');
    const svg = await fs.readFile(path.join(directory, file), 'utf8');
    // Defense in depth: writer only permits primitives; reject active/resource-bearing markup here too.
    const inert = svg.replaceAll('href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="','');
    if (/<(?:script|foreignObject|use|style)\b|\bon\w+\s*=|(?:href|url\s*\(|<!DOCTYPE|<!ENTITY)/i.test(inert)) throw Error('Active SVG is forbidden');
    const size = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
    if (!size) throw Error('Missing validated canvas');
    const width = Number(size[1]), height = Number(size[2]);
    const page = await context.newPage();
    await page.setViewportSize({ width, height });
    await page.setContent(`<html><body style="margin:0">${svg}</body></html>`, { timeout: 10000 });
    const overflow = await page.locator('svg > *').evaluateAll((nodes, box) => nodes.filter(n => {
      const b = n.getBBox(); return b.x < -0.5 || b.y < -0.5 || b.x + b.width > box.width + .5 || b.y + b.height > box.height + .5;
    }).map(n => n.id), { width, height });
    const preview = `${file.slice(0, -4)}.png`;
    await page.screenshot({ path: path.join(directory, preview), timeout: 10000 });
    checks.push({ unit: file.slice(0, -4), preview, width, height, overflow });
    await page.close();
  }
} finally { await browser.close(); }
await fs.writeFile(path.join(directory, 'render-checks.json'), JSON.stringify(checks, null, 2), { flag: 'wx' });
process.stdout.write(JSON.stringify({ checks }));
