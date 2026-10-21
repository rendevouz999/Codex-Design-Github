#!/usr/bin/env node
// UserPromptSubmit hook for the Codex Design Brain plugin.
// Matches the prompt against a compact intent table and prints the route for the
// matched intent only. No match means no output, so idle prompts cost nothing.

import { fileURLToPath } from "node:url";
import { readFileSync } from "node:fs";


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
const SCOPE = JSON.parse(readFileSync(`${PLUGIN_ROOT}/.design-brain/PRESENTATION_SCOPE.json`, "utf8"));
const DOMAIN_ANCHORS = prep([...SCOPE.presentationTerms, ...SCOPE.webTerms]);

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
  if (!DOMAIN_ANCHORS.some((term) => text.includes(term))) return null;
  if (new RegExp(SCOPE.nonPresentationTargetPattern).test(text.trim())) return null;
  const rules = JSON.parse(readFileSync(`${PLUGIN_ROOT}/skills/presentation-deck/resources/routing.json`, "utf8"));
  const value = ` ${String(prompt).toLowerCase().replace(/[^a-z0-9&]+/g, " ").trim()} `;
  const has = (terms) => terms.some((term) => value.includes(` ${term} `));
  if (new RegExp(rules.dualPattern).test(value)) {
    return { id: "presentation-and-web", label: "two artifacts and two receipts", skill: "presentation-deck", files: ["skills/presentation-deck/workflows/native.md", "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md", "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md"] };
  }
  const native = new RegExp(rules.toNativePattern).test(value) || (has(rules.nativeTerms) && !has(rules.browserTerms));
  const byPhrase = INTENTS.find((entry) => entry.phrases.some((term) => text.includes(term)));
  const staticIntent = INTENTS.find((entry) => entry.id === "presentation-deck");
  const unresolvedTarget = {
    ...staticIntent,
    label: "presentation output target unresolved",
    files: ["skills/presentation-deck/SKILL.md", "skills/presentation-deck/design/WORKFLOW.md", ".design-brain/PRESENTATION_SCOPE.md"],
  };
  if (new RegExp(SCOPE.toHostPattern).test(text.trim()) || (!native && SCOPE.hostTerms.some((term) => text.includes(normalize(term))))) {
    return { ...INTENTS.find((entry) => entry.id === "presentation-deck"), label: "host-directed presentation target", files: ["skills/presentation-deck/SKILL.md", "skills/presentation-deck/design/WORKFLOW.md"] };
  }
  if (!native && SCOPE.webTerms.some((term) => text.includes(normalize(term)))) {
    return INTENTS.find((entry) => entry.id === "web-deck");
  }
  if (native && (byPhrase || gateOpen(text))) return INTENTS.find((entry) => entry.id === "presentation-deck");
  if (has(rules.nativeTerms) && has(rules.browserTerms) && (byPhrase || gateOpen(text))) return INTENTS.find((entry) => entry.id === "web-deck");
  if (byPhrase) return byPhrase.id === "presentation-deck" ? unresolvedTarget : byPhrase;
  if (!gateOpen(text)) return null;
  const matched = INTENTS.find((entry) => entry.terms.some((term) => text.includes(term))) ?? null;
  return matched?.id === "presentation-deck" ? unresolvedTarget : matched;
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
    // Paths are structural fields, never truncate them at a whitespace budget.
    // Resolve relative paths against the single explicit root, including spaces.
    const block = [
      `PLUGIN_ROOT: ${PLUGIN_ROOT}`,
      `Brain Design route: ${intent.id} (${intent.label}).`,
      `Read first: ${intent.files.map((file) => `${PLUGIN_ROOT}/${file}`).join(", ")}`,
      `Plugin team: Main + ONE reused Engineer. Claude Code: codex-design:general-design-production-engineer (claude-opus-5-5, xhigh); Codex: gpt-6.1-sol (xhigh). Main owns creative direction and PASS/REVISE. Contract: ${PLUGIN_ROOT}/.design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md.`,
      `Before host production/handoff: read ${PLUGIN_ROOT}/.design-brain/runtime/TOKEN_EFFICIENT_CONTINUITY.md; start/resume one project session, initialize its actual slide roster, checkpoint each batch.`,
      `Supabase/local memory: ${PLUGIN_ROOT}/.design-brain/LOCAL_MEMORY_POLICY.md; Engineer reads, Main writes/readbacks.`,
      `PPTX: read ${PLUGIN_ROOT}/skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md and sibling PPTX_IMAGE_SELECTION_POLICY.md. Preserve owner calibration and full creative quality. Ask unspecified other-platform size. SDK remains explicit.`,
    ].join("\n");
    process.stdout.write(block + "\n");
  }
} catch {
  // Routing is advisory only. Stay silent and never block the prompt.
}

process.exit(0);
