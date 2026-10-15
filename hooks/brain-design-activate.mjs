#!/usr/bin/env node
// SessionStart hook for the Codex Design Brain plugin.
// Prints one compact activation block and never blocks the session. A Claude plugin package
// may hold at most 5,000 files, so the account build (scripts/design_brain_build_claude_plugin.py)
// ships skills/presentation-deck/resources/icons as icons.tar.gz; restoreIcons() unpacks it in
// place once per install, so every runtime path stays unchanged. In the source tree the folder
// exists and it is a no-op.

import { existsSync, mkdtempSync, renameSync, rmSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const PLUGIN_ROOT = String(
  process.env.CLAUDE_PLUGIN_ROOT || fileURLToPath(new URL("../", import.meta.url)),
)
  .replace(/\\/g, "/")
  .replace(/\/+$/, "");
const RESOURCES = `${PLUGIN_ROOT}/skills/presentation-deck/resources`;

function restoreIcons() {
  const icons = `${RESOURCES}/icons`;
  const archive = `${RESOURCES}/icons.tar.gz`;
  if (existsSync(icons) || !existsSync(archive)) return "";
  let tmp;
  try {
    tmp = mkdtempSync(`${RESOURCES}/.icons-`);
    const run = spawnSync("tar", ["-xzf", archive, "-C", tmp], { timeout: 25000, stdio: "ignore" });
    if (run.status !== 0) throw new Error("tar failed");
    renameSync(`${tmp}/icons`, icons);
    return "";
  } catch {
    if (existsSync(icons)) return ""; // a parallel session restored it first
    return `Icon library not unpacked: extract ${archive} with tar -xzf before icon work.`;
  } finally {
    if (tmp) rmSync(tmp, { recursive: true, force: true });
  }
}

try {
  process.stdout.write(
    [
      "Codex Design Brain v2.8.0 available. Only during this plugin's use: Main (Claude Fable 5.1 on Claude Code; GPT-6 Astra on Codex) + ONE General Design Production Engineer: on Claude Code the plugin agent codex-design:general-design-production-engineer (claude-opus-5-5, effort xhigh), on Codex gpt-6.1-sol at reasoning_effort=xhigh; Main has auto-full trust for creative direction and PASS/REVISE. Unrelated work does not inherit these rules.",
      "Visual inspection: load .design-brain/VISUAL_INSPECTION_PROTOCOL.md. Main + Engineer inspect original-source overview/detail/context evidence; empty or stale visual receipts never PASS.",
    "Protected plugin changes require owner verification; reuse verification already satisfied for the authorized scope.",
      "Shared memory: load .design-brain/LOCAL_MEMORY_POLICY.md. Use the bundled Supabase/local adapter. Engineer reads/searches; Main updates/readbacks positive and negative decisions, reconciles queued operations and refreshes offline cache. No Agent Core memory dependency.",
      "Owner calibration mode (2026-10-14): for PPTX design builds deliver the complete PPTX only, no delivery package (zip/START_HERE/guides/preview kit) until the owner says exactly 'kita mulai jalur produksi'; solve every correction properly, never with a safe or minimalist fallback.",
      "New native PPTX only: 10 x 5.625 inches landscape; read skills/presentation-deck/workflows/PPTX_SIZE_POLICY.md. PPTX sourced images also require skills/presentation-deck/workflows/PPTX_IMAGE_SELECTION_POLICY.md: Main reviews, takes over search after two rejected rounds, and assigns exact slides/crops. Ask missing size for other platforms. Authorized host subagents use .design-brain/runtime/HOST_DESIGN_PRODUCTION_SPECIALIST.md.",
      `Presentation design template work: read ${PLUGIN_ROOT}/PRESENTATION_TEMPLATE_GUIDE.md in full first (owner standard). On gates the plugin files win; on design taste and file construction the guide wins.`,
      ...[restoreIcons()].filter(Boolean),
      "",
    ].join("\n"),
  );
} catch {
  // Activation notice is advisory only. Never fail the session over it.
}

process.exit(0);
