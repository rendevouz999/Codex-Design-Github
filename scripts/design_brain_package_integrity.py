#!/usr/bin/env python
"""Validate Brain Design v2.8.0 source and exported ZIP package integrity."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True

from design_brain_process_utils import python_command, resolve_python_invocation, run_command as run_process_command


PYTHON_INVOCATION = resolve_python_invocation()

PACKAGE_VERSION = "2.8.0"
FINAL_ZIP_NAME = "brain-design-v2.8.0-web-deck-medium.zip"

PPTX_NATIVE_MANDATORY_FILES = [
    "skills/presentation-deck/workflows/native.md",
    "skills/presentation-deck/provenance/adoption.json",
    "skills/presentation-deck/resources/routing.json",
    "skills/presentation-deck/resources/receipt-schema.json",
    "skills/presentation-deck/provenance/ppt-master-LICENSE",
    "skills/presentation-deck/runtime/presentation.py",
    "skills/presentation-deck/runtime/routing.py",
    "skills/presentation-deck/tests/design_brain_pptx_smoke_test.py",
]


def py_command(args: list[str]) -> list[str]:
    return python_command(args, PYTHON_INVOCATION)


def typeui_marker() -> str:
    return "TYPEUI_SH_" + "MANAGED_START"


SIMULATION_MANDATORY_FILES = [
    ".design-brain/DESIGN_SIMULATION_LAYER.md",
    ".design-brain/design-simulation/agents.json",
    ".design-brain/design-simulation/verdict-schema.json",
    ".design-brain/templates/DESIGN_SIMULATION_VERDICT.md",
    "scripts/design_brain_design_simulate.py",
    "scripts/design_brain_design_sim_smoke_test.py",
    "scripts/design_brain_process_utils.py",
    "scripts/design_brain_process_utils_smoke_test.py",
]

POST_BUILD_MANDATORY_FILES = [
    ".design-brain/POST_BUILD_COMPLETION_GATE.md",
    ".design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md",
    ".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md",
    ".design-brain/post-build/design-system-receipt-schema.json",
    ".design-brain/post-build/post-build-audit-schema.json",
    ".design-brain/post-build/batch-similarity-schema.json",
    ".design-brain/templates/DESIGN_SYSTEM_RECEIPT.md",
    ".design-brain/templates/POST_BUILD_AUDIT_RECEIPT.md",
    ".design-brain/templates/BATCH_SIMILARITY_AUDIT_RECEIPT.md",
    "scripts/design_brain_post_build_audit.py",
    "scripts/design_brain_design_system_check.py",
    "scripts/design_brain_batch_similarity_audit.py",
    "scripts/design_brain_build_session.py",
    "scripts/design_brain_sequential_provenance_check.py",
    "scripts/design_brain_post_build_smoke_test.py",
]

COGNITION_MANDATORY_FILES = [
    ".design-brain/DESIGN_COGNITION_CONTRACT.md",
    ".design-brain/DESIGN_COGNITION_GATE.md",
    ".design-brain/design-cognition/design-cognition-receipt-schema.json",
    ".design-brain/templates/DESIGN_COGNITION_RECEIPT.md",
    ".design-brain/templates/DESIGN_COGNITION_RECEIPT.json",
    "scripts/design_brain_design_cognition_check.py",
    "scripts/design_brain_design_cognition_smoke_test.py",
]

LAYOUT_MANDATORY_FILES = [
    ".design-brain/BUILD_SESSION_LIFECYCLE.md",
    ".design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md",
    ".design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md",
    ".design-brain/IDEA_RECOVERY_CORPUS.md",
    ".design-brain/idea-recovery-corpus.example.json",
    ".design-brain/lifecycle/build-session-schema.json",
    ".design-brain/lifecycle/layout-fingerprint-schema.json",
    ".design-brain/lifecycle/reference-layout-audit-schema.json",
    ".design-brain/lifecycle/ai-pairwise-layout-audit-schema.json",
    ".design-brain/templates/LAYOUT_FINGERPRINT.md",
    ".design-brain/templates/REFERENCE_LAYOUT_AUDIT_RECEIPT.md",
    ".design-brain/templates/AI_PAIRWISE_LAYOUT_AUDIT_RECEIPT.md",
    "scripts/design_brain_layout_similarity_audit.py",
    "scripts/design_brain_build_session.py",
    "scripts/design_brain_sequential_layout_smoke_test.py",
]

SUBAGENT_MANDATORY_FILES = [
    ".design-brain/SUBAGENT_ORCHESTRATION_LAYER.md",
    ".design-brain/SUBAGENT_RECEIPT_SEMANTIC_VALIDATOR.md",
    ".design-brain/design-subagents/README.md",
    ".design-brain/design-subagents/agents.json",
    ".design-brain/design-subagents/subagent-schema.json",
    ".design-brain/design-subagents/orchestration-receipt-schema.json",
    ".design-brain/design-subagents/semantic-validation-schema.json",
    ".design-brain/design-subagents/semantic-validation-rules.json",
    ".design-brain/templates/SUBAGENT_ORCHESTRATION_RECEIPT.md",
    "scripts/design_brain_subagent_orchestrate.py",
    "scripts/design_brain_subagent_receipt_validate.py",
    "scripts/design_brain_subagent_smoke_test.py",
    "scripts/design_brain_subagent_semantic_smoke_test.py",
]

CRAFT_CONTRACT_MANDATORY_FILES = [
    ".design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md",
]

RUNTIME_MANDATORY_FILES = [
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
    ".design-brain/runtime/schemas/command-registry-schema.json",
    ".design-brain/runtime/schemas/tool-registry-schema.json",
    ".design-brain/runtime/schemas/session-state-schema.json",
    ".design-brain/runtime/schemas/repair-ticket-schema.json",
    ".design-brain/runtime/schemas/hook-config-schema.json",
    ".design-brain/runtime/schemas/runtime-result-schema.json",
    ".design-brain/runtime/schemas/permission-mode-schema.json",
    ".design-brain/runtime/schemas/compact-context-schema.json",
    "scripts/design_brain_runtime.py",
    "scripts/design_brain_command_router.py",
    "scripts/design_brain_tool_registry.py",
    "scripts/design_brain_permission.py",
    "scripts/design_brain_repair_ticket.py",
    "scripts/design_brain_context_compact.py",
    "scripts/design_brain_status_runtime.py",
    "scripts/design_brain_doctor.py",
    "scripts/design_brain_runtime_smoke_test.py",
    "scripts/design_brain_craft_adapter_bridge_smoke_test.py",
]

DESIGN_CRAFT_ADAPTER_CORE_FILES = [
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


def bundled_design_craft_adapter_files() -> list[str]:
    adapter_root = Path(__file__).resolve().parents[1] / ".design-brain" / "adapters" / "design-craft"
    if not adapter_root.exists():
        return DESIGN_CRAFT_ADAPTER_CORE_FILES
    files: list[str] = []
    for path in sorted(adapter_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(adapter_root).as_posix()
        if (
            relative.startswith("exports/")
            or relative.startswith("design-craft-backups/")
            or "__pycache__/" in relative
            or relative.endswith(".pyc")
            or relative.endswith(".zip")
            or relative.endswith(".local.json")
        ):
            continue
        files.append(f".design-brain/adapters/design-craft/{relative}")
    return files or DESIGN_CRAFT_ADAPTER_CORE_FILES


DESIGN_CRAFT_ADAPTER_MANDATORY_FILES = bundled_design_craft_adapter_files()

REFERENCE_USAGE_MANDATORY_FILES = [
    ".design-brain/TEMPLATE_REFERENCE_USAGE_POLICY.md",
    ".design-brain/TEMPLATE_REFERENCE_USAGE_REGISTRY.json",
    ".design-brain/lifecycle/brand-reference-usage-schema.json",
    ".design-brain/templates/BRAND_REFERENCE_USAGE_RECORD.md",
    "scripts/design_brain_reference_usage_gate.py",
    "scripts/design_brain_reference_usage_smoke_test.py",
    "scripts/design_brain_reference_usage_receipt_check.py",
]

SECTION_LAYOUT_MANDATORY_FILES = [
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

WEB_DECK_MANDATORY_FILES = [
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

RELEASE_REPORT_MANDATORY_FILES = [
    "reports/brain-design-runtime-upgrade/RUNTIME_UPGRADE_REPORT.md",
    "reports/brain-design-runtime-upgrade/CLAUDE_CODE_ARCHITECTURE_STUDY.md",
    "reports/brain-design-runtime-upgrade/claude-code-adaptation-boundary.md",
    "reports/brain-design-total-integration/TOTAL_INTEGRATION_STABILIZATION_REPORT.md",
    "reports/brain-design-total-integration/INPUT_REPORT_DIGEST.md",
    "reports/brain-design-total-integration/cleanup/CLEANUP_PLAN.md",
    "reports/brain-design-total-integration/cleanup/cleanup-manifest.json",
]

MANDATORY_FILES = [
    ".design-brain/LOCAL_MEMORY_POLICY.md",
    "scripts/design_brain_local_memory.py",
    "capabilities/design-memory/capability.json",
    "capabilities/design-memory/supabase.project.json",
    "scripts/design_brain_memory_adapter.py",
    "scripts/design_brain_memory_supabase.sql",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.txt",
    "package.json",
    "package-lock.json",
    ".gitignore",
    "PUBLIC_PACKAGE_NOTES.md",
    "PACKAGE_MANIFEST.generated.json",
    ".design-brain/VERSION.md",
    ".design-brain/MANIFEST.json",
    ".design-brain/MIGRATION_LOG.md",
    ".design-brain/AUTOLOAD_POLICY.md",
    ".design-brain/WORKFLOW_TRIGGER_MAP.md",
    ".design-brain/SOURCE_OF_TRUTH_MAP.md",
    "scripts/install_design_brain.py",
    "scripts/design_brain_package_integrity.py",
    "scripts/design_brain_export_package.py",
    "scripts/design_brain_router_smoke_test.py",
] + SIMULATION_MANDATORY_FILES + POST_BUILD_MANDATORY_FILES + COGNITION_MANDATORY_FILES + LAYOUT_MANDATORY_FILES + SUBAGENT_MANDATORY_FILES + CRAFT_CONTRACT_MANDATORY_FILES + RUNTIME_MANDATORY_FILES + DESIGN_CRAFT_ADAPTER_MANDATORY_FILES + REFERENCE_USAGE_MANDATORY_FILES + SECTION_LAYOUT_MANDATORY_FILES + WEB_DECK_MANDATORY_FILES + PPTX_NATIVE_MANDATORY_FILES + RELEASE_REPORT_MANDATORY_FILES

FORBIDDEN_ZIP_PATTERNS = [
    ".design-brain/local-memory/*",
    ".git/*",
    ".design-brain-backups/*",
    "*/.design-brain-backups/*",
    "node_modules/*",
    "*/node_modules/*",
    "__pycache__/*",
    "*/__pycache__/*",
    "*.pyc",
    "*.bak-*",
    "*.backup-*",
    "*.orig",
    "*.tmp",
    "*.old",
    ".DS_Store",
    "*/.DS_Store",
    ".env",
    ".env.*",
    "*/.env",
    "*/.env.*",
    "exports/*",
    "*/exports/*",
    ".design-brain/FIGMA_OUTPUT_TARGET.local.json",
    ".design-brain/idea-recovery-corpus.local.json",
    ".design-brain/tmp/*",
    ".design-brain/exports/*",
    ".design-brain/runtime/state/*",
    ".design-brain/runtime/hooks.local.json",
    ".design-brain/adapters/design-craft/exports/*",
    ".design-brain/adapters/design-craft/design-craft-backups/*",
    ".design-brain/adapters/design-craft/data/user_extensions.local.json",
    "Template Website/*",
    "references/*",
    "downloads/claude-code-main/*",
    "downloads/_analysis/claude-code-main/*",
    "claude-code-main/*",
    "mirofish/*",
    "MiroFish/*",
    "mirofish-cli/*",
    "OASIS/*",
    ".agents/skills/design-system/SKILL.md",
    "skills/design-system/SKILL.md",
    ".design-brain/typeui-skills/*/DESIGN.md",
    ".design-brain/typeui-skills/raw/*",
    ".design-brain/typeui-skills/extracted/*",
]

NATIVE_ADAPTATION_NOTE = (
    "This Design Simulation Layer is a Brain Design-native implementation inspired by the MiroFish-style workflow pattern"
)


@dataclass
class IntegrityResult:
    mode: str
    target: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def add(self, message: str) -> None:
        self.info.append(message)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Brain Design package integrity.")
    parser.add_argument("--root", default="", help="Source root. Defaults to this package root.")
    parser.add_argument("--zip", default="", help="ZIP to validate.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--skip-runtime", action="store_true")
    parser.add_argument("--runtime-timeout", type=int, default=180, help="Overall runtime budget hint for nested checks.")
    parser.add_argument("--command-timeout", type=int, default=60, help="Timeout for each runtime subprocess command.")
    parser.add_argument("--full-runtime", action="store_true", help="Run bounded full simulation smoke after quick smoke.")
    parser.add_argument("--process-smoke-repeat", type=int, default=3, help="Repeat count for process utils smoke.")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def run_command(root: Path, args: list[str], timeout: int = 120, verbose: bool = False) -> tuple[int, str]:
    result = run_process_command(args, cwd=root, timeout=timeout, verbose=verbose)
    combined = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.timedOut:
        combined = (
            f"TIMEOUT after {timeout}s; killed process tree: {result.command}\n"
            f"killStrategy={result.killStrategy}; killedPids={result.killedPids}\n"
            f"stdout:\n{result.stdoutExcerpt}\n"
            f"stderr:\n{result.stderrExcerpt}"
        ).strip()
    return result.returncode, combined


def run_command_split(root: Path, args: list[str], timeout: int = 120, verbose: bool = False) -> tuple[int, str, str]:
    result = run_process_command(args, cwd=root, timeout=timeout, verbose=verbose)
    stderr = result.stderr
    if result.timedOut:
        stderr = (
            f"TIMEOUT after {timeout}s; killed process tree: {result.command}\n"
            f"killStrategy={result.killStrategy}; killedPids={result.killedPids}\n"
            f"stdout:\n{result.stdoutExcerpt}\n"
            f"stderr:\n{result.stderrExcerpt}"
        ).strip()
    return result.returncode, result.stdout.strip(), stderr.strip()


def load_json(path: Path, result: IntegrityResult, label: str) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        result.error(f"{label} invalid JSON: {exc}")
        return {}


def parse_version_text(text: str) -> str:
    import re

    match = re.search(r"v?(\d+\.\d+\.\d+)", text)
    return match.group(1) if match else ""


def check_versions(root: Path, result: IntegrityResult) -> None:
    package = load_json(root / "package.json", result, "package.json")
    manifest = load_json(root / ".design-brain" / "MANIFEST.json", result, "MANIFEST.json")
    versions = {
        "package.json": str(package.get("version", "")),
        ".design-brain/MANIFEST.json": str(manifest.get("version", "")),
        ".design-brain/VERSION.md": parse_version_text(read_text(root / ".design-brain" / "VERSION.md")),
    }
    lock_path = root / "package-lock.json"
    if lock_path.exists():
        lock = load_json(lock_path, result, "package-lock.json")
        versions["package-lock.json"] = str(lock.get("version", ""))
        packages = lock.get("packages", {})
        if isinstance(packages, dict) and isinstance(packages.get(""), dict):
            versions["package-lock.json packages['']"] = str(packages[""].get("version", ""))
    for name, value in versions.items():
        if value != PACKAGE_VERSION:
            result.error(f"Version mismatch: {name} has {value!r}, expected {PACKAGE_VERSION!r}")
    if not any("Version mismatch" in error for error in result.errors):
        result.add(f"Version sync: {PACKAGE_VERSION}")


def validate_agents_payload(payload: dict[str, object], result: IntegrityResult, label: str) -> None:
    agents = payload.get("agents")
    if not isinstance(agents, list) or not agents:
        result.error(f"{label} must contain a non-empty agents array.")
        return
    for index, agent in enumerate(agents, start=1):
        if not isinstance(agent, dict):
            result.error(f"{label} agent #{index} must be an object.")
            continue
        for key in ("id", "name", "role", "focus"):
            if not isinstance(agent.get(key), str) or not str(agent.get(key)).strip():
                result.error(f"{label} agent #{index} missing {key}.")
        if not isinstance(agent.get("checklist"), list) and not isinstance(agent.get("evaluation_axes"), list):
            result.error(f"{label} agent #{index} missing checklist/evaluation_axes.")
        if not isinstance(agent.get("vote_rules"), str) and not isinstance(agent.get("verdict_behavior"), str):
            result.error(f"{label} agent #{index} missing vote_rules/verdict_behavior.")


def validate_verdict_schema(payload: dict[str, object], result: IntegrityResult, label: str) -> None:
    required = payload.get("required")
    if not isinstance(required, list):
        result.error(f"{label} missing required array.")
        return
    needed = {
        "runId",
        "artifactDir",
        "verdict",
        "status",
        "confidence",
        "productFamily",
        "mode",
        "scores",
        "blockers",
        "requiredRepairs",
        "recommendedImprovements",
        "routing",
        "cognition",
        "layoutOriginality",
        "layoutOriginalityStatus",
        "referenceLayoutRisk",
        "aiPairwiseLayoutRisk",
        "requiredLayoutRepairs",
        "agentVotes",
        "manifestPath",
        "reportPath",
        "verdictPath",
    }
    missing = sorted(needed - set(str(item) for item in required))
    if missing:
        result.error(f"{label} required fields missing: {missing}")


def check_mandatory_source(root: Path, result: IntegrityResult) -> None:
    for path in MANDATORY_FILES:
        if not (root / path).is_file():
            result.error(f"Missing mandatory source file: {path}")
    manifest = load_json(root / ".design-brain" / "MANIFEST.json", result, "MANIFEST.json")
    managed = set(str(item).replace("\\", "/") for item in manifest.get("managed_files", []) if isinstance(item, str))
    mandatory = set(str(item).replace("\\", "/") for item in manifest.get("mandatory_files", []) if isinstance(item, str))
    for path in SIMULATION_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Simulation file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Simulation file not listed in mandatory_files: {path}")
    for path in POST_BUILD_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Post-build file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Post-build file not listed in mandatory_files: {path}")
    for path in COGNITION_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Cognition file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Cognition file not listed in mandatory_files: {path}")
    for path in LAYOUT_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Lifecycle/layout file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Lifecycle/layout file not listed in mandatory_files: {path}")
    for path in SUBAGENT_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Subagent orchestration file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Subagent orchestration file not listed in mandatory_files: {path}")
    for path in CRAFT_CONTRACT_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Design Craft contract file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Design Craft contract file not listed in mandatory_files: {path}")
    for path in RUNTIME_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Runtime file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Runtime file not listed in mandatory_files: {path}")
    for path in DESIGN_CRAFT_ADAPTER_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Bundled Design Craft adapter file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Bundled Design Craft adapter file not listed in mandatory_files: {path}")
    for path in REFERENCE_USAGE_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Reference usage file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Reference usage file not listed in mandatory_files: {path}")
    for path in SECTION_LAYOUT_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Section layout file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Section layout file not listed in mandatory_files: {path}")
    for path in WEB_DECK_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Web deck file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Web deck file not listed in mandatory_files: {path}")
    for path in PPTX_NATIVE_MANDATORY_FILES:
        if path not in managed or path not in mandatory:
            result.error(f"Native PPTX file must be managed and mandatory: {path}")
    for path in RELEASE_REPORT_MANDATORY_FILES:
        if path not in managed:
            result.error(f"Release report evidence file not listed in managed_files: {path}")
        if path not in mandatory:
            result.error(f"Release report evidence file not listed in mandatory_files: {path}")
    result.add("Simulation, post-build, cognition, lifecycle/layout, subagent orchestration, craft-contract, runtime, bundled Design Craft adapter, reference usage, section layout, web deck, and release report evidence mandatory source files: checked")


def check_subagent_metadata_source(root: Path, result: IntegrityResult) -> None:
    agents = load_json(root / ".design-brain" / "design-subagents" / "agents.json", result, "design-subagents/agents.json")
    schema = load_json(root / ".design-brain" / "design-subagents" / "subagent-schema.json", result, "design-subagents/subagent-schema.json")
    receipt_schema = load_json(root / ".design-brain" / "design-subagents" / "orchestration-receipt-schema.json", result, "design-subagents/orchestration-receipt-schema.json")
    semantic_schema = load_json(root / ".design-brain" / "design-subagents" / "semantic-validation-schema.json", result, "design-subagents/semantic-validation-schema.json")
    semantic_rules = load_json(root / ".design-brain" / "design-subagents" / "semantic-validation-rules.json", result, "design-subagents/semantic-validation-rules.json")
    if agents.get("schema") != "design-brain.design-subagents.agents.v1":
        result.error("design-subagents/agents.json schema mismatch.")
    agent_list = agents.get("agents")
    expected_ids = {
        "reference_visual_analyst",
        "style_dna_extractor",
        "brand_reference_memory_guardian",
        "template_product_architect",
        "section_flow_strategist",
        "layout_composition_director",
        "design_system_director",
        "visual_signature_builder",
        "figma_source_qa",
        "originality_similarity_auditor",
        "visual_qa_inspector",
        "marketplace_readiness_judge",
    }
    if not isinstance(agent_list, list) or len(agent_list) != 12:
        result.error("design-subagents/agents.json must define exactly 12 core subagents.")
        agent_list = []
    found_ids = {str(agent.get("id") or "") for agent in agent_list if isinstance(agent, dict)}
    missing_ids = sorted(expected_ids - found_ids)
    extra_ids = sorted(found_ids - expected_ids)
    if missing_ids:
        result.error(f"design-subagents/agents.json missing core subagents: {missing_ids}")
    if extra_ids:
        result.error(f"design-subagents/agents.json has unexpected subagents: {extra_ids}")
    for index, agent in enumerate(agent_list, start=1):
        if not isinstance(agent, dict):
            result.error(f"design-subagents/agents.json agent #{index} is not an object.")
            continue
        for key in ("id", "name", "role", "phase", "focus", "requiredInputs", "requiredOutputs", "evaluation_axes", "blockingAuthority", "critical", "blockingRules", "vote_rules"):
            if key not in agent:
                result.error(f"design-subagents/agents.json agent #{index} missing {key}.")
        if agent.get("blockingAuthority") not in {"none", "revise", "required-block"}:
            result.error(f"design-subagents/agents.json agent #{index} invalid blockingAuthority.")
    for mode in ("full", "standard", "lightweight"):
        mode_payload = agents.get("modes", {}).get(mode, {})
        required = mode_payload.get("requiredAgentIds")
        if not isinstance(required, list) or not required:
            result.error(f"design-subagents/agents.json mode {mode} missing requiredAgentIds.")
    if schema.get("$id") != "design-brain.design-subagents.agents.v1":
        result.error("design-subagents/subagent-schema.json $id mismatch.")
    if receipt_schema.get("$id") != "design-brain.design-subagents.orchestration-receipt.v1":
        result.error("design-subagents/orchestration-receipt-schema.json $id mismatch.")
    if semantic_schema.get("$id") != "design-brain.design-subagents.semantic-validation.v1":
        result.error("design-subagents/semantic-validation-schema.json $id mismatch.")
    if semantic_rules.get("schema") != "design-brain.design-subagents.semantic-validation-rules.v1":
        result.error("design-subagents/semantic-validation-rules.json schema mismatch.")
    contracts = semantic_rules.get("agentSemanticContracts")
    if not isinstance(contracts, dict):
        result.error("design-subagents/semantic-validation-rules.json missing agentSemanticContracts.")
    else:
        missing_contracts = sorted(expected_ids - set(contracts.keys()))
        if missing_contracts:
            result.error(f"semantic-validation-rules.json missing subagent contracts: {missing_contracts}")
    result.add("Subagent orchestration agents/schemas/semantic validator: checked")


def check_simulation_metadata_source(root: Path, result: IntegrityResult) -> None:
    agents = load_json(root / ".design-brain" / "design-simulation" / "agents.json", result, "agents.json")
    validate_agents_payload(agents, result, "agents.json")
    schema = load_json(root / ".design-brain" / "design-simulation" / "verdict-schema.json", result, "verdict-schema.json")
    validate_verdict_schema(schema, result, "verdict-schema.json")
    layer = read_text(root / ".design-brain" / "DESIGN_SIMULATION_LAYER.md")
    notes = read_text(root / "PUBLIC_PACKAGE_NOTES.md") + "\n" + read_text(root / "README.md")
    required_fragments = [
        "It does not bundle, copy, import, or execute MiroFish source code.",
        "It does not run OASIS or social/public-opinion simulation.",
        "It adapts the architectural idea into a local design review and quality-gate workflow.",
    ]
    if NATIVE_ADAPTATION_NOTE not in layer:
        result.error("DESIGN_SIMULATION_LAYER.md missing required native adaptation note.")
    for fragment in required_fragments:
        if fragment not in layer:
            result.error(f"DESIGN_SIMULATION_LAYER.md missing licensing fragment: {fragment}")
        if fragment not in notes:
            result.error(f"README/PUBLIC_PACKAGE_NOTES missing licensing fragment: {fragment}")
    result.add("Simulation agents/schema/licensing notes: checked")


def check_post_build_metadata_source(root: Path, result: IntegrityResult) -> None:
    for schema_path in (
        ".design-brain/post-build/design-system-receipt-schema.json",
        ".design-brain/post-build/post-build-audit-schema.json",
        ".design-brain/post-build/batch-similarity-schema.json",
    ):
        payload = load_json(root / schema_path, result, schema_path)
        if not payload.get("required"):
            result.error(f"{schema_path} missing required-field declaration.")
    docs = {
        ".design-brain/POST_BUILD_COMPLETION_GATE.md": ["Post-Build Completion Gate", "READY_WITH_LIMITATIONS", "Completion Receipt"],
        ".design-brain/DESIGN_SYSTEM_BUILD_REQUIREMENTS.md": ["Mandatory Design System Build", "Color Roles", "Figma and Source Rules"],
        ".design-brain/POST_BUILD_TRIPLE_AUDIT_GATE.md": ["Audit Pass 1", "Audit Pass 2", "Audit Pass 3"],
    }
    for path, fragments in docs.items():
        text = read_text(root / path)
        for fragment in fragments:
            if fragment not in text:
                result.error(f"{path} missing required fragment: {fragment}")
    result.add("Post-build docs/templates/schemas: checked")


def check_cognition_metadata_source(root: Path, result: IntegrityResult) -> None:
    schema = load_json(
        root / ".design-brain" / "design-cognition" / "design-cognition-receipt-schema.json",
        result,
        "design-cognition-receipt-schema.json",
    )
    required = set(str(item) for item in schema.get("required", []) if isinstance(item, str))
    needed = {
        "task",
        "productFamily",
        "mode",
        "styleDNA",
        "referenceStandard",
        "designIntentLock",
        "visualGrammar",
        "referenceBoundary",
        "colorRoleRemapping",
        "visualMoodReinterpretation",
        "structuralReconfiguration",
        "patternDivergence",
        "sectionLogic",
        "marketplaceReadiness",
        "status",
    }
    missing = sorted(needed - required)
    if missing:
        result.error(f"design-cognition-receipt-schema.json required fields missing: {missing}")

    docs = {
        ".design-brain/DESIGN_COGNITION_CONTRACT.md": [
            "Style DNA",
            "Reference Standard",
            "Color Role Re-Mapping",
            "Reference Boundary",
            "Structural Reconfiguration",
            "Marketplace Readiness",
        ],
        ".design-brain/DESIGN_COGNITION_GATE.md": [
            "Color Role Re-Mapping",
            "generic Hero > Features > CTA",
            "cognition receipt",
        ],
        ".design-brain/templates/DESIGN_COGNITION_RECEIPT.md": [
            "Design Cognition Receipt",
            "Color Role Re-Mapping",
            "Pattern Divergence",
            "Marketplace Readiness",
        ],
        ".design-brain/templates/DESIGN_COGNITION_RECEIPT.json": [
            "styleDNA",
            "referenceStandard",
            "colorRoleRemapping",
            "referenceBoundary",
            "marketplaceReadiness",
        ],
    }
    for path, fragments in docs.items():
        text = read_text(root / path)
        for fragment in fragments:
            if fragment not in text:
                result.error(f"{path} missing required cognition fragment: {fragment}")
    result.add("Design cognition docs/template/schema: checked")


def check_layout_metadata_source(root: Path, result: IntegrityResult) -> None:
    for schema_path in (
        ".design-brain/lifecycle/build-session-schema.json",
        ".design-brain/lifecycle/layout-fingerprint-schema.json",
        ".design-brain/lifecycle/reference-layout-audit-schema.json",
        ".design-brain/lifecycle/ai-pairwise-layout-audit-schema.json",
    ):
        payload = load_json(root / schema_path, result, schema_path)
        if not payload.get("required"):
            result.error(f"{schema_path} missing required-field declaration.")
    docs = {
        ".design-brain/BUILD_SESSION_LIFECYCLE.md": ["session_started", "fingerprint_locked", "Lifecycle ledger"],
        ".design-brain/SEQUENTIAL_LAYOUT_ORIGINALITY_GATE.md": ["Template A", "Template B", "Fingerprint Lock"],
        ".design-brain/LAYOUT_SIMILARITY_AXIS_RULES.md": ["heroGrammarSimilarity", "overallScaffoldRisk", "Hard Fail"],
        ".design-brain/IDEA_RECOVERY_CORPUS.md": ["Template Website", "Do not copy corpus layout", "local-only"],
        ".design-brain/templates/LAYOUT_FINGERPRINT.md": ["Hero grammar", "Section order", "Design system ID"],
        ".design-brain/templates/REFERENCE_LAYOUT_AUDIT_RECEIPT.md": ["ai_vs_reference", "Overall scaffold risk"],
        ".design-brain/templates/AI_PAIRWISE_LAYOUT_AUDIT_RECEIPT.md": ["ai_vs_ai", "Shared scaffold risk"],
    }
    for path, fragments in docs.items():
        text = read_text(root / path)
        for fragment in fragments:
            if fragment not in text:
                result.error(f"{path} missing required layout fragment: {fragment}")
    result.add("Sequential layout lifecycle docs/templates/schemas: checked")


def check_design_craft_contract_source(root: Path, result: IntegrityResult) -> None:
    docs = {
        ".design-brain/DESIGN_CRAFT_NON_OVERRIDE_CONTRACT.md": [
            "Design Craft must not override",
            "Design Cognition Contract",
            "Design Simulation Layer",
            "Build Session Lifecycle",
            "Post-Build Completion Gate",
        ],
        ".design-brain/SOURCE_OF_TRUTH_MAP.md": ["Design Craft", "non-override support"],
        ".design-brain/craft/README.md": ["non-override support", "DESIGN_CRAFT_NON_OVERRIDE_CONTRACT"],
        ".agents/skills/design-critic/SKILL.md": ["craft support layer", "Brain Design gates win"],
    }
    for path, fragments in docs.items():
        text = read_text(root / path)
        for fragment in fragments:
            if fragment not in text:
                result.error(f"{path} missing Design Craft non-override fragment: {fragment}")
    result.add("Design Craft non-override contract: checked")


def check_runtime_metadata_source(root: Path, result: IntegrityResult) -> None:
    schema_required = {
        ".design-brain/runtime/schemas/command-registry-schema.json": ["command", "tool", "requiredStages"],
        ".design-brain/runtime/schemas/tool-registry-schema.json": ["name", "purpose", "blockingAuthority"],
        ".design-brain/runtime/schemas/session-state-schema.json": ["sessionId", "permissionMode", "requiredStages"],
        ".design-brain/runtime/schemas/repair-ticket-schema.json": ["ticketId", "status", "requiredRepair"],
        ".design-brain/runtime/schemas/hook-config-schema.json": ["hooks"],
        ".design-brain/runtime/schemas/runtime-result-schema.json": ["status", "command", "tool", "evidence"],
        ".design-brain/runtime/schemas/permission-mode-schema.json": ["mode", "allowedCommands"],
        ".design-brain/runtime/schemas/compact-context-schema.json": ["sessionId", "compactSummary", "openTickets"],
    }
    for schema_path, required_fragments in schema_required.items():
        payload = load_json(root / schema_path, result, schema_path)
        text = json.dumps(payload)
        for fragment in required_fragments:
            if fragment not in text:
                result.error(f"{schema_path} missing runtime schema fragment: {fragment}")
    docs = {
        ".design-brain/runtime/DESIGN_AGENT_RUNTIME.md": ["Design Agent Runtime", "Design Craft", "non-override"],
        ".design-brain/runtime/COMMAND_REGISTRY.md": ["/design-route", "/design-cognition", "/design-finalize"],
        ".design-brain/runtime/TOOL_REGISTRY.md": ["design_craft_adapter_tool", "Support-only"],
        ".design-brain/runtime/PERMISSION_MODES.md": ["diagnostic_only", "plan_only", "full_build"],
        ".design-brain/runtime/HOOKS.md": ["hooks.example.json", "hooks.local.json"],
        ".design-brain/runtime/SESSION_STATE.md": ["session-state.json", "requiredStages"],
        ".design-brain/runtime/REPAIR_TICKETS.md": ["repair ticket", "BLOCKED"],
        ".design-brain/runtime/CONTEXT_COMPACTION.md": ["compact context", "open tickets"],
        ".design-brain/runtime/DOCTOR_STATUS.md": ["doctor", "status"],
    }
    for path, fragments in docs.items():
        text = read_text(root / path)
        for fragment in fragments:
            if fragment not in text:
                result.error(f"{path} missing runtime fragment: {fragment}")
    report_dir = root / "reports" / "brain-design-runtime-upgrade"
    for report in (
        "CLAUDE_CODE_ARCHITECTURE_STUDY.md",
        "claude-code-adaptation-boundary.md",
    ):
        if not (report_dir / report).is_file():
            result.error(f"Runtime architecture study report missing: reports/brain-design-runtime-upgrade/{report}")
    result.add("Design Agent Runtime docs/schemas/reports: checked")


def check_total_integration_source(root: Path, result: IntegrityResult) -> None:
    cleanup_manifest = root / "reports" / "brain-design-total-integration" / "cleanup" / "cleanup-manifest.json"
    stabilization_digest = root / "reports" / "brain-design-total-integration" / "INPUT_REPORT_DIGEST.md"
    for path in (cleanup_manifest, stabilization_digest):
        if not path.exists():
            result.error(f"Total integration cleanup/report file missing: {rel(path, root)}")
    build_session_text = read_text(root / "scripts" / "design_brain_build_session.py")
    post_build_text = read_text(root / "scripts" / "design_brain_post_build_audit.py")
    design_system_text = read_text(root / "scripts" / "design_brain_design_system_check.py")
    layout_text = read_text(root / "scripts" / "design_brain_layout_similarity_audit.py")
    required_fragments = {
        "scripts/design_brain_build_session.py": ["verify-final", "verify_ledger_final", "completionReceiptPresent"],
        "scripts/design_brain_post_build_audit.py": ["diagnostic-only", "completionReceiptRequired", "artifact evidence is"],
        "scripts/design_brain_design_system_check.py": ["artifactEvidenceStatus", "ARTIFACT_EVIDENCE_FIELDS"],
        "scripts/design_brain_layout_similarity_audit.py": ["hardFailAxes", "softRiskAxes", "structureDefiningAxisSimilarity"],
    }
    text_map = {
        "scripts/design_brain_build_session.py": build_session_text,
        "scripts/design_brain_post_build_audit.py": post_build_text,
        "scripts/design_brain_design_system_check.py": design_system_text,
        "scripts/design_brain_layout_similarity_audit.py": layout_text,
    }
    for path, fragments in required_fragments.items():
        for fragment in fragments:
            if fragment not in text_map[path]:
                result.error(f"{path} missing total-integration fragment: {fragment}")

    active_roots = [".design-brain", "scripts", ".agents", ".codex", "tests"]
    backup_patterns = ["*.bak-*", "*.backup-*", "*.orig", "*.old", "*.tmp"]
    for active_root in active_roots:
        root_path = root / active_root
        if not root_path.exists():
            continue
        for path in root_path.rglob("*"):
            if path.is_file() and any(fnmatch.fnmatch(path.name, pattern) for pattern in backup_patterns):
                result.error(f"Active backup/temp file remains in source: {rel(path, root)}")
    generated_dirs = [
        ".design-brain/context-packets",
        ".design-brain/pptx-precision-reviews",
        ".design-brain/tmp",
    ]
    for generated_dir in generated_dirs:
        if (root / generated_dir).exists():
            result.error(f"Generated evidence/temp directory remains active: {generated_dir}")
    result.add("Total integration cleanup/enforcement source checks: checked")


def check_no_mirofish_source(root: Path, result: IntegrityResult) -> None:
    forbidden_dirs = {"mirofish", "MiroFish", "mirofish-cli", "OASIS", "oasis", "claude-code-main"}
    for current, dirs, _files in os.walk(root):
        current_path = Path(current)
        if any(part in {".design-brain-backups", "exports", "__pycache__", "node_modules"} for part in current_path.parts):
            dirs[:] = []
            continue
        for dirname in list(dirs):
            if dirname in forbidden_dirs:
                result.error(f"Forbidden external source directory bundled: {rel(current_path / dirname, root)}")
    analysis_dir = root / "downloads" / "_analysis" / "claude-code-main"
    if analysis_dir.exists():
        result.error("Forbidden extracted Claude Code analysis directory remains active: downloads/_analysis/claude-code-main")
    result.add("MiroFish/OASIS/Claude Code source directory check: PASS")


def run_json_simulation(root: Path, result: IntegrityResult, timeout: int, verbose: bool = False) -> None:
    with tempfile.TemporaryDirectory(prefix="brain-design-integrity-json-") as tmp:
        code, stdout, stderr = run_command_split(
            root,
            py_command([
                "scripts/design_brain_design_simulate.py",
                "--task",
                "restaurant website template",
                "--template-type",
                "website template",
                "--niche",
                "restaurant",
                "--target-buyer",
                "restaurant owners buying editable marketplace templates",
                "--visual-mood",
                "immersive hospitality with warm image-led hierarchy",
                "--proposed-structure",
                "Immersive hero; Signature menu; Dining atmosphere gallery; Reservation flow; Location and hours; Reviews; Service details; CTA reservation; Footer; Cover preview; Source hygiene components auto-layout documentation",
                "--reference-summary",
                "Do-not-copy exact layout and color palette; reinterpret mood.",
                "--json",
                "--output-dir",
                str(Path(tmp) / "integrity-json-sim"),
            ]),
            timeout=timeout,
            verbose=verbose,
        )
    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError as exc:
        context = "\n".join(part for part in (stdout[-500:], stderr[-500:]) if part)
        result.error(f"--json simulation stdout is not valid JSON: {exc}; output={context}")
        return
    for key in ("artifactDir", "agentSource", "agentVotes", "verdictPath", "routing", "cognition", "recommendedImprovements"):
        if key not in parsed:
            result.error(f"--json simulation output missing {key}")
    if parsed.get("agentSource") != ".design-brain/design-simulation/agents.json":
        result.error("--json simulation did not load agents.json as source of truth.")
    routing = parsed.get("routing", {})
    if not isinstance(routing, dict) or routing.get("routeSource") not in {"brain_design_router", "explicit_cli", "fallback"}:
        result.error("--json simulation routing object is invalid.")
    if isinstance(routing, dict):
        if routing.get("routeSource") != "brain_design_router":
            result.error("--json simulation did not defer to the Brain Design router.")
        if routing.get("module") != "website-template" or routing.get("websiteType") != "event_venue_travel_booking":
            result.error("--json restaurant marketplace/gallery route alignment failed.")
    if parsed.get("verdict") == "PASS" and parsed.get("requiredRepairs"):
        result.error("PASS simulation output contains requiredRepairs.")
    if code not in (0, 2):
        result.error(f"--json simulation command failed unexpectedly: {(stdout + stderr)[-800:]}")
    result.add("--json simulation parse: PASS")


def check_route_alignment_subset(root: Path, result: IntegrityResult, timeout: int, verbose: bool = False) -> None:
    cases = [
        ("newsletter website template", {"module": "website-template", "not_mode": "email-newsletter"}),
        ("coffee shop website template", {"module": "website-template", "not_mode": "ecommerce"}),
        ("restaurant website template for editable marketplace template buyers with gallery visual motif", {"module": "website-template", "not_module": "portfolio", "websiteType": "event_venue_travel_booking"}),
        ("ui kit dashboard components", {"module": "ui-kit", "not_mode": "dashboard"}),
        ("pricing page website template", {"module": "website-template", "not_mode": "ecommerce"}),
        ("Envato marketplace template", {"not_module": "ecommerce", "not_mode": "ecommerce"}),
    ]
    for task, expected in cases:
        with tempfile.TemporaryDirectory(prefix="brain-design-route-integrity-") as tmp:
            code, stdout, stderr = run_command_split(
                root,
                py_command([
                    "scripts/design_brain_design_simulate.py",
                    "--json",
                    "--output-dir",
                    str(Path(tmp) / "artifacts"),
                    "--task",
                    task,
                    "--target-buyer",
                    "marketplace template buyer",
                    "--visual-mood",
                    "gallery typography contrast editable marketplace template",
                    "--proposed-structure",
                    "Primary format; Role-specific hierarchy; Key content block; Supporting proof or metadata; States or export notes; Components; Source hygiene; Preview notes; Documentation",
                    "--reference-summary",
                    "Do-not-copy exact layout and color palette; reinterpret mood.",
                ]),
                timeout=timeout,
                verbose=verbose,
            )
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError as exc:
            result.error(f"Route alignment JSON parse failed for {task!r}: {exc}; {stderr[-500:]}")
            continue
        routing = parsed.get("routing", {})
        if not isinstance(routing, dict):
            result.error(f"Route alignment missing routing object for {task!r}.")
            continue
        if routing.get("routeSource") != "brain_design_router":
            result.error(f"Route alignment used {routing.get('routeSource')} for {task!r}; expected brain_design_router.")
        if "module" in expected and routing.get("module") != expected["module"]:
            result.error(f"Route alignment module mismatch for {task!r}: {routing.get('module')} != {expected['module']}")
        if "websiteType" in expected and routing.get("websiteType") != expected["websiteType"]:
            result.error(f"Route alignment websiteType mismatch for {task!r}: {routing.get('websiteType')} != {expected['websiteType']}")
        if "not_mode" in expected and routing.get("mode") == expected["not_mode"]:
            result.error(f"Route alignment old mode regression for {task!r}: {expected['not_mode']}")
        if "not_module" in expected and routing.get("module") == expected["not_module"]:
            result.error(f"Route alignment old module regression for {task!r}: {expected['not_module']}")
        if code not in (0, 2):
            result.error(f"Route alignment simulation failed unexpectedly for {task!r}: {stderr[-600:] or stdout[-600:]}")
    result.add("Simulation route alignment subset: checked")


def check_cognition_enforcement_runtime(root: Path, result: IntegrityResult, timeout: int, verbose: bool = False) -> None:
    base_args = py_command([
        "scripts/design_brain_design_simulate.py",
        "--json",
        "--task",
        "restaurant website template from reference",
        "--template-type",
        "website template",
        "--niche",
        "restaurant",
        "--target-buyer",
        "restaurant owners buying editable marketplace templates",
        "--visual-mood",
        "immersive hospitality with warm image-led hierarchy",
        "--proposed-structure",
        "Immersive hero; Signature menu; Dining atmosphere gallery; Reservation process flow; Location and hours; Testimonials and reviews proof; Service details; CTA reservation; Footer; Cover preview; Source hygiene components auto-layout documentation",
        "--reference-summary",
        "Do-not-copy exact layout and color palette; reinterpret mood from reference.",
    ])
    with tempfile.TemporaryDirectory(prefix="brain-design-cognition-enforce-") as tmp:
        artifacts = Path(tmp) / "artifacts"
        code, stdout, stderr = run_command_split(root, base_args + ["--output-dir", str(artifacts / "missing")], timeout=timeout, verbose=verbose)
        try:
            missing = json.loads(stdout)
        except json.JSONDecodeError as exc:
            result.error(f"Missing-cognition enforcement JSON parse failed: {exc}; {stderr[-500:]}")
            return
        if code == 0 or missing.get("verdict") == "PASS":
            result.error("Simulation can still PASS without cognition receipt for reference-led/template task.")

        fake = Path(tmp) / "fake-cognition.json"
        fake.write_text('{"status":"PASS"}\n', encoding="utf-8", newline="\n")
        code, stdout, stderr = run_command_split(root, base_args + ["--output-dir", str(artifacts / "fake"), "--cognition-receipt", str(fake)], timeout=timeout, verbose=verbose)
        try:
            fake_result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            result.error(f"Fake-cognition enforcement JSON parse failed: {exc}; {stderr[-500:]}")
            return
        if code == 0 or fake_result.get("verdict") == "PASS" or fake_result.get("cognition", {}).get("status") != "FAIL":
            result.error("Simulation can still PASS or trust fake status-only cognition receipt.")

        valid = root / ".design-brain" / "templates" / "DESIGN_COGNITION_RECEIPT.json"
        code, stdout, stderr = run_command_split(root, base_args + ["--output-dir", str(artifacts / "valid"), "--cognition-receipt", str(valid)], timeout=timeout, verbose=verbose)
        try:
            valid_result = json.loads(stdout)
        except json.JSONDecodeError as exc:
            result.error(f"Valid-cognition enforcement JSON parse failed: {exc}; {stderr[-500:]}")
            return
        if code != 0 or valid_result.get("verdict") != "PASS" or valid_result.get("cognition", {}).get("status") != "PASS":
            result.error("Valid cognition receipt did not allow strong reference-led template simulation to PASS.")
    result.add("Simulation cognition enforcement runtime: PASS")


def check_install_target(root: Path, result: IntegrityResult, timeout: int, verbose: bool = False) -> None:
    with tempfile.TemporaryDirectory(prefix="brain-design-install-") as tmp:
        target = Path(tmp) / "target"
        code, output = run_command(root, py_command(["scripts/install_design_brain.py", "--target", str(target)]), timeout=timeout, verbose=verbose)
        if code != 0:
            result.error(f"Actual temp install failed: {output[-1200:]}")
            return
        for path in [
            "AGENTS.md",
            ".design-brain/AUTOLOAD_POLICY.md",
        ] + SIMULATION_MANDATORY_FILES + POST_BUILD_MANDATORY_FILES + COGNITION_MANDATORY_FILES + LAYOUT_MANDATORY_FILES + SUBAGENT_MANDATORY_FILES + CRAFT_CONTRACT_MANDATORY_FILES + RUNTIME_MANDATORY_FILES + DESIGN_CRAFT_ADAPTER_MANDATORY_FILES + REFERENCE_USAGE_MANDATORY_FILES + WEB_DECK_MANDATORY_FILES + PPTX_NATIVE_MANDATORY_FILES + RELEASE_REPORT_MANDATORY_FILES:
            if not (target / path).is_file():
                result.error(f"Temp install missing runtime/simulation/post-build/cognition/layout/web-deck/core file: {path}")
        result.add("Actual temp install includes runtime, simulation, post-build, cognition, layout lifecycle, subagent orchestration, bundled Design Craft adapter, reference usage, web deck medium, and release report evidence files: PASS")


def check_runtime_source(root: Path, result: IntegrityResult, timeout: int, verbose: bool = False, full_runtime: bool = False, process_smoke_repeat: int = 3) -> None:
    code, output = run_command(root, py_command(["scripts/design_brain_router_smoke_test.py"]), timeout=timeout, verbose=verbose)
    if code != 0:
        result.error(f"Router smoke failed: {output[-1200:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Router smoke: PASS")
    code, output = run_command(
        root,
        py_command(["scripts/design_brain_process_utils_smoke_test.py", "--repeat", str(process_smoke_repeat), "--timeout", "8", "--max-duration", str(max(90, process_smoke_repeat * 18))]),
        timeout=min(timeout, 120),
        verbose=verbose,
    )
    if code != 0:
        result.error(f"Process utils smoke failed: {output[-1200:]}")
    else:
        if "Python invocation mode:" not in output or "Selected Python invocation:" not in output:
            result.error("Process utils smoke did not report selected Python invocation mode.")
        result.add(output.splitlines()[-1] if output.splitlines() else "Process utils smoke: PASS")
    quick_command = py_command([
        "scripts/design_brain_design_sim_smoke_test.py",
        "--quick",
        "--global-timeout",
        "90",
        "--case-timeout",
        "20",
    ])
    code, output = run_command(root, quick_command, timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Design simulation quick smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Design simulation quick smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_post_build_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Post-build smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Post-build smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_design_cognition_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Design cognition smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Design cognition smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_sequential_layout_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Sequential layout smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Sequential layout smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_subagent_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Subagent orchestration smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Subagent orchestration smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_subagent_semantic_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Subagent semantic validation smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Subagent semantic validation smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_reference_usage_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Reference usage smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Reference usage smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_doctor.py", "--json"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Runtime doctor failed: {output[-1600:]}")
    else:
        result.add("Runtime doctor: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_craft_adapter_bridge_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Design Craft adapter bridge smoke failed: {output[-1600:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Design Craft adapter bridge smoke: PASS")
    code, output = run_command(root, py_command(["scripts/design_brain_runtime_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
    if code != 0:
        result.error(f"Design Agent Runtime smoke failed: {output[-2000:]}")
    else:
        result.add(output.splitlines()[-1] if output.splitlines() else "Design Agent Runtime smoke: PASS")
    if full_runtime:
        full_command = py_command([
            "scripts/design_brain_design_sim_smoke_test.py",
            "--full",
            "--global-timeout",
            "300",
            "--case-timeout",
            "45",
        ])
        code, output = run_command(root, full_command, timeout=max(timeout, 300), verbose=verbose)
        if code != 0:
            result.error(f"Design simulation full smoke failed: {output[-1600:]}")
        else:
            result.add(output.splitlines()[-1] if output.splitlines() else "Design simulation full smoke: PASS")
    check_install_target(root, result, timeout, verbose)
    run_json_simulation(root, result, timeout, verbose)
    check_cognition_enforcement_runtime(root, result, timeout, verbose)


def forbidden_zip_reason(name: str) -> str:
    normalized = name.replace("\\", "/")
    for pattern in FORBIDDEN_ZIP_PATTERNS:
        if fnmatch.fnmatch(normalized, pattern):
            return pattern
    return ""


def zip_text(zip_file: zipfile.ZipFile, name: str) -> str:
    try:
        return zip_file.read(name).decode("utf-8")
    except Exception:
        return ""


def check_zip(zip_path: Path, result: IntegrityResult, skip_runtime: bool, timeout: int, verbose: bool = False, full_runtime: bool = False, process_smoke_repeat: int = 3) -> None:
    with zipfile.ZipFile(zip_path) as zip_file:
        names = {name for name in zip_file.namelist() if not name.endswith("/")}
        for path in MANDATORY_FILES:
            if path not in names:
                result.error(f"ZIP missing mandatory file: {path}")
        for name in sorted(names):
            reason = forbidden_zip_reason(name)
            if reason:
                result.error(f"ZIP contains forbidden file {name}: {reason}")
            if name.endswith(".md") or name.endswith(".py") or name.endswith(".json") or name.endswith(".txt"):
                text = zip_text(zip_file, name)
                if typeui_marker() in text:
                    result.error(f"ZIP contains TypeUI-managed marker in public-core file: {name}")
        try:
            package = json.loads(zip_text(zip_file, "package.json"))
            manifest = json.loads(zip_text(zip_file, ".design-brain/MANIFEST.json"))
            generated = json.loads(zip_text(zip_file, "PACKAGE_MANIFEST.generated.json"))
        except json.JSONDecodeError as exc:
            result.error(f"ZIP JSON parse failure: {exc}")
            return
        if str(package.get("version")) != PACKAGE_VERSION:
            result.error("ZIP package.json version mismatch.")
        if str(manifest.get("version")) != PACKAGE_VERSION:
            result.error("ZIP MANIFEST version mismatch.")
        if str(generated.get("packageVersion")) != PACKAGE_VERSION:
            result.error("ZIP generated manifest packageVersion mismatch.")
        if generated.get("outputFileName") != FINAL_ZIP_NAME:
            result.error("Generated package manifest outputFileName mismatch.")
        if generated.get("cognitionFilesPresent") is not True:
            result.error("Generated package manifest does not confirm cognition files are present.")
        if generated.get("layoutLifecycleFilesPresent") is not True:
            result.error("Generated package manifest does not confirm lifecycle/layout files are present.")
        if generated.get("runtimeFilesPresent") is not True:
            result.error("Generated package manifest does not confirm Design Agent Runtime files are present.")
        if generated.get("designCraftAdapterFilesPresent") is not True:
            result.error("Generated package manifest does not confirm bundled Design Craft adapter files are present.")
        if generated.get("referenceUsageFilesPresent") is not True:
            result.error("Generated package manifest does not confirm reference usage files are present.")
        if generated.get("subagentFilesPresent") is not True:
            result.error("Generated package manifest does not confirm subagent orchestration files are present.")
        if generated.get("subagentSemanticValidatorPresent") is not True:
            result.error("Generated package manifest does not confirm subagent semantic validator files are present.")
        if generated.get("webDeckFilesPresent") is not True:
            result.error("Generated package manifest does not confirm web deck medium files are present.")
        if generated.get("releaseReportFilesPresent") is not True:
            result.error("Generated package manifest does not confirm release report evidence files are present.")
        layer_text = zip_text(zip_file, ".design-brain/DESIGN_SIMULATION_LAYER.md")
        if NATIVE_ADAPTATION_NOTE not in layer_text:
            result.error("ZIP simulation layer missing native adaptation note.")
        result.add(f"ZIP file count: {len(names)}")
    if not skip_runtime:
        with tempfile.TemporaryDirectory(prefix="brain-design-zip-") as tmp:
            extract_root = Path(tmp) / "package"
            extract_root.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(zip_path) as zip_file:
                zip_file.extractall(extract_root)
            check_install_target(extract_root, result, timeout, verbose)
            code, output = run_command(
                extract_root,
                py_command(["scripts/design_brain_process_utils_smoke_test.py", "--repeat", str(process_smoke_repeat), "--timeout", "8", "--max-duration", str(max(90, process_smoke_repeat * 18))]),
                timeout=min(timeout, 120),
                verbose=verbose,
            )
            if code != 0:
                result.error(f"Process utils smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                if "Python invocation mode:" not in output or "Selected Python invocation:" not in output:
                    result.error("Extracted ZIP process utils smoke did not report selected Python invocation mode.")
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP process utils smoke: PASS")
            quick_command = py_command([
                "scripts/design_brain_design_sim_smoke_test.py",
                "--quick",
                "--global-timeout",
                "90",
                "--case-timeout",
                "20",
            ])
            code, output = run_command(extract_root, quick_command, timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Design simulation quick smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP simulation quick smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_post_build_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Post-build smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP post-build smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_design_cognition_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Design cognition smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP design cognition smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_sequential_layout_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Sequential layout smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP sequential layout smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_subagent_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Subagent orchestration smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP subagent orchestration smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_subagent_semantic_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Subagent semantic validation smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP subagent semantic validation smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_doctor.py", "--json"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Runtime doctor failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add("Extracted ZIP runtime doctor: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_craft_adapter_bridge_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Design Craft adapter bridge smoke failed from extracted ZIP: {output[-1600:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP Design Craft adapter bridge smoke: PASS")
            code, output = run_command(extract_root, py_command(["scripts/design_brain_runtime_smoke_test.py"]), timeout=min(timeout, 120), verbose=verbose)
            if code != 0:
                result.error(f"Design Agent Runtime smoke failed from extracted ZIP: {output[-2000:]}")
            else:
                result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP Design Agent Runtime smoke: PASS")
            if full_runtime:
                full_command = py_command([
                    "scripts/design_brain_design_sim_smoke_test.py",
                    "--full",
                    "--global-timeout",
                    "300",
                    "--case-timeout",
                    "45",
                ])
                code, output = run_command(extract_root, full_command, timeout=max(timeout, 300), verbose=verbose)
                if code != 0:
                    result.error(f"Design simulation full smoke failed from extracted ZIP: {output[-1600:]}")
                else:
                    result.add(output.splitlines()[-1] if output.splitlines() else "Extracted ZIP simulation full smoke: PASS")


def validate_source(root: Path, skip_runtime: bool = False, command_timeout: int = 60, verbose: bool = False, full_runtime: bool = False, process_smoke_repeat: int = 3) -> IntegrityResult:
    result = IntegrityResult(mode="source", target=str(root))
    check_mandatory_source(root, result)
    check_versions(root, result)
    check_simulation_metadata_source(root, result)
    check_post_build_metadata_source(root, result)
    check_cognition_metadata_source(root, result)
    check_layout_metadata_source(root, result)
    check_subagent_metadata_source(root, result)
    check_design_craft_contract_source(root, result)
    check_runtime_metadata_source(root, result)
    check_total_integration_source(root, result)
    check_no_mirofish_source(root, result)
    if not skip_runtime:
        check_runtime_source(root, result, command_timeout, verbose, full_runtime, process_smoke_repeat)
    else:
        result.add("Runtime checks skipped by --skip-runtime.")
    return result


def validate_zip(zip_path: Path, skip_runtime: bool = False, command_timeout: int = 60, verbose: bool = False, full_runtime: bool = False, process_smoke_repeat: int = 3) -> IntegrityResult:
    result = IntegrityResult(mode="zip", target=str(zip_path))
    if not zip_path.is_file():
        result.error(f"ZIP not found: {zip_path}")
        return result
    check_zip(zip_path, result, skip_runtime, command_timeout, verbose, full_runtime, process_smoke_repeat)
    return result


def result_to_dict(result: IntegrityResult) -> dict[str, object]:
    return {
        "mode": result.mode,
        "target": result.target,
        "ok": result.ok,
        "errors": result.errors,
        "warnings": result.warnings,
        "info": result.info,
    }


def print_report(result: IntegrityResult) -> None:
    print("Design Brain Package Integrity")
    print("==============================")
    print(f"Mode: {result.mode}")
    print(f"Target: {result.target}")
    print(f"RESULT: {'PASS' if result.ok else 'FAIL'}")
    if result.errors:
        print("\nErrors")
        for error in result.errors:
            print(f"- {error}")
    if result.warnings:
        print("\nWarnings")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.info:
        print("\nInfo")
        for item in result.info:
            print(f"- {item}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve() if args.root else repo_root()
    command_timeout = min(args.command_timeout, args.runtime_timeout) if args.runtime_timeout else args.command_timeout
    result = (
        validate_zip(Path(args.zip).expanduser().resolve(), args.skip_runtime, command_timeout, args.verbose, args.full_runtime, args.process_smoke_repeat)
        if args.zip
        else validate_source(root, args.skip_runtime, command_timeout, args.verbose, args.full_runtime, args.process_smoke_repeat)
    )
    if args.json:
        print(json.dumps(result_to_dict(result), indent=2, ensure_ascii=False))
    else:
        print_report(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

