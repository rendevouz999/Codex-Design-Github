#!/usr/bin/env node
/**
 * Build a single-file web deck from a Brain Design deck plan.
 *
 * Reads the canonical runtime kit from `skills/presentation-deck/resources/web-deck/`, validates the
 * plan against `deck-plan-schema.json`, and emits one self-contained HTML file
 * with `stage-base.css` and `deck-runtime.js` inlined verbatim.
 *
 * Exit codes: 0 PASS, 2 BLOCKED (plan or contract defect), 1 tool or usage error.
 */
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const KIT_FILES = [
  ["css", "stage-base.css"],
  ["js", "deck-runtime.js"],
  ["schema", "deck-plan-schema.json"],
];
const KIT_WAIT_ATTEMPTS = 12;
const KIT_WAIT_MS = 400;

const PLAN_SCHEMA_ID = "design-brain.web-deck.deck-plan.v1";
const STAGE_WIDTH = 1920;
const STAGE_HEIGHT = 1080;

/** `tokens.<group>` numeric values are serialized with these CSS units. */
const TOKEN_UNITS = { color: "", type: "px", space: "px", motion: "ms" };
const TOKEN_GROUPS = ["color", "type", "space", "motion"];

/** Transition families, mirroring the `tokens.motion.transition` enum. */
const TRANSITIONS = ["fade", "rise", "slide", "scale", "mask"];

/** Reveal primitives, mirroring the `.deck-reveal--*` modifiers in `stage-base.css`. */
const ENTRANCE_PRIMITIVES = ["rise", "scale", "slide", "blur", "mask"];

/** `stage-base.css` declares twelve explicit stagger slots, `data-deck-step` 0 to 11. */
const MAX_REVEAL_STEPS = 12;

/**
 * Per-archetype transition override. A divider resets energy and a data slide
 * stays calm, so entrance behavior varies with slide role instead of repeating
 * one move for the whole deck. `null` inherits the deck transition family.
 */
const ARCHETYPE_TRANSITION = {
  cover: "scale",
  "section-divider": "mask",
  data: "fade",
  dashboard: "fade",
  testimonial: "fade",
  closing: "rise",
};

/** Support-item step id prefixes accepted from `revealOrder`. */
const SUPPORT_STEP_PREFIXES = ["item", "card", "metric", "node", "panel"];

/** Generic font families that never need a web font request. */
const GENERIC_FAMILIES = new Set([
  "serif",
  "sans-serif",
  "monospace",
  "cursive",
  "fantasy",
  "system-ui",
  "ui-serif",
  "ui-sans-serif",
  "ui-monospace",
  "-apple-system",
]);

function repoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
}

function printHelp() {
  process.stdout.write(
    [
      "Usage: design_brain_web_deck_plan.mjs [options]",
      "",
      "  --plan <file.json>   Build from an existing deck plan.",
      "  --demo               Synthesize a valid demo deck plan and build it.",
      "  --out <file.html>    Output path for the generated deck.",
      "  --json               Print a machine-readable result object.",
      "  --dry-run            Validate and report without writing anything.",
      "  --help               Print this message.",
      "",
      "Exit codes: 0 PASS, 2 BLOCKED, 1 tool or usage error.",
      "",
    ].join("\n")
  );
}

function parseArgs(argv) {
  const args = { plan: "", demo: false, out: "", json: false, dryRun: false };
  const rest = argv.slice(2);
  for (let i = 0; i < rest.length; i += 1) {
    const flag = rest[i];
    if (flag === "--help" || flag === "-h") {
      printHelp();
      process.exit(0);
    } else if (flag === "--demo") {
      args.demo = true;
    } else if (flag === "--json") {
      args.json = true;
    } else if (flag === "--dry-run") {
      args.dryRun = true;
    } else if (flag === "--plan") {
      args.plan = rest[i + 1] || "";
      i += 1;
    } else if (flag === "--out") {
      args.out = rest[i + 1] || "";
      i += 1;
    } else {
      throw new Error(`Unknown flag \`${flag}\`. Run with --help for usage.`);
    }
  }
  return args;
}

function sleep(ms) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}

/**
 * Read the canonical runtime kit. The kit is authored by the knowledge layer,
 * so a short poll covers a build that starts while the kit is still landing.
 */
async function readKit(root) {
  const dir = path.join(root, "skills", "presentation-deck", "resources", "web-deck");
  let lastError = null;
  for (let attempt = 0; attempt < KIT_WAIT_ATTEMPTS; attempt += 1) {
    try {
      const kit = { dir };
      for (const [key, name] of KIT_FILES) {
        const text = await fs.readFile(path.join(dir, name), "utf8");
        if (!text.trim()) throw new Error(`${name} is empty`);
        kit[key] = text;
      }
      return kit;
    } catch (error) {
      lastError = error;
      if (attempt < KIT_WAIT_ATTEMPTS - 1) await sleep(KIT_WAIT_MS);
    }
  }
  const names = KIT_FILES.map((entry) => entry[1]).join(", ");
  throw new Error(
    `Web deck runtime kit missing or incomplete under \`${dir}\`: ${lastError && lastError.message}. ` +
      `Expected ${names}. The kit is the single source of the stage and runtime contract; it is inlined, never re-implemented.`
  );
}

/* =========================================================================
   Schema validation
   A purpose-built walker over the JSON Schema keywords `deck-plan-schema.json`
   actually uses, so the validator cannot drift from the schema file.
   ========================================================================= */

function deref(root, node) {
  let current = node;
  for (let guard = 0; current && typeof current.$ref === "string" && guard < 8; guard += 1) {
    const parts = current.$ref.replace(/^#\//, "").split("/");
    let target = root;
    for (const part of parts) target = target ? target[part] : undefined;
    current = target;
  }
  return current || {};
}

function typeOf(value) {
  if (value === null) return "null";
  if (Array.isArray(value)) return "array";
  if (typeof value === "number") return Number.isInteger(value) ? "integer" : "number";
  return typeof value;
}

function typeMatches(expected, value) {
  const actual = typeOf(value);
  if (expected === "number") return actual === "number" || actual === "integer";
  return expected === actual;
}

function walkSchema(root, node, value, pointer, errors) {
  const schema = deref(root, node);
  const at = pointer || "(root)";

  if ("const" in schema && value !== schema.const) {
    errors.push(`${at}: expected the constant ${JSON.stringify(schema.const)}, found ${JSON.stringify(value)}`);
    return;
  }
  if (Array.isArray(schema.enum) && !schema.enum.includes(value)) {
    errors.push(`${at}: expected one of ${schema.enum.join(", ")}, found ${JSON.stringify(value)}`);
    return;
  }
  if (schema.type) {
    const allowed = Array.isArray(schema.type) ? schema.type : [schema.type];
    if (!allowed.some((candidate) => typeMatches(candidate, value))) {
      errors.push(`${at}: expected type ${allowed.join(" or ")}, found ${typeOf(value)}`);
      return;
    }
  }

  if (typeof value === "string") {
    if (typeof schema.minLength === "number" && value.length < schema.minLength) {
      errors.push(`${at}: needs at least ${schema.minLength} characters`);
    }
    if (typeof schema.pattern === "string" && !new RegExp(schema.pattern).test(value)) {
      errors.push(`${at}: does not match the required pattern \`${schema.pattern}\``);
    }
  }

  if (typeof value === "number") {
    if (typeof schema.minimum === "number" && value < schema.minimum) {
      errors.push(`${at}: must be at least ${schema.minimum}`);
    }
    if (typeof schema.exclusiveMinimum === "number" && value <= schema.exclusiveMinimum) {
      errors.push(`${at}: must be greater than ${schema.exclusiveMinimum}`);
    }
  }

  if (Array.isArray(value)) {
    if (typeof schema.minItems === "number" && value.length < schema.minItems) {
      errors.push(`${at}: needs at least ${schema.minItems} item(s)`);
    }
    if (schema.items) {
      value.forEach((item, i) => walkSchema(root, schema.items, item, `${at}[${i}]`, errors));
    }
  }

  if (value && typeof value === "object" && !Array.isArray(value)) {
    for (const key of schema.required || []) {
      if (!(key in value)) errors.push(`${at}: missing required key \`${key}\``);
    }
    for (const [key, sub] of Object.entries(schema.properties || {})) {
      if (key in value) walkSchema(root, sub, value[key], pointer ? `${pointer}.${key}` : key, errors);
    }
  }
}

/**
 * Contract rules the schema cannot express: reveal step ids must have something
 * in the markup to reveal, and the stagger slot count is capped by the CSS.
 */
function validateStageContract(plan) {
  const errors = [];
  const slides = Array.isArray(plan.slides) ? plan.slides : [];

  slides.forEach((slide, i) => {
    if (!slide || typeof slide !== "object") return;
    const at = `slides[${i}]`;
    if (slide.index !== i) {
      errors.push(`${at}.index: must be ${i} so plan order and deck order agree, found ${JSON.stringify(slide.index)}`);
    }
    const producible = producibleSteps(slide);
    const order = Array.isArray(slide.revealOrder) ? slide.revealOrder : [];
    if (order.length > MAX_REVEAL_STEPS) {
      errors.push(
        `${at}.revealOrder: ${order.length} steps exceed the ${MAX_REVEAL_STEPS} stagger slots declared in \`stage-base.css\``
      );
    }
    for (const step of order) {
      if (!producible.has(step)) {
        errors.push(
          `${at}.revealOrder: step id \`${step}\` has nothing to reveal. Producible ids for this slide: ${[...producible].join(", ")}`
        );
      }
    }
    const seen = new Set();
    for (const step of order) {
      if (seen.has(step)) errors.push(`${at}.revealOrder: step id \`${step}\` is listed twice`);
      seen.add(step);
    }
  });

  const ids = new Set();
  for (const slide of slides) {
    if (!slide || typeof slide.id !== "string") continue;
    if (ids.has(slide.id)) errors.push(`slides: slide id \`${slide.id}\` is used more than once`);
    ids.add(slide.id);
  }

  return errors;
}

/* =========================================================================
   Reveal step bookkeeping
   ========================================================================= */

function producibleSteps(slide) {
  const steps = new Set(["headline", "rule"]);
  if (typeof slide.role === "string" && slide.role.trim()) steps.add("eyebrow");
  const support = Array.isArray(slide.support) ? slide.support : [];
  for (let i = 1; i <= support.length; i += 1) {
    for (const prefix of SUPPORT_STEP_PREFIXES) steps.add(`${prefix}-${i}`);
  }
  const media = Array.isArray(slide.media) ? slide.media : [];
  if (media.length) steps.add("media");
  for (let i = 1; i <= media.length; i += 1) steps.add(`media-${i}`);
  if (typeof slide.footnote === "string" && slide.footnote.trim()) steps.add("footnote");
  if (typeof slide.cta === "string" && slide.cta.trim()) steps.add("cta");
  return steps;
}

/** Resolve the step id a support item carries, honoring the prefix the plan used. */
function supportStepId(slide, position) {
  const order = Array.isArray(slide.revealOrder) ? slide.revealOrder : [];
  for (const prefix of SUPPORT_STEP_PREFIXES) {
    const candidate = `${prefix}-${position}`;
    if (order.includes(candidate)) return candidate;
  }
  return `item-${position}`;
}

function mediaStepId(slide, position) {
  const order = Array.isArray(slide.revealOrder) ? slide.revealOrder : [];
  if (position === 1 && order.includes("media")) return "media";
  return `media-${position}`;
}

/* =========================================================================
   HTML emission
   ========================================================================= */

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function banner(label) {
  const rule = "=".repeat(74);
  return `<!-- ${rule}\n     ${label}\n     ${rule} -->`;
}

function cssBanner(label) {
  const rule = "=".repeat(70);
  return `/* ${rule}\n   ${label}\n   ${rule} */`;
}

function tokenLayer(plan) {
  const lines = [];
  for (const group of TOKEN_GROUPS) {
    const values = plan.tokens[group] || {};
    lines.push(`  /* ${group} */`);
    for (const [key, value] of Object.entries(values)) {
      const unit = typeof value === "number" ? TOKEN_UNITS[group] : "";
      lines.push(`  --deck-${group}-${key}: ${value}${unit};`);
    }
    lines.push("");
  }
  // `stage-base.css` carries neutral defaults on a plain `:root` and is inlined
  // after this block, so the deck layer needs one extra point of specificity to
  // survive source order. `<html>` carries `data-deck` for exactly that.
  return [`:root[data-deck] {`, ...lines.slice(0, -1), `}`].join("\n");
}

/**
 * Deck layout layer. `stage-base.css` owns the stage, switching, chrome,
 * reduced-motion and print behavior; the archetype silhouettes and the content
 * typography are the deck's own, and they live here.
 */
function layoutLayer() {
  return `.deck-slide {
  justify-content: center;
}

.deck-eyebrow {
  font-family: var(--deck-type-bodyFamily);
  font-size: var(--deck-type-captionSize);
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--deck-color-accent);
}

.deck-headline {
  font-family: var(--deck-type-displayFamily);
  font-size: var(--deck-type-displaySize);
  font-weight: 600;
  line-height: 1.04;
  letter-spacing: -0.02em;
  max-width: 1420px;
  text-wrap: balance;
}

.deck-rule {
  display: block;
  width: 180px;
  height: 6px;
  background: var(--deck-color-border);
}

.deck-rule.deck-accent {
  width: 360px;
  background: var(--deck-color-accent);
}

.deck-support {
  display: flex;
  flex-direction: column;
  gap: var(--deck-space-itemGap);
  max-width: 1280px;
}

.deck-support-item {
  position: relative;
  padding-left: 40px;
  font-size: var(--deck-type-bodySize);
  color: var(--deck-color-muted);
}

.deck-support-item::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.6em;
  width: 20px;
  height: 2px;
  background: var(--deck-color-accent);
}

/* Overflow control. Text blocks are fixed at their authored height and the
   media frame is the one block that gives way, so a tall aspect can never push
   a slide past the stage. The frame keeps a floor so an empty slot still reads
   as a designed frame rather than a sliver. */

.deck-eyebrow,
.deck-headline,
.deck-rule,
.deck-support,
.deck-footnote {
  flex-shrink: 0;
}

.deck-media {
  display: flex;
  flex-direction: column;
  flex: 0 1 auto;
  gap: 16px;
  min-height: 0;
}

.deck-media-frame {
  display: grid;
  place-items: center;
  width: 100%;
  min-height: 180px;
  padding: 32px;
  border: 1px solid var(--deck-color-border);
  background: var(--deck-color-surface);
}

.deck-media-clue {
  max-width: 620px;
  font-size: var(--deck-type-captionSize);
  letter-spacing: 0.04em;
  text-align: center;
  color: var(--deck-color-muted);
}

.deck-media-caption {
  font-size: var(--deck-type-captionSize);
  color: var(--deck-color-muted);
}

.deck-footnote {
  font-size: var(--deck-type-captionSize);
  color: var(--deck-color-muted);
}

/* Archetype silhouettes. Two slides on the same archetype may still diverge;
   these are starting geometries, not a locked template. */

.deck-slide--cover,
.deck-slide--closing {
  justify-content: flex-end;
  padding-bottom: 136px;
}

.deck-slide--cover .deck-headline,
.deck-slide--closing .deck-headline {
  max-width: 1200px;
}

.deck-slide--section-divider {
  background: var(--deck-color-surface);
}

.deck-slide--section-divider .deck-headline {
  font-size: calc(var(--deck-type-displaySize) * 1.2);
  max-width: 1500px;
}

.deck-slide--agenda .deck-support,
.deck-slide--timeline .deck-support,
.deck-slide--roadmap .deck-support {
  counter-reset: deck-row;
  max-width: 1420px;
}

.deck-slide--agenda .deck-support-item,
.deck-slide--timeline .deck-support-item,
.deck-slide--roadmap .deck-support-item {
  counter-increment: deck-row;
  padding: 20px 0 20px 108px;
  border-top: 1px solid var(--deck-color-border);
  font-size: var(--deck-type-leadSize);
  color: var(--deck-color-text);
}

.deck-slide--agenda .deck-support-item::before,
.deck-slide--timeline .deck-support-item::before,
.deck-slide--roadmap .deck-support-item::before {
  content: counter(deck-row, decimal-leading-zero);
  position: absolute;
  left: 0;
  top: 22px;
  width: auto;
  height: auto;
  background: none;
  font-family: var(--deck-type-bodyFamily);
  font-size: var(--deck-type-captionSize);
  font-weight: 600;
  letter-spacing: 0.12em;
  color: var(--deck-color-accent);
}

.deck-slide--feature .deck-support,
.deck-slide--team .deck-support,
.deck-slide--pricing .deck-support,
.deck-slide--case-study .deck-support {
  flex-direction: row;
  align-items: stretch;
  gap: 48px;
  max-width: 1728px;
}

.deck-slide--feature .deck-support-item,
.deck-slide--team .deck-support-item,
.deck-slide--pricing .deck-support-item,
.deck-slide--case-study .deck-support-item {
  flex: 1 1 0;
  padding: 36px 32px 44px;
  border-top: 4px solid var(--deck-color-accent);
  background: var(--deck-color-surface);
  color: var(--deck-color-text);
}

.deck-slide--feature .deck-support-item::before,
.deck-slide--team .deck-support-item::before,
.deck-slide--pricing .deck-support-item::before,
.deck-slide--case-study .deck-support-item::before {
  content: none;
}

.deck-slide--data .deck-media-frame,
.deck-slide--dashboard .deck-media-frame,
.deck-slide--portfolio .deck-media-frame {
  min-height: 260px;
}

.deck-slide--testimonial {
  align-items: center;
  text-align: center;
}

.deck-slide--testimonial .deck-headline {
  font-size: var(--deck-type-leadSize);
  font-weight: 400;
  max-width: 1340px;
}

.deck-slide--testimonial .deck-support-item {
  padding-left: 0;
  color: var(--deck-color-text);
}

.deck-slide--testimonial .deck-support-item::before {
  content: none;
}

/* Notes pane. The pane is runtime-owned chrome: \`is-open\` is its programmatic
   hook, and a peeking grab edge opens it on hover or keyboard focus so a
   presenter aid needs no second script. */

.deck-notes {
  transform: translateY(calc(100% - 44px));
}

.deck-notes:hover,
.deck-notes:focus-within {
  transform: translateY(0);
}

.deck-notes-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--deck-color-accent);
}

.deck-notes-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}

.deck-notes-item {
  color: var(--deck-color-muted);
}

.deck-notes-index {
  margin-right: 8px;
  font-variant-numeric: tabular-nums;
  color: var(--deck-color-accent);
}`;
}

function familyNames(type) {
  const names = [];
  for (const key of ["displayFamily", "bodyFamily"]) {
    const stack = typeof type[key] === "string" ? type[key] : "";
    const first = stack.split(",")[0].trim().replace(/^['"]|['"]$/g, "");
    if (!first) continue;
    if (GENERIC_FAMILIES.has(first.toLowerCase())) continue;
    if (!names.includes(first)) names.push(first);
  }
  return names;
}

/**
 * Head font block. `google` is the only source that emits an external request;
 * `self-host` and `system-stack` stay offline by contract.
 */
function fontBlock(plan) {
  const source = plan.delivery.fontSource;
  if (source === "system-stack") {
    return "<!-- fontSource: system-stack. No downloaded face, no external font request. -->";
  }
  if (source === "self-host") {
    const dir = plan.delivery.assetsDir || "assets";
    return [
      `<!-- fontSource: self-host. Add the \`@font-face\` rules for the .woff2 files in`,
      `     \`${escapeHtml(dir)}/\` to the deck layout layer, with \`font-display: swap\`.`,
      `     No external font request is emitted. -->`,
    ].join("\n");
  }
  const names = familyNames(plan.tokens.type);
  if (!names.length) {
    return "<!-- fontSource: google, but every family token resolves to a generic stack. No font request emitted. -->";
  }
  const query = names
    .map((name) => `family=${encodeURIComponent(name).replace(/%20/g, "+")}:wght@400;600;700`)
    .join("&amp;");
  return [
    '<link rel="preconnect" href="https://fonts.googleapis.com">',
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
    `<link rel="stylesheet" href="https://fonts.googleapis.com/css2?${query}&amp;display=swap">`,
  ].join("\n");
}

function revealAttrs(slide, stepId, primary) {
  const order = Array.isArray(slide.revealOrder) ? slide.revealOrder : [];
  const position = order.indexOf(stepId);
  const classes = [];
  const attrs = [`data-deck-step-id="${escapeHtml(stepId)}"`];
  if (position >= 0 && position < MAX_REVEAL_STEPS) {
    classes.push("deck-reveal");
    if (primary) classes.push(`deck-reveal--${primary}`);
    attrs.push(`data-deck-step="${position}"`);
  }
  return { classes, attrs };
}

function openTag(tag, classes, attrs) {
  const parts = [tag];
  const classList = classes.filter(Boolean);
  if (classList.length) parts.push(`class="${classList.join(" ")}"`);
  for (const attr of attrs.filter(Boolean)) parts.push(attr);
  return `<${parts.join(" ")}>`;
}

function slideMarkup(plan, slide, total, entrances) {
  const indent = "      ";
  const inner = `${indent}  `;
  const archetype = slide.archetype;
  const family = ARCHETYPE_TRANSITION[archetype];
  const slideClasses = ["deck-slide", `deck-slide--${archetype}`];
  if (family && TRANSITIONS.includes(family)) slideClasses.push(`deck-slide--${family}`);

  const headlineId = `deck-headline-${slide.id}`;
  const lines = [];
  lines.push(`${indent}<!-- slide ${slide.index + 1} of ${total} - ${archetype} - ${slide.id} -->`);
  lines.push(
    `${indent}${openTag("section", slideClasses, [
      `id="slide-${escapeHtml(slide.id)}"`,
      'role="group"',
      'aria-roledescription="slide"',
      `aria-labelledby="${headlineId}"`,
      `data-deck-archetype="${escapeHtml(archetype)}"`,
      `data-deck-density="${escapeHtml(slide.density)}"`,
      family && TRANSITIONS.includes(family) ? `data-deck-slide-transition="${family}"` : "",
    ])}`
  );

  if (typeof slide.role === "string" && slide.role.trim()) {
    const reveal = revealAttrs(slide, "eyebrow", entrances.text);
    lines.push(
      `${inner}${openTag("p", ["deck-eyebrow", ...reveal.classes], reveal.attrs)}${escapeHtml(slide.role)}</p>`
    );
  }

  const headlineReveal = revealAttrs(slide, "headline", entrances.text);
  lines.push(
    `${inner}${openTag("h2", ["deck-headline", ...headlineReveal.classes], [
      `id="${headlineId}"`,
      "data-deck-headline",
      ...headlineReveal.attrs,
    ])}${escapeHtml(slide.headline)}</h2>`
  );

  const ruleReveal = revealAttrs(slide, "rule", entrances.accent ? "mask" : entrances.text);
  lines.push(
    `${inner}${openTag("span", ["deck-rule", entrances.accent ? "deck-accent" : "", ...ruleReveal.classes], [
      'aria-hidden="true"',
      ...ruleReveal.attrs,
    ])}</span>`
  );

  const support = Array.isArray(slide.support) ? slide.support : [];
  if (support.length) {
    lines.push(`${inner}<ul class="deck-support">`);
    support.forEach((item, i) => {
      const stepId = supportStepId(slide, i + 1);
      const reveal = revealAttrs(slide, stepId, entrances.block);
      lines.push(
        `${inner}  ${openTag("li", ["deck-support-item", ...reveal.classes], reveal.attrs)}${escapeHtml(item)}</li>`
      );
    });
    lines.push(`${inner}</ul>`);
  }

  const media = Array.isArray(slide.media) ? slide.media : [];
  media.forEach((slot, i) => {
    const stepId = mediaStepId(slide, i + 1);
    const reveal = revealAttrs(slide, stepId, entrances.block);
    lines.push(`${inner}${openTag("figure", ["deck-media", ...reveal.classes], reveal.attrs)}`);
    lines.push(
      `${inner}  <div class="deck-media-frame" style="aspect-ratio: ${escapeHtml(slot.aspect)};" role="img" aria-label="${escapeHtml(slot.placeholder)}">`
    );
    lines.push(`${inner}    <p class="deck-media-clue">${escapeHtml(slot.placeholder)}</p>`);
    lines.push(`${inner}  </div>`);
    lines.push(`${inner}  <figcaption class="deck-media-caption">${escapeHtml(slot.purpose)}</figcaption>`);
    lines.push(`${inner}</figure>`);
  });

  for (const key of ["footnote", "cta"]) {
    if (typeof slide[key] !== "string" || !slide[key].trim()) continue;
    const reveal = revealAttrs(slide, key, entrances.text);
    lines.push(
      `${inner}${openTag("p", ["deck-footnote", key === "cta" ? "deck-cta" : "", ...reveal.classes], reveal.attrs)}${escapeHtml(slide[key])}</p>`
    );
  }

  lines.push(`${indent}</section>`);
  return lines.join("\n");
}

function chromeMarkup(plan, total, notes) {
  const lines = ['<div class="deck-chrome">'];
  if (plan.chrome.progress) {
    lines.push('  <div class="deck-progress" role="progressbar" aria-label="Deck progress">');
    lines.push('    <div class="deck-progress-bar"></div>');
    lines.push("  </div>");
  }
  if (plan.chrome.pageNumber) {
    lines.push('  <p class="deck-counter">');
    lines.push('    <span class="deck-counter-current">1</span>');
    lines.push('    <span aria-hidden="true"> / </span>');
    lines.push(`    <span class="deck-counter-total">${total}</span>`);
    lines.push("  </p>");
  }
  lines.push('  <div class="deck-controls">');
  lines.push(
    '    <button class="deck-control deck-control--prev" type="button" data-deck-nav="prev" aria-label="Previous slide">&#8592;</button>'
  );
  lines.push(
    '    <button class="deck-control deck-control--next" type="button" data-deck-nav="next" aria-label="Next slide">&#8594;</button>'
  );
  lines.push("  </div>");
  lines.push('  <div class="deck-tap deck-tap--prev" aria-hidden="true"></div>');
  lines.push('  <div class="deck-tap deck-tap--next" aria-hidden="true"></div>');
  if (plan.chrome.notesPane && notes.length) {
    lines.push('  <aside class="deck-notes" tabindex="0" data-deck-ignore-keys aria-label="Speaker notes">');
    lines.push('    <p class="deck-notes-title">Speaker notes</p>');
    lines.push('    <ol class="deck-notes-list">');
    for (const note of notes) {
      lines.push(
        `      <li class="deck-notes-item" id="notes-${note.index + 1}"><span class="deck-notes-index">${note.index + 1}</span>${escapeHtml(note.notes)}</li>`
      );
    }
    lines.push("    </ol>");
    lines.push("  </aside>");
  }
  lines.push('  <p class="deck-live" role="status" aria-live="polite"></p>');
  lines.push("</div>");
  return lines.map((line) => `  ${line}`).join("\n");
}

function buildHtml(plan, kit) {
  const slides = plan.slides;
  const total = slides.length;
  const lang = typeof plan.lang === "string" && plan.lang ? plan.lang : "en";
  const transition = plan.tokens.motion.transition;

  const declared = (plan.motionSignature.entrance || []).filter((item) => ENTRANCE_PRIMITIVES.includes(item));
  const textEntrance = declared[0] || "";
  const blockEntrance = declared[1] || declared[0] || "";
  const hasAccent = (plan.motionSignature.accent || []).length > 0;

  const notes = slides
    .filter((slide) => typeof slide.notes === "string" && slide.notes.trim())
    .map((slide) => ({ index: slide.index, id: slide.id, notes: slide.notes.trim() }));

  const slideBlocks = slides.map((slide, i) => {
    // The accent move is the one memorable gesture, capped at two uses and kept
    // off `data` and `dashboard` slides: the opening and closing rule carry it.
    const accent =
      hasAccent && (i === 0 || i === total - 1) && slide.archetype !== "data" && slide.archetype !== "dashboard";
    return slideMarkup(plan, slide, total, { text: textEntrance, block: blockEntrance, accent });
  });

  const head = [
    "<!DOCTYPE html>",
    `<html lang="${escapeHtml(lang)}" data-deck="brain-design">`,
    "<head>",
    '<meta charset="utf-8">',
    '<meta name="viewport" content="width=device-width, initial-scale=1">',
    `<title>${escapeHtml(plan.title)}</title>`,
    plan.subtitle ? `<meta name="description" content="${escapeHtml(plan.subtitle)}">` : "",
    '<meta name="generator" content="Brain Design web-deck">',
    `<meta name="deck-plan" content="${escapeHtml(PLAN_SCHEMA_ID)}">`,
    fontBlock(plan),
    "<style>",
    cssBanner("01 - Token layer, generated from the deck plan `tokens` object"),
    tokenLayer(plan),
    "",
    cssBanner("02 - Stage base, inlined verbatim from `skills/presentation-deck/resources/web-deck/stage-base.css`"),
    kit.css.trimEnd(),
    "",
    cssBanner("03 - Deck layout layer, archetype silhouettes and content typography"),
    layoutLayer(),
    "</style>",
    "</head>",
  ]
    .filter((line) => line !== "")
    .join("\n");

  const body = [
    "<body>",
    banner(`Deck: ${plan.deckId} - ${total} slides - density mode ${plan.densityMode}`),
    `  <div class="deck-viewport" data-deck-deep-link="${plan.chrome.deepLink ? "on" : "off"}">`,
    `    <div class="deck-stage deck-stage--${escapeHtml(transition)}" data-deck-transition="${escapeHtml(transition)}" role="region" aria-label="${escapeHtml(plan.title)} slides">`,
    slideBlocks.join("\n\n"),
    "    </div>",
    "  </div>",
    "",
    banner("Deck chrome. Outside the scaled stage by contract, hidden in print."),
    chromeMarkup(plan, total, notes),
    "",
    banner("Speaker notes, structured data. Shipped inside the file; never confidential."),
    notes.length
      ? `  <script type="application/json" id="deck-notes-data">\n${JSON.stringify(notes, null, 2).replace(/<\//g, "<\\/")}\n  </script>`
      : "  <!-- No slide in this plan carries speaker notes. -->",
    "",
    banner("Deck runtime, inlined verbatim from `skills/presentation-deck/resources/web-deck/deck-runtime.js`"),
    "  <script>",
    kit.js.trimEnd(),
    "  </script>",
    "</body>",
    "</html>",
    "",
  ].join("\n");

  return `${head}\n${body}`;
}

/* =========================================================================
   Demo plan
   A complete, contract-valid `speaker_led` plan so the audit tool and the smoke
   test always have a real deck and a real plan to work against.
   ========================================================================= */

const DEMO_SLIDES = [
  {
    id: "cover",
    archetype: "cover",
    role: "Quarterly review",
    headline: "Service calls now close in one visit",
    support: ["Field operations, quarter three"],
    media: [{ purpose: "Opening backdrop", aspect: "16 / 9", placeholder: "image placeholder: depot bay at shift start" }],
    footnote: "Operations review, 10 October 2026",
    revealOrder: ["media", "eyebrow", "headline", "item-1", "footnote"],
    notes: "Open on the claim, not the agenda. Let the number land before the breakdown.",
    density: "light",
  },
  {
    id: "agenda",
    archetype: "agenda",
    role: "Sequence",
    headline: "Three answers, one budget ask",
    support: ["Where visits still failed", "What the routing change did", "What the next wave costs"],
    media: [],
    revealOrder: ["headline", "rule", "item-1", "item-2", "item-3"],
    notes: "Name the three rows and promise the ask up front. Nobody should wonder where this ends.",
    density: "light",
  },
  {
    id: "divider-diagnosis",
    archetype: "section-divider",
    role: "Section one",
    headline: "Where visits failed",
    support: ["Diagnosis before remedy"],
    media: [],
    revealOrder: ["eyebrow", "headline", "item-1"],
    notes: "Breath point. Drop the pace here before the cost slide.",
    density: "light",
  },
  {
    id: "repeat-visit-cost",
    archetype: "problem",
    role: "Current state",
    headline: "Repeat visits ate a third of capacity",
    support: ["Dispatch pays the travel twice", "Technicians lose a slot each day", "Customers wait a second week"],
    media: [],
    revealOrder: ["headline", "rule", "item-1", "item-2", "item-3"],
    notes: "Who pays, and how often. Hold on the third line; that is the one finance remembers.",
    density: "medium",
  },
  {
    id: "repeat-visit-trend",
    archetype: "data",
    role: "Evidence",
    headline: "Repeat visits peaked in July",
    support: ["Peak at 34 percent of jobs", "Down to 11 percent by September"],
    media: [{ purpose: "Repeat-visit rate by month, quarter two to quarter three", aspect: "16 / 7", placeholder: "chart placeholder: repeat-visit rate by month" }],
    footnote: "Source: dispatch log, April to September 2026",
    revealOrder: ["headline", "media", "item-1", "item-2", "footnote"],
    notes: "Read the conclusion, then the axis. Expect a question about the August dip.",
    density: "medium",
  },
  {
    id: "divider-change",
    archetype: "section-divider",
    role: "Section two",
    headline: "What the routing change did",
    support: ["Remedy, then proof"],
    media: [],
    revealOrder: ["eyebrow", "headline", "item-1"],
    notes: "Gear change. The next run is the remedy and its evidence.",
    density: "light",
  },
  {
    id: "parts-with-tech",
    archetype: "solution",
    role: "Remedy",
    headline: "Parts travel with the technician",
    support: ["Stock the van from the job code", "Route by part, not postcode", "Close the job on first call"],
    media: [],
    revealOrder: ["headline", "rule", "item-1", "item-2", "item-3"],
    notes: "Same grammar as the problem headline. Three actions, not three features.",
    density: "light",
  },
  {
    id: "three-changes",
    archetype: "feature",
    role: "Mechanism",
    headline: "Three changes carried the gain",
    support: ["Job codes name the part.", "Routing reads van stock.", "Dispatch closes jobs on site."],
    media: [],
    revealOrder: ["headline", "card-1", "card-2", "card-3"],
    notes: "Card titles are benefits. Give each one a sentence and move on.",
    density: "medium",
  },
  {
    id: "rollout",
    archetype: "timeline",
    role: "How it shipped",
    headline: "Rollout ran eight weeks",
    support: ["May: job codes rewritten", "June: routing live at one depot", "July: four depots on the new flow"],
    media: [],
    revealOrder: ["headline", "rule", "node-1", "node-2", "node-3"],
    notes: "Past tense only. The future wave belongs on the ask slide.",
    density: "light",
  },
  {
    id: "north-depot",
    archetype: "case-study",
    role: "North depot, field service",
    headline: "North depot closed 94 percent first visit",
    support: [
      "Context: oldest fleet, worst repeat rate.",
      "Action: part-led routing from week one.",
      "Result: 94 percent first-visit close.",
    ],
    media: [{ purpose: "First-visit close rate before and after", aspect: "16 / 9", placeholder: "chart placeholder: first-visit close rate, north depot" }],
    revealOrder: ["headline", "item-1", "item-2", "item-3", "media"],
    notes: "Hardest depot first. If it worked here it works at the easy sites.",
    density: "medium",
  },
  {
    id: "dispatcher-quote",
    archetype: "testimonial",
    role: "From the floor",
    headline: "The van leaves loaded for the job it is going to.",
    support: ["Lead dispatcher, north depot"],
    media: [],
    revealOrder: ["headline", "item-1"],
    notes: "Read the quote, then stop. Do not paraphrase it.",
    density: "light",
  },
  {
    id: "divider-ask",
    archetype: "section-divider",
    role: "Section three",
    headline: "The budget ask",
    support: ["One number, one year"],
    media: [],
    revealOrder: ["eyebrow", "headline", "item-1"],
    notes: "Shift posture here. Everything after this is the decision.",
    density: "light",
  },
  {
    id: "second-wave-cost",
    archetype: "pricing",
    role: "What it costs",
    headline: "Two depots, one year, flat cost",
    support: ["Stock cover, one-off.", "Routing seats, per depot.", "Training, two weeks."],
    media: [],
    footnote: "Fleet replacement is budgeted separately.",
    revealOrder: ["headline", "card-1", "card-2", "card-3", "footnote"],
    notes: "Parallel rows across the three blocks. Let them compare, do not sell.",
    density: "medium",
  },
  {
    id: "closing",
    archetype: "closing",
    role: "Decision",
    headline: "Fund the second wave",
    support: ["Two depots, starting in November"],
    media: [],
    cta: "Approve the stock cover this week so November holds.",
    revealOrder: ["eyebrow", "headline", "item-1", "cta"],
    notes: "One thing to remember, one thing to do. Stop talking after the ask.",
    density: "light",
  },
];

function demoPlan() {
  return {
    schema: PLAN_SCHEMA_ID,
    deckId: "field-service-quarterly",
    title: "Field Service Quarterly Review",
    subtitle: "Quarter three operations and the budget ask",
    generatedBy: "brain-design",
    densityMode: "speaker_led",
    stage: { width: STAGE_WIDTH, height: STAGE_HEIGHT, fit: "uniform-scale", overflow: "letterbox" },
    stylePack: "Web Deck Pack",
    directionPack: "motion-stage",
    tokens: {
      color: {
        bg: "#0d1014",
        surface: "#171d24",
        text: "#f2f5f7",
        muted: "#9aa7b4",
        border: "#2b333d",
        accent: "#f0b429",
        accentContrast: "#0d1014",
      },
      type: {
        displayFamily: '"Fraunces", "Iowan Old Style", Georgia, serif',
        bodyFamily: '"Inter", "Segoe UI", system-ui, Arial, sans-serif',
        displaySize: 120,
        leadSize: 48,
        bodySize: 34,
        captionSize: 24,
      },
      space: { stagePadX: 96, stagePadY: 96, blockGap: 48, itemGap: 24 },
      motion: {
        entranceMs: 520,
        transitionMs: 440,
        staggerMs: 80,
        easing: "cubic-bezier(0.22, 0.68, 0.28, 1)",
        transition: "rise",
      },
    },
    motionSignature: {
      id: "ledger-rise",
      entrance: ["rise", "mask"],
      accent: ["accent rule wipe on the opening and closing frame, twice in the deck"],
      forbidden: [
        "bounce-in or elastic headlines",
        "typewriter or letter-by-letter display type",
        "numbers counting up on metrics",
        "infinite floating or hovering cards",
        "parallax backgrounds inside the fixed stage",
        "full-stage cube, flip or page-curl rotations",
        "confetti, sparkle bursts and neon pulse loops",
        "blur-to-focus or slow zoom on every image",
        "cursor-following particles or glow",
        "a spinning logo on the cover",
        "gradient hue rotation as a background loop",
      ],
    },
    chrome: { progress: true, pageNumber: true, deepLink: true, notesPane: true },
    delivery: { singleFile: true, assetsDir: null, fontSource: "google", pdfExport: false },
    slides: DEMO_SLIDES.map((slide, index) => ({ ...slide, index })),
  };
}

/* =========================================================================
   Reporting
   ========================================================================= */

function markdownReport(result) {
  const lines = [
    "# Web Deck Build",
    "",
    `- Status: ${result.status}`,
    `- Deck id: \`${result.deckId}\``,
    `- Title: ${result.title}`,
    `- Density mode: ${result.densityMode}`,
    `- Slides: ${result.slides}`,
    `- Source: ${result.source}`,
    `- Runtime kit: \`${result.kit.dir}\` (stage-base.css ${result.kit.cssBytes} bytes, deck-runtime.js ${result.kit.jsBytes} bytes, inlined verbatim)`,
    `- Font source: ${result.fontSource}`,
  ];
  if (result.errors.length) {
    lines.push("", "## Plan Defects", "");
    for (const error of result.errors) lines.push(`- ${error}`);
    lines.push("", "Repair the plan and rebuild. No deck was written.");
  } else if (result.dryRun) {
    lines.push("", `- Dry run: validated only, ${result.bytes} bytes would be written to \`${result.out}\``);
  } else {
    lines.push("", `- Deck written: \`${result.out}\` (${result.bytes} bytes)`);
    if (result.planOut) lines.push(`- Deck plan written: \`${result.planOut}\``);
    lines.push(
      "",
      "Next: run `skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs` on the deck, then",
      "`skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs` before any completion claim.",
    );
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

  if (!args.demo && !args.plan) {
    process.stderr.write("Nothing to build. Pass --plan <file.json> or --demo. Run with --help for usage.\n");
    return 1;
  }
  if (args.demo && args.plan) {
    process.stderr.write("Pass either --plan or --demo, not both.\n");
    return 1;
  }
  if (!args.out && !args.dryRun) {
    process.stderr.write("Missing --out <file.html>. Pass --dry-run to validate without an output path.\n");
    return 1;
  }

  const root = repoRoot();
  let kit;
  try {
    kit = await readKit(root);
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    return 1;
  }

  let plan;
  let source;
  if (args.demo) {
    plan = demoPlan();
    source = "demo plan synthesized by the plan tool";
  } else {
    try {
      plan = JSON.parse(await fs.readFile(path.resolve(args.plan), "utf8"));
      source = path.resolve(args.plan);
    } catch (error) {
      process.stderr.write(`Could not read the deck plan \`${args.plan}\`: ${error.message}\n`);
      return 1;
    }
  }

  let schema;
  try {
    schema = JSON.parse(kit.schema);
  } catch (error) {
    process.stderr.write(`Could not parse \`${path.join(kit.dir, "deck-plan-schema.json")}\`: ${error.message}\n`);
    return 1;
  }

  const errors = [];
  walkSchema(schema, schema, plan, "", errors);
  if (!errors.length) errors.push(...validateStageContract(plan));

  const out = args.out ? path.resolve(args.out) : "";
  const result = {
    tool: "design_brain_web_deck_plan",
    schema: PLAN_SCHEMA_ID,
    status: errors.length ? "BLOCKED" : "PASS",
    source,
    deckId: (plan && plan.deckId) || "unknown",
    title: (plan && plan.title) || "unknown",
    densityMode: (plan && plan.densityMode) || "unknown",
    fontSource: (plan && plan.delivery && plan.delivery.fontSource) || "unknown",
    slides: Array.isArray(plan && plan.slides) ? plan.slides.length : 0,
    out,
    planOut: "",
    bytes: 0,
    dryRun: args.dryRun,
    kit: {
      dir: kit.dir,
      cssBytes: Buffer.byteLength(kit.css, "utf8"),
      jsBytes: Buffer.byteLength(kit.js, "utf8"),
    },
    errors,
  };

  if (!errors.length) {
    const html = buildHtml(plan, kit);
    result.bytes = Buffer.byteLength(html, "utf8");
    if (!args.dryRun) {
      try {
        await fs.mkdir(path.dirname(out), { recursive: true });
        await fs.writeFile(out, html, "utf8");
        if (args.demo) {
          const planOut = `${out.replace(/\.html?$/i, "")}.deck-plan.json`;
          await fs.writeFile(planOut, `${JSON.stringify(plan, null, 2)}\n`, "utf8");
          result.planOut = planOut;
        }
      } catch (error) {
        process.stderr.write(`Could not write \`${out}\`: ${error.message}\n`);
        return 1;
      }
    }
  }

  process.stdout.write(args.json ? `${JSON.stringify(result, null, 2)}\n` : markdownReport(result));
  return errors.length ? 2 : 0;
}

main().then(
  (code) => {
    process.exit(code);
  },
  (error) => {
    process.stderr.write(`design_brain_web_deck_plan failed: ${error && error.stack ? error.stack : error}\n`);
    process.exit(1);
  }
);
