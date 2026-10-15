#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import JSZip from "jszip";

const EMU_PER_PX = 9525;
const DEFAULT_OUTPUT_ROOT = ".design-brain/evidence/deck-source-extracts";
const FORBIDDEN_OUTPUT_SEGMENTS = [".design-brain/context-packets", ".design-brain/tmp"];

const MEDIA_TYPES = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".bmp": "image/bmp",
  ".tif": "image/tiff",
  ".tiff": "image/tiff",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".emf": "image/x-emf",
  ".wmf": "image/x-wmf",
};

const AGENDA_WORDS = ["agenda", "contents", "table of contents", "outline", "overview", "daftar isi", "ringkasan isi"];
const CLOSING_WORDS = ["thank you", "thanks", "terima kasih", "questions", "q&a", "contact", "kontak", "get in touch", "hubungi"];
const DATA_WORDS = ["metric", "metrics", "result", "results", "revenue", "growth", "traction", "benchmark", "data", "angka", "hasil"];

const BASE_DEGRADATION = [
  "Master and layout placeholder geometry is not carried over. A placeholder tree is not a stage grid.",
  "Absolute shape coordinates are recorded as evidence only and are never replayed on the stage.",
  "Static-format effects (WordArt, bevel, 3-D rotation, soft and inner shadow, picture artistic effects, theme-indexed gradients) are dropped.",
  "Per-shape animations, build order, and slide transition timings are dropped. Motion comes from `skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md`.",
  "Licensed source fonts are recorded as inventory, not resolved. The web replacement is decided under `delivery.fontSource`.",
  "Chart data fidelity is not guaranteed. Only cached label text is readable here; series values must be re-authored from the real data source.",
  "Tables are reported as presence plus readable cell text, not as a rendered grid. Rebuild the table natively.",
  "Theme colors and theme indices are recorded as inventory. Token values stay unresolved until Color Role Re-Mapping runs.",
];

function parseArgs(argv) {
  const args = {
    source: null,
    out: null,
    json: false,
    dryRun: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--out") {
      args.out = argv[++i];
      if (!args.out) throw new UsageError("--out requires a directory path.");
    } else if (token === "--json") args.json = true;
    else if (token === "--dry-run") args.dryRun = true;
    else if (token === "--help" || token === "-h") {
      printHelp();
      process.exit(0);
    } else if (token.startsWith("-")) {
      throw new UsageError(`Unknown argument: ${token}`);
    } else if (args.source === null) {
      args.source = token;
    } else {
      throw new UsageError(`Unexpected extra argument: ${token}`);
    }
  }

  if (!args.source) throw new UsageError("A source .pptx path is required.");
  return args;
}

function printHelp() {
  console.log(`Usage: node skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs <source.pptx> [options]

Options:
  --out PATH   Output folder. Default: ${DEFAULT_OUTPUT_ROOT}/<timestamp>-<deck-slug>
  --json       Print the evidence JSON instead of the human report.
  --dry-run    Report what would be written without writing anything.

Exit codes: 0 success, 1 usage error, 2 unreadable source or zero slides.
`);
}

class UsageError extends Error {}
class SourceError extends Error {}

function repoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../../../..");
}

function resolveFromRoot(root, value) {
  return path.isAbsolute(value) ? path.normalize(value) : path.resolve(root, value);
}

function toPosix(value) {
  return value.replace(/\\/g, "/");
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

function slug(value, fallback = "deck-source") {
  const cleaned = String(value ?? "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return (cleaned || fallback).slice(0, 60).replace(/-+$/g, "") || fallback;
}

function round(value) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value * 100) / 100 : value;
}

function emuToPx(value) {
  const emu = Number(value);
  return Number.isFinite(emu) ? round(emu / EMU_PER_PX) : null;
}

function collapse(value) {
  return String(value ?? "").replace(/\s+/g, " ").trim();
}

function uniqueList(items, limit = 400) {
  const seen = new Set();
  const result = [];
  for (const item of items) {
    const cleaned = collapse(item);
    if (!cleaned || seen.has(cleaned)) continue;
    seen.add(cleaned);
    result.push(cleaned);
    if (result.length >= limit) break;
  }
  return result;
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

// --- Minimal OpenXML reader -------------------------------------------------
// Purpose-built tag-stream reader. Element names are matched on local name so
// any namespace prefix the producing application chose still resolves.

const ENTITIES = { amp: "&", lt: "<", gt: ">", quot: '"', apos: "'" };

function decodeEntities(value) {
  return value.replace(/&(#x?[0-9a-fA-F]+|[a-zA-Z]+);/g, (match, body) => {
    if (body.startsWith("#x") || body.startsWith("#X")) {
      const code = Number.parseInt(body.slice(2), 16);
      return Number.isFinite(code) ? String.fromCodePoint(code) : match;
    }
    if (body.startsWith("#")) {
      const code = Number.parseInt(body.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : match;
    }
    return ENTITIES[body] ?? match;
  });
}

function parseAttrs(raw) {
  const attrs = {};
  const attrRe = /([A-Za-z_][\w.:-]*)\s*=\s*("([^"]*)"|'([^']*)')/g;
  let match;
  while ((match = attrRe.exec(raw))) {
    attrs[match[1]] = decodeEntities(match[3] ?? match[4] ?? "");
  }
  return attrs;
}

function parseXml(xml) {
  const root = { name: "#root", local: "#root", attrs: {}, children: [] };
  const stack = [root];
  const tagRe = /<([?!/]?)([A-Za-z_][\w.:-]*)((?:[^>"']|"[^"]*"|'[^']*')*?)(\/?)>/g;
  let cursor = 0;
  let match;

  while ((match = tagRe.exec(xml))) {
    const text = xml.slice(cursor, match.index);
    if (text.length > 0) {
      stack[stack.length - 1].children.push({ name: "#text", local: "#text", text: decodeEntities(text) });
    }
    cursor = tagRe.lastIndex;

    const [, prefix, name, rawAttrs, selfClose] = match;
    if (prefix === "?" || prefix === "!") continue;
    if (prefix === "/") {
      if (stack.length > 1) stack.pop();
      continue;
    }

    const node = { name, local: name.includes(":") ? name.slice(name.indexOf(":") + 1) : name, attrs: parseAttrs(rawAttrs), children: [] };
    stack[stack.length - 1].children.push(node);
    if (!selfClose) stack.push(node);
  }

  return root;
}

function children(node, local) {
  return node.children.filter((child) => child.local === local);
}

function descendants(node, local, out = []) {
  for (const child of node.children) {
    if (child.local === local) out.push(child);
    if (child.children) descendants(child, local, out);
  }
  return out;
}

function firstDescendant(node, local) {
  return descendants(node, local)[0] ?? null;
}

function attr(node, name) {
  return node?.attrs?.[name] ?? null;
}

function attrLocal(node, local) {
  if (!node) return null;
  for (const [key, value] of Object.entries(node.attrs)) {
    if (key === local || key.endsWith(`:${local}`)) return value;
  }
  return null;
}

function directText(node) {
  return node.children
    .filter((child) => child.local === "#text")
    .map((child) => child.text)
    .join("");
}

// --- Package plumbing -------------------------------------------------------

function joinPart(baseDir, target) {
  const parts = [];
  for (const segment of `${baseDir}/${target}`.split("/")) {
    if (!segment || segment === ".") continue;
    if (segment === "..") parts.pop();
    else parts.push(segment);
  }
  return parts.join("/");
}

async function readPart(zip, partName) {
  const entry = zip.file(partName);
  return entry ? entry.async("string") : null;
}

async function readRels(zip, partName) {
  const dir = path.posix.dirname(partName);
  const relsXml = await readPart(zip, `${dir}/_rels/${path.posix.basename(partName)}.rels`);
  const map = new Map();
  if (!relsXml) return map;
  for (const rel of descendants(parseXml(relsXml), "Relationship")) {
    const id = attr(rel, "Id");
    const target = attr(rel, "Target");
    if (!id || !target) continue;
    const external = attr(rel, "TargetMode") === "External";
    map.set(id, {
      id,
      type: attr(rel, "Type") ?? "",
      target,
      external,
      part: external ? null : joinPart(dir, target),
    });
  }
  return map;
}

async function resolveSlideOrder(zip) {
  const presentationXml = await readPart(zip, "ppt/presentation.xml");
  if (!presentationXml) throw new SourceError("No `ppt/presentation.xml` part. The file is not a readable PPTX package.");

  const presentation = parseXml(presentationXml);
  const rels = await readRels(zip, "ppt/presentation.xml");
  const sldSz = firstDescendant(presentation, "sldSz");
  const order = [];

  for (const sldId of descendants(presentation, "sldId")) {
    // Order is authoritative only from `p:sldIdLst` -> `r:id` -> presentation rels.
    // `p:sldId` also carries a plain `id` attribute, so the relationship id must be
    // read from the prefixed attribute, never from filename sort order.
    const relationshipId = Object.entries(sldId.attrs).find(([key]) => key.endsWith(":id"))?.[1] ?? null;
    const rel = relationshipId ? rels.get(relationshipId) : null;
    if (rel?.part && zip.file(rel.part)) order.push(rel.part);
  }

  return {
    order,
    slideSizeEmu: sldSz ? { cx: Number(attr(sldSz, "cx")) || null, cy: Number(attr(sldSz, "cy")) || null } : null,
    layoutCount: Object.keys(zip.files).filter((name) => /^ppt\/slideLayouts\/slideLayout\d+\.xml$/.test(name)).length,
    masterCount: Object.keys(zip.files).filter((name) => /^ppt\/slideMasters\/slideMaster\d+\.xml$/.test(name)).length,
    themeCount: Object.keys(zip.files).filter((name) => /^ppt\/theme\/theme\d+\.xml$/.test(name)).length,
    mediaPartCount: Object.keys(zip.files).filter((name) => name.startsWith("ppt/media/") && !zip.files[name].dir).length,
  };
}

// --- Slide extraction -------------------------------------------------------

function paragraphRecord(paragraph) {
  const pPr = children(paragraph, "pPr")[0] ?? null;
  const level = Number(attr(pPr, "lvl") ?? 0) || 0;
  const pieces = [];
  for (const child of paragraph.children) {
    if (child.local === "r" || child.local === "fld") {
      for (const t of descendants(child, "t")) pieces.push(directText(t));
    } else if (child.local === "br") {
      pieces.push(" ");
    }
  }
  const bullet = pPr ? Boolean(firstDescendant(pPr, "buChar") || firstDescendant(pPr, "buAutoNum")) : false;
  const bulletSuppressed = pPr ? Boolean(firstDescendant(pPr, "buNone")) : false;
  return { level, text: collapse(pieces.join("")), bullet, bulletSuppressed };
}

function textBlock(shape, placeholderType) {
  const txBody = firstDescendant(shape, "txBody");
  if (!txBody) return null;
  const paragraphs = children(txBody, "p").map(paragraphRecord).filter((item) => item.text.length > 0);
  if (paragraphs.length === 0) return null;

  const explicitBullet = paragraphs.some((item) => item.bullet);
  const nested = paragraphs.some((item) => item.level > 0);
  const suppressed = paragraphs.every((item) => item.bulletSuppressed);
  const kind = !suppressed && (explicitBullet || nested || paragraphs.length > 1) ? "list" : "paragraph";

  return {
    shapeName: collapse(attr(firstDescendant(shape, "cNvPr"), "name")) || null,
    placeholder: placeholderType,
    kind,
    items: paragraphs.map((item) => ({ level: item.level, text: item.text })),
  };
}

function shapeExtents(shape) {
  // `a:ext` is overloaded in OpenXML: extension-list entries carry a `uri` and no
  // geometry, so take the first one that actually reports both EMU extents.
  for (const ext of descendants(shape, "ext")) {
    const cx = Number(attr(ext, "cx"));
    const cy = Number(attr(ext, "cy"));
    if (!Number.isFinite(cx) || !Number.isFinite(cy) || cx <= 0 || cy <= 0) continue;
    return { emu: { cx, cy }, px: { width: emuToPx(cx), height: emuToPx(cy) } };
  }
  return null;
}

function findRelId(node) {
  if (!node || !node.attrs) return null;
  for (const [key, value] of Object.entries(node.attrs)) {
    if (key.endsWith(":id")) return value;
  }
  for (const child of node.children ?? []) {
    const found = findRelId(child);
    if (found) return found;
  }
  return null;
}

function aspectLabel(width, height) {
  if (!width || !height) return "unknown";
  return `${round(width / height)}:1`;
}

function flattenShapes(node, out = []) {
  for (const child of node.children) {
    if (child.local === "sp" || child.local === "pic" || child.local === "graphicFrame") {
      out.push(child);
    } else if (child.local === "grpSp") {
      flattenShapes(child, out);
    }
  }
  return out;
}

async function graphicLabels(zip, frame, rels) {
  const labels = descendants(frame, "t").map(directText);
  // The chart relationship id sits on `c:chart` inside `a:graphicData`, not on the
  // frame itself, so walk down for it.
  const relId = findRelId(firstDescendant(frame, "graphicData"));
  const rel = relId ? rels.get(relId) : null;
  if (rel?.part && /charts\/chart\d*\.xml$/.test(rel.part)) {
    const chartXml = await readPart(zip, rel.part);
    if (chartXml) {
      const chart = parseXml(chartXml);
      for (const cache of descendants(chart, "strCache")) {
        for (const value of descendants(cache, "v")) labels.push(directText(value));
      }
      for (const t of descendants(chart, "t")) labels.push(directText(t));
    }
  }
  return { labels: uniqueList(labels, 24), chartPart: rel?.part ?? null };
}

async function notesText(zip, rels) {
  for (const rel of rels.values()) {
    if (!rel.part || !rel.type.endsWith("/notesSlide")) continue;
    const xml = await readPart(zip, rel.part);
    if (!xml) continue;
    const tree = parseXml(xml);
    const pieces = [];
    for (const shape of flattenShapes(firstDescendant(tree, "spTree") ?? tree)) {
      const phType = attr(firstDescendant(shape, "ph"), "type");
      if (phType === "sldNum" || phType === "dt" || phType === "ftr") continue;
      const block = textBlock(shape, phType);
      if (block) pieces.push(...block.items.map((item) => item.text));
    }
    return { part: rel.part, text: collapse(pieces.join(" ")) };
  }
  return { part: null, text: "" };
}

async function extractSlide(zip, partName, number) {
  const xml = await readPart(zip, partName);
  if (!xml) throw new SourceError(`Slide part is unreadable: \`${partName}\``);

  const tree = parseXml(xml);
  const sld = children(tree, "sld")[0] ?? tree;
  const hidden = attr(sld, "show") === "0";
  const rels = await readRels(zip, partName);
  const spTree = firstDescendant(tree, "spTree") ?? tree;

  const record = {
    number,
    part: partName,
    hidden,
    title: "",
    titleSource: null,
    blocks: [],
    images: [],
    hasChart: false,
    hasTable: false,
    hasSmartArt: false,
    graphicLabels: [],
    notes: "",
    notesPart: null,
    fontNames: [],
    colorValues: [],
  };

  for (const shape of flattenShapes(spTree)) {
    if (shape.local === "sp") {
      const phType = attr(firstDescendant(shape, "ph"), "type");
      if (phType === "sldNum" || phType === "dt" || phType === "ftr") continue;
      const block = textBlock(shape, phType);
      if (!block) continue;
      if (!record.title && (phType === "title" || phType === "ctrTitle")) {
        record.title = block.items.map((item) => item.text).join(" ");
        record.titleSource = phType;
        continue;
      }
      record.blocks.push(block);
      continue;
    }

    if (shape.local === "pic") {
      const embed = attrLocal(firstDescendant(shape, "blip"), "embed");
      const rel = embed ? rels.get(embed) : null;
      const extents = shapeExtents(shape);
      const fileName = rel?.part ? path.posix.basename(rel.part) : collapse(rel?.target) || "unresolved";
      record.images.push({
        part: rel?.part ?? null,
        external: Boolean(rel?.external),
        fileName,
        mediaType: MEDIA_TYPES[path.posix.extname(fileName).toLowerCase()] ?? "application/octet-stream",
        name: collapse(attr(firstDescendant(shape, "cNvPr"), "name")) || null,
        descr: collapse(attr(firstDescendant(shape, "cNvPr"), "descr")) || null,
        emu: extents?.emu ?? null,
        px: extents?.px ?? null,
        aspect: aspectLabel(extents?.px?.width, extents?.px?.height),
      });
      continue;
    }

    const uri = attr(firstDescendant(shape, "graphicData"), "uri") ?? "";
    if (uri.endsWith("/table")) record.hasTable = true;
    else if (uri.endsWith("/chart")) record.hasChart = true;
    else if (uri.endsWith("/diagram")) record.hasSmartArt = true;
    const { labels } = await graphicLabels(zip, shape, rels);
    record.graphicLabels.push(...labels);
  }

  record.graphicLabels = uniqueList(record.graphicLabels, 24);
  record.fontNames = uniqueList(descendants(tree, "latin").map((node) => attr(node, "typeface")), 40);
  record.colorValues = uniqueList(
    descendants(tree, "srgbClr").map((node) => {
      const value = attr(node, "val");
      return value ? `#${value.toLowerCase()}` : "";
    }),
    60,
  );

  if (!record.title) {
    const firstText = record.blocks[0]?.items?.[0]?.text ?? "";
    record.title = firstText;
    record.titleSource = firstText ? "first-text-block" : null;
  }

  const notes = await notesText(zip, rels);
  record.notes = notes.text;
  record.notesPart = notes.part;
  return record;
}

// --- Inference --------------------------------------------------------------

function matchesAny(text, words) {
  const lower = text.toLowerCase();
  return words.some((word) => lower.includes(word));
}

function supportTexts(slide) {
  return slide.blocks.flatMap((block) => block.items.map((item) => item.text));
}

function inferArchetype(slide, position, total) {
  const title = slide.title || "";
  const support = supportTexts(slide);
  const body = [title, ...support, ...slide.graphicLabels].join(" ");

  if (position === 1) return "cover";
  if (matchesAny(title, AGENDA_WORDS)) return "agenda";
  if (position === total && matchesAny(body, CLOSING_WORDS)) return "closing";
  if (slide.hasChart || slide.hasTable) return "data";
  if (support.length === 0 && title.length > 0 && title.length <= 60) return "section-divider";
  if (matchesAny(body, DATA_WORDS) && /\d/.test(body)) return "data";
  return "feature";
}

function inferDensity(slide) {
  const support = supportTexts(slide);
  const characters = support.join(" ").length;
  if (support.length <= 2 && characters <= 160) return "light";
  if (support.length <= 6 && characters <= 520) return "medium";
  return "dense";
}

function revealSteps(slide, supportCount) {
  const steps = ["headline"];
  for (let i = 1; i <= supportCount; i += 1) steps.push(`support-${i}`);
  for (let i = 1; i <= slide.images.length; i += 1) steps.push(`media-${i}`);
  if (slide.hasChart) steps.push("data-figure");
  if (slide.hasTable) steps.push("data-table");
  return steps;
}

function draftDeckPlan(deckTitle, deckId, slides, assetsDir) {
  const withNotes = slides.filter((slide) => slide.notes.length > 0).length;
  const total = slides.length;

  return {
    schema: "design-brain.web-deck.deck-plan.v1",
    deckId,
    title: deckTitle,
    generatedBy: "brain-design",
    densityMode: withNotes * 2 >= total ? "speaker_led" : "reading_first",
    stage: { width: 1920, height: 1080, fit: "uniform-scale", overflow: "letterbox" },
    stylePack: "unresolved",
    directionPack: "unresolved",
    tokens: {
      color: {
        bg: "#ffffff",
        surface: "#f3f4f7",
        text: "#14171c",
        muted: "#5b6472",
        border: "#dcdfe5",
        accent: "#1f5fd0",
        accentContrast: "#ffffff",
      },
      type: {
        displayFamily: "system-stack",
        bodyFamily: "system-stack",
        displaySize: 96,
        leadSize: 44,
        bodySize: 28,
        captionSize: 20,
      },
      space: { stagePadX: 128, stagePadY: 96, blockGap: 48, itemGap: 20 },
      motion: {
        entranceMs: 560,
        transitionMs: 480,
        staggerMs: 90,
        easing: "cubic-bezier(0.2, 0.65, 0.3, 1)",
        transition: "fade",
      },
    },
    motionSignature: { id: "unresolved", entrance: [], accent: [], forbidden: [] },
    chrome: { progress: true, pageNumber: true, deepLink: true, notesPane: withNotes > 0 },
    delivery: {
      singleFile: slides.every((slide) => slide.images.length === 0),
      assetsDir: assetsDir,
      fontSource: "system-stack",
      pdfExport: false,
    },
    extraction: {
      status: "draft-evidence",
      marker: "UNRESOLVED PLACEHOLDERS - NOT A BUILD SCAFFOLD",
      note: "Archetypes below are conservatively inferred from source text and object presence. Archetype choice, token values, `stylePack`, `directionPack` and `motionSignature` are placeholders a designer must decide. Token values are the stage defaults from `skills/presentation-deck/resources/web-deck/stage-base.css`, not values read from the source. No source color or font was promoted into a token; the inventory lives in the evidence JSON.",
      unresolved: [
        "slides[].archetype",
        "slides[].role",
        "slides[].headline (verbatim source text, not yet a takeaway title)",
        "slides[].density",
        "slides[].revealOrder",
        "densityMode",
        "stylePack",
        "directionPack",
        "tokens.color",
        "tokens.type",
        "tokens.space",
        "tokens.motion",
        "motionSignature",
        "delivery.fontSource",
      ],
      nextStep: "Run Design Cognition per `.design-brain/DESIGN_COGNITION_CONTRACT.md`, then the stage gate in `skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md`, before any layout decision.",
    },
    slides: slides.map((slide, index) => {
      const support = supportTexts(slide);
      const archetype = inferArchetype(slide, index + 1, total);
      const headline = slide.title || support[0] || `Source slide ${slide.number}`;
      return {
        index,
        id: `slide-${String(index + 1).padStart(2, "0")}-${slug(headline, "untitled")}`,
        archetype,
        role: `inferred ${archetype} from source slide ${slide.number}`,
        headline,
        support: slide.titleSource === "first-text-block" ? support.slice(1) : support,
        media: slide.images.map((image, position) => ({
          purpose: `source image ${position + 1} on slide ${slide.number}`,
          aspect: image.aspect === "unknown" ? "unknown:1" : image.aspect,
          placeholder: assetsDir ? `${assetsDir}/${image.fileName}` : image.fileName,
        })),
        revealOrder: revealSteps(slide, slide.titleSource === "first-text-block" ? Math.max(support.length - 1, 0) : support.length),
        notes: slide.notes,
        density: inferDensity(slide),
      };
    }),
  };
}

function degradationReport(slides, hiddenSlides) {
  const lines = [...BASE_DEGRADATION];

  const smartArt = slides.filter((slide) => slide.hasSmartArt).map((slide) => slide.number);
  if (smartArt.length) {
    lines.push(`SmartArt found on source slide ${smartArt.join(", ")}. Only the text survives; rebuild the relationship natively on the stage.`);
  }

  const charts = slides.filter((slide) => slide.hasChart).map((slide) => slide.number);
  if (charts.length) {
    lines.push(`Chart objects on source slide ${charts.join(", ")} are reported as presence plus cached labels. Series values are not carried.`);
  }

  const tables = slides.filter((slide) => slide.hasTable).map((slide) => slide.number);
  if (tables.length) {
    lines.push(`Table objects on source slide ${tables.join(", ")} are reported as cell text. Grid geometry is not carried.`);
  }

  const external = slides.filter((slide) => slide.images.some((image) => image.external)).map((slide) => slide.number);
  if (external.length) {
    lines.push(`Linked (non-embedded) media on source slide ${external.join(", ")} is not retrievable from the package. Re-source the asset.`);
  }

  const unresolvedMedia = slides.filter((slide) => slide.images.some((image) => !image.part && !image.external)).map((slide) => slide.number);
  if (unresolvedMedia.length) {
    lines.push(`Media relationship could not be resolved on source slide ${unresolvedMedia.join(", ")}. The image is recorded as a placeholder only.`);
  }

  if (hiddenSlides.length) {
    lines.push(`Hidden source slide ${hiddenSlides.join(", ")} is excluded from the deck plan, per the Not Carried Across list.`);
  }

  const untitled = slides.filter((slide) => !slide.title).map((slide) => slide.number);
  if (untitled.length) {
    lines.push(`No title text on source slide ${untitled.join(", ")}. The headline falls back to the first body run and must be re-edited.`);
  }

  lines.push("Comments, revision marks, and macro content are not read.");
  lines.push("Slide count, order, and archetype choice are re-decided during re-design. Any delta against the source belongs in the build receipt.");
  return lines;
}

// --- Output -----------------------------------------------------------------

async function writeJsonFile(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function humanReport(evidence, plan) {
  const lines = [
    "# Deck Source Extraction",
    "",
    `Generated: ${evidence.generatedAt}`,
    `Source: ${evidence.source.path}`,
    `Output: ${evidence.output.dir}${evidence.output.dryRun ? " (dry run, nothing written)" : ""}`,
    "",
    "## Package",
    "",
    `- Slides in presentation order: ${evidence.deck.slideCount}`,
    `- Hidden slides excluded: ${evidence.deck.hiddenSlides.length ? evidence.deck.hiddenSlides.join(", ") : "none"}`,
    `- Authored slide size: ${evidence.deck.slideSize.px ? `${evidence.deck.slideSize.px.width}x${evidence.deck.slideSize.px.height} px` : "unknown"}`,
    `- Masters: ${evidence.deck.masterCount} | Layouts: ${evidence.deck.layoutCount} | Themes: ${evidence.deck.themeCount}`,
    `- Media parts in package: ${evidence.deck.mediaPartCount} | Extracted assets: ${evidence.output.assets.length}`,
    "",
    "## Slides",
    "",
  ];

  for (const slide of evidence.slides) {
    const planSlide = plan.slides.find((item) => item.role.endsWith(`source slide ${slide.number}`));
    const support = supportTexts(slide);
    lines.push(`### ${slide.number}. ${slide.title || "(no title text)"}`);
    lines.push("");
    lines.push(`- Inferred archetype: ${planSlide?.archetype ?? "excluded"} (unresolved placeholder)`);
    lines.push(`- Body runs: ${support.length} across ${slide.blocks.length} block(s)`);
    lines.push(`- Deepest indent level: ${slide.blocks.reduce((max, block) => Math.max(max, ...block.items.map((item) => item.level)), 0)}`);
    lines.push(`- Images: ${slide.images.length ? slide.images.map((image) => `${image.fileName} (${image.px ? `${image.px.width}x${image.px.height} px` : "no extents"})`).join(", ") : "none"}`);
    lines.push(`- Chart: ${slide.hasChart ? "yes" : "no"} | Table: ${slide.hasTable ? "yes" : "no"} | SmartArt: ${slide.hasSmartArt ? "yes" : "no"}`);
    if (slide.graphicLabels.length) lines.push(`- Readable object labels: ${slide.graphicLabels.slice(0, 8).join(" / ")}`);
    lines.push(`- Speaker notes: ${slide.notes ? `${slide.notes.length} chars` : "none"}`);
    lines.push("");
  }

  lines.push("## Source Inventory (evidence only)", "");
  lines.push(`- Font names found: ${evidence.inventory.fontNames.length ? evidence.inventory.fontNames.join(", ") : "none"}`);
  lines.push(`- Color values found: ${evidence.inventory.colorValues.length ? evidence.inventory.colorValues.slice(0, 16).join(", ") : "none"}`);
  lines.push(`- ${evidence.inventory.note}`);
  lines.push("", "## Degradation", "");
  lines.push(...evidence.degradation.map((item) => `- ${item}`));
  lines.push("", "## Writes", "");
  lines.push(`- ${evidence.output.evidenceFile}`);
  lines.push(`- ${evidence.output.planFile}`);
  for (const asset of evidence.output.assets) lines.push(`- ${asset}`);
  if (!evidence.output.assets.length) lines.push("- no media assets");
  lines.push("", "## Next", "");
  lines.push("- Extraction output is evidence for re-design, not a build scaffold or a pixel clone.");
  lines.push("- Run Design Cognition before any layout decision, per `skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md`.");
  lines.push("- Resolve every entry in `extraction.unresolved` in the draft plan before handing it to `skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs`.");
  lines.push("");
  return lines.join("\n");
}

// --- Main -------------------------------------------------------------------

async function main() {
  const args = parseArgs(process.argv);
  const root = repoRoot();
  const sourcePath = resolveFromRoot(process.cwd(), args.source);

  let buffer;
  try {
    buffer = await fs.readFile(sourcePath);
  } catch (error) {
    throw new SourceError(`Cannot read source deck: ${error?.message || error}`);
  }

  let zip;
  try {
    zip = await JSZip.loadAsync(buffer);
  } catch (error) {
    throw new SourceError(`Source is not a readable PPTX (OpenXML ZIP) package: ${error?.message || error}`);
  }

  const deckInfo = await resolveSlideOrder(zip);
  if (deckInfo.order.length === 0) {
    throw new SourceError("Presentation part lists zero slides. Nothing to extract.");
  }

  const deckName = path.basename(sourcePath, path.extname(sourcePath));
  const deckId = slug(deckName, "deck-source");
  const outDir = args.out
    ? resolveFromRoot(process.cwd(), args.out)
    : path.join(root, DEFAULT_OUTPUT_ROOT, `${timestamp()}-${deckId}`);

  const outPosix = toPosix(outDir);
  if (FORBIDDEN_OUTPUT_SEGMENTS.some((segment) => outPosix.includes(segment))) {
    throw new UsageError(`Output folder is a protected path and release gates fail on it: \`${outPosix}\``);
  }

  const slides = [];
  let number = 0;
  const hiddenSlides = [];
  for (const partName of deckInfo.order) {
    number += 1;
    const slide = await extractSlide(zip, partName, number);
    if (slide.hidden) {
      hiddenSlides.push(number);
      continue;
    }
    slides.push(slide);
  }

  if (slides.length === 0) {
    throw new SourceError("Every slide in the presentation is hidden. Nothing to extract.");
  }

  const assetsDir = slides.some((slide) => slide.images.length > 0) ? "assets" : null;
  const assetParts = new Map();
  for (const slide of slides) {
    for (const image of slide.images) {
      if (image.part && !assetParts.has(image.part)) assetParts.set(image.part, image.fileName);
    }
  }

  const plan = draftDeckPlan(collapse(deckName) || deckId, deckId, slides, assetsDir);
  const evidence = {
    generatedAt: new Date().toISOString(),
    generatedBy: "brain-design",
    tool: "skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs",
    mode: "generated deck-source evidence; not stable memory",
    purpose: "evidence for web-deck re-design, never a pixel clone or a build scaffold",
    bridge: "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md",
    source: {
      path: toPosix(path.relative(root, sourcePath)).startsWith("..") ? toPosix(sourcePath) : toPosix(path.relative(root, sourcePath)),
      fileName: path.basename(sourcePath),
      sizeBytes: buffer.byteLength,
      sha256: sha256(buffer),
    },
    deck: {
      slideCount: slides.length,
      hiddenSlides,
      slideSize: {
        emu: deckInfo.slideSizeEmu,
        px: deckInfo.slideSizeEmu
          ? { width: emuToPx(deckInfo.slideSizeEmu.cx), height: emuToPx(deckInfo.slideSizeEmu.cy) }
          : null,
      },
      masterCount: deckInfo.masterCount,
      layoutCount: deckInfo.layoutCount,
      themeCount: deckInfo.themeCount,
      mediaPartCount: deckInfo.mediaPartCount,
    },
    slides,
    inventory: {
      fontNames: uniqueList(slides.flatMap((slide) => slide.fontNames), 80),
      colorValues: uniqueList(slides.flatMap((slide) => slide.colorValues), 120),
      note: "Fonts and colors are recorded as source inventory only. No value here was promoted into a deck-plan token; token values stay unresolved until Color Role Re-Mapping runs.",
    },
    degradation: degradationReport(slides, hiddenSlides),
    output: {
      dir: toPosix(path.relative(root, outDir)).startsWith("..") ? outPosix : toPosix(path.relative(root, outDir)),
      dryRun: args.dryRun,
      evidenceFile: "deck-source-evidence.json",
      planFile: "deck-plan.draft.json",
      assets: [...assetParts.values()].map((fileName) => `assets/${fileName}`),
    },
  };

  if (!args.dryRun) {
    await fs.mkdir(outDir, { recursive: true });
    for (const [partName, fileName] of assetParts) {
      const entry = zip.file(partName);
      if (!entry) continue;
      await fs.mkdir(path.join(outDir, "assets"), { recursive: true });
      await fs.writeFile(path.join(outDir, "assets", fileName), await entry.async("nodebuffer"));
    }
    await writeJsonFile(path.join(outDir, "deck-source-evidence.json"), evidence);
    await writeJsonFile(path.join(outDir, "deck-plan.draft.json"), plan);
  }

  console.log(args.json ? JSON.stringify({ evidence, draftDeckPlan: plan }, null, 2) : humanReport(evidence, plan));
  return 0;
}

main()
  .then((code) => process.exit(code))
  .catch((error) => {
    if (error instanceof UsageError) {
      console.error(`Usage error: ${error.message}`);
      printHelp();
      process.exit(1);
    }
    if (error instanceof SourceError) {
      console.error(`Source error: ${error.message}`);
      process.exit(2);
    }
    console.error(error?.stack || error?.message || String(error));
    process.exit(2);
  });
