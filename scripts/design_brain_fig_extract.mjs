#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { FigmaArchiveParser } from "fig-kiwi/dist/index.esm.js";
import { compileSchema, decodeBinarySchema } from "kiwi-schema";
import { decompress as zstdDecompress } from "fzstd";
import { inflateRaw } from "pako";
import JSZip from "jszip";
import { parseFigBinary } from "openfig-core";

const FIG_PRELUDE = Buffer.from("fig-kiwi", "utf8");
const ZIP_PRELUDE = Buffer.from("PK");
const PNG_PRELUDE = Buffer.from([0x89, 0x50, 0x4e, 0x47]);
const JPEG_PRELUDE = Buffer.from([0xff, 0xd8, 0xff]);
const ZSTD_PRELUDE = Buffer.from([0x28, 0xb5, 0x2f, 0xfd]);

const SECTION_KEYWORDS = [
  ["navigation", ["nav", "navbar", "menu", "header menu"]],
  ["hero", ["hero", "headline", "banner", "header", "above fold"]],
  ["about", ["about", "story", "mission", "vision"]],
  ["services", ["service", "services", "what we do", "solutions"]],
  ["features", ["feature", "features", "benefit", "benefits"]],
  ["process", ["process", "workflow", "step", "steps", "how it works"]],
  ["stats", ["stat", "stats", "metric", "metrics", "counter", "kpi"]],
  ["portfolio", ["portfolio", "case", "case study", "work", "project"]],
  ["gallery", ["gallery", "showcase", "photo", "image grid"]],
  ["pricing", ["pricing", "price", "plan", "plans", "package"]],
  ["team", ["team", "member", "people", "staff"]],
  ["testimonial", ["testimonial", "review", "client", "quote"]],
  ["faq", ["faq", "question", "questions"]],
  ["blog", ["blog", "news", "article", "journal"]],
  ["contact", ["contact", "email", "phone", "address", "location"]],
  ["footer", ["footer", "copyright", "subscribe"]],
  ["commerce", ["shop", "product", "cart", "checkout", "category", "collection"]],
  ["dashboard", ["dashboard", "analytics", "sidebar", "chart", "table", "widget"]],
  ["auth", ["login", "sign in", "register", "password", "account"]],
  ["mobile", ["mobile", "app", "iphone", "android", "screen"]],
];

const TYPE_RULES = [
  ["full website template", ["website", "web design", "template kit", "agency", "portfolio", "wellness", "jewelry"]],
  ["landing page", ["landing", "homepage", "home page"]],
  ["hero/header kit", ["header", "hero"]],
  ["dashboard/ui kit", ["dashboard", "ui kit", "admin", "management", "analytics"]],
  ["ecommerce", ["ecommerce", "shopping", "shop", "store", "product", "jewelry"]],
  ["portfolio", ["portfolio", "photographer", "cv", "resume"]],
  ["mobile app", ["mobile", "package", "app screen"]],
  ["event/entertainment", ["festival", "music", "podcast", "game"]],
  ["technology/saas", ["ai", "platform", "tech", "hosting", "cloud", "file management"]],
  ["travel", ["travel", "tour", "agency", "adventour"]],
];

function parseArgs(argv) {
  const args = {
    source: "Template Website",
    output: ".design-brain/evidence/fig-extracts",
    includeAppleDouble: false,
    writeFullJson: false,
    maxTextSamples: 2500,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === "--source") args.source = argv[++i];
    else if (token === "--output") args.output = argv[++i];
    else if (token === "--include-appledouble") args.includeAppleDouble = true;
    else if (token === "--write-full-json") args.writeFullJson = true;
    else if (token === "--max-text-samples") args.maxTextSamples = Number(argv[++i]);
    else if (token === "--help" || token === "-h") {
      printHelp();
      process.exit(0);
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  return args;
}

function printHelp() {
  console.log(`Usage: node scripts/design_brain_fig_extract.mjs [options]

Options:
  --source PATH              Folder containing .fig files. Default: Template Website
  --output PATH              Evidence output folder. Default: .design-brain/evidence/fig-extracts
  --include-appledouble      Include __MACOSX/._*.fig resource fork files.
  --write-full-json          Also write decoded full-message.json when decoding succeeds.
  --max-text-samples N       Max text samples per file. Default: 2500
`);
}

function repoRoot() {
  return path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
}

function resolveFromRoot(root, value) {
  return path.isAbsolute(value) ? path.normalize(value) : path.resolve(root, value);
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
  return (cleaned || "fig-file").slice(0, 90);
}

function round(value) {
  return typeof value === "number" && Number.isFinite(value) ? Math.round(value * 100) / 100 : value;
}

function ensureJsonSafe(value) {
  return JSON.stringify(
    value,
    (_key, current) => {
      if (current instanceof Uint8Array || Buffer.isBuffer(current)) {
        return { byteLength: current.byteLength, omitted: "binary" };
      }
      return current;
    },
    2,
  );
}

async function writeJson(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, `${ensureJsonSafe(value)}\n`, "utf8");
}

async function writeText(filePath, value) {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, value, "utf8");
}

async function walkFigFiles(root) {
  const found = [];

  async function visit(dir) {
    const entries = await fs.readdir(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        await visit(full);
      } else if (entry.isFile() && entry.name.toLowerCase().endsWith(".fig")) {
        found.push(full);
      }
    }
  }

  await visit(root);
  return found.sort((a, b) => a.localeCompare(b));
}

function isAppleDouble(filePath) {
  const parts = filePath.split(/[\\/]+/);
  return parts.includes("__MACOSX") || path.basename(filePath).startsWith("._");
}

function sha256(buffer) {
  return crypto.createHash("sha256").update(buffer).digest("hex");
}

function detectFormat(buffer) {
  if (buffer.subarray(0, FIG_PRELUDE.length).equals(FIG_PRELUDE)) return "fig-kiwi";
  if (buffer.subarray(0, ZIP_PRELUDE.length).equals(ZIP_PRELUDE)) return "zip";
  return "unknown";
}

function toPlainUint8Array(buffer) {
  const view = new Uint8Array(buffer.byteLength);
  view.set(buffer);
  return view;
}

function guidToString(guid) {
  if (!guid) return null;
  return `${guid.sessionID ?? 0}:${guid.localID ?? "?"}`;
}

function colorToHex(color) {
  if (!color) return null;
  const channel = (value) => {
    const scaled = Math.max(0, Math.min(255, Math.round((value ?? 0) * 255)));
    return scaled.toString(16).padStart(2, "0");
  };
  return `#${channel(color.r)}${channel(color.g)}${channel(color.b)}`;
}

function paintSummary(paint) {
  if (!paint) return null;
  const summary = {
    type: paint.type ?? null,
    visible: paint.visible ?? null,
    opacity: round(paint.opacity),
    color: colorToHex(paint.color),
  };
  return compactObject(summary);
}

function compactObject(value) {
  const result = {};
  for (const [key, current] of Object.entries(value)) {
    if (current === null || current === undefined) continue;
    if (Array.isArray(current) && current.length === 0) continue;
    if (typeof current === "object" && !Array.isArray(current) && Object.keys(current).length === 0) continue;
    result[key] = current;
  }
  return result;
}

function summarizeNode(change) {
  const fills = Array.isArray(change.fillPaints) ? change.fillPaints.map(paintSummary).filter(Boolean) : [];
  const strokes = Array.isArray(change.strokePaints) ? change.strokePaints.map(paintSummary).filter(Boolean) : [];
  const transform = change.transform ?? {};
  const characters =
    typeof change.characters === "string"
      ? change.characters
      : typeof change.textData?.characters === "string"
        ? change.textData.characters
        : null;
  return compactObject({
    guid: guidToString(change.guid),
    parentGuid: guidToString(change.parentIndex?.guid),
    phase: change.phase,
    type: change.type,
    name: change.name,
    visible: change.visible,
    locked: change.locked,
    opacity: round(change.opacity),
    blendMode: change.blendMode,
    position: compactObject({ x: round(transform.m02), y: round(transform.m12) }),
    size: change.size ? compactObject({ x: round(change.size.x), y: round(change.size.y) }) : null,
    characters,
    stackMode: change.stackMode,
    layoutMode: change.layoutMode,
    fills,
    strokes,
    effectCount: Array.isArray(change.effects) ? change.effects.length : undefined,
    exportSettingsCount: Array.isArray(change.exportSettings) ? change.exportSettings.length : undefined,
  });
}

function uniqueList(items, limit = 5000) {
  const seen = new Set();
  const result = [];
  for (const item of items) {
    const cleaned = String(item ?? "").replace(/\s+/g, " ").trim();
    if (!cleaned || seen.has(cleaned)) continue;
    seen.add(cleaned);
    result.push(cleaned);
    if (result.length >= limit) break;
  }
  return result;
}

function keywordCounts(text) {
  const lower = text.toLowerCase();
  const counts = {};
  for (const [name, words] of SECTION_KEYWORDS) {
    let count = 0;
    for (const word of words) {
      const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const matches = lower.match(new RegExp(`\\b${escaped}\\b`, "g"));
      count += matches ? matches.length : 0;
    }
    if (count > 0) counts[name] = count;
  }
  return counts;
}

function inferTemplateTypes(text) {
  const lower = text.toLowerCase();
  const scores = TYPE_RULES.map(([type, words]) => {
    let score = 0;
    for (const word of words) {
      const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      const matches = lower.match(new RegExp(`\\b${escaped}\\b`, "g"));
      score += matches ? matches.length : 0;
    }
    return { type, score };
  })
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score || a.type.localeCompare(b.type));
  return scores.length ? scores : [{ type: "unknown template/product type", score: 0 }];
}

function summarizeMessage(messageOrNodes, relativeSource, maxTextSamples, metadata = {}) {
  const isNodeArray = Array.isArray(messageOrNodes);
  const changes = isNodeArray
    ? messageOrNodes
    : Array.isArray(messageOrNodes.nodeChanges)
      ? messageOrNodes.nodeChanges
      : [];
  const nodes = changes.map(summarizeNode);
  const nodeMap = new Map(nodes.map((node) => [node.guid, node]));

  const names = uniqueList(nodes.map((node) => node.name), 10000);
  const texts = uniqueList(
    nodes
      .map((node) => node.characters)
      .filter((text) => typeof text === "string" && text.trim().length > 0),
    maxTextSamples,
  );

  const nodesByType = {};
  for (const node of nodes) {
    const type = node.type || "UNKNOWN";
    nodesByType[type] = (nodesByType[type] || 0) + 1;
  }

  const canvasNames = nodes.filter((node) => node.type === "CANVAS").map((node) => node.name);
  const topFrames = nodes
    .filter((node) => {
      const parent = nodeMap.get(node.parentGuid);
      return parent?.type === "CANVAS" && ["FRAME", "COMPONENT", "INSTANCE", "GROUP"].includes(node.type);
    })
    .map((node) => ({
      guid: node.guid,
      name: node.name,
      type: node.type,
      size: node.size,
      position: node.position,
      childCount: nodes.filter((child) => child.parentGuid === node.guid).length,
    }))
    .sort((a, b) => (a.position?.y ?? 0) - (b.position?.y ?? 0) || (a.position?.x ?? 0) - (b.position?.x ?? 0));

  const sectionCandidates = [];
  for (const frame of topFrames.slice(0, 40)) {
    const children = nodes
      .filter((node) => node.parentGuid === frame.guid && ["FRAME", "GROUP", "COMPONENT", "INSTANCE", "TEXT"].includes(node.type))
      .map((node) => ({
        name: node.name,
        type: node.type,
        size: node.size,
        position: node.position,
      }))
      .sort((a, b) => (a.position?.y ?? 0) - (b.position?.y ?? 0));
    if (children.length > 0) {
      sectionCandidates.push({ frame: frame.name, sections: children.slice(0, 80) });
    }
  }

  const analysisText = [relativeSource, ...names, ...texts].join("\n");
  const sectionSignals = keywordCounts(analysisText);
  const inferredTemplateTypes = inferTemplateTypes(analysisText);

  const summary = {
    source: relativeSource,
    decoder: metadata.decoder ?? (isNodeArray ? "node-array" : "kiwi-message"),
    messageType: metadata.messageType ?? (!isNodeArray ? messageOrNodes.type : null),
    sessionID: metadata.sessionID ?? (!isNodeArray ? messageOrNodes.sessionID : null),
    ackID: metadata.ackID ?? (!isNodeArray ? messageOrNodes.ackID : null),
    nodeCount: nodes.length,
    nodesByType,
    blobCount: metadata.blobCount ?? (!isNodeArray && Array.isArray(messageOrNodes.blobs) ? messageOrNodes.blobs.length : 0),
    canvasNames,
    topFrameCount: topFrames.length,
    topFrames: topFrames.slice(0, 120),
    sectionSignals,
    inferredTemplateTypes,
    nameCount: names.length,
    textCount: texts.length,
    sectionCandidateGroups: sectionCandidates.length,
    sectionCandidates: sectionCandidates.slice(0, 30),
  };

  return { summary, nodes, names, texts };
}

function bufferKind(buffer) {
  if (buffer.subarray(0, PNG_PRELUDE.length).equals(PNG_PRELUDE)) return { ext: ".png", mime: "image/png" };
  if (buffer.subarray(0, JPEG_PRELUDE.length).equals(JPEG_PRELUDE)) return { ext: ".jpg", mime: "image/jpeg" };
  return null;
}

function isZstd(buffer) {
  return Buffer.from(buffer).subarray(0, ZSTD_PRELUDE.length).equals(ZSTD_PRELUDE);
}

function decompressChunk(chunk) {
  const attempts = isZstd(chunk)
    ? [
        ["zstd", () => zstdDecompress(chunk)],
        ["deflateRaw", () => inflateRaw(chunk)],
      ]
    : [
        ["deflateRaw", () => inflateRaw(chunk)],
        ["zstd", () => zstdDecompress(chunk)],
      ];

  const errors = [];
  for (const [compression, action] of attempts) {
    try {
      return { compression, data: action() };
    } catch (error) {
      errors.push(`${compression}: ${error?.message || error}`);
    }
  }

  throw new Error(`Unable to decompress chunk. ${errors.join(" | ")}`);
}

async function decodeFigBuffer(buffer, itemDir, relativeSource, options) {
  const decoded = {
    ok: false,
    error: null,
    archive: null,
    summary: null,
    previewFiles: [],
  };

  try {
    const doc = parseFigBinary(toPlainUint8Array(buffer));
    decoded.archive = {
      decoder: "openfig-core",
      header: doc.header,
      chunkCount: Array.isArray(doc.rawChunks) ? doc.rawChunks.length : 0,
      chunks: (doc.rawChunks ?? []).map((file, index) => ({
        index,
        compressedBytes: file.byteLength,
        detectedKind: bufferKind(Buffer.from(file))?.mime ?? null,
        zstdFrame: isZstd(file),
      })),
    };

    for (let i = 2; i < (doc.rawChunks ?? []).length; i += 1) {
      const chunkBuffer = Buffer.from(doc.rawChunks[i]);
      const kind = bufferKind(chunkBuffer);
      if (!kind) continue;
      const fileName = `preview-chunk-${i}${kind.ext}`;
      await fs.writeFile(path.join(itemDir, fileName), chunkBuffer);
      decoded.previewFiles.push(fileName);
    }

    const { summary, nodes, names, texts } = summarizeMessage(doc.nodes, relativeSource, options.maxTextSamples, {
      decoder: "openfig-core",
      messageType: doc.message?.type ?? null,
      sessionID: doc.message?.sessionID ?? null,
      ackID: doc.message?.ackID ?? null,
      blobCount: Array.isArray(doc.message?.blobs) ? doc.message.blobs.length : 0,
    });

    await writeJson(path.join(itemDir, "archive.json"), decoded.archive);
    await writeJson(path.join(itemDir, "message-summary.json"), summary);
    await writeJson(path.join(itemDir, "nodes.json"), nodes);
    await writeText(path.join(itemDir, "layer-names.txt"), `${names.join("\n")}\n`);
    await writeText(path.join(itemDir, "text-content.txt"), `${texts.join("\n")}\n`);
    await writeText(path.join(itemDir, "structure.md"), structureMarkdown(summary));

    if (options.writeFullJson) {
      await writeJson(path.join(itemDir, "full-message.json"), doc.message);
    }

    decoded.ok = true;
    decoded.summary = summary;
    return decoded;
  } catch (openfigError) {
    decoded.error = `openfig-core failed, legacy fallback will run. ${openfigError?.message || openfigError}`;
  }

  try {
    const parsed = FigmaArchiveParser.parseArchive(toPlainUint8Array(buffer));
    decoded.archive = {
      header: parsed.header,
      chunkCount: parsed.files.length,
      chunks: parsed.files.map((file, index) => ({
        index,
        compressedBytes: file.byteLength,
        detectedKind: bufferKind(Buffer.from(file))?.mime ?? null,
        zstdFrame: isZstd(file),
      })),
    };

    for (let i = 2; i < parsed.files.length; i += 1) {
      const chunkBuffer = Buffer.from(parsed.files[i]);
      const kind = bufferKind(chunkBuffer);
      if (!kind) continue;
      const fileName = `preview-chunk-${i}${kind.ext}`;
      await fs.writeFile(path.join(itemDir, fileName), chunkBuffer);
      decoded.previewFiles.push(fileName);
    }

    const schemaChunk = decompressChunk(parsed.files[0]);
    const messageChunk = decompressChunk(parsed.files[1]);
    decoded.archive.chunks[0].compression = schemaChunk.compression;
    decoded.archive.chunks[0].inflatedBytes = schemaChunk.data.byteLength;
    decoded.archive.chunks[1].compression = messageChunk.compression;
    decoded.archive.chunks[1].inflatedBytes = messageChunk.data.byteLength;

    const schema = decodeBinarySchema(schemaChunk.data);
    const compiledSchema = compileSchema(schema);
    const message = compiledSchema.decodeMessage(messageChunk.data);
    const { summary, nodes, names, texts } = summarizeMessage(message, relativeSource, options.maxTextSamples);

    await writeJson(path.join(itemDir, "archive.json"), decoded.archive);
    await writeJson(path.join(itemDir, "message-summary.json"), summary);
    await writeJson(path.join(itemDir, "nodes.json"), nodes);
    await writeText(path.join(itemDir, "layer-names.txt"), `${names.join("\n")}\n`);
    await writeText(path.join(itemDir, "text-content.txt"), `${texts.join("\n")}\n`);
    await writeText(path.join(itemDir, "structure.md"), structureMarkdown(summary));

    if (options.writeFullJson) {
      await writeJson(path.join(itemDir, "full-message.json"), message);
    }

    decoded.ok = true;
    decoded.summary = summary;
  } catch (error) {
    decoded.error = error?.stack || error?.message || String(error);
    await writeJson(path.join(itemDir, "decode-error.json"), { source: relativeSource, error: decoded.error });
  }

  return decoded;
}

function structureMarkdown(summary) {
  const lines = [
    "# FIG Template Structure Extract",
    "",
    `Source: ${summary.source}`,
    `Message type: ${summary.messageType || "unknown"}`,
    `Node count: ${summary.nodeCount}`,
    `Canvas pages: ${summary.canvasNames.join(", ") || "none detected"}`,
    `Top frames: ${summary.topFrameCount}`,
    "",
    "## Inferred Template Type",
    "",
    ...summary.inferredTemplateTypes.slice(0, 6).map((item) => `- ${item.type} (${item.score})`),
    "",
    "## Section Signals",
    "",
  ];

  const sectionEntries = Object.entries(summary.sectionSignals).sort((a, b) => b[1] - a[1]);
  lines.push(...(sectionEntries.length ? sectionEntries.map(([key, count]) => `- ${key}: ${count}`) : ["- none detected"]));
  lines.push("", "## Top Frames", "");

  if (summary.topFrames.length === 0) {
    lines.push("- none detected");
  } else {
    for (const frame of summary.topFrames.slice(0, 80)) {
      const size = frame.size ? `${frame.size.x}x${frame.size.y}` : "unknown size";
      lines.push(`- ${frame.name || "(unnamed)"} | ${frame.type} | ${size} | children: ${frame.childCount}`);
    }
  }

  lines.push("", "## Candidate Section Groups", "");
  if (!summary.sectionCandidates.length) {
    lines.push("- none detected");
  } else {
    for (const group of summary.sectionCandidates.slice(0, 12)) {
      lines.push(`### ${group.frame || "(unnamed frame)"}`, "");
      for (const section of group.sections.slice(0, 40)) {
        const size = section.size ? `${section.size.x}x${section.size.y}` : "unknown size";
        lines.push(`- ${section.name || "(unnamed)"} | ${section.type} | ${size}`);
      }
      lines.push("");
    }
  }

  return `${lines.join("\n")}\n`;
}

function safeZipPath(entryName) {
  const parts = entryName.replace(/\\/g, "/").split("/").filter(Boolean);
  if (parts.some((part) => part === "." || part === "..")) return null;
  return path.join(...parts);
}

async function processZip(buffer, itemDir, relativeSource, options) {
  const zip = await JSZip.loadAsync(buffer);
  const entries = [];
  let canvasBuffer = null;
  let canvasEntryName = null;

  for (const entry of Object.values(zip.files)) {
    entries.push({ name: entry.name, dir: entry.dir, date: entry.date?.toISOString?.() ?? null });
    if (entry.dir) continue;

    const safePath = safeZipPath(entry.name);
    if (safePath) {
      const entryBuffer = await entry.async("nodebuffer");
      await fs.mkdir(path.dirname(path.join(itemDir, "raw", safePath)), { recursive: true });
      await fs.writeFile(path.join(itemDir, "raw", safePath), entryBuffer);
    }
  }

  const figEntries = Object.values(zip.files).filter((entry) => !entry.dir && entry.name.toLowerCase().endsWith(".fig"));
  const preferred = zip.file("canvas.fig") || figEntries[0];
  if (preferred) {
    canvasEntryName = preferred.name;
    canvasBuffer = await preferred.async("nodebuffer");
    await fs.writeFile(path.join(itemDir, "canvas.fig"), canvasBuffer);
  }

  await writeJson(path.join(itemDir, "zip-entries.json"), entries);
  return { entries, canvasBuffer, canvasEntryName };
}

async function processFigFile(filePath, index, sourceRoot, runDir, options) {
  const relativeSource = path.relative(sourceRoot, filePath).replace(/\\/g, "/");
  const itemDir = path.join(runDir, `${String(index).padStart(3, "0")}-${slug(path.basename(filePath, ".fig"))}`);
  await fs.mkdir(itemDir, { recursive: true });

  const buffer = await fs.readFile(filePath);
  const format = detectFormat(buffer);
  const record = {
    index,
    source: relativeSource,
    output: path.relative(runDir, itemDir).replace(/\\/g, "/"),
    sizeBytes: buffer.byteLength,
    sha256: sha256(buffer),
    format,
    decoded: false,
    skipped: false,
    error: null,
    zipEntries: 0,
    canvasEntryName: null,
    previewFiles: [],
    summary: null,
  };

  await fs.writeFile(path.join(itemDir, "source.fig"), buffer);

  try {
    let canvasBuffer = null;
    if (format === "zip") {
      const zipResult = await processZip(buffer, itemDir, relativeSource, options);
      record.zipEntries = zipResult.entries.length;
      record.canvasEntryName = zipResult.canvasEntryName;
      canvasBuffer = zipResult.canvasBuffer;
    } else if (format === "fig-kiwi") {
      canvasBuffer = buffer;
      await fs.writeFile(path.join(itemDir, "canvas.fig"), canvasBuffer);
    } else {
      throw new Error(`Unsupported .fig format: ${format}`);
    }

    if (!canvasBuffer) {
      throw new Error("No canvas.fig payload found.");
    }

    const decoded = await decodeFigBuffer(canvasBuffer, itemDir, relativeSource, options);
    record.decoded = decoded.ok;
    record.previewFiles = decoded.previewFiles;
    record.summary = decoded.summary
      ? {
          nodeCount: decoded.summary.nodeCount,
          nodesByType: decoded.summary.nodesByType,
          canvasNames: decoded.summary.canvasNames,
          topFrameCount: decoded.summary.topFrameCount,
          inferredTemplateTypes: decoded.summary.inferredTemplateTypes,
          sectionSignals: decoded.summary.sectionSignals,
        }
      : null;
    if (decoded.error) record.error = decoded.error;
  } catch (error) {
    record.error = error?.stack || error?.message || String(error);
    await writeJson(path.join(itemDir, "extract-error.json"), { source: relativeSource, error: record.error });
  }

  await writeJson(path.join(itemDir, "summary.json"), record);
  return record;
}

function aggregate(records, skipped) {
  const formats = {};
  const templateTypes = {};
  const sectionTotals = {};
  let decodedCount = 0;
  let totalBytes = 0;

  for (const record of records) {
    formats[record.format] = (formats[record.format] || 0) + 1;
    totalBytes += record.sizeBytes;
    if (record.decoded) decodedCount += 1;

    const types = record.summary?.inferredTemplateTypes ?? [];
    for (const item of types.slice(0, 3)) {
      templateTypes[item.type] = (templateTypes[item.type] || 0) + 1;
    }

    const signals = record.summary?.sectionSignals ?? {};
    for (const [key, count] of Object.entries(signals)) {
      sectionTotals[key] = (sectionTotals[key] || 0) + count;
    }
  }

  return {
    sourceFiles: records.length + skipped.length,
    processedFiles: records.length,
    skippedFiles: skipped.length,
    decodedFiles: decodedCount,
    failedFiles: records.filter((record) => !record.decoded).length,
    totalBytes,
    formats,
    templateTypes,
    sectionTotals: Object.fromEntries(Object.entries(sectionTotals).sort((a, b) => b[1] - a[1])),
  };
}

function reportMarkdown(manifest) {
  const lines = [
    "# FIG Template Corpus Extraction",
    "",
    `Generated: ${manifest.generatedAt}`,
    `Source: ${manifest.source}`,
    `Output: ${manifest.output}`,
    "",
    "## Totals",
    "",
    `- Source files: ${manifest.totals.sourceFiles}`,
    `- Processed files: ${manifest.totals.processedFiles}`,
    `- Skipped AppleDouble/resource files: ${manifest.totals.skippedFiles}`,
    `- Decoded files: ${manifest.totals.decodedFiles}`,
    `- Failed files: ${manifest.totals.failedFiles}`,
    `- Total processed bytes: ${manifest.totals.totalBytes}`,
    "",
    "## Formats",
    "",
  ];

  lines.push(...Object.entries(manifest.totals.formats).map(([key, count]) => `- ${key}: ${count}`));
  lines.push("", "## Corpus Section Signals", "");
  lines.push(...Object.entries(manifest.totals.sectionTotals).slice(0, 30).map(([key, count]) => `- ${key}: ${count}`));
  lines.push("", "## Files", "");

  for (const record of manifest.records) {
    const types = record.summary?.inferredTemplateTypes?.slice(0, 3).map((item) => `${item.type} (${item.score})`).join(", ") || "unknown";
    const sections = Object.entries(record.summary?.sectionSignals ?? {})
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([key]) => key)
      .join(", ") || "none";
    lines.push(`### ${String(record.index).padStart(3, "0")} - ${record.source}`, "");
    lines.push(`- Format: ${record.format}`);
    lines.push(`- Decoded: ${record.decoded ? "yes" : "no"}`);
    lines.push(`- Nodes: ${record.summary?.nodeCount ?? "unknown"}`);
    lines.push(`- Top frames: ${record.summary?.topFrameCount ?? "unknown"}`);
    lines.push(`- Inferred type: ${types}`);
    lines.push(`- Section signals: ${sections}`);
    if (record.error) lines.push(`- Error: ${String(record.error).split("\n")[0]}`);
    lines.push("");
  }

  if (manifest.skipped.length) {
    lines.push("## Skipped Files", "");
    for (const item of manifest.skipped) {
      lines.push(`- ${item.source} (${item.reason})`);
    }
    lines.push("");
  }

  lines.push(
    "## Design Brain Learning Notes",
    "",
    "- Treat `.fig` files as product evidence, not just screenshots.",
    "- Read template purpose from file names, page names, frame hierarchy, section names, and text content together.",
    "- A website template standard is scope-based: hero/header kits, landing pages, full websites, ecommerce, dashboards, portfolios, resumes, and mobile kits require different structural depth.",
    "- Do not force a thin section count. Quiet visual language can still require complete navigation, content proof, inner pages, states, responsive variants, and marketplace preview evidence.",
    "- Use decoded node/frame structure as reference insight only. Do not clone exact layout, copywriting, color system, image placement, or component rhythm.",
    "",
  );

  return `${lines.join("\n")}\n`;
}

async function main() {
  const args = parseArgs(process.argv);
  const root = repoRoot();
  const sourceRoot = resolveFromRoot(root, args.source);
  const outputRoot = resolveFromRoot(root, args.output);
  const runName = `${timestamp()}-fig-template-corpus`;
  const runDir = path.join(outputRoot, runName);

  await fs.mkdir(runDir, { recursive: true });
  const allFiles = await walkFigFiles(sourceRoot);
  const records = [];
  const skipped = [];

  let index = 1;
  for (const filePath of allFiles) {
    const relativeSource = path.relative(sourceRoot, filePath).replace(/\\/g, "/");
    if (!args.includeAppleDouble && isAppleDouble(filePath)) {
      skipped.push({ source: relativeSource, reason: "AppleDouble/resource fork file" });
      continue;
    }

    console.log(`[fig-extract] ${index}/${allFiles.length - skipped.length}: ${relativeSource}`);
    const record = await processFigFile(filePath, index, sourceRoot, runDir, args);
    records.push(record);
    index += 1;
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    mode: "generated fig corpus evidence; not stable memory",
    source: path.relative(root, sourceRoot).replace(/\\/g, "/"),
    output: path.relative(root, runDir).replace(/\\/g, "/"),
    decoder: {
      figKiwi: "fig-kiwi 0.0.1 plus kiwi-schema/pako",
      note: "Semantic extraction summarizes node changes. Binary blobs and exact vector geometry are preserved in raw files but not expanded by default.",
    },
    totals: aggregate(records, skipped),
    records,
    skipped,
  };

  await writeJson(path.join(runDir, "manifest.json"), manifest);
  await writeText(path.join(runDir, "fig-extraction-report.md"), reportMarkdown(manifest));
  await writeJson(path.join(outputRoot, "latest.json"), {
    generatedAt: manifest.generatedAt,
    latestRun: manifest.output,
    processedFiles: manifest.totals.processedFiles,
    decodedFiles: manifest.totals.decodedFiles,
    failedFiles: manifest.totals.failedFiles,
  });

  console.log("");
  console.log(`FIG corpus extraction complete: ${manifest.output}`);
  console.log(`Processed ${manifest.totals.processedFiles}, decoded ${manifest.totals.decodedFiles}, skipped ${manifest.totals.skippedFiles}.`);
}

main().catch((error) => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
