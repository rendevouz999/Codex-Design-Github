#!/usr/bin/env node
// UserPromptSubmit hook for the Codex Design Brain plugin.
// Matches the prompt against a compact intent table and prints the route for the
// matched intent only. No match means no output, so idle prompts cost nothing.

import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";

const MAX_WORDS = 120;

// The plugin installs at user scope, so this hook also runs in projects that are not
// this repository. Routes therefore name absolute paths inside the plugin tree.
const PLUGIN_ROOT = String(
  process.env.CLAUDE_PLUGIN_ROOT || fileURLToPath(new URL("../", import.meta.url)),
)
  .replace(/\\/g, "/")
  .replace(/\/+$/, "");

// Normalizing both sides of the comparison turns matching into a word-boundary test
// instead of bare containment, so `template` no longer fires on `template literal`.
function normalize(text) {
  return ` ${String(text).toLowerCase().replace(/[^a-z0-9]+/g, " ").trim()} `;
}

function prep(terms) {
  return terms.map(normalize);
}

function hits(text, terms) {
  return terms.filter((term) => text.includes(term));
}

// Tier one: a domain anchor, the noun naming a design surface this repository owns.
const DOMAIN_ANCHORS = prep([
  "design", "desain", "ui", "ux", "frontend", "front end", "layout", "tampilan",
  "template", "templates", "landing page", "website", "situs", "halaman website",
  "dashboard", "ui kit", "design system", "design token", "figma", "deck", "slide",
  "slides", "presentation", "presentasi", "ppt", "pptx", "powerpoint", "keynote",
  "google slides", "mockup", "marketplace", "komponen", "typography", "tipografi",
  "moodboard", "referensi",
]);

// Tier two: what the user wants done to that surface. Ordinary session words live
// here on purpose, because a term from this list alone never routes anything.
const INTENT_TERMS = prep([
  "buat", "buatkan", "buatin", "bikin", "bikinin", "design", "desain", "redesign",
  "mendesain", "create", "make", "build", "generate", "convert", "ubah", "jadikan",
  "jadiin", "turn", "rework", "revamp", "improve", "perbaiki", "polish", "critique",
  "kritik", "review", "audit", "diagnose", "name", "naming", "kasih nama", "preview",
  "style", "color", "warna", "batch", "variants", "varian", "variasi", "beberapa",
  "animate", "animasi", "pelajari", "extract", "ekstrak", "premium", "mirip", "copy",
  "flat", "repetitive", "repetitif", "bland", "boring", "monoton",
]);

// Most specific intent first. The first match wins. `phrases` are unambiguous on
// their own; `terms` only route once the two-tier gate has already proven intent.
const INTENTS = [
  {
    id: "web-deck",
    label: "browser-rendered animated deck",
    skill: "presentation-deck",
    phrases: prep([
      "web deck", "html deck", "html presentation", "web presentation", "browser deck",
      "animated deck", "animated slides", "animated presentation", "interactive deck",
      "slide deck html", "single file deck", "presenter deck", "webinar deck",
      "demo day deck", "deck to web", "ppt to web", "pptx to html",
      "convert deck to html", "self running deck",
      "deck html", "presentasi web", "presentasi html", "slide web", "slide animasi",
      "presentasi animasi", "deck browser", "deck interaktif", "ppt ke web",
      "ppt ke html", "pptx ke html", "ubah ppt jadi web", "presentasi satu file",
      "slide buat live", "deck buat webinar",
    ]),
    // Web deck must only win on explicit web-deck intent, never on a bare deck word.
    terms: [],
    files: [
      "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md",
      "skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md",
      "skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md",
      "skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md",
      "skills/presentation-deck/resources/web-deck/deck-plan-schema.json",
      "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md",
    ],
  },
  {
    id: "figma",
    label: "Figma or editable source template",
    skill: "brain-design",
    phrases: prep(["figma", "auto layout", "source template", "template figma", "sumber template"]),
    terms: prep(["figma", "fig"]),
    files: [
      ".design-brain/FIGMA_REFERENCE_DEEP_STUDY.md",
      ".design-brain/FIGMA_PROFESSIONAL_TEMPLATE_LEARNING.md",
      ".design-brain/FIGMA_AUTO_LAYOUT_ENFORCEMENT.md",
      ".design-brain/FIGMA_OUTPUT_TARGET.md",
      ".design-brain/TEMPLATE_IMAGE_PLACEHOLDER_POLICY.md",
    ],
  },
  {
    id: "batch",
    label: "multi-output batch",
    skill: "brain-design",
    phrases: prep([
      "batch template", "template batch", "buat batch", "batch of templates",
      "multiple templates", "several templates", "template variants", "design variants",
      "satu per satu", "1 per 1", "gambar design", "gambar desain",
    ]),
    terms: prep([
      "batch", "beberapa", "varian", "variasi", "variants", "masing masing",
      "one by one", "per template", "per desain", "per gambar",
    ]),
    files: [
      ".design-brain/SEQUENTIAL_REFERENCE_BATCH_WORKFLOW.md",
      ".design-brain/BATCH_TEMPLATE_HARD_GATES.md",
      ".design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md",
      "scripts/design_brain_sequential_batch.py",
    ],
  },
  {
    id: "review",
    label: "critique or similarity diagnosis",
    skill: "brain-design",
    phrases: prep([
      "design review", "design critique", "review the design", "review this design",
      "too similar", "terlalu mirip", "jangan mirip", "jangan copy", "kurang premium",
      "lebih premium", "perbaiki design", "perbaiki desain", "de generic",
    ]),
    terms: prep(["critique", "kritik", "review", "audit", "polish", "generic", "mirip", "premium"]),
    files: [
      ".design-brain/VISUAL_CRITIQUE_CHECKLIST.md",
      ".design-brain/ORIGINALITY_SIMILARITY_SCORECARD.md",
      ".design-brain/QUALITY_GATE_FAILURE_TAXONOMY.md",
      ".agents/skills/design-critic/SKILL.md",
    ],
  },
  {
    id: "naming",
    label: "name originality",
    skill: "brain-design",
    phrases: prep(["kasih nama", "nama template", "judul template", "template name", "brand name"]),
    terms: prep(["naming", "nama", "name"]),
    files: [
      ".design-brain/ORIGINALITY_GUARD.md",
      ".design-brain/templates/TEMPLATE_NAME_CHECK.md",
      "scripts/design_brain_name_check.py",
    ],
  },
  {
    id: "presentation-deck",
    label: "static slide artifact",
    skill: "presentation-deck",
    phrases: prep(["slide deck", "pitch deck", "powerpoint", "pptx", "keynote", "google slides"]),
    terms: prep(["presentation", "presentasi", "deck", "slide", "slides", "ppt"]),
    files: [
      "skills/presentation-deck/design/PRESENTATION_DECK_INTELLIGENCE.md",
      "skills/presentation-deck/workflows/native.md",
      ".design-brain/MEDIUM_PRODUCT_PLAYBOOKS.md",
      ".design-brain/adapters/design-craft/SKILL.md",
    ],
  },
  {
    id: "template",
    label: "template or design-system product",
    skill: "brain-design",
    phrases: prep([
      "template website", "website template", "landing page", "design system",
      "design token", "ui kit", "marketplace template", "buat template",
      "bikin template", "halaman website", "preview marketplace", "marketplace preview",
    ]),
    terms: prep([
      "template", "templates", "marketplace", "website", "situs", "dashboard",
      "preview", "cover", "mockup",
    ]),
    files: [
      ".design-brain/APPROVED_TEMPLATE_CORPUS.md",
      ".design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md",
      ".design-brain/POST_BUILD_COMPLETION_GATE.md",
      ".design-brain/WEBSITE_TEMPLATE_REFERENCE_CORPUS.md",
      "scripts/design_brain_module_select.py",
    ],
  },
  {
    id: "design",
    label: "general design work",
    skill: "brain-design",
    phrases: prep(["buat design", "buat desain", "bikin design", "bikin desain", "design brain"]),
    terms: prep([
      "design", "desain", "ui", "ux", "frontend", "front end", "layout", "tampilan",
      "komponen", "component",
    ]),
    files: [
      "AGENTS.md",
      ".design-brain/AUTOLOAD_POLICY.md",
      ".design-brain/CONTEXT_PRIORITY.md",
      ".design-brain/DESIGN_OPERATING_RULES.md",
    ],
  },
];

// An unambiguous phrase routes on its own. Otherwise the prompt needs a domain anchor
// and a separate intent term, so one weak keyword can never print a route block.
function gateOpen(text) {
  const domain = hits(text, DOMAIN_ANCHORS);
  if (!domain.length) return false;
  const intent = hits(text, INTENT_TERMS);
  if (!intent.length) return false;
  return domain.length > 1 || intent.length > 1 || domain[0] !== intent[0];
}

function route(prompt) {
  const text = normalize(prompt);
  if (text === " ") return null;
  const rules = JSON.parse(readFileSync(`${PLUGIN_ROOT}/skills/presentation-deck/resources/routing.json`, "utf8"));
  const value = ` ${String(prompt).toLowerCase().replace(/[^a-z0-9&]+/g, " ").trim()} `;
  const has = (terms) => terms.some((term) => value.includes(` ${term} `));
  if (new RegExp(rules.dualPattern).test(value)) {
    return { id: "presentation-and-web", label: "two artifacts and two receipts", skill: "brain-design", files: ["skills/presentation-deck/workflows/native.md", "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md", "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md"] };
  }
  const native = new RegExp(rules.toNativePattern).test(value) || (has(rules.nativeTerms) && !has(rules.browserTerms));
  const byPhrase = INTENTS.find((entry) => entry.phrases.some((term) => text.includes(term)));
  if (native && (byPhrase || gateOpen(text))) return INTENTS.find((entry) => entry.id === "presentation-deck");
  if (has(rules.nativeTerms) && has(rules.browserTerms) && (byPhrase || gateOpen(text))) return INTENTS.find((entry) => entry.id === "web-deck");
  if (byPhrase) return byPhrase;
  if (!gateOpen(text)) return null;
  return INTENTS.find((entry) => entry.terms.some((term) => text.includes(term))) ?? null;
}

function capWords(text, limit) {
  const words = text.split(/\s+/).filter(Boolean);
  return words.length <= limit ? text : words.slice(0, limit).join(" ");
}

async function readStdin() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  return Buffer.concat(chunks).toString("utf8");
}

try {
  const payload = JSON.parse((await readStdin()) || "{}");
  const intent = route(payload.prompt ?? payload.user_prompt ?? "");

  if (intent) {
    const block = [
      `Brain Design route: ${intent.id} (${intent.label}).`,
      `Skill: ${intent.skill}`,
      `Plugin scope only: Main + ONE Engineer (Claude Code: agent codex-design:general-design-production-engineer, claude-opus-5-5, effort xhigh; Codex: gpt-6.1-sol, reasoning_effort=xhigh); Main owns creative direction and PASS/REVISE under auto-full trust. Read ${PLUGIN_ROOT}/.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md.`,
      `Supabase/local memory: ${PLUGIN_ROOT}/.design-brain/LOCAL_MEMORY_POLICY.md. Engineer retrieves both sources; Main updates/readbacks and reconciles. No Agent Core dependency.`,
      `Owner calibration mode: PPTX design builds deliver the complete PPTX only, no delivery package, until the owner says exactly 'kita mulai jalur produksi'; corrections get real solutions, never safe/minimalist fallbacks.`,
      `Native PPTX: 10 x 5.625 inches. Read ${PLUGIN_ROOT}/skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md and sibling PPTX_IMAGE_SELECTION_POLICY.md. Ask unspecified other-platform size. SDK requires explicit replacement choice.`,
      `Read first: ${intent.files.map((file) => `${PLUGIN_ROOT}/${file}`).join(", ")}`,
    ].join("\n");
    process.stdout.write(capWords(block, MAX_WORDS) + "\n");
  }
} catch {
  // Routing is advisory only. Stay silent and never block the prompt.
}

process.exit(0);
