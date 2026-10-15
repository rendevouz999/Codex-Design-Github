#!/usr/bin/env node
/**
 * Static enforcement tool for the Web Deck Stage Gate.
 *
 * Reads a generated deck as text and asserts the stage, switching, breakpoint,
 * reduced-motion, print, token, chrome, dependency, navigation, lifecycle,
 * density, motion, accessibility and overflow rules. No browser is launched:
 * the rendered half of the gate belongs to
 * `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs`.
 *
 * Exit codes: 0 PASS (no P0 finding), 2 BLOCKED (any P0 finding),
 * 1 tool or usage error.
 */
import fs from "node:fs/promises";
import path from "node:path";

const STAGE_WIDTH = 1920;
const STAGE_HEIGHT = 1080;

/** Token keys the deck-plan contract fixes, in contract order. */
const TOKEN_KEYS = [
  ["color", ["bg", "surface", "text", "muted", "border", "accent", "accentContrast"]],
  ["type", ["displayFamily", "bodyFamily", "displaySize", "leadSize", "bodySize", "captionSize"]],
  ["space", ["stagePadX", "stagePadY", "blockGap", "itemGap"]],
  ["motion", ["entranceMs", "transitionMs", "staggerMs", "easing", "transition"]],
];

const TRANSITIONS = ["fade", "rise", "slide", "scale", "mask"];

/** Fonts are the only permitted external request. */
const ALLOWED_HOSTS = new Set(["fonts.googleapis.com", "fonts.gstatic.com"]);

/** Any selector that targets a slide. `display` toggling here is the gate's hard fail. */
const SLIDE_SELECTOR = /\.deck-slide(?![-\w])|\[data-deck-index\]/;

/** Selectors that style content inside the scaled stage. */
const STAGE_CONTENT_SELECTOR =
  /\.deck-(slide|stage|headline|eyebrow|rule|support|support-item|media|media-frame|media-clue|media-caption|footnote|reveal)(?![-\w])/;

/** Media features that re-layout a page. None of them may touch stage content. */
const BREAKPOINT_FEATURE =
  /\b(min-width|max-width|min-height|max-height|min-aspect-ratio|max-aspect-ratio|aspect-ratio|orientation|min-device-width|max-device-width)\b|\(\s*(width|height)\s*[:<>=]/i;

/** Density budgets, from `skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md`. */
const DENSITY_BUDGET = {
  speaker_led: {
    minSlides: 12,
    maxSlides: 20,
    maxWords: 25,
    maxHeadlineWords: 8,
    maxSupport: 3,
    minLightRatio: 0.6,
    densePerSlides: 10,
  },
  reading_first: {
    minSlides: 18,
    maxSlides: 32,
    maxWords: 90,
    maxHeadlineWords: 12,
    maxSupport: 5,
    minLightRatio: 0,
    densePerSlides: 4,
  },
};

/**
 * Per-archetype text capacity, derived from the zone geometry in
 * `skills/presentation-deck/resources/seed-packs/web-deck/layouts.md`.
 */
const TEXT_BUDGET = {
  default: { headline: 90, support: 160, supportCount: 6 },
  cover: { headline: 72, support: 90, supportCount: 2 },
  agenda: { headline: 72, support: 48, supportCount: 6 },
  "section-divider": { headline: 60, support: 60, supportCount: 1 },
  data: { headline: 80, support: 110, supportCount: 3 },
  dashboard: { headline: 80, support: 110, supportCount: 6 },
  feature: { headline: 80, support: 150, supportCount: 4 },
  pricing: { headline: 80, support: 150, supportCount: 4 },
  portfolio: { headline: 72, support: 60, supportCount: 6 },
  testimonial: { headline: 240, support: 80, supportCount: 1 },
  closing: { headline: 60, support: 90, supportCount: 2 },
};

/**
 * The cliche blacklist from `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.
 * `anywhere` tokens are unambiguous in a stylesheet or a script. `animation`
 * tokens are ordinary English words, so they are matched only inside keyframe
 * names and `animation` values, where they can only mean the cliche.
 */
const CLICHE_ANYWHERE = [
  ["bounce", "bounce-in or elastic headlines"],
  ["elastic", "bounce-in or elastic headlines"],
  ["wobble", "bounce-in or elastic headlines"],
  ["typewriter", "typewriter or letter-by-letter display type"],
  ["countup", "numbers counting up on every metric"],
  ["count-up", "numbers counting up on every metric"],
  ["parallax", "parallax backgrounds inside a fixed stage"],
  ["confetti", "confetti, sparkle bursts and neon pulse loops"],
  ["sparkle", "confetti, sparkle bursts and neon pulse loops"],
  ["hue-rotate", "gradient hue rotation as a permanent background loop"],
  ["page-curl", "full-stage cube, flip or page-curl rotations"],
  ["kenburns", "a slow zoom on every photograph"],
  ["ken-burns", "a slow zoom on every photograph"],
];
const CLICHE_IN_ANIMATION = [
  ["float", "infinite floating or hovering cards"],
  ["spin", "a spinning or self-drawing logo"],
  ["pulse", "neon pulse loops"],
  ["flip", "full-stage cube, flip or page-curl rotations"],
  ["cube", "full-stage cube, flip or page-curl rotations"],
  ["particle", "mouse-trailing particles and cursor-following glow"],
];

function printHelp() {
  process.stdout.write(
    [
      "Usage: design_brain_web_deck_audit.mjs <deck.html> [options]",
      "",
      "  --plan <file.json>   Audit the deck against its deck plan as well.",
      "  --json               Print a machine-readable result object.",
      "  --help               Print this message.",
      "",
      "Exit codes: 0 PASS, 2 BLOCKED, 1 tool or usage error.",
      "",
    ].join("\n")
  );
}

function parseArgs(argv) {
  const args = { deck: "", plan: "", json: false };
  const rest = argv.slice(2);
  for (let i = 0; i < rest.length; i += 1) {
    const flag = rest[i];
    if (flag === "--help" || flag === "-h") {
      printHelp();
      process.exit(0);
    } else if (flag === "--json") {
      args.json = true;
    } else if (flag === "--plan") {
      args.plan = rest[i + 1] || "";
      i += 1;
    } else if (flag.startsWith("--")) {
      throw new Error(`Unknown flag \`${flag}\`. Run with --help for usage.`);
    } else if (!args.deck) {
      args.deck = flag;
    } else {
      throw new Error(`Unexpected argument \`${flag}\`. Audit one deck at a time.`);
    }
  }
  return args;
}

/* =========================================================================
   Text extraction
   ========================================================================= */

function stripCssComments(css) {
  return css.replace(/\/\*[\s\S]*?\*\//g, " ");
}

function styleText(html) {
  const blocks = [];
  const re = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
  let match;
  while ((match = re.exec(html))) blocks.push(match[1]);
  return blocks.join("\n");
}

/**
 * Executable script text only. A `<script type="application/json">` block is
 * data, and scanning it for motion or navigation evidence would be wrong.
 */
function scriptText(html) {
  const blocks = [];
  const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let match;
  while ((match = re.exec(html))) {
    const typeMatch = /\btype\s*=\s*["']?([^"'\s>]+)/i.exec(match[1] || "");
    const type = typeMatch ? typeMatch[1].toLowerCase() : "";
    if (type && !/^(module|text\/javascript|application\/javascript)$/.test(type)) continue;
    blocks.push(match[2]);
  }
  return blocks.join("\n");
}

/** Flat `selector { declarations }` rules, including rules nested in at-rules. */
function cssRules(css) {
  const rules = [];
  const re = /([^{}]+)\{([^{}]*)\}/g;
  let match;
  while ((match = re.exec(css))) {
    rules.push({ selector: match[1].trim(), body: match[2] });
  }
  return rules;
}

/** Drop every at-rule block, leaving the unconditional rules. */
function stripAtBlocks(css) {
  const out = [];
  let i = 0;
  while (i < css.length) {
    if (css[i] !== "@") {
      out.push(css[i]);
      i += 1;
      continue;
    }
    let j = i;
    while (j < css.length && css[j] !== "{" && css[j] !== ";") j += 1;
    if (css[j] === "{") {
      let depth = 1;
      j += 1;
      while (j < css.length && depth > 0) {
        if (css[j] === "{") depth += 1;
        else if (css[j] === "}") depth -= 1;
        j += 1;
      }
    } else {
      j += 1;
    }
    i = j;
  }
  return out.join("");
}

function atRuleBlocks(css, name) {
  const blocks = [];
  const re = new RegExp(`@${name}([^{]*)\\{`, "gi");
  let match;
  while ((match = re.exec(css))) {
    const start = match.index + match[0].length;
    let depth = 1;
    let i = start;
    while (i < css.length && depth > 0) {
      if (css[i] === "{") depth += 1;
      else if (css[i] === "}") depth -= 1;
      i += 1;
    }
    blocks.push({ condition: match[1].trim(), body: css.slice(start, i - 1) });
  }
  return blocks;
}

/**
 * Declared property names. Custom properties keep their case on purpose: the
 * token contract spells keys camelCase and `--deck-color-accentContrast` is a
 * different property from `--deck-color-accentcontrast`.
 */
function declaredProps(body) {
  const props = new Set();
  for (const part of body.split(";")) {
    const colon = part.indexOf(":");
    if (colon < 0) continue;
    const name = part.slice(0, colon).trim();
    props.add(name.startsWith("--") ? name : name.toLowerCase());
  }
  return props;
}

function declarationValue(body, prop) {
  const re = new RegExp(`(?:^|;)\\s*${prop}\\s*:\\s*([^;]+)`, "i");
  const match = re.exec(body);
  return match ? match[1].trim() : "";
}

/** Elements carrying a class, with their attribute text and inner markup. */
function elementsByClass(html, className) {
  const found = [];
  const re = new RegExp(`<([a-z][a-z0-9]*)\\b([^>]*\\bclass\\s*=\\s*"[^"]*\\b${className}\\b[^"]*"[^>]*)>`, "gi");
  let match;
  while ((match = re.exec(html))) {
    const tag = match[1].toLowerCase();
    const attrs = match[2];
    const start = match.index + match[0].length;
    const inner = innerMarkup(html, tag, start);
    found.push({ tag, attrs, start, inner });
  }
  return found;
}

/** Inner markup of an element, by counting same-tag opens and closes. */
function innerMarkup(html, tag, start) {
  const re = new RegExp(`</?${tag}\\b[^>]*>`, "gi");
  re.lastIndex = start;
  let depth = 1;
  let match;
  while ((match = re.exec(html))) {
    if (match[0][1] === "/") depth -= 1;
    else if (!/\/>\s*$/.test(match[0])) depth += 1;
    if (depth === 0) return html.slice(start, match.index);
  }
  return html.slice(start);
}

function textOf(markup) {
  return markup
    .replace(/<[^>]*>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#\d+;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function wordCount(value) {
  const trimmed = value.trim();
  return trimmed ? trimmed.split(/\s+/).length : 0;
}

function attrValue(attrs, name) {
  const match = new RegExp(`\\b${name}\\s*=\\s*"([^"]*)"`, "i").exec(attrs);
  return match ? match[1] : null;
}

function hasAttr(attrs, name) {
  return new RegExp(`\\b${name}\\b`, "i").test(attrs);
}

function clip(value, limit = 140) {
  const flat = String(value).replace(/\s+/g, " ").trim();
  return flat.length > limit ? `${flat.slice(0, limit - 3)}...` : flat;
}

/* =========================================================================
   Audit
   ========================================================================= */

function auditDeck(html, plan) {
  const findings = [];
  const add = (id, severity, area, message, evidence, repair) => {
    findings.push({ id, severity, area, message, evidence: clip(evidence), repair });
  };

  const rawStyle = styleText(html);
  const css = stripCssComments(rawStyle);
  const topCss = stripAtBlocks(css);
  const script = scriptText(html);
  const allRules = cssRules(css);
  const topRules = cssRules(topCss);

  /* --- Stage ------------------------------------------------------------ */

  const stages = elementsByClass(html, "deck-stage");
  const viewports = elementsByClass(html, "deck-viewport");
  if (!stages.length) {
    add(
      "stage-present",
      "P0",
      "stage",
      "No `.deck-stage` element in the deck.",
      "class=\"deck-stage\" not found",
      "Wrap the slides in `<div class=\"deck-viewport\"><div class=\"deck-stage\">`, the structure `stage-base.css` and `deck-runtime.js` both target."
    );
  } else if (!viewports.length) {
    add(
      "stage-present",
      "P0",
      "stage",
      "The stage has no `.deck-viewport` frame around it.",
      stages[0].attrs,
      "Add the fixed full-window `<div class=\"deck-viewport\">` wrapper so the stage has a frame to be centred and letterboxed inside."
    );
  }

  const stageRules = topRules.filter((rule) => /\.deck-stage(?![-\w])/.test(rule.selector));
  const stageProps = new Map();
  for (const rule of stageRules) {
    for (const prop of ["width", "height", "transform-origin"]) {
      const value = declarationValue(rule.body, prop);
      if (value) stageProps.set(prop, value);
    }
  }
  const stageWidth = stageProps.get("width") || "";
  const stageHeight = stageProps.get("height") || "";
  if (stageWidth !== `${STAGE_WIDTH}px` || stageHeight !== `${STAGE_HEIGHT}px`) {
    add(
      "stage-authored-size",
      "P0",
      "stage",
      `The stage is not authored at ${STAGE_WIDTH}x${STAGE_HEIGHT} px.`,
      `width: ${stageWidth || "not declared"}; height: ${stageHeight || "not declared"}`,
      `Declare \`width: ${STAGE_WIDTH}px\` and \`height: ${STAGE_HEIGHT}px\` on \`.deck-stage\`. A percentage, \`vw\`, \`vh\` or \`auto\` stage size reflows the slide instead of scaling it.`
    );
  }

  const hasOrigin = /transform-origin\s*:\s*0\s+0/.test(topCss);
  const hasUniformScale = /Math\.min\s*\(/.test(script) && /1920/.test(script) && /1080/.test(script);
  const hasResize = /addEventListener\s*\(\s*["']resize["']/.test(script);
  if (!hasOrigin || !hasUniformScale || !hasResize) {
    add(
      "stage-uniform-scale",
      "P0",
      "stage",
      "The uniform fit transform is incomplete.",
      `transform-origin: 0 0 ${hasOrigin ? "present" : "missing"}; Math.min fit ${hasUniformScale ? "present" : "missing"}; resize listener ${hasResize ? "present" : "missing"}`,
      `Set \`transform-origin: 0 0\` on the stage and compute \`scale = Math.min(innerWidth / ${STAGE_WIDTH}, innerHeight / ${STAGE_HEIGHT})\` with an explicit centring translate, recomputed on \`resize\`.`
    );
  }

  /* --- Slide switching -------------------------------------------------- */

  const displayToggles = allRules.filter(
    (rule) => SLIDE_SELECTOR.test(rule.selector) && /display\s*:\s*none/i.test(rule.body)
  );
  const scriptDisplay = /\.style\.display\s*=/.test(script) || /setProperty\s*\(\s*["']display["']/.test(script);
  if (displayToggles.length || scriptDisplay) {
    add(
      "slide-switch-no-display-toggle",
      "P0",
      "switching",
      "Slide visibility is toggled with `display`.",
      displayToggles.length ? `${displayToggles[0].selector} { ${displayToggles[0].body} }` : "script assigns style.display",
      "Switch slides with `visibility`, `opacity` and `pointer-events` only. A later `display: flex` or `display: grid` layout rule overrides a `display: none` hide and reveals every slide at once."
    );
  }

  const slideRules = topRules.filter((rule) => SLIDE_SELECTOR.test(rule.selector));
  const slideProps = new Set();
  for (const rule of slideRules) for (const prop of declaredProps(rule.body)) slideProps.add(prop);
  const missingSwitch = ["visibility", "opacity", "pointer-events"].filter((prop) => !slideProps.has(prop));
  if (missingSwitch.length) {
    add(
      "slide-switch-technique",
      "P0",
      "switching",
      "The slide switch does not declare the full visibility technique.",
      `missing on slide rules: ${missingSwitch.join(", ")}`,
      "Declare `visibility`, `opacity` and `pointer-events` on `.deck-slide` and flip all three on `.is-active`. `opacity: 0` alone leaves an inactive slide hit-testable and announced."
    );
  }

  /* --- Breakpoints ------------------------------------------------------ */

  for (const block of atRuleBlocks(css, "media")) {
    if (!BREAKPOINT_FEATURE.test(block.condition)) continue;
    const offending = cssRules(block.body).filter((rule) => STAGE_CONTENT_SELECTOR.test(rule.selector));
    if (!offending.length) continue;
    add(
      "no-stage-breakpoints",
      "P0",
      "stage",
      "A viewport breakpoint re-layouts content inside the scaled stage.",
      `@media ${block.condition} { ${offending[0].selector} { ${offending[0].body} } }`,
      "Delete the breakpoint. Stage geometry is authored once at stage size and fitted by the single uniform transform; a breakpoint inside the stage reflows the slide and breaks the 16:9 contract."
    );
    break;
  }

  /* --- Reduced motion --------------------------------------------------- */

  const reducedBlocks = atRuleBlocks(css, "media").filter((block) =>
    /prefers-reduced-motion\s*:\s*reduce/i.test(block.condition)
  );
  const reducedDeclarations = reducedBlocks.reduce(
    (total, block) => total + (block.body.match(/[a-z-]+\s*:/gi) || []).length,
    0
  );
  if (!reducedBlocks.length || reducedDeclarations < 3) {
    add(
      "reduced-motion-block",
      "P0",
      "motion",
      "The mandatory reduced-motion block is missing or empty.",
      reducedBlocks.length ? `${reducedDeclarations} declaration(s) in the block` : "no @media (prefers-reduced-motion: reduce) rule in the stylesheet",
      "Add `@media (prefers-reduced-motion: reduce)` and remove entrance animations, transitions and loops inside it, leaving every reveal at its final visible state."
    );
  }
  if (reducedBlocks.length && !/prefers-reduced-motion/.test(script)) {
    add(
      "reduced-motion-block",
      "P0",
      "motion",
      "The runtime never checks the reduced-motion query, so the CSS block is bypassed at runtime.",
      "script has no matchMedia(\"(prefers-reduced-motion: reduce)\") check",
      "Read `matchMedia(\"(prefers-reduced-motion: reduce)\")` in the runtime and jump straight to the end state when it matches."
    );
  }

  /* --- Print ------------------------------------------------------------ */

  const pageBlocks = atRuleBlocks(css, "page");
  const pageBody = pageBlocks.map((block) => block.body).join(" ");
  const sizeValue = declarationValue(pageBody, "size");
  const marginValue = declarationValue(pageBody, "margin");
  if (!pageBlocks.length || !/1920px\s+1080px/.test(sizeValue) || !/^0(\w*)?$/.test(marginValue.replace(/\s+/g, ""))) {
    add(
      "print-page-setup",
      "P0",
      "print",
      "The print page box is missing or not the authored stage size.",
      pageBlocks.length ? `@page { size: ${sizeValue || "not declared"}; margin: ${marginValue || "not declared"} }` : "no @page rule in the stylesheet",
      `Add \`@page { size: ${STAGE_WIDTH}px ${STAGE_HEIGHT}px; margin: 0 }\` so browser print produces one full-bleed slide per page.`
    );
  }

  const printBlocks = atRuleBlocks(css, "media").filter((block) => /\bprint\b/i.test(block.condition));
  const printRules = printBlocks.flatMap((block) => cssRules(block.body));
  const breaksSlides = printRules.some(
    (rule) => SLIDE_SELECTOR.test(rule.selector) && /break-after\s*:\s*page/i.test(rule.body)
  );
  const forcesVisible = printRules.some(
    (rule) => SLIDE_SELECTOR.test(rule.selector) && /visibility\s*:\s*visible/i.test(rule.body)
  );
  if (!printBlocks.length || !breaksSlides || !forcesVisible) {
    add(
      "print-slide-breaks",
      "P0",
      "print",
      "The print block does not force one slide per page.",
      `@media print ${printBlocks.length ? "present" : "missing"}; break-after: page on slides ${breaksSlides ? "present" : "missing"}; slides forced visible ${forcesVisible ? "present" : "missing"}`,
      "In `@media print`, drop the stage transform, set `visibility: visible` and `break-after: page` on every slide, and hide all chrome. Without it print yields one cropped page."
    );
  }

  /* --- Token layer ------------------------------------------------------ */

  const rootRules = allRules.filter((rule) => /(^|,)\s*:root\b/.test(rule.selector));
  const rootProps = new Set();
  for (const rule of rootRules) for (const prop of declaredProps(rule.body)) rootProps.add(prop);
  const missingTokens = [];
  for (const [group, keys] of TOKEN_KEYS) {
    for (const key of keys) {
      const name = `--deck-${group}-${key}`;
      if (!rootProps.has(name)) missingTokens.push(name);
    }
  }
  if (missingTokens.length) {
    add(
      "token-layer-root",
      "P0",
      "tokens",
      `The token layer is missing ${missingTokens.length} contract token(s).`,
      missingTokens.join(", "),
      "Declare every `--deck-<group>-<key>` custom property on `:root`, generated from the deck-plan `tokens` object, so a palette or type change is one edit."
    );
  }

  /* --- Chrome ----------------------------------------------------------- */

  if (stages.length) {
    const inside = ["deck-chrome", "deck-progress", "deck-counter", "deck-controls", "deck-notes", "deck-live"].filter(
      (name) => new RegExp(`class\\s*=\\s*"[^"]*\\b${name}\\b`).test(stages[0].inner)
    );
    if (inside.length) {
      add(
        "chrome-outside-stage",
        "P0",
        "chrome",
        "Deck chrome is a child of the scaled stage.",
        `inside .deck-stage: ${inside.join(", ")}`,
        "Move the chrome layer out of `.deck-stage` and into its own fixed layer. Chrome inside the stage is multiplied by the fit scale and goes illegible on a laptop viewport."
      );
    }
  }

  /* --- Dependencies ----------------------------------------------------- */

  const hosts = new Set();
  const urlRe = /https?:\/\/([^/"'\s)<>]+)/g;
  let urlMatch;
  while ((urlMatch = urlRe.exec(html))) hosts.add(urlMatch[1].toLowerCase());
  const foreignHosts = [...hosts].filter((host) => !ALLOWED_HOSTS.has(host));
  const remoteScripts = /<script\b[^>]*\bsrc\s*=/i.test(html);
  const remoteStyles = [...html.matchAll(/<link\b[^>]*>/gi)]
    .filter((match) => /stylesheet/i.test(match[0]))
    .filter((match) => {
      const href = attrValue(match[0], "href") || "";
      const host = /https?:\/\/([^/"'\s]+)/.exec(href);
      return host ? !ALLOWED_HOSTS.has(host[1].toLowerCase()) : false;
    });
  if (foreignHosts.length || remoteScripts || remoteStyles.length || /@import/i.test(css)) {
    add(
      "external-requests-fonts-only",
      "P0",
      "dependencies",
      "The deck makes an external request for something other than a font.",
      [
        foreignHosts.length ? `hosts: ${foreignHosts.join(", ")}` : "",
        remoteScripts ? "a <script src> tag is present" : "",
        remoteStyles.length ? `remote stylesheet: ${attrValue(remoteStyles[0][0], "href")}` : "",
        /@import/i.test(css) ? "the stylesheet uses @import" : "",
      ]
        .filter(Boolean)
        .join("; "),
      `Inline every script and stylesheet. A web deck has zero runtime dependencies and the only permitted external request is a font from ${[...ALLOWED_HOSTS].join(" or ")}.`
    );
  }

  const buildMarkers = [
    [/type\s*=\s*["']importmap["']/i, "an import map"],
    [/sourceMappingURL/i, "a source map reference"],
    [/<base\b[^>]*href/i, "a <base href> tag"],
    [/\b__webpack_|\bSystem\.import\b|\bdata-vite\b/, "a bundler artifact"],
    [/\brequire\s*\(\s*["']/, "a CommonJS require call"],
  ].filter(([pattern]) => pattern.test(html));
  if (buildMarkers.length) {
    add(
      "no-build-step-artifacts",
      "P0",
      "dependencies",
      "The deck carries a build-step artifact.",
      buildMarkers.map(([, label]) => label).join(", "),
      "Deliver a file that runs from the filesystem as delivered. No bundler output, no import map, no base href, no source map; a deck that needs a dev server is not delivered."
    );
  }

  /* --- Navigation, deep link, lifecycle --------------------------------- */

  const navKeys = ["ArrowRight", "ArrowLeft", "PageDown", "PageUp", "Home", "End"];
  const missingKeys = navKeys.filter((key) => !script.includes(key));
  const hasKeydown = /addEventListener\s*\(\s*["']keydown["']/.test(script);
  const hasWheel = /addEventListener\s*\(\s*["']wheel["']/.test(script);
  const hasNavHooks = /data-deck-nav/.test(script) && /data-deck-nav/.test(html);
  if (missingKeys.length || !hasKeydown || !hasWheel || !hasNavHooks) {
    add(
      "navigation-wiring",
      "P0",
      "runtime",
      "The navigation wiring is incomplete.",
      [
        missingKeys.length ? `missing keys: ${missingKeys.join(", ")}` : "",
        hasKeydown ? "" : "no keydown listener",
        hasWheel ? "" : "no wheel listener",
        hasNavHooks ? "" : "no [data-deck-nav] control wiring",
      ]
        .filter(Boolean)
        .join("; "),
      "Bind ArrowRight, ArrowLeft, PageDown, PageUp, Space, Home and End, a debounced wheel step, coarse-pointer tap zones, and the `[data-deck-nav]` chrome controls."
    );
  }

  const hasReplaceState = /replaceState/.test(script);
  const hasHashRead = /location\.hash/.test(script);
  const hasPushState = /pushState/.test(script);
  if (!hasReplaceState || !hasHashRead || hasPushState) {
    add(
      "deep-link-wiring",
      "P0",
      "runtime",
      "Deep linking is missing or poisons the back button.",
      `location.hash read ${hasHashRead ? "present" : "missing"}; replaceState ${hasReplaceState ? "present" : "missing"}; pushState ${hasPushState ? "present (forbidden)" : "absent"}`,
      "Read `#<n>` as a 1-based slide number on load and call `history.replaceState` on every slide change. `pushState` adds one history entry per slide and breaks the back button."
    );
  }

  const reasons = ["init", "key", "pointer", "wheel", "api"];
  const missingReasons = reasons.filter((reason) => !new RegExp(`["']${reason}["']`).test(script));
  const hasEvent = /deckslidechange/.test(script);
  const hasEventShape = /bubbles/.test(script) && /composed/.test(script) && /previousIndex/.test(script);
  if (!hasEvent || !hasEventShape || missingReasons.length) {
    add(
      "lifecycle-event",
      "P0",
      "runtime",
      "The per-slide lifecycle event does not match the contract.",
      `deckslidechange ${hasEvent ? "present" : "missing"}; payload shape ${hasEventShape ? "present" : "incomplete"}; missing reasons: ${missingReasons.join(", ") || "none"}`,
      "Dispatch a `deckslidechange` CustomEvent with `bubbles: true`, `composed: true` and detail `{ index, previousIndex, total, reason }`, where reason is init, key, pointer, wheel or api."
    );
  }

  /* --- Slides, density, motion, accessibility, overflow ----------------- */

  const slides = elementsByClass(html, "deck-slide").map((slide) => {
    const archetype =
      attrValue(slide.attrs, "data-deck-archetype") ||
      (/\bdeck-slide--([a-z-]+)\b/.exec(attrValue(slide.attrs, "class") || "") || [])[1] ||
      "";
    const headline = textOf((elementsByClass(slide.inner, "deck-headline")[0] || { inner: "" }).inner);
    const support = elementsByClass(slide.inner, "deck-support-item").map((item) => textOf(item.inner));
    const footnotes = elementsByClass(slide.inner, "deck-footnote").map((item) => textOf(item.inner));
    const steps = [...slide.inner.matchAll(/data-deck-step-id\s*=\s*"([^"]*)"/g)].map((match) => match[1]);
    const revealModifiers = [...slide.inner.matchAll(/\bdeck-reveal--([a-z]+)\b/g)].map((match) => match[1]);
    const slideTransition = (/\bdeck-slide--(fade|rise|slide|scale|mask)\b/.exec(attrValue(slide.attrs, "class") || "") || [])[1] || "";
    return {
      attrs: slide.attrs,
      inner: slide.inner,
      archetype,
      density: attrValue(slide.attrs, "data-deck-density") || "",
      headline,
      support,
      footnotes,
      steps,
      revealModifiers,
      slideTransition,
    };
  });

  if (plan) {
    const budget = DENSITY_BUDGET[plan.densityMode];
    const plannedCount = Array.isArray(plan.slides) ? plan.slides.length : 0;
    if (slides.length !== plannedCount) {
      add(
        "slide-count-budget",
        "P1",
        "density",
        "The deck and its plan disagree on slide count.",
        `deck ${slides.length}, plan ${plannedCount}`,
        "Rebuild the deck from the plan, or update the plan. The artifact and the plan are one deliverable and a mismatch is a delivery defect."
      );
    } else if (budget && (slides.length < budget.minSlides || slides.length > budget.maxSlides)) {
      add(
        "slide-count-budget",
        "P1",
        "density",
        `Slide count sits outside the \`${plan.densityMode}\` budget.`,
        `${slides.length} slides, budget ${budget.minSlides} to ${budget.maxSlides}`,
        `Bring the deck inside ${budget.minSlides} to ${budget.maxSlides} slides for \`${plan.densityMode}\`, or change \`densityMode\` and rebuild the content to match it.`
      );
    }

    if (budget) {
      for (const slide of slides) {
        const onStage = [slide.headline, ...slide.support, ...slide.footnotes].join(" ");
        const words = wordCount(onStage);
        if (words > budget.maxWords) {
          add(
            "slide-density-budget",
            "P1",
            "density",
            `Slide \`${slide.archetype}\` carries more on-stage words than \`${plan.densityMode}\` allows.`,
            `${words} words, budget ${budget.maxWords}: ${onStage}`,
            `Cut to ${budget.maxWords} on-stage words or split the slide. One claim per slide; a second claim is a second slide.`
          );
        }
        // A testimonial headline is the quote itself, governed by the quote rule
        // rather than the headline word cap.
        if (slide.archetype !== "testimonial" && wordCount(slide.headline) > budget.maxHeadlineWords) {
          add(
            "slide-density-budget",
            "P1",
            "density",
            `Headline on \`${slide.archetype}\` is longer than \`${plan.densityMode}\` allows.`,
            `${wordCount(slide.headline)} words: ${slide.headline}`,
            `Rewrite the headline as a takeaway in ${budget.maxHeadlineWords} words or fewer.`
          );
        }
        if (slide.support.length > budget.maxSupport) {
          add(
            "slide-density-budget",
            "P1",
            "density",
            `Slide \`${slide.archetype}\` carries more support items than \`${plan.densityMode}\` allows.`,
            `${slide.support.length} items, budget ${budget.maxSupport}`,
            `Reduce to ${budget.maxSupport} support items. Evidence, not restatement; a bullet that repeats the headline goes.`
          );
        }
      }

      const light = slides.filter((slide) => slide.density === "light").length;
      const dense = slides.filter((slide) => slide.density === "dense").length;
      if (budget.minLightRatio && slides.length && light / slides.length < budget.minLightRatio) {
        add(
          "slide-density-budget",
          "P1",
          "density",
          `Too few light slides for \`${plan.densityMode}\`.`,
          `${light} of ${slides.length} light, budget at least ${Math.round(budget.minLightRatio * 100)} percent`,
          "Mark and build more light slides. A deck with no rest slides flattens pace and exhausts the room."
        );
      }
      const denseAllowance = Math.max(1, Math.floor(slides.length / budget.densePerSlides));
      if (dense > denseAllowance) {
        add(
          "slide-density-budget",
          "P1",
          "density",
          `Too many dense slides for \`${plan.densityMode}\`.`,
          `${dense} dense slides, allowance ${denseAllowance}`,
          `Split the surplus dense slides, and give every remaining dense slide a light neighbour.`
        );
      }
    }

    for (const plannedSlide of Array.isArray(plan.slides) ? plan.slides : []) {
      const slide = slides[plannedSlide.index];
      if (!slide) continue;
      const order = Array.isArray(plannedSlide.revealOrder) ? plannedSlide.revealOrder : [];
      const missing = order.filter((step) => !slide.steps.includes(step));
      if (missing.length) {
        add(
          "reveal-order-agreement",
          "P1",
          "motion",
          `Reveal steps planned for slide ${plannedSlide.index + 1} are not in the artifact.`,
          `missing step ids: ${missing.join(", ")}`,
          "Emit a `data-deck-step-id` for every id in the slide `revealOrder`, or drop the id from the plan. A step in one and not the other is a reveal defect."
        );
      }
    }
  }

  const stageTransition = /data-deck-transition\s*=\s*"([^"]*)"/.exec(html);
  const stageFamilyClass = /\bdeck-stage--(fade|rise|slide|scale|mask)\b/.exec(html);
  if (!stageTransition || !TRANSITIONS.includes(stageTransition[1]) || !stageFamilyClass) {
    add(
      "motion-transition-family",
      "P1",
      "motion",
      "The deck does not declare one transition family on the stage.",
      `data-deck-transition ${stageTransition ? stageTransition[1] : "missing"}; deck-stage--<family> class ${stageFamilyClass ? "present" : "missing"}`,
      `Set one \`deck-stage--<family>\` class and the matching \`data-deck-transition\` attribute from \`tokens.motion.transition\` (${TRANSITIONS.join(", ")}).`
    );
  }

  if (slides.length >= 6) {
    const signatures = new Set(
      slides.map((slide) => `${slide.slideTransition}|${[...new Set(slide.revealModifiers)].sort().join(",")}`)
    );
    if (signatures.size <= 1) {
      add(
        "motion-entrance-variety",
        "P1",
        "motion",
        "Every slide arrives with an identical entrance.",
        `${slides.length} slides, 1 distinct entrance signature: ${[...signatures][0]}`,
        "Vary entrance behavior by slide role: a cover arrives differently from a data slide, and a divider resets energy instead of repeating it. One verb repeated for the whole deck is motion monotone."
      );
    }
  }

  const animationSurface = [
    ...(css.match(/@keyframes[^{]*/gi) || []),
    ...(css.match(/animation(?:-name)?\s*:[^;]*/gi) || []),
    ...(script.match(/animate\s*\([^)]*/gi) || []),
  ].join(" ");
  const motionText = `${css}\n${script}`;
  const planForbidden = plan && plan.motionSignature ? plan.motionSignature.forbidden || [] : [];
  for (const [token, label] of CLICHE_ANYWHERE) {
    if (!motionText.toLowerCase().includes(token)) continue;
    add(
      "motion-forbidden-cliche",
      "P1",
      "motion",
      `A blacklisted motion cliche is present: ${label}.`,
      `token \`${token}\` found in the stylesheet or the runtime${planForbidden.length ? "; the plan lists it under motionSignature.forbidden" : ""}`,
      "Remove the move and replace it with a gesture from the deck motion signature. A cliche belongs in `motionSignature.forbidden`, not in the deck."
    );
  }
  for (const [token, label] of CLICHE_IN_ANIMATION) {
    if (!animationSurface.toLowerCase().includes(token)) continue;
    add(
      "motion-forbidden-cliche",
      "P1",
      "motion",
      `A blacklisted motion cliche is present: ${label}.`,
      `token \`${token}\` found in a keyframe name or an animation value`,
      "Remove the move and replace it with a gesture from the deck motion signature. A cliche belongs in `motionSignature.forbidden`, not in the deck."
    );
  }

  /* --- Accessibility ---------------------------------------------------- */

  const runtimeLabels = /aria-roledescription/.test(script) && /aria-label/.test(script);
  const unlabelled = slides.filter(
    (slide) =>
      !(hasAttr(slide.attrs, "aria-roledescription") || hasAttr(slide.attrs, "role")) ||
      !(attrValue(slide.attrs, "aria-label") || attrValue(slide.attrs, "aria-labelledby"))
  );
  if (slides.length && unlabelled.length && !runtimeLabels) {
    add(
      "a11y-slide-labelling",
      "P1",
      "accessibility",
      `${unlabelled.length} slide region(s) carry no role or accessible name.`,
      unlabelled[0].attrs,
      "Give every slide `role=\"group\"`, `aria-roledescription=\"slide\"` and an accessible name, and set `aria-hidden` plus `inert` on the inactive slides."
    );
  }

  const liveInMarkup = /aria-live\s*=/.test(html);
  const liveInScript = /aria-live/.test(script);
  if (!liveInMarkup && !liveInScript) {
    add(
      "a11y-live-region",
      "P1",
      "accessibility",
      "The deck has no live region, so a slide change is never announced.",
      "no aria-live attribute in the markup or the runtime",
      "Add a visually hidden `.deck-live` element with `role=\"status\"` and `aria-live=\"polite\"`, and write the slide position and headline into it on every change."
    );
  }

  const positiveTabindex = /tabindex\s*=\s*"[1-9]/.test(html);
  const tabIntercept = /["']Tab["']/.test(script) || /keyCode\s*===?\s*9/.test(script);
  if (positiveTabindex || tabIntercept) {
    add(
      "a11y-keyboard-trap",
      "P1",
      "accessibility",
      "The deck contains a keyboard trap pattern.",
      positiveTabindex ? "a positive tabindex is present" : "the runtime intercepts the Tab key",
      "Never use a positive `tabindex` and never intercept `Tab`. Keep inactive slides out of the tab order with `inert` instead of trapping focus."
    );
  }

  /* --- Overflow risk ---------------------------------------------------- */

  for (const slide of slides) {
    const budget = TEXT_BUDGET[slide.archetype] || TEXT_BUDGET.default;
    if (slide.headline.length > budget.headline) {
      add(
        "overflow-text-budget",
        "P1",
        "overflow",
        `The \`${slide.archetype}\` headline is longer than the archetype budget.`,
        `${slide.headline.length} characters, budget ${budget.headline}: ${slide.headline}`,
        `Trim the headline to ${budget.headline} characters. Past that the display line wraps past its authored zone and overflows the stage.`
      );
    }
    const long = slide.support.find((item) => item.length > budget.support);
    if (long) {
      add(
        "overflow-text-budget",
        "P1",
        "overflow",
        `A support item on \`${slide.archetype}\` exceeds the archetype budget.`,
        `${long.length} characters, budget ${budget.support}: ${long}`,
        `Trim the item to ${budget.support} characters or move the detail into the slide notes.`
      );
    }
    if (slide.support.length > budget.supportCount) {
      add(
        "overflow-text-budget",
        "P1",
        "overflow",
        `\`${slide.archetype}\` carries more support items than its zones hold.`,
        `${slide.support.length} items, zone capacity ${budget.supportCount}`,
        `Reduce to ${budget.supportCount} items or split the slide. Rows beyond the authored capacity run past the stage safe area.`
      );
    }
  }

  const bounds = { left: STAGE_WIDTH, right: STAGE_WIDTH, top: STAGE_HEIGHT, bottom: STAGE_HEIGHT };
  const positioned = [
    ...topRules
      .filter((rule) => /position\s*:\s*absolute/i.test(rule.body) && STAGE_CONTENT_SELECTOR.test(rule.selector))
      .map((rule) => ({ where: rule.selector, body: rule.body })),
    ...[...html.matchAll(/style\s*=\s*"([^"]*)"/g)]
      .filter((match) => /position\s*:\s*absolute/i.test(match[1]))
      .map((match) => ({ where: "inline style", body: match[1] })),
  ];
  for (const entry of positioned) {
    for (const side of ["left", "right", "top", "bottom"]) {
      const value = declarationValue(entry.body, side);
      const px = /^(-?[\d.]+)px$/.exec(value.trim());
      if (!px) continue;
      const amount = Number(px[1]);
      if (amount >= 0 && amount <= bounds[side]) continue;
      add(
        "overflow-absolute-bounds",
        "P1",
        "overflow",
        "An absolutely positioned element sits outside the stage box.",
        `${entry.where} { ${side}: ${value} } against a ${STAGE_WIDTH}x${STAGE_HEIGHT} stage`,
        `Keep every authored coordinate inside 0 to ${STAGE_WIDTH} horizontally and 0 to ${STAGE_HEIGHT} vertically. Content outside the box is clipped by the stage, not letterboxed.`
      );
      break;
    }
  }

  const globalMediaCap = /(^|\})[^{}]*\b(img|video|canvas|svg)\b[^{}]*\{[^}]*max-width\s*:/i.test(topCss);
  const mediaTags = [...html.matchAll(/<(img|video|iframe)\b([^>]*)>/gi)];
  for (const match of mediaTags) {
    const attrs = match[2] || "";
    const constrained =
      globalMediaCap ||
      /\bwidth\s*=/.test(attrs) ||
      /\bheight\s*=/.test(attrs) ||
      /max-width\s*:/.test(attrs) ||
      /\bclass\s*=/.test(attrs);
    if (constrained) continue;
    add(
      "overflow-media-constraint",
      "P1",
      "overflow",
      `A <${match[1].toLowerCase()}> has no size constraint.`,
      clip(match[0]),
      "Give the element an authored frame: a width and height, a `max-width`, or a class that constrains it. Unconstrained media paints at intrinsic size and overflows the stage."
    );
  }

  return findings;
}

/* =========================================================================
   Reporting
   ========================================================================= */

function markdownReport(result) {
  const lines = [
    "# Web Deck Static Audit",
    "",
    `- Status: ${result.status}`,
    `- Deck: \`${result.deck}\``,
    `- Plan: ${result.plan ? `\`${result.plan}\`` : "not supplied, plan-relative checks skipped"}`,
    `- Findings: ${result.p0Count} P0, ${result.p1Count} P1`,
  ];
  if (!result.findings.length) {
    lines.push(
      "",
      "No findings. The stage, switching, runtime, dependency and print rules hold.",
      "Run `skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` next: a static PASS is half the gate.",
    );
  } else {
    for (const finding of result.findings) {
      lines.push(
        "",
        `## ${finding.severity} - ${finding.id}`,
        "",
        `- Area: ${finding.area}`,
        `- Defect: ${finding.message}`,
        `- Evidence: ${finding.evidence}`,
        `- Repair: ${finding.repair}`,
      );
    }
    if (result.p0Count) {
      lines.push("", "A P0 finding blocks delivery. Repair the named rule, not the visible symptom, and rerun this tool.");
    }
  }
  return `${lines.join("\n")}\n`;
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    return 1;
  }
  if (!args.deck) {
    process.stderr.write("Missing the deck path. Usage: design_brain_web_deck_audit.mjs <deck.html> [--plan <plan.json>] [--json]\n");
    return 1;
  }

  const deckPath = path.resolve(args.deck);
  let html;
  try {
    html = await fs.readFile(deckPath, "utf8");
  } catch (error) {
    process.stderr.write(`Could not read the deck \`${deckPath}\`: ${error.message}\n`);
    return 1;
  }

  let plan = null;
  if (args.plan) {
    try {
      plan = JSON.parse(await fs.readFile(path.resolve(args.plan), "utf8"));
    } catch (error) {
      process.stderr.write(`Could not read the deck plan \`${args.plan}\`: ${error.message}\n`);
      return 1;
    }
  }

  const findings = auditDeck(html, plan);
  const order = { P0: 0, P1: 1 };
  findings.sort((a, b) => order[a.severity] - order[b.severity]);
  const p0Count = findings.filter((finding) => finding.severity === "P0").length;
  const result = {
    tool: "design_brain_web_deck_audit",
    status: p0Count ? "BLOCKED" : "PASS",
    deck: deckPath,
    plan: args.plan ? path.resolve(args.plan) : "",
    bytes: Buffer.byteLength(html, "utf8"),
    findingCount: findings.length,
    p0Count,
    p1Count: findings.length - p0Count,
    findings,
  };

  process.stdout.write(args.json ? `${JSON.stringify(result, null, 2)}\n` : markdownReport(result));
  return p0Count ? 2 : 0;
}

main().then(
  (code) => {
    process.exit(code);
  },
  (error) => {
    process.stderr.write(`design_brain_web_deck_audit failed: ${error && error.stack ? error.stack : error}\n`);
    process.exit(1);
  }
);
