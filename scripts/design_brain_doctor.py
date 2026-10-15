#!/usr/bin/env python
"""Doctor checks for Brain Design runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]

RUNTIME_FILES = [
    ".design-brain/runtime/README.md",
    ".design-brain/runtime/DESIGN_AGENT_RUNTIME.md",
    ".design-brain/runtime/COMMAND_REGISTRY.md",
    ".design-brain/runtime/TOOL_REGISTRY.md",
    ".design-brain/runtime/PERMISSION_MODES.md",
    ".design-brain/runtime/HOOKS.md",
    ".design-brain/runtime/SESSION_STATE.md",
    ".design-brain/runtime/REPAIR_TICKETS.md",
    ".design-brain/runtime/CONTEXT_COMPACTION.md",
    ".design-brain/runtime/DOCTOR_STATUS.md",
    ".design-brain/runtime/hooks.example.json",
]

RUNTIME_SCHEMAS = [
    ".design-brain/runtime/schemas/command-registry-schema.json",
    ".design-brain/runtime/schemas/tool-registry-schema.json",
    ".design-brain/runtime/schemas/session-state-schema.json",
    ".design-brain/runtime/schemas/repair-ticket-schema.json",
    ".design-brain/runtime/schemas/hook-config-schema.json",
    ".design-brain/runtime/schemas/runtime-result-schema.json",
    ".design-brain/runtime/schemas/permission-mode-schema.json",
    ".design-brain/runtime/schemas/compact-context-schema.json",
]

RUNTIME_SCRIPTS = [
    "scripts/design_brain_runtime.py",
    "scripts/design_brain_command_router.py",
    "scripts/design_brain_tool_registry.py",
    "scripts/design_brain_permission.py",
    "scripts/design_brain_repair_ticket.py",
    "scripts/design_brain_doctor.py",
    "scripts/design_brain_status_runtime.py",
    "scripts/design_brain_context_compact.py",
    "scripts/design_brain_runtime_smoke_test.py",
]

REFERENCE_USAGE_FILES = [
    ".design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md",
    ".design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json",
    ".design-brain/lifecycle/brand-reference-usage-schema.json",
    ".design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md",
    "scripts/design_brain_reference_usage_gate.py",
    "scripts/design_brain_reference_usage_smoke_test.py",
    "scripts/design_brain_reference_usage_receipt_check.py",
]

SECTION_LAYOUT_FILES = [
    ".design-brain/SECTION_LAYOUT_EXTRACTION_LIBRARY.md",
    ".design-brain/SECTION_LAYOUT_HYPER_ACCURACY_GATE.md",
    ".design-brain/SECTION_LAYOUT_MATCHING_GATE.md",
    ".design-brain/section-layout-library/README.md",
    ".design-brain/section-layout-library/pattern-schema.json",
    ".design-brain/templates/SECTION_LAYOUT_PATTERN.md",
    "scripts/design_brain_section_layout_extract.py",
    "scripts/design_brain_section_layout_matching_smoke_test.py",
    "scripts/design_brain_section_layout_smoke_test.py",
]

DESIGN_CRAFT_ADAPTER_FILES = [
    ".design-brain/adapters/design-craft/SKILL.md",
    ".design-brain/adapters/design-craft/README.md",
    ".design-brain/adapters/design-craft/CRAFT_TOOL_ADAPTER.md",
    ".design-brain/adapters/design-craft/CRAFT_OUTPUT_CONTRACT.md",
    ".design-brain/adapters/design-craft/BRAIN_DESIGN_COMPATIBILITY.md",
    ".design-brain/adapters/design-craft/scripts/craft_adapter.py",
    ".design-brain/adapters/design-craft/scripts/craft_adapter_smoke_test.py",
    ".design-brain/adapters/design-craft/scripts/search.py",
    ".design-brain/adapters/design-craft/schemas/craft-request-schema.json",
    ".design-brain/adapters/design-craft/schemas/craft-result-schema.json",
    ".design-brain/adapters/design-craft/schemas/brain-design-compatibility-schema.json",
]

WEB_DECK_FILES = [
    "skills/presentation-deck/design/WEB_DECK_INTELLIGENCE.md",
    "skills/presentation-deck/design/WEB_DECK_STAGE_GATE.md",
    "skills/presentation-deck/design/WEB_DECK_MOTION_GRAMMAR.md",
    "skills/presentation-deck/design/WEB_DECK_DELIVERY_CONTRACT.md",
    "skills/presentation-deck/design/DECK_SOURCE_BRIDGE.md",
    "skills/presentation-deck/resources/web-deck/README.md",
    "skills/presentation-deck/resources/web-deck/deck-plan-schema.json",
    "skills/presentation-deck/resources/web-deck/stage-base.css",
    "skills/presentation-deck/resources/web-deck/deck-runtime.js",
    "skills/presentation-deck/design/craft/deck-motion.md",
    "skills/presentation-deck/design/craft/web-deck-stage-fidelity.md",
    "skills/presentation-deck/resources/seed-packs/web-deck/layouts.md",
    "skills/presentation-deck/resources/seed-packs/web-deck/checklist.md",
    "skills/presentation-deck/resources/seed-packs/web-deck/content-patterns.md",
    "skills/presentation-deck/resources/seed-packs/web-deck/design-system-scope.md",
    "skills/presentation-deck/resources/WEB_DECK_RECEIPT.md",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs",
    "skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs",
    "skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs",
    "skills/presentation-deck/tests/design_brain_web_deck_smoke_test.mjs",
]


def design_craft_root() -> Path:
    return ROOT / ".design-brain" / "adapters" / "design-craft"


def has_typeui_marker(path: Path) -> bool:
    marker = "TYPEUI_SH_" + "MANAGED_START"
    try:
        return marker in path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False


def run_doctor() -> dict:
    required = RUNTIME_FILES + RUNTIME_SCHEMAS + RUNTIME_SCRIPTS + REFERENCE_USAGE_FILES + SECTION_LAYOUT_FILES + DESIGN_CRAFT_ADAPTER_FILES + WEB_DECK_FILES
    missing = [path for path in required if not (ROOT / path).exists()]
    reference_registry_json_valid = True
    reference_registry_error = ""
    registry_path = ROOT / ".design-brain" / "TEMPLATE_REFERENCE_USAGE_REGISTRY.json"
    if registry_path.exists():
        try:
            json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            reference_registry_json_valid = False
            reference_registry_error = str(exc)
    state_root = ROOT / ".design-brain" / "runtime" / "state"
    state_root.mkdir(parents=True, exist_ok=True)
    writable = state_root.is_dir()
    forbidden = []
    for rel in ["downloads/MiroFish", "downloads/OASIS", "downloads/claude-code-main", "downloads/_analysis/claude-code-main"]:
        if (ROOT / rel).exists():
            forbidden.append(rel)
    active_roots = [p for p in [ROOT / ".design-brain", ROOT / "scripts", ROOT / ".agents", ROOT / "tests"] if p.exists()]
    backup_files = []
    typeui_markers = []
    for base in active_roots:
        for path in base.rglob("*"):
            if path.is_file():
                rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
                if path.name.endswith(".orig") or ".bak-" in path.name or ".backup-" in path.name:
                    backup_files.append(rel_path)
                if rel_path == ".agents/skills/design-system/SKILL.md" or rel_path.startswith(".design-brain/typeui-skills/"):
                    continue
                if path.suffix.lower() in {".md", ".py", ".json", ".txt"} and has_typeui_marker(path):
                    typeui_markers.append(rel_path)
    bundled_craft_adapter = design_craft_root() / "scripts" / "craft_adapter.py"
    checks = {
        "runtimeDocs": not [p for p in RUNTIME_FILES if not (ROOT / p).exists()],
        "runtimeSchemas": not [p for p in RUNTIME_SCHEMAS if not (ROOT / p).exists()],
        "runtimeScripts": not [p for p in RUNTIME_SCRIPTS if not (ROOT / p).exists()],
        "referenceUsageFiles": not [p for p in REFERENCE_USAGE_FILES if not (ROOT / p).exists()],
        "sectionLayoutFiles": not [p for p in SECTION_LAYOUT_FILES if not (ROOT / p).exists()],
        "designCraftBundledAdapterFiles": not [p for p in DESIGN_CRAFT_ADAPTER_FILES if not (ROOT / p).exists()],
        "webDeckFiles": not [p for p in WEB_DECK_FILES if not (ROOT / p).exists()],
        "referenceUsageRegistryJson": reference_registry_json_valid,
        "stateWritable": writable,
        "designCraftAdapterPresent": bundled_craft_adapter.exists(),
        "packageIntegrityAvailable": (ROOT / "scripts" / "design_brain_package_integrity.py").exists(),
        "noForbiddenSourceDirs": not forbidden,
        "noBackupFiles": not backup_files,
        "noTypeuiMarkers": not typeui_markers,
    }
    failures = []
    if missing:
        failures.append({"missing": missing})
    if not reference_registry_json_valid:
        failures.append({"referenceUsageRegistryJson": reference_registry_error})
    if forbidden:
        failures.append({"forbiddenSourceDirs": forbidden})
    if backup_files:
        failures.append({"backupFiles": backup_files[:20]})
    if typeui_markers:
        failures.append({"typeuiMarkers": typeui_markers[:20]})
    status = "PASS" if all(checks.values()) and not failures else "BLOCKED"
    return {"status": status, "checks": checks, "failures": failures}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Brain Design runtime doctor.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = run_doctor()
    print(json.dumps(payload, indent=2) if args.json else ("PASS" if payload["status"] == "PASS" else json.dumps(payload, indent=2)))
    return 0 if payload["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
