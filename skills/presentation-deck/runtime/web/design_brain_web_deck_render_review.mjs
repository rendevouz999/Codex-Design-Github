#!/usr/bin/env node
/**
 * Brain Design - Web Deck Medium - rendered review pass.
 *
 * The runtime counterpart of `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs`. The static
 * audit proves the deck source obeys the stage and runtime contract. This tool
 * serves the deck over a local http server, drives it in chromium, and measures
 * what actually painted: slide count, navigation, deep link, lifecycle event,
 * reveal state, stage fit, overflow, overlap, contrast, reduced motion, and print.
 *
 * Contract: `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md` and `skills/presentation-deck/resources/web-deck/`.
 * Rubric: `skills/presentation-deck/design/craft/web-deck-stage-fidelity.md`.
 *
 * Usage
 *   node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs <deck.html> [options]
 *
 * Options
 *   --out <dir>          Directory for every output of the run, including the
 *                        Markdown report, so a review can stay outside the repo.
 *                        Default: `.design-brain/screenshots/<stamp>-<slug>-web-deck-render`
 *   --plan <file>        Deck plan JSON to cross-check. Auto-detected when omitted.
 *   --phone-width <px>   Narrow-viewport width for the letterbox pass. Default: 390
 *   --keep-shots         Also keep the diagnostic captures (fit probes and the
 *                        reduced-motion frame), not only the required evidence set.
 *   --json               Print the JSON result to stdout and nothing else.
 *
 * Evidence written on every successful run
 *   - one screenshot per slide at stage size, under `slides/`
 *   - one narrow-viewport screenshot
 *   - `deck-print.pdf` from the print path
 *   - `render-review.json` in the evidence directory
 *   - a Markdown review report, in `.design-brain/visual-reviews/` by default and
 *     in the evidence directory when `--out` is given
 *
 * Exit codes
 *   0  no P0 finding
 *   2  at least one P0 finding
 *   1  usage error, unreadable deck, or chromium not installed
 *
 * This tool never reports a check it did not perform. When chromium is missing it
 * exits 1 and says so, and `NOT_RUN` is the only honest render-review value for
 * the receipt in that case.
 */
import fs from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const STAGE_WIDTH = 1920;
const STAGE_HEIGHT = 1080;

/** Narrow-viewport height. Paired with `--phone-width` for the letterbox pass. */
const PHONE_HEIGHT = 844;

/** Non-16:9 probe viewports: one taller than 16:9, one wider than 16:9. */
const LETTERBOX_VIEWPORT = { width: 1440, height: 1080 };
const PILLARBOX_VIEWPORT = { width: 1600, height: 600 };

/** Transitions are allowed this long to finish before a frame is measured. */
const SETTLE_BUDGET_MS = 2600;

/** Two boxes are reported as overlapping past this share of the smaller box. */
const OVERLAP_RATIO = 0.25;

/** Stage-relative box ratios may drift this much across a resize. */
const RATIO_TOLERANCE = 0.005;

/** Letterbox and fill measurements are rounded by the fit transform. */
const BOX_TOLERANCE_PX = 2;

/**
 * Clipping tolerance. Subpixel line boxes round up by a pixel or two without
 * losing a glyph, and real clipping is tens of pixels, so a tight 1px threshold
 * would only manufacture P0 findings.
 */
const CLIP_TOLERANCE_PX = 2;

/** WCAG 2.2 large-text thresholds, in authored stage pixels. */
const LARGE_TEXT_PX = 24;
const LARGE_BOLD_TEXT_PX = 18.66;

const MIME_TYPES = {
  ".avif": "image/avif",
  ".css": "text/css; charset=utf-8",
  ".gif": "image/gif",
  ".htm": "text/html; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".ico": "image/x-icon",
  ".jpeg": "image/jpeg",
  ".jpg": "image/jpeg",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".map": "application/json; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".mp4": "video/mp4",
  ".otf": "font/otf",
  ".png": "image/png",
  ".svg": "image/svg+xml",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8",
  ".webm": "video/webm",
  ".webp": "image/webp",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
};

/**
 * The check register. Order here is the order in the report and the JSON, and
 * severity here decides the exit code: any failed `P0` blocks the deck.
 */
const CHECKS = [
  {
    id: "slide-count",
    severity: "P0",
    label: "Slide count agrees across DOM, runtime and plan",
    repair:
      "Rebuild the deck from the plan so the rendered slide count, the runtime length, and the plan `slides` array are the same number.",
  },
  {
    id: "nav-advance",
    severity: "P0",
    label: "Key navigation moves the active slide",
    repair:
      "Bind ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home and End to the runtime step functions and confirm the active index changes on each key.",
  },
  {
    id: "nav-bounds",
    severity: "P0",
    label: "Navigation stays in range at both ends",
    repair:
      "Clamp or wrap the index inside the runtime step function so the first and last slide cannot be navigated past.",
  },
  {
    id: "deep-link-load",
    severity: "P0",
    label: "Deep link `#3` activates slide 3 on load",
    repair:
      "Read `#<n>` as a 1-based index during runtime init, clamp it to the slide range, and apply it before the first paint.",
  },
  {
    id: "deep-link-sync",
    severity: "P0",
    label: "Hash follows the active slide",
    repair:
      "Write the 1-based index with `history.replaceState` on every slide change so the deep link matches what is on screen.",
  },
  {
    id: "lifecycle-event",
    severity: "P0",
    label: "`deckslidechange` fires with the documented payload",
    repair:
      "Dispatch a `deckslidechange` CustomEvent with `bubbles` and `composed` true and a detail of exactly `{ index, previousIndex, total, reason }` on init and on every change.",
  },
  {
    id: "reveal-final-state",
    severity: "P0",
    label: "Reveal targets reach their final computed state",
    repair:
      "Drive reveals from a class on the active slide and give every reveal primitive a final rule that lands on full opacity and an identity transform.",
  },
  {
    id: "reveal-replay",
    severity: "P1",
    label: "Re-entering a slide replays its reveals",
    repair:
      "Reset the reveal state for one frame when a slide becomes active again so a revisited slide replays its entrance instead of appearing pre-revealed.",
  },
  {
    id: "stage-fit-fill",
    severity: "P0",
    label: "Stage fills a 16:9 viewport",
    repair:
      "Fit the stage with one uniform `min(viewportWidth / 1920, viewportHeight / 1080)` scale and an explicit translate so a 16:9 viewport leaves no bars.",
  },
  {
    id: "stage-fit-box",
    severity: "P0",
    label: "Non-16:9 and narrow viewports letterbox or pillarbox",
    repair:
      "Keep the fit scale uniform on both axes so leftover space becomes letterbox or pillarbox instead of stretching or cropping the stage.",
  },
  {
    id: "stage-no-reflow",
    severity: "P0",
    label: "Slide content does not reflow on resize",
    repair:
      "Remove the breakpoint, `clamp()`, `vw` or `vh` value that restyles slide content, and author every slide at stage size only.",
  },
  {
    id: "slide-overflow",
    severity: "P0",
    label: "No text overflow and no clipped content per slide",
    repair:
      "Cut content, change archetype, or reduce the type step on the named slide so every text box fits its container and the stage.",
  },
  {
    id: "slide-overlap",
    severity: "P0",
    label: "No element overlap per slide",
    repair:
      "Re-space the named elements so panels and text blocks no longer cover each other at full stage size.",
  },
  {
    id: "text-contrast",
    severity: "P0",
    label: "Headline and body contrast meets WCAG 2.2 AA",
    repair:
      "Raise the text or surface value on the named slide until the sampled pair reaches 4.5:1, or 3:1 for large text.",
  },
  {
    id: "reduced-motion",
    severity: "P0",
    label: "Reduced motion shows final states with motion neutralized",
    repair:
      "Add or repair the `@media (prefers-reduced-motion: reduce)` block so reveals start at their final state with transitions at `0s`.",
  },
  {
    id: "print-page-count",
    severity: "P0",
    label: "Print produces one page per slide",
    repair:
      "Set `@page { size: 1920px 1080px; margin: 0 }`, drop the stage transform in print, force every slide visible with `break-after: page`, and hide the chrome.",
  },
];

/** A failure the operator can act on. Reported as a one-line error, exit 1. */
class ToolError extends Error {}

function parseArgs(argv) {
  const args = {
    deck: "",
    out: "",
    plan: "",
    phoneWidth: 390,
    keepShots: false,
    json: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--out") args.out = argv[++i] || "";
    else if (token === "--plan") args.plan = argv[++i] || "";
    else if (token === "--phone-width") args.phoneWidth = Number(argv[++i]);
    else if (token === "--keep-shots") args.keepShots = true;
    else if (token === "--json") args.json = true;
    else if (token === "--help" || token === "-h") {
      printHelp();
      process.exit(0);
    } else if (token.startsWith("-")) {
      throw new ToolError(`Unknown argument: ${token}`);
    } else if (!args.deck) {
      args.deck = token;
    } else {
      throw new ToolError(`Unexpected second deck path: ${token}`);
    }
  }

  if (!args.deck) throw new ToolError("A deck HTML path is required. Run with --help for usage.");
  if (!Number.isFinite(args.phoneWidth) || args.phoneWidth < 240 || args.phoneWidth > 1024) {
    throw new ToolError("--phone-width must be a number between 240 and 1024.");
  }

  return args;
}

function printHelp() {
  console.log(`Usage: node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs <deck.html> [options]

Options:
  --out DIR             Directory for every output, report included. Default: .design-brain/screenshots/<stamp>-<slug>-web-deck-render
  --plan FILE           Deck plan JSON to cross-check. Auto-detected when omitted.
  --phone-width PX      Narrow-viewport width for the letterbox pass. Default: 390
  --keep-shots          Keep the diagnostic captures as well as the required evidence set.
  --json                Print the JSON result to stdout and nothing else.

Exit codes:
  0  no P0 finding
  2  at least one P0 finding
  1  usage error, unreadable deck, or chromium not installed

Required evidence per run: one screenshot per slide at stage size, one narrow-viewport
screenshot, deck-print.pdf, render-review.json, and a Markdown report in
.design-brain/visual-reviews/, or beside the other outputs when --out is given.
A run that cannot reach the browser produces no evidence and no render-review result.
`);
}

function repoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
}

function resolveFromCwd(value) {
  return path.isAbsolute(value) ? path.normalize(value) : path.resolve(process.cwd(), value);
}

function displayPath(root, target) {
  const relative = path.relative(root, target);
  if (relative && !relative.startsWith("..")) return relative.replace(/\\/g, "/");
  return target.replace(/\\/g, "/");
}

function timestamp() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    "-",
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");
}

function slug(value) {
  const cleaned = value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return (cleaned || "web-deck").slice(0, 70);
}

function round(value, digits = 2) {
  const factor = 10 ** digits;
  return Math.round(Number(value) * factor) / factor;
}

async function pathExists(target) {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

async function writeJson(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

async function writeText(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, value, "utf8");
}

/* ===========================================================================
   Check register
   =========================================================================== */

function createRegister() {
  const byId = new Map(CHECKS.map((check) => [check.id, check]));
  const results = new Map();

  function record(id, status, detail, evidence) {
    const check = byId.get(id);
    if (!check) throw new Error(`Unregistered check id: ${id}`);
    const entry = {
      id,
      label: check.label,
      severity: check.severity,
      status,
      detail: detail || "",
      evidence: evidence || null,
    };
    if (status === "FAIL") entry.repair = check.repair;
    results.set(id, entry);
  }

  return {
    pass: (id, detail, evidence) => record(id, "PASS", detail, evidence),
    fail: (id, detail, evidence) => record(id, "FAIL", detail, evidence),
    skip: (id, detail) => record(id, "SKIP", detail, null),
    list() {
      return CHECKS.map(
        (check) =>
          results.get(check.id) || {
            id: check.id,
            label: check.label,
            severity: check.severity,
            status: "SKIP",
            detail: "Check did not run.",
            evidence: null,
          }
      );
    },
  };
}

/* ===========================================================================
   Local server
   Relative assets and web fonts only resolve over http, so the deck is served
   from its own directory on an OS-assigned port instead of opened as a file.
   =========================================================================== */

async function startDeckServer(rootDir) {
  const server = http.createServer((request, response) => {
    const requested = new URL(request.url || "/", "http://127.0.0.1");
    let relative = "";
    try {
      relative = decodeURIComponent(requested.pathname).replace(/^\/+/, "");
    } catch {
      response.writeHead(400, { "content-type": "text/plain; charset=utf-8" });
      response.end("Bad request");
      return;
    }

    const target = path.resolve(rootDir, relative);
    if (target !== rootDir && !target.startsWith(`${rootDir}${path.sep}`)) {
      response.writeHead(403, { "content-type": "text/plain; charset=utf-8" });
      response.end("Forbidden");
      return;
    }

    fs.readFile(target)
      .then((data) => {
        response.writeHead(200, {
          "content-type": MIME_TYPES[path.extname(target).toLowerCase()] || "application/octet-stream",
          "content-length": data.byteLength,
          "cache-control": "no-store",
        });
        response.end(data);
      })
      .catch(() => {
        response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
        response.end("Not found");
      });
  });

  return new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      resolve({ server, port: typeof address === "object" && address ? address.port : 0 });
    });
  });
}

function closeServer(server) {
  return new Promise((resolve) => {
    server.close(() => resolve());
    server.closeAllConnections?.();
  });
}

/* ===========================================================================
   Browser acquisition
   =========================================================================== */

async function loadChromium() {
  const attempts = [];
  for (const id of ["@playwright/test", "playwright"]) {
    try {
      const mod = await import(id);
      const chromium = mod.chromium || mod.default?.chromium;
      if (chromium) return chromium;
      attempts.push(`${id}: no chromium export`);
    } catch (error) {
      attempts.push(`${id}: ${error?.message || String(error)}`);
    }
  }
  throw new ToolError(
    [
      "Playwright is not importable from this repo, so no rendered check could run.",
      `Tried: ${attempts.join(" | ")}`,
      "Install the existing devDependencies with `npm install`, then run `npx playwright install chromium`.",
      "Record the render review as NOT_RUN until this command produces evidence.",
    ].join("\n")
  );
}

function chromiumMissingError(detail) {
  return new ToolError(
    [
      "Playwright chromium is not installed, so no rendered check could run.",
      detail ? `Reason: ${detail}` : "",
      "Install the browser this project already depends on: `npx playwright install chromium`",
      "Then re-run: node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs <deck.html>",
      "No screenshots, PDF, or review report were written. Record the render review as NOT_RUN,",
      "and do not claim a visual check happened.",
    ]
      .filter(Boolean)
      .join("\n")
  );
}

async function launchChromium(chromium) {
  let executable = "";
  try {
    executable = chromium.executablePath();
  } catch (error) {
    throw chromiumMissingError(error?.message || String(error));
  }
  if (executable && !(await pathExists(executable))) {
    throw chromiumMissingError(`browser executable missing at ${executable.replace(/\\/g, "/")}`);
  }

  try {
    return await chromium.launch();
  } catch (error) {
    const message = error?.message || String(error);
    if (/Executable doesn't exist|playwright install|browserType.launch/i.test(message)) {
      throw chromiumMissingError(message.split("\n")[0]);
    }
    throw error;
  }
}

/* ===========================================================================
   In-page probes
   Every function below is serialized into the page. They read geometry and
   computed values only; all judgment stays in this script.
   =========================================================================== */

/** Collects the lifecycle events the init script recorded. */
function probeEvents() {
  const store = window.__deckRenderReview;
  return store && Array.isArray(store.events) ? store.events : [];
}

/** Reads the active index from the DOM and, when present, from the runtime API. */
function probeIndex() {
  const slides = Array.prototype.slice.call(document.querySelectorAll(".deck-slide"));
  const active = slides.findIndex((slide) => slide.classList.contains("is-active"));
  const api = window.BrainDeck && typeof window.BrainDeck.index === "number" ? window.BrainDeck.index : null;
  const visible = slides.filter((slide) => getComputedStyle(slide).visibility === "visible").length;
  return {
    dom: active,
    api,
    total: slides.length,
    visible,
    hash: window.location.hash || "",
    runtimeLength: window.BrainDeck && typeof window.BrainDeck.length === "number" ? window.BrainDeck.length : null,
  };
}

/** Reads the stage box against the viewport for the fit checks. */
function probeFit() {
  const stage = document.querySelector(".deck-stage");
  if (!stage) return null;
  const rect = stage.getBoundingClientRect();
  return {
    viewport: { width: window.innerWidth, height: window.innerHeight },
    stage: {
      x: rect.x,
      y: rect.y,
      width: rect.width,
      height: rect.height,
      layoutWidth: stage.offsetWidth,
      layoutHeight: stage.offsetHeight,
    },
    scale: getComputedStyle(document.documentElement).getPropertyValue("--deck-scale").trim(),
    documentScroll: {
      x: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      y: document.documentElement.scrollHeight - document.documentElement.clientHeight,
    },
  };
}

/**
 * Measures one slide: reveal state, clipping, stage-relative box ratios,
 * overlapping content boxes, and the headline/body colour samples.
 */
function probeSlide(options) {
  const stage = document.querySelector(".deck-stage");
  const slides = Array.prototype.slice.call(document.querySelectorAll(".deck-slide"));
  const slide = slides[options.index];
  if (!stage || !slide) return null;

  const stageRect = stage.getBoundingClientRect();
  const slideRect = slide.getBoundingClientRect();
  const nodes = Array.prototype.slice.call(slide.querySelectorAll("*"));

  const labelFor = (el, key) => {
    const classes = String(el.getAttribute("class") || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .slice(0, 2)
      .join(".");
    const text = (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 36);
    return `#${key} ${el.tagName.toLowerCase()}${classes ? `.${classes}` : ""}${text ? ` "${text}"` : ""}`;
  };

  const parseColor = (value) => {
    const match = /^rgba?\(([^)]+)\)$/.exec(String(value || "").trim());
    if (!match) return null;
    const parts = match[1]
      .split(/[\s,/]+/)
      .filter(Boolean)
      .map(Number);
    if (parts.length < 3 || parts.slice(0, 3).some((n) => !Number.isFinite(n))) return null;
    const alpha = parts.length > 3 && Number.isFinite(parts[3]) ? parts[3] : 1;
    return { r: parts[0], g: parts[1], b: parts[2], a: alpha };
  };

  const blend = (top, bottom) => ({
    r: top.r * top.a + bottom.r * (1 - top.a),
    g: top.g * top.a + bottom.g * (1 - top.a),
    b: top.b * top.a + bottom.b * (1 - top.a),
    a: 1,
  });

  /** Walks up to the first opaque background, compositing translucent layers. */
  const backgroundFor = (el) => {
    const stack = [];
    let hasImage = false;
    let node = el;
    while (node instanceof Element) {
      const style = getComputedStyle(node);
      if (style.backgroundImage && style.backgroundImage !== "none") hasImage = true;
      const color = parseColor(style.backgroundColor);
      if (color && color.a > 0) {
        stack.push(color);
        if (color.a >= 0.999) break;
      }
      node = node.parentElement;
    }
    let base = { r: 255, g: 255, b: 255, a: 1 };
    for (let i = stack.length - 1; i >= 0; i -= 1) base = blend(stack[i], base);
    return { r: base.r, g: base.g, b: base.b, hasImage, resolved: stack.length > 0 };
  };

  const isHidden = (el, style) =>
    style.display === "none" || style.visibility === "hidden" || Number(style.opacity) === 0;

  const isDecorative = (el, style) =>
    style.pointerEvents === "none" ||
    /scrim|overlay|backdrop|glow|grain|noise|gradient|watermark/i.test(String(el.getAttribute("class") || ""));

  const sample = (role, el) => {
    if (!el) return null;
    const style = getComputedStyle(el);
    const color = parseColor(style.color) || { r: 0, g: 0, b: 0, a: 1 };
    const background = backgroundFor(el);
    const text = blend(color, { r: background.r, g: background.g, b: background.b, a: 1 });
    return {
      role,
      label: labelFor(el, nodes.indexOf(el)),
      text: (el.textContent || "").replace(/\s+/g, " ").trim().slice(0, 60),
      fontSize: parseFloat(style.fontSize) || 0,
      fontWeight: Number(style.fontWeight) || 400,
      color: [text.r, text.g, text.b],
      background: [background.r, background.g, background.b],
      backgroundResolved: background.resolved,
      backgroundImage: background.hasImage,
    };
  };

  const reveals = [];
  const selfClip = [];
  const spill = [];
  const boxes = [];
  const candidates = [];

  for (let key = 0; key < nodes.length; key += 1) {
    const el = nodes[key];
    const style = getComputedStyle(el);
    const rect = el.getBoundingClientRect();
    const hidden = isHidden(el, style);

    if (el.classList.contains("deck-reveal")) {
      reveals.push({
        label: labelFor(el, key),
        opacity: Number(style.opacity),
        transform: style.transform,
        transitionDuration: style.transitionDuration,
        transitionDelay: style.transitionDelay,
        filter: style.filter,
        clipPath: style.clipPath,
      });
    }

    if (hidden || rect.width <= 0 || rect.height <= 0) continue;

    const textLeaf = el.childElementCount === 0 && (el.textContent || "").trim().length > 0;
    const panel = /panel|card|surface|tile/i.test(String(el.getAttribute("class") || ""));

    if (textLeaf || panel || el.parentElement === slide) {
      boxes.push({
        key,
        rx: (rect.x - stageRect.x) / stageRect.width,
        ry: (rect.y - stageRect.y) / stageRect.height,
        rw: rect.width / stageRect.width,
        rh: rect.height / stageRect.height,
      });
    }

    if (textLeaf && style.overflow !== "visible") {
      if (
        el.scrollWidth > el.clientWidth + options.clipTolerance ||
        el.scrollHeight > el.clientHeight + options.clipTolerance
      ) {
        selfClip.push({
          label: labelFor(el, key),
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          scrollHeight: el.scrollHeight,
          clientHeight: el.clientHeight,
        });
      }
    }

    if (textLeaf) {
      // Nearest clipping ancestor inside the stage. The slide itself clips, so
      // the walk always terminates on a real container.
      let container = el.parentElement;
      while (container && container !== slide && getComputedStyle(container).overflow === "visible") {
        container = container.parentElement;
      }
      const clipper = container || slide;
      const clipperLabel = clipper === slide ? "the slide box" : labelFor(clipper, nodes.indexOf(clipper));
      const clipRect = clipper.getBoundingClientRect();
      const overLeft = clipRect.x - rect.x;
      const overTop = clipRect.y - rect.y;
      const overRight = rect.right - clipRect.right;
      const overBottom = rect.bottom - clipRect.bottom;
      const worst = Math.max(overLeft, overTop, overRight, overBottom);
      if (worst > options.clipTolerance) {
        spill.push({
          label: labelFor(el, key),
          container: clipperLabel,
          overflowPx: worst,
          edge: [
            overLeft > options.clipTolerance ? "left" : "",
            overTop > options.clipTolerance ? "top" : "",
            overRight > options.clipTolerance ? "right" : "",
            overBottom > options.clipTolerance ? "bottom" : "",
          ]
            .filter(Boolean)
            .join("+"),
        });
      }

      if (!isDecorative(el, style)) candidates.push({ el, key, rect });
    } else if (panel && !isDecorative(el, style)) {
      candidates.push({ el, key, rect });
    }
  }

  const overlaps = [];
  for (let i = 0; i < candidates.length; i += 1) {
    for (let j = i + 1; j < candidates.length; j += 1) {
      const a = candidates[i];
      const b = candidates[j];
      if (a.el.contains(b.el) || b.el.contains(a.el)) continue;
      const width = Math.min(a.rect.right, b.rect.right) - Math.max(a.rect.x, b.rect.x);
      const height = Math.min(a.rect.bottom, b.rect.bottom) - Math.max(a.rect.y, b.rect.y);
      if (width <= 1 || height <= 1) continue;
      const area = width * height;
      const smallest = Math.min(a.rect.width * a.rect.height, b.rect.width * b.rect.height);
      if (smallest <= 0) continue;
      const share = area / smallest;
      if (share < options.overlapRatio) continue;
      overlaps.push({ a: labelFor(a.el, a.key), b: labelFor(b.el, b.key), share });
    }
  }

  const headline = slide.querySelector("[data-deck-headline], h1, h2, h3");
  const bodyCandidate = Array.prototype.slice
    .call(slide.querySelectorAll("p, li, [data-deck-body]"))
    .find((el) => (el.textContent || "").trim().length > 2);

  return {
    index: options.index,
    id: slide.id || "",
    stage: { x: stageRect.x, y: stageRect.y, width: stageRect.width, height: stageRect.height },
    slide: {
      x: slideRect.x,
      y: slideRect.y,
      width: slideRect.width,
      height: slideRect.height,
      scrollWidth: slide.scrollWidth,
      clientWidth: slide.clientWidth,
      scrollHeight: slide.scrollHeight,
      clientHeight: slide.clientHeight,
    },
    reveals,
    selfClip,
    spill,
    boxes,
    overlaps,
    samples: [sample("headline", headline), sample("body", bodyCandidate)].filter(Boolean),
  };
}

/**
 * Leaves the slide, returns to it, and samples reveal opacity across a few
 * frames. A replayed entrance dips below its final value on re-entry.
 */
async function probeReplay(options) {
  const slides = Array.prototype.slice.call(document.querySelectorAll(".deck-slide"));
  const target = slides[options.index];
  if (!target) return { status: "no-slide" };
  const reveals = Array.prototype.slice.call(target.querySelectorAll(".deck-reveal"));
  if (!reveals.length) return { status: "no-reveals" };
  if (!window.BrainDeck || typeof window.BrainDeck.goTo !== "function") return { status: "no-api" };
  if (slides.length < 2) return { status: "single-slide" };

  const away = options.index === 0 ? 1 : 0;
  window.BrainDeck.goTo(away);
  await new Promise((resolve) => setTimeout(resolve, 60));
  window.BrainDeck.goTo(options.index);

  let minOpacity = 1;
  for (let frame = 0; frame < 6; frame += 1) {
    await new Promise((resolve) => requestAnimationFrame(() => resolve()));
    for (const el of reveals) minOpacity = Math.min(minOpacity, Number(getComputedStyle(el).opacity));
  }
  return { status: "measured", minOpacity, revealCount: reveals.length };
}

/** Waits for the running transitions, then one more frame. */
async function settlePage(page, budget = SETTLE_BUDGET_MS) {
  await page.evaluate(async (ms) => {
    const animations = typeof document.getAnimations === "function" ? document.getAnimations() : [];
    const finished = Promise.all(animations.map((animation) => animation.finished.catch(() => {})));
    await Promise.race([finished, new Promise((resolve) => setTimeout(resolve, ms))]);
    await new Promise((resolve) => requestAnimationFrame(() => resolve()));
  }, budget);
}

/* ===========================================================================
   Judgment helpers
   =========================================================================== */

function relativeLuminance([r, g, b]) {
  const channel = (value) => {
    const srgb = value / 255;
    return srgb <= 0.03928 ? srgb / 12.92 : ((srgb + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

function contrastRatio(foreground, background) {
  const a = relativeLuminance(foreground);
  const b = relativeLuminance(background);
  const lighter = Math.max(a, b);
  const darker = Math.min(a, b);
  return (lighter + 0.05) / (darker + 0.05);
}

function contrastFloor(sample) {
  const large = sample.fontSize >= LARGE_TEXT_PX || (sample.fontWeight >= 700 && sample.fontSize >= LARGE_BOLD_TEXT_PX);
  return large ? 3 : 4.5;
}

function isIdentityTransform(value) {
  if (!value || value === "none") return true;
  const match = /^matrix(3d)?\(([^)]+)\)$/.exec(value.trim());
  if (!match) return false;
  const parts = match[2].split(",").map((n) => Number(n.trim()));
  if (match[1]) {
    const identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
    return parts.length === 16 && parts.every((n, i) => Math.abs(n - identity[i]) < 0.01);
  }
  const identity = [1, 0, 0, 1, 0, 0];
  return parts.length === 6 && parts.every((n, i) => Math.abs(n - identity[i]) < 0.01);
}

function isZeroDuration(value) {
  return String(value || "")
    .split(",")
    .every((part) => Math.abs(Number.parseFloat(part) || 0) < 0.001);
}

/**
 * Counts PDF pages from the page objects, cross-checked against the page-tree
 * `/Count`. No PDF dependency is added for one integer.
 */
function pdfPageCount(buffer) {
  const text = Buffer.from(buffer).toString("latin1");
  const pageObjects = text.match(/\/Type\s*\/Page\b/g);
  if (pageObjects && pageObjects.length) return pageObjects.length;
  const counts = Array.from(text.matchAll(/\/Count\s+(\d+)/g)).map((match) => Number(match[1]));
  if (counts.length) return Math.max(...counts);
  return 0;
}

async function readPlan(root, deckPath, explicit) {
  const candidates = [];
  if (explicit) candidates.push(resolveFromCwd(explicit));
  else {
    const dir = path.dirname(deckPath);
    const stem = path.basename(deckPath, path.extname(deckPath));
    // `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs` writes `<stem>.deck-plan.json`
    // beside the deck. The rest are fallbacks for a hand-placed plan.
    candidates.push(
      path.join(dir, `${stem}.deck-plan.json`),
      path.join(dir, `${stem}.plan.json`),
      path.join(dir, `${stem}-plan.json`),
      path.join(dir, "deck-plan.json")
    );
  }

  for (const candidate of candidates) {
    if (!(await pathExists(candidate))) continue;
    try {
      const plan = JSON.parse(await fs.readFile(candidate, "utf8"));
      return { path: candidate, display: displayPath(root, candidate), plan };
    } catch (error) {
      if (explicit) throw new ToolError(`Deck plan is not readable JSON: ${candidate} (${error?.message})`);
    }
  }

  if (explicit) throw new ToolError(`Deck plan not found: ${candidates[0]}`);
  return { path: "", display: null, plan: null };
}

/* ===========================================================================
   Review passes
   =========================================================================== */

async function reviewSlideCount(page, register, plan, planDisplay) {
  const state = await page.evaluate(probeIndex);
  const planCount = Array.isArray(plan?.slides) ? plan.slides.length : null;
  const detail = `DOM ${state.total}, runtime ${state.runtimeLength === null ? "no API" : state.runtimeLength}, plan ${
    planCount === null ? "not supplied" : planCount
  }.`;

  if (!state.total) {
    register.fail("slide-count", `No \`.deck-slide\` element rendered. ${detail}`, null);
    return state;
  }
  const problems = [];
  if (state.runtimeLength !== null && state.runtimeLength !== state.total) {
    problems.push("the runtime slide length does not match the DOM");
  }
  if (planCount !== null && planCount !== state.total) {
    problems.push(`the plan declares ${planCount} slides`);
  }
  if (state.visible !== 1) {
    problems.push(`${state.visible} slides are visible at once instead of exactly one`);
  }

  if (problems.length) {
    register.fail("slide-count", `${problems.join("; ")}. ${detail}`, planDisplay);
  } else {
    register.pass("slide-count", detail, planDisplay);
  }
  return state;
}

async function reviewNavigation(page, register, total) {
  if (total < 2) {
    register.skip("nav-advance", "Deck has a single slide; key navigation cannot advance.");
    register.skip("nav-bounds", "Deck has a single slide; there are no two ends to test.");
    return;
  }

  const read = async () => (await page.evaluate(probeIndex)).dom;
  const press = async (key) => {
    await page.keyboard.press(key);
    await page.waitForTimeout(140);
    return read();
  };

  await page.keyboard.press("Home");
  await page.waitForTimeout(140);

  const advanceFailures = [];
  const forward = ["ArrowRight", "PageDown", " "];
  for (const key of forward) {
    const before = await read();
    const after = await press(key);
    const expected = Math.min(total - 1, before + 1);
    if (after !== expected) advanceFailures.push(`${key.trim() || "Space"}: ${before} -> ${after}, expected ${expected}`);
  }

  const backward = ["ArrowLeft", "PageUp"];
  for (const key of backward) {
    const before = await read();
    const after = await press(key);
    const expected = Math.max(0, before - 1);
    if (after !== expected) advanceFailures.push(`${key}: ${before} -> ${after}, expected ${expected}`);
  }

  const atEnd = await press("End");
  if (atEnd !== total - 1) advanceFailures.push(`End: landed on ${atEnd}, expected ${total - 1}`);
  const atStart = await press("Home");
  if (atStart !== 0) advanceFailures.push(`Home: landed on ${atStart}, expected 0`);

  if (advanceFailures.length) {
    register.fail("nav-advance", `Key navigation did not move as declared. ${advanceFailures.join("; ")}.`, null);
  } else {
    register.pass("nav-advance", "ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home and End all move the active index.", null);
  }

  // Both ends: clamping and wrapping are both legal, leaving the range is not.
  await page.keyboard.press("Home");
  await page.waitForTimeout(140);
  const beforeStart = await read();
  const pastStart = await press("ArrowLeft");
  await page.keyboard.press("End");
  await page.waitForTimeout(140);
  const beforeEnd = await read();
  const pastEnd = await press("ArrowRight");

  const startBehavior = pastStart === 0 ? "clamp" : pastStart === total - 1 ? "wrap" : "out of range";
  const endBehavior = pastEnd === total - 1 ? "clamp" : pastEnd === 0 ? "wrap" : "out of range";
  const boundsDetail = `First slide: ${beforeStart} -> ${pastStart} (${startBehavior}). Last slide: ${beforeEnd} -> ${pastEnd} (${endBehavior}).`;

  if (startBehavior === "out of range" || endBehavior === "out of range") {
    register.fail("nav-bounds", `Navigation left the slide range at an end. ${boundsDetail}`, null);
  } else {
    register.pass("nav-bounds", boundsDetail, null);
  }
}

async function reviewLifecycle(page, register) {
  const events = await page.evaluate(probeEvents);
  if (!events.length) {
    register.fail(
      "lifecycle-event",
      "No `deckslidechange` event was observed on load or on key navigation.",
      null
    );
    return;
  }

  const expectedKeys = ["index", "previousIndex", "total", "reason"].sort().join(",");
  const reasons = ["init", "key", "pointer", "wheel", "api"];
  const problems = [];
  const init = events[0];

  if (init.reason !== "init") problems.push(`the first event carries reason \`${init.reason}\` instead of \`init\``);
  for (const event of events) {
    if (event.keys.join(",") !== expectedKeys) {
      problems.push(`a payload carries keys [${event.keys.join(", ")}] instead of index, previousIndex, total, reason`);
      break;
    }
  }
  const badReason = events.find((event) => !reasons.includes(event.reason));
  if (badReason) problems.push(`reason \`${badReason.reason}\` is outside init|key|pointer|wheel|api`);
  if (!events.every((event) => event.bubbles && event.composed)) {
    problems.push("an event was dispatched without both `bubbles` and `composed`");
  }
  if (!events.some((event) => event.reason === "key")) {
    problems.push("no event reported reason `key` during key navigation");
  }
  const badTotal = events.find((event) => !Number.isInteger(event.total) || event.total < 1);
  if (badTotal) problems.push(`a payload reported total \`${badTotal.total}\``);

  const detail = `${events.length} events observed, reasons ${[...new Set(events.map((event) => event.reason))].join("/")}.`;
  if (problems.length) register.fail("lifecycle-event", `${problems.join("; ")}. ${detail}`, null);
  else register.pass("lifecycle-event", detail, null);
}

async function reviewDeepLink(page, register, deckUrl, total) {
  if (total < 3) {
    register.skip("deep-link-load", "Deck has fewer than three slides; `#3` is not addressable.");
    register.skip("deep-link-sync", "Deck has fewer than three slides; hash sync was not measured.");
    return;
  }

  // A fragment-only navigation does not re-run the runtime, so the hash is set
  // first and the document is then reloaded with it in place.
  await page.goto(`${deckUrl}#3`);
  await page.reload();
  await page.waitForSelector(".deck-slide", { state: "attached" });
  await settlePage(page);

  const loaded = await page.evaluate(probeIndex);
  if (loaded.dom === 2) {
    register.pass("deep-link-load", "`#3` activated slide 3 on load.", null);
  } else {
    register.fail(
      "deep-link-load",
      `\`#3\` activated slide ${loaded.dom + 1} instead of slide 3. Hash on load: ${loaded.hash || "none"}.`,
      null
    );
  }

  await page.keyboard.press("ArrowRight");
  await page.waitForTimeout(180);
  const moved = await page.evaluate(probeIndex);
  const expectedHash = `#${moved.dom + 1}`;
  if (moved.hash === expectedHash) {
    register.pass("deep-link-sync", `Hash followed navigation to ${expectedHash}.`, null);
  } else {
    register.fail(
      "deep-link-sync",
      `Hash is ${moved.hash || "empty"} while slide ${moved.dom + 1} is active; expected ${expectedHash}.`,
      null
    );
  }
}

async function captureSlides(page, register, total, evidenceDir, evidenceDisplay, navigateTo) {
  const slidesDir = path.join(evidenceDir, "slides");
  await fs.mkdir(slidesDir, { recursive: true });

  const shots = [];
  const measurements = [];
  const overflowProblems = [];
  const overlapProblems = [];
  const revealProblems = [];
  const contrastProblems = [];
  const contrastSamples = [];
  let revealTotal = 0;

  for (let index = 0; index < total; index += 1) {
    await navigateTo(index);
    await settlePage(page);

    const name = `slide-${String(index + 1).padStart(3, "0")}.png`;
    const file = path.join(slidesDir, name);
    await page.screenshot({ path: file });
    shots.push(`${evidenceDisplay}/slides/${name}`);

    const measured = await page.evaluate(probeSlide, {
      index,
      overlapRatio: OVERLAP_RATIO,
      clipTolerance: CLIP_TOLERANCE_PX,
    });
    if (!measured) continue;
    measurements.push(measured);
    const slideRef = `slide ${index + 1}`;
    const shotRef = `${evidenceDisplay}/slides/${name}`;

    if (measured.slide.scrollWidth > measured.slide.clientWidth + 1) {
      overflowProblems.push(
        `${slideRef} content is ${measured.slide.scrollWidth - measured.slide.clientWidth}px wider than the stage`
      );
    }
    if (measured.slide.scrollHeight > measured.slide.clientHeight + 1) {
      overflowProblems.push(
        `${slideRef} content is ${measured.slide.scrollHeight - measured.slide.clientHeight}px taller than the stage`
      );
    }
    for (const clipped of measured.selfClip) {
      overflowProblems.push(`${slideRef} ${clipped.label} is clipped by its own box`);
    }
    for (const item of measured.spill) {
      overflowProblems.push(
        `${slideRef} ${item.label} spills ${Math.round(item.overflowPx)}px past ${item.container} on ${item.edge}`
      );
    }
    for (const pair of measured.overlaps) {
      overlapProblems.push(
        `${slideRef} ${pair.a} covers ${Math.round(pair.share * 100)}% of ${pair.b}`
      );
    }

    revealTotal += measured.reveals.length;
    for (const reveal of measured.reveals) {
      if (reveal.opacity < 0.99) {
        revealProblems.push(`${slideRef} ${reveal.label} settled at opacity ${round(reveal.opacity)}`);
      } else if (!isIdentityTransform(reveal.transform)) {
        revealProblems.push(`${slideRef} ${reveal.label} settled at transform ${reveal.transform}`);
      }
    }

    for (const sample of measured.samples) {
      const ratio = contrastRatio(sample.color, sample.background);
      const floor = contrastFloor(sample);
      contrastSamples.push({
        slide: index + 1,
        role: sample.role,
        label: sample.label,
        fontSize: round(sample.fontSize, 1),
        ratio: round(ratio),
        required: floor,
        overImage: sample.backgroundImage,
        evidence: shotRef,
      });
      if (ratio + 0.05 < floor) {
        contrastProblems.push(
          `${slideRef} ${sample.role} ${sample.label} samples ${round(ratio)}:1 against its painted background, below ${floor}:1`
        );
      }
    }
  }

  const firstShot = shots[0] || null;
  if (overflowProblems.length) {
    register.fail("slide-overflow", overflowProblems.slice(0, 12).join("; "), firstShot);
  } else {
    register.pass("slide-overflow", `No clipped text and no stage overflow across ${total} slides.`, firstShot);
  }

  if (overlapProblems.length) {
    register.fail("slide-overlap", overlapProblems.slice(0, 12).join("; "), firstShot);
  } else {
    register.pass(
      "slide-overlap",
      `No content box covers another past ${Math.round(OVERLAP_RATIO * 100)}% of its area across ${total} slides.`,
      firstShot
    );
  }

  if (!revealTotal) {
    register.skip("reveal-final-state", "No `.deck-reveal` target exists in this deck.");
  } else if (revealProblems.length) {
    register.fail("reveal-final-state", revealProblems.slice(0, 12).join("; "), firstShot);
  } else {
    register.pass("reveal-final-state", `${revealTotal} reveal targets reached full opacity and an identity transform.`, firstShot);
  }

  if (!contrastSamples.length) {
    register.skip("text-contrast", "No headline or body text was found to sample.");
  } else if (contrastProblems.length) {
    register.fail("text-contrast", contrastProblems.slice(0, 12).join("; "), firstShot);
  } else {
    const worst = contrastSamples.reduce((low, item) => (item.ratio < low.ratio ? item : low), contrastSamples[0]);
    const overImage = contrastSamples.filter((item) => item.overImage).length;
    register.pass(
      "text-contrast",
      `${contrastSamples.length} samples pass, lowest ${worst.ratio}:1 on slide ${worst.slide} ${worst.role}` +
        (overImage ? `; ${overImage} sampled over a background image and need an eye check on the scrim.` : "."),
      firstShot
    );
  }

  return { shots, measurements, contrastSamples };
}

async function reviewReplay(page, register, index, navigateTo) {
  await navigateTo(index);
  await settlePage(page);
  const result = await page.evaluate(probeReplay, { index });

  if (result.status === "no-reveals" || result.status === "no-slide") {
    register.skip("reveal-replay", "Slide has no reveal target to replay.");
    return;
  }
  if (result.status === "no-api") {
    register.skip("reveal-replay", "No runtime API was exposed, so re-entry could not be driven.");
    return;
  }
  if (result.status === "single-slide") {
    register.skip("reveal-replay", "Deck has a single slide; there is no re-entry to measure.");
    return;
  }

  // Sampled across frames rather than asserted on one, because the reset class
  // lives for a single frame. A replay has to dip before it rises again.
  if (result.minOpacity < 0.9) {
    register.pass(
      "reveal-replay",
      `Re-entering slide ${index + 1} reset ${result.revealCount} reveals to opacity ${round(result.minOpacity)} before replaying.`,
      null
    );
  } else {
    register.fail(
      "reveal-replay",
      `Re-entering slide ${index + 1} left its reveals at opacity ${round(result.minOpacity)}, so the entrance did not replay.`,
      null
    );
  }
  await settlePage(page);
}

async function reviewStageFit(page, register, options) {
  const { phoneWidth, evidenceDir, evidenceDisplay, keepShots, navigateTo } = options;

  await page.setViewportSize({ width: STAGE_WIDTH, height: STAGE_HEIGHT });
  await navigateTo(0);
  await settlePage(page);

  const fill = await page.evaluate(probeFit);
  if (!fill) {
    register.fail("stage-fit-fill", "No `.deck-stage` element was found to fit.", null);
    register.skip("stage-fit-box", "No stage element to measure.");
    register.skip("stage-no-reflow", "No stage element to measure.");
    return;
  }

  const baseline = await page.evaluate(probeSlide, {
    index: 0,
    overlapRatio: OVERLAP_RATIO,
    clipTolerance: CLIP_TOLERANCE_PX,
  });
  if (keepShots) {
    await page.screenshot({ path: path.join(evidenceDir, "fit-1920x1080.png") });
  }

  const fillGapX = Math.abs(fill.stage.width - fill.viewport.width);
  const fillGapY = Math.abs(fill.stage.height - fill.viewport.height);
  const fillDetail = `At ${fill.viewport.width}x${fill.viewport.height} the stage paints ${round(fill.stage.width)}x${round(
    fill.stage.height
  )} at ${round(fill.stage.x)},${round(fill.stage.y)} with --deck-scale ${fill.scale || "unset"}.`;
  if (fillGapX <= BOX_TOLERANCE_PX && fillGapY <= BOX_TOLERANCE_PX && Math.abs(fill.stage.x) <= BOX_TOLERANCE_PX && Math.abs(fill.stage.y) <= BOX_TOLERANCE_PX) {
    register.pass("stage-fit-fill", fillDetail, null);
  } else {
    register.fail("stage-fit-fill", `The stage does not fill a 16:9 viewport. ${fillDetail}`, null);
  }

  const probes = [
    { name: "letterbox", viewport: LETTERBOX_VIEWPORT, expect: "letterbox" },
    { name: "pillarbox", viewport: PILLARBOX_VIEWPORT, expect: "pillarbox" },
    { name: "phone", viewport: { width: phoneWidth, height: PHONE_HEIGHT }, expect: "letterbox" },
  ];

  const boxProblems = [];
  const boxNotes = [];
  let narrowShot = null;
  let reflowReport = null;

  for (const probe of probes) {
    await page.setViewportSize(probe.viewport);
    await page.waitForTimeout(160);
    await settlePage(page);
    const measured = await page.evaluate(probeFit);
    if (!measured) continue;

    const fillsWidth = Math.abs(measured.stage.width - measured.viewport.width) <= BOX_TOLERANCE_PX;
    const fillsHeight = Math.abs(measured.stage.height - measured.viewport.height) <= BOX_TOLERANCE_PX;
    const uniform =
      Math.abs(measured.stage.width / STAGE_WIDTH - measured.stage.height / STAGE_HEIGHT) < 0.002 &&
      measured.stage.layoutWidth === STAGE_WIDTH &&
      measured.stage.layoutHeight === STAGE_HEIGHT;
    const observed = fillsWidth && !fillsHeight ? "letterbox" : fillsHeight && !fillsWidth ? "pillarbox" : fillsWidth && fillsHeight ? "exact fill" : "neither";

    boxNotes.push(
      `${probe.name} ${measured.viewport.width}x${measured.viewport.height}: stage ${round(measured.stage.width)}x${round(
        measured.stage.height
      )}, ${observed}`
    );
    if (!uniform) {
      boxProblems.push(
        `${probe.name} viewport scaled the stage non-uniformly (${round(measured.stage.width / STAGE_WIDTH, 4)} by ${round(
          measured.stage.height / STAGE_HEIGHT,
          4
        )}) or the authored box is no longer ${STAGE_WIDTH}x${STAGE_HEIGHT}`
      );
    } else if (observed !== probe.expect) {
      boxProblems.push(`${probe.name} viewport produced ${observed} instead of ${probe.expect}`);
    }
    if (measured.documentScroll.x > BOX_TOLERANCE_PX || measured.documentScroll.y > BOX_TOLERANCE_PX) {
      boxProblems.push(`${probe.name} viewport left the document scrollable by ${measured.documentScroll.x}x${measured.documentScroll.y}px`);
    }

    if (probe.name === "phone") {
      const name = `narrow-${probe.viewport.width}x${probe.viewport.height}.png`;
      await page.screenshot({ path: path.join(evidenceDir, name) });
      narrowShot = `${evidenceDisplay}/${name}`;

      if (baseline) {
        const after = await page.evaluate(probeSlide, {
          index: 0,
          overlapRatio: OVERLAP_RATIO,
          clipTolerance: CLIP_TOLERANCE_PX,
        });
        reflowReport = compareBoxes(baseline.boxes, after ? after.boxes : []);
      }
    } else if (keepShots) {
      await page.screenshot({ path: path.join(evidenceDir, `fit-${probe.viewport.width}x${probe.viewport.height}.png`) });
    }
  }

  if (boxProblems.length) {
    register.fail("stage-fit-box", `${boxProblems.join("; ")}. Measured: ${boxNotes.join("; ")}.`, narrowShot);
  } else {
    register.pass("stage-fit-box", boxNotes.join("; "), narrowShot);
  }

  if (!reflowReport) {
    register.skip("stage-no-reflow", "Slide 0 could not be measured on both sides of the resize.");
  } else if (reflowReport.missing) {
    register.fail(
      "stage-no-reflow",
      `${reflowReport.missing} measured boxes on slide 1 disappeared or appeared across the resize, so the slide reflowed.`,
      narrowShot
    );
  } else if (reflowReport.worst > RATIO_TOLERANCE) {
    register.fail(
      "stage-no-reflow",
      `Stage-relative box ratios on slide 1 moved by ${round(reflowReport.worst, 4)} across the resize, past the ${RATIO_TOLERANCE} tolerance, on ${reflowReport.worstKey}.`,
      narrowShot
    );
  } else {
    register.pass(
      "stage-no-reflow",
      `${reflowReport.compared} box ratios on slide 1 held within ${round(reflowReport.worst, 4)} across the resize from ${STAGE_WIDTH}x${STAGE_HEIGHT} to ${phoneWidth}x${PHONE_HEIGHT}.`,
      narrowShot
    );
  }

  await page.setViewportSize({ width: STAGE_WIDTH, height: STAGE_HEIGHT });
  await page.waitForTimeout(160);
  return { narrowShot };
}

function compareBoxes(before, after) {
  const afterByKey = new Map(after.map((box) => [box.key, box]));
  const beforeKeys = new Set(before.map((box) => box.key));
  let worst = 0;
  let worstKey = "none";
  let compared = 0;
  let missing = after.filter((box) => !beforeKeys.has(box.key)).length;

  for (const box of before) {
    const match = afterByKey.get(box.key);
    if (!match) {
      missing += 1;
      continue;
    }
    compared += 1;
    const deltas = [
      Math.abs(box.rx - match.rx),
      Math.abs(box.ry - match.ry),
      Math.abs(box.rw - match.rw),
      Math.abs(box.rh - match.rh),
    ];
    const delta = Math.max(...deltas);
    if (delta > worst) {
      worst = delta;
      worstKey = `box ${box.key}`;
    }
  }
  return { worst, worstKey, compared, missing };
}

async function reviewReducedMotion(page, register, deckUrl, options) {
  const { evidenceDir, evidenceDisplay, keepShots } = options;
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto(deckUrl);
  await page.reload();
  await page.waitForSelector(".deck-slide", { state: "attached" });
  await page.waitForTimeout(120);

  const state = await page.evaluate(probeIndex);
  const measured = await page.evaluate(probeSlide, {
    index: Math.max(0, state.dom),
    overlapRatio: OVERLAP_RATIO,
    clipTolerance: CLIP_TOLERANCE_PX,
  });
  let evidence = null;
  if (keepShots) {
    const name = "reduced-motion.png";
    await page.screenshot({ path: path.join(evidenceDir, name) });
    evidence = `${evidenceDisplay}/${name}`;
  }

  if (!measured) {
    register.fail("reduced-motion", "The active slide could not be measured under `prefers-reduced-motion: reduce`.", evidence);
  } else if (!measured.reveals.length) {
    register.pass(
      "reduced-motion",
      "Deck declares no reveal target, and the active slide rendered under `prefers-reduced-motion: reduce`.",
      evidence
    );
  } else {
    const notFinal = measured.reveals.filter((reveal) => reveal.opacity < 0.99 || !isIdentityTransform(reveal.transform));
    const animated = measured.reveals.filter((reveal) => !isZeroDuration(reveal.transitionDuration));
    const problems = [];
    if (notFinal.length) {
      problems.push(
        `${notFinal.length} of ${measured.reveals.length} reveals are not at their final state (first: ${notFinal[0].label} at opacity ${round(
          notFinal[0].opacity
        )})`
      );
    }
    if (animated.length) {
      problems.push(
        `${animated.length} reveals still carry a transition duration (first: ${animated[0].label} at ${animated[0].transitionDuration})`
      );
    }
    if (problems.length) {
      register.fail("reduced-motion", problems.join("; "), evidence);
    } else {
      register.pass(
        "reduced-motion",
        `All ${measured.reveals.length} reveals on the active slide are visible at their final state with transitions at 0s.`,
        evidence
      );
    }
  }

  await page.emulateMedia({ reducedMotion: "no-preference" });
}

async function reviewPrint(page, register, total, evidenceDir, evidenceDisplay) {
  const name = "deck-print.pdf";
  const file = path.join(evidenceDir, name);
  const evidence = `${evidenceDisplay}/${name}`;
  let buffer = null;

  try {
    buffer = await page.pdf({ preferCSSPageSize: true, printBackground: true });
  } catch (error) {
    register.fail("print-page-count", `The print path failed: ${error?.message || String(error)}.`, null);
    return { pdf: null, pages: 0 };
  }

  await fs.mkdir(evidenceDir, { recursive: true });
  await fs.writeFile(file, buffer);
  const pages = pdfPageCount(buffer);

  if (!pages) {
    register.fail("print-page-count", "The printed PDF reports no readable page count.", evidence);
  } else if (pages !== total) {
    register.fail(
      "print-page-count",
      `The printed PDF has ${pages} pages for ${total} slides, so print is not one slide per page.`,
      evidence
    );
  } else {
    register.pass("print-page-count", `The printed PDF has ${pages} pages for ${total} slides.`, evidence);
  }
  return { pdf: evidence, pages };
}

/* ===========================================================================
   Report
   =========================================================================== */

function reportMarkdown(result) {
  const lines = [
    `# Web Deck Render Review: ${result.deckTitle}`,
    "",
    "## Review Metadata",
    "",
    `- Deck artifact: \`${result.deck}\``,
    `- Deck plan: ${result.plan ? `\`${result.plan}\`` : "not supplied"}`,
    `- Evidence directory: \`${result.evidenceDir}\``,
    `- Served from: ${result.servedFrom}`,
    `- Browser: chromium ${result.browserVersion}`,
    `- Authored stage: ${STAGE_WIDTH} x ${STAGE_HEIGHT}`,
    `- Slide count: ${result.slideCount.dom} rendered, ${
      result.slideCount.runtime === null ? "no runtime API" : `${result.slideCount.runtime} in the runtime`
    }, ${result.slideCount.plan === null ? "no plan count" : `${result.slideCount.plan} in the plan`}`,
    `- Viewports exercised: ${result.viewports.join(", ")}`,
    `- Date/time: ${result.generatedAt}`,
    "- Generated by: `node skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`",
    "",
    "## Result",
    "",
    `- Render review result: ${result.result}`,
    `- P0 findings: ${result.counts.p0}`,
    `- P1 findings: ${result.counts.p1}`,
    `- Checks passed: ${result.counts.passed}`,
    `- Checks skipped: ${result.counts.skipped}`,
    `- Visual verification status: ${result.visualVerification}`,
    `- Exit code: ${result.exitCode}`,
    "",
    "This report is rendered evidence. Every line below was measured from a real chromium",
    "render of the served deck, not from reading the deck source.",
    "",
    "## Check Register",
    "",
    "| Check | Severity | Status | Evidence |",
    "| --- | --- | --- | --- |",
  ];

  for (const check of result.checks) {
    lines.push(
      `| ${check.id} | ${check.severity} | ${check.status} | ${check.evidence ? `\`${check.evidence}\`` : "-"} |`
    );
  }

  lines.push("", "## Check Detail", "");
  for (const check of result.checks) {
    lines.push(`- \`${check.id}\` ${check.status}: ${check.detail || check.label}`);
  }

  lines.push("", "## Findings", "");
  if (!result.findings.length) {
    lines.push("- none");
  } else {
    for (const finding of result.findings) {
      lines.push(`### ${finding.severity} ${finding.id}`, "");
      lines.push(`- Check: ${finding.label}`);
      lines.push(`- Observed: ${finding.detail}`);
      lines.push(`- Evidence: ${finding.evidence ? `\`${finding.evidence}\`` : "see the per-slide captures in the evidence directory"}`);
      lines.push(`- Repair: ${finding.repair}`);
      lines.push("");
    }
  }

  lines.push("## Rendered Evidence", "");
  for (const shot of result.evidence.slides) lines.push(`- \`${shot}\``);
  if (result.evidence.narrow) lines.push(`- \`${result.evidence.narrow}\``);
  if (result.evidence.pdf) lines.push(`- \`${result.evidence.pdf}\``);
  lines.push(`- \`${result.evidence.json}\``);

  lines.push("", "## Contrast Samples", "");
  if (!result.contrastSamples.length) {
    lines.push("- none sampled");
  } else {
    lines.push("| Slide | Role | Size | Ratio | Required | Over image |");
    lines.push("| --- | --- | --- | --- | --- | --- |");
    for (const sample of result.contrastSamples) {
      lines.push(
        `| ${sample.slide} | ${sample.role} | ${sample.fontSize}px | ${sample.ratio}:1 | ${sample.required}:1 | ${
          sample.overImage ? "yes" : "no"
        } |`
      );
    }
  }

  lines.push(
    "",
    "## Next Pass",
    "",
    "- Judge craft from the per-slide captures against `skills/presentation-deck/design/craft/web-deck-stage-fidelity.md`",
    "  and `skills/presentation-deck/design/craft/deck-motion.md`. A passing register proves the stage and runtime contract,",
    "  not the design.",
    "- Record this report and its evidence paths in the receipt built from",
    "  `skills/presentation-deck/resources/WEB_DECK_RECEIPT.md`.",
    "- A P0 finding is a repair ticket, not a note. Fix the deck, rebuild, then re-run the static audit",
    "  and this review.",
    ""
  );

  return `${lines.join("\n")}\n`;
}

/* ===========================================================================
   Main
   =========================================================================== */

async function main() {
  const args = parseArgs(process.argv);
  const root = repoRoot();
  const deckPath = resolveFromCwd(args.deck);

  if (!(await pathExists(deckPath))) throw new ToolError(`Deck file not found: ${deckPath}`);
  const deckStat = await fs.stat(deckPath);
  if (!deckStat.isFile()) throw new ToolError(`Deck path is not a file: ${deckPath}`);
  if (!/\.html?$/i.test(deckPath)) throw new ToolError(`Deck file must be .html or .htm: ${deckPath}`);

  const deckDir = path.dirname(deckPath);
  const deckSlug = slug(path.basename(deckPath, path.extname(deckPath)));
  const stamp = timestamp();
  const planInfo = await readPlan(root, deckPath, args.plan);

  const evidenceDir = args.out
    ? resolveFromCwd(args.out)
    : path.join(root, ".design-brain", "screenshots", `${stamp}-${deckSlug}-web-deck-render`);
  // `--out` owns every output, so a run can stay entirely outside the repo. The
  // default keeps the Brain Design evidence convention: captures under
  // `.design-brain/screenshots/`, the report under `.design-brain/visual-reviews/`.
  const reportName = `${stamp}-${deckSlug}-web-deck-render-review.md`;
  const reportPath = args.out
    ? path.join(evidenceDir, reportName)
    : path.join(root, ".design-brain", "visual-reviews", reportName);
  const evidenceDisplay = displayPath(root, evidenceDir);

  const chromium = await loadChromium();
  const browser = await launchChromium(chromium);
  const { server, port } = await startDeckServer(deckDir);
  const deckUrl = `http://127.0.0.1:${port}/${encodeURIComponent(path.basename(deckPath))}`;
  const register = createRegister();

  let payload = null;
  try {
    const context = await browser.newContext({
      viewport: { width: STAGE_WIDTH, height: STAGE_HEIGHT },
      deviceScaleFactor: 1,
    });
    context.setDefaultTimeout(20000);
    const page = await context.newPage();

    await page.addInitScript(() => {
      window.__deckRenderReview = { events: [] };
      document.addEventListener("deckslidechange", (event) => {
        const detail = event.detail && typeof event.detail === "object" ? event.detail : {};
        window.__deckRenderReview.events.push({
          keys: Object.keys(detail).sort(),
          index: detail.index,
          previousIndex: detail.previousIndex,
          total: detail.total,
          reason: detail.reason,
          bubbles: event.bubbles,
          composed: event.composed,
        });
      });
    });

    await page.goto(deckUrl);
    await page.waitForSelector(".deck-slide", { state: "attached" });
    await settlePage(page);

    const state = await reviewSlideCount(page, register, planInfo.plan, planInfo.display);
    const total = state.total;
    if (!total) throw new ToolError(`No slide rendered from ${displayPath(root, deckPath)}; there is nothing to review.`);

    /** Drives the deck through its own API when exposed, through keys when not. */
    const navigateTo = async (index) => {
      const moved = await page.evaluate((target) => {
        if (window.BrainDeck && typeof window.BrainDeck.goTo === "function") {
          window.BrainDeck.goTo(target);
          return true;
        }
        return false;
      }, index);
      if (!moved) {
        await page.keyboard.press("Home");
        for (let i = 0; i < index; i += 1) await page.keyboard.press("ArrowRight");
      }
      await page.waitForTimeout(120);
    };

    await reviewNavigation(page, register, total);
    await reviewLifecycle(page, register);
    await reviewDeepLink(page, register, deckUrl, total);

    await fs.mkdir(evidenceDir, { recursive: true });
    const captured = await captureSlides(page, register, total, evidenceDir, evidenceDisplay, navigateTo);
    await reviewReplay(page, register, 0, navigateTo);

    const fit = await reviewStageFit(page, register, {
      phoneWidth: args.phoneWidth,
      evidenceDir,
      evidenceDisplay,
      keepShots: args.keepShots,
      navigateTo,
    });

    const print = await reviewPrint(page, register, total, evidenceDir, evidenceDisplay);
    await reviewReducedMotion(page, register, deckUrl, {
      evidenceDir,
      evidenceDisplay,
      keepShots: args.keepShots,
    });

    const checks = register.list();
    const findings = checks.filter((check) => check.status === "FAIL");
    const counts = {
      p0: findings.filter((check) => check.severity === "P0").length,
      p1: findings.filter((check) => check.severity === "P1").length,
      passed: checks.filter((check) => check.status === "PASS").length,
      skipped: checks.filter((check) => check.status === "SKIP").length,
    };
    const exitCode = counts.p0 ? 2 : 0;

    payload = {
      schema: "design-brain.web-deck.render-review.v1",
      tool: "skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs",
      generatedAt: new Date().toISOString(),
      deck: displayPath(root, deckPath),
      deckTitle: (await page.title()) || path.basename(deckPath),
      plan: planInfo.display,
      servedFrom: deckUrl,
      browserVersion: browser.version(),
      stage: { width: STAGE_WIDTH, height: STAGE_HEIGHT },
      slideCount: {
        dom: total,
        runtime: state.runtimeLength,
        plan: Array.isArray(planInfo.plan?.slides) ? planInfo.plan.slides.length : null,
      },
      viewports: [
        `${STAGE_WIDTH}x${STAGE_HEIGHT}`,
        `${LETTERBOX_VIEWPORT.width}x${LETTERBOX_VIEWPORT.height}`,
        `${PILLARBOX_VIEWPORT.width}x${PILLARBOX_VIEWPORT.height}`,
        `${args.phoneWidth}x${PHONE_HEIGHT}`,
      ],
      evidenceDir: evidenceDisplay,
      evidence: {
        slides: captured.shots,
        narrow: fit?.narrowShot || null,
        pdf: print.pdf,
        json: `${evidenceDisplay}/render-review.json`,
        report: displayPath(root, reportPath),
      },
      contrastSamples: captured.contrastSamples,
      checks,
      findings,
      counts,
      result: counts.p0 ? "FAIL" : "PASS",
      visualVerification: "screenshot/render verified",
      exitCode,
    };

    await context.close();
  } finally {
    await browser.close();
    await closeServer(server);
  }

  payload.report = displayPath(root, reportPath);
  await writeJson(path.join(evidenceDir, "render-review.json"), payload);
  await writeText(reportPath, reportMarkdown(payload));

  if (args.json) {
    console.log(JSON.stringify(payload, null, 2));
  } else {
    console.log(`Web deck render review: ${payload.result}`);
    console.log(`Slides reviewed: ${payload.slideCount.dom}`);
    console.log(`P0 findings: ${payload.counts.p0}, P1 findings: ${payload.counts.p1}, skipped: ${payload.counts.skipped}`);
    for (const finding of payload.findings) {
      console.log(`- ${finding.severity} ${finding.id}: ${finding.detail}`);
      console.log(`  repair: ${finding.repair}`);
    }
    console.log(`Evidence: ${payload.evidenceDir}`);
    console.log(`Report: ${payload.report}`);
  }

  process.exitCode = payload.exitCode;
}

main().catch((error) => {
  if (error instanceof ToolError) console.error(`ERROR: ${error.message}`);
  else console.error(error?.stack || error?.message || String(error));
  process.exitCode = 1;
});
