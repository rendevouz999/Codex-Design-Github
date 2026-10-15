#!/usr/bin/env python
"""Brain Design runtime tool registry."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_process_utils import python_command, resolve_python_invocation, run_command


ROOT = Path(__file__).resolve().parents[1]
PYTHON = resolve_python_invocation()


@dataclass(frozen=True)
class RuntimeTool:
    name: str
    purpose: str
    input: str
    output: str
    blockingAuthority: str
    permissionLevel: str
    scriptBackend: str
    failureBehavior: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


TOOLS = [
    RuntimeTool("design_production_tool", "Run one authorized general Design Production Specialist through the existing runtime", "start/run with Main-authored DesignTask JSON", "DesignHookDecision, DesignResult, manifests and QA; Main review pending", "blocks delivery until exact artifacts have Main approval", "full_build", "scripts/design_brain_runtime.py", "preserve interrupted job; reconcile and request a bounded revision"),
    RuntimeTool("route_tool", "Resolve route/product family", "task text", "route result", "blocks wrong workflow route", "diagnostic_only", "scripts/design_brain_module_select.py", "create route repair ticket"),
    RuntimeTool("reference_usage_tool", "Check output brand and reference group usage", "candidate brand/reference IDs", "usage gate result", "blocks repeated brand/reference reuse", "plan_only", "scripts/design_brain_reference_usage_gate.py", "create reference-usage repair ticket"),
    RuntimeTool("cognition_check_tool", "Validate cognition receipt", "receipt JSON", "cognition result", "blocks reference-led/template planning", "plan_only", "scripts/design_brain_design_cognition_check.py", "create cognition repair ticket"),
    RuntimeTool("section_layout_tool", "Extract, validate, and select section layout patterns", "reference evidence/catalog query", "section layout result", "blocks stable selection when no PASS pattern exists", "plan_only", "scripts/design_brain_section_layout_extract.py", "keep weak candidates in incoming review"),
    RuntimeTool("subagent_orchestration_tool", "Plan and verify design subagent evidence", "task/mode/evidence", "subagent receipt", "blocks final when critical subagent evidence is missing", "plan_only", "scripts/design_brain_subagent_orchestrate.py", "create subagent orchestration repair ticket"),
    RuntimeTool("subagent_semantic_validator_tool", "Validate subagent receipt content quality", "evidence directory", "semantic validation result", "blocks final when receipt content is fake or weak", "plan_only", "scripts/design_brain_subagent_receipt_validate.py", "create subagent evidence repair ticket"),
    RuntimeTool("simulation_tool", "Run Design Simulation Layer", "task/plan/cognition", "simulation verdict", "blocks build on REVISE/BLOCKED", "plan_only", "scripts/design_brain_design_simulate.py", "create simulation repair ticket"),
    RuntimeTool("layout_similarity_tool", "Run layout originality audit", "fingerprints", "layout audit", "blocks copied scaffold", "plan_only", "scripts/design_brain_layout_similarity_audit.py", "create layout repair ticket"),
    RuntimeTool("build_session_tool", "Manage build-session lifecycle", "session evidence", "lifecycle state", "blocks next/final if missing", "full_build", "scripts/design_brain_build_session.py", "create lifecycle repair ticket"),
    RuntimeTool("design_craft_adapter_tool", "Call bundled Design Craft support adapter", "Brain Design request JSON", "craft support result", "support-only, blocks override attempts", "plan_only", ".design-brain/adapters/design-craft/scripts/craft_adapter.py", "block override and create craft ticket"),
    RuntimeTool("design_system_check_tool", "Validate design system", "receipt/build dir", "design system status", "blocks final if missing", "full_build", "scripts/design_brain_design_system_check.py", "create design-system repair ticket"),
    RuntimeTool("web_deck_tool", "Plan web deck stage, slide archetypes, and motion signature", "task/style/direction", "deck plan", "blocks build on an off-contract deck plan", "plan_only", "skills/presentation-deck/runtime/web/design_brain_web_deck_plan.mjs", "create web-deck plan repair ticket"),
    RuntimeTool("web_deck_audit_tool", "Statically audit web deck stage and runtime fidelity", "built deck", "stage audit result", "blocks web-deck final on a P0 stage or runtime defect", "plan_only", "skills/presentation-deck/runtime/web/design_brain_web_deck_audit.mjs", "create web-deck stage repair ticket"),
    RuntimeTool("web_deck_render_review_tool", "Review rendered web deck slides in a browser", "built deck/required viewports", "render review result", "blocks web-deck final on a P0 rendered defect or when the review cannot run", "plan_only", "skills/presentation-deck/runtime/web/design_brain_web_deck_render_review.mjs", "create web-deck render repair ticket"),
    RuntimeTool("post_build_audit_tool", "Run post-build audit", "build/session", "post-build receipt", "blocks final", "full_build", "scripts/design_brain_post_build_audit.py", "create post-build repair ticket"),
    RuntimeTool("batch_similarity_tool", "Run batch pairwise similarity audit", "fingerprints", "batch matrix", "blocks similar batch", "plan_only", "scripts/design_brain_batch_similarity_audit.py", "create batch similarity ticket"),
    RuntimeTool("completion_receipt_tool", "Finalize/verify completion receipt", "session", "final readiness", "blocks final", "full_build", "scripts/design_brain_build_session.py", "create completion ticket"),
    RuntimeTool("doctor_tool", "Run runtime doctor", "repo root", "doctor result", "blocks export if failing", "diagnostic_only", "scripts/design_brain_doctor.py", "report missing runtime files"),
    RuntimeTool("status_tool", "Report runtime status", "session", "status JSON", "non-blocking", "diagnostic_only", "scripts/design_brain_status_runtime.py", "report missing state"),
    RuntimeTool("compact_context_tool", "Compact session context", "session", "compact context", "non-blocking", "diagnostic_only", "scripts/design_brain_context_compact.py", "report compaction issue"),
]


def registry() -> dict[str, Any]:
    return {"tools": [tool.to_dict() for tool in TOOLS]}


def get_tool(name: str) -> RuntimeTool | None:
    for tool in TOOLS:
        if tool.name == name:
            return tool
    return None


def find_design_craft_root() -> Path | None:
    env = os.environ.get("BRAIN_DESIGN_CRAFT_ROOT", "").strip()
    candidates = []
    if env:
        candidates.append(Path(env))
    candidates.extend([
        ROOT / ".design-brain" / "adapters" / "design-craft",
        ROOT / "design-craft",
        Path.home() / ".codex" / "skills" / "design-craft",
    ])
    for candidate in candidates:
        if (candidate / "SKILL.md").is_file() and (candidate / "scripts" / "craft_adapter.py").is_file():
            return candidate
    return None


def validate_tools() -> dict[str, Any]:
    missing = []
    for tool in TOOLS:
        if tool.name == "design_craft_adapter_tool":
            if not find_design_craft_root():
                missing.append("Design Craft craft_adapter.py")
            continue
        backend = tool.scriptBackend
        if backend.startswith("scripts/") and not (ROOT / backend).is_file():
            missing.append(backend)
    return {"status": "PASS" if not missing else "BLOCKED", "missing": missing, "toolCount": len(TOOLS)}


def normalize_status(returncode: int, stdout: str = "", stderr: str = "") -> str:
    text = f"{stdout}\n{stderr}".upper()
    if returncode == 0 and "FAIL" not in text and "BLOCKED" not in text:
        return "PASS"
    if "BLOCKED" in text:
        return "BLOCKED"
    if "REVISE" in text or "FAIL" in text:
        return "REVISE_REQUIRED"
    return "ERROR"


def run_tool(name: str, args: list[str], timeout: int = 60) -> dict[str, Any]:
    tool = get_tool(name)
    if not tool:
        return {"status": "ERROR", "tool": name, "error": "unknown tool"}
    if name == "design_craft_adapter_tool":
        craft_root = find_design_craft_root()
        if not craft_root:
            return {"status": "BLOCKED", "tool": name, "error": "Design Craft adapter not found"}
        cmd = python_command(["scripts/craft_adapter.py", *args], PYTHON)
        result = run_command(cmd, cwd=craft_root, timeout=timeout, label=name)
    elif tool.scriptBackend.endswith(".mjs"):
        cmd = ["node", tool.scriptBackend, *args]
        result = run_command(cmd, cwd=ROOT, timeout=timeout, label=name)
    else:
        cmd = python_command([tool.scriptBackend, *args], PYTHON)
        result = run_command(cmd, cwd=ROOT, timeout=timeout, label=name)
    return {
        "status": normalize_status(result.returncode or 0, result.stdout or "", result.stderr or ""),
        "tool": name,
        "returncode": result.returncode,
        "timedOut": result.timedOut,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Brain Design runtime tool registry.")
    sub = parser.add_subparsers(dest="command", required=True)
    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--json", action="store_true")
    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("--json", action="store_true")
    call = sub.add_parser("call")
    call.add_argument("--tool", required=True)
    call.add_argument("--json", action="store_true")
    call.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.command == "list":
        payload = registry()
    elif args.command == "validate":
        payload = validate_tools()
    else:
        payload = run_tool(args.tool, args.tool_args)

    print(json.dumps(payload, indent=2) if args.json else payload)
    return 0 if payload.get("status", "PASS") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
