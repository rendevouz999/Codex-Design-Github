#!/usr/bin/env python
"""Brain Design Design Agent Runtime.

This script wraps existing Brain Design gates as a CLI/JSON runtime loop.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_scope import require_presentation
from design_brain_modules import build_selection
from design_brain_command_router import COMMAND_TO_STAGE, COMMAND_TO_TOOL, route_command
from design_brain_permission import can_run
from design_brain_visual_gate import validate_post_build_receipt
from design_brain_repair_ticket import create_ticket, open_tickets, load_tickets, save_tickets, ticket_file


ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = ROOT / ".design-brain" / "runtime" / "state"
REQUIRED_STAGES = [
    "route",
    "reference_usage",
    "cognition",
    "section_layout",
    "subagent_orchestration",
    "simulation",
    "layout_audit",
    "build_session_verify",
    "craft_support",
    "design_system_check",
    "post_build_audit",
    "completion_receipt",
    "verify_final",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def session_id() -> str:
    return "runtime-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def state_path(session: Path) -> Path:
    return session / "session-state.json"


def history_path(session: Path) -> Path:
    return session / "history.jsonl"


def load_state(session: Path) -> dict[str, Any]:
    state = json.loads(state_path(session).read_text(encoding="utf-8"))
    refresh_tickets(session, state)
    state["checkpointIssues"] = checkpoint_issues(state, session)
    return state


def checkpoint_file(session: Path, reference: dict[str, Any]) -> Path:
    """Checkpoint reads are confined to the project session or public plugin sources."""
    name = reference.get("path", "")
    if not isinstance(name, str) or not 0 < len(name) <= 1000:
        raise ValueError("checkpoint reference needs a bounded relative path")
    base = ROOT if name.startswith("plugin:") else session
    name = name.removeprefix("plugin:")
    relative = Path(name)
    path = (base / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(base.resolve()):
        raise ValueError("checkpoint reference escapes its allowed root")
    if base == ROOT and ("local-memory" in relative.parts or ".git" in relative.parts
                         or "secret" in name.lower() or relative.suffix not in {".md", ".json", ".py", ".mjs", ".css", ".js"}):
        raise ValueError("checkpoint plugin references must be public source/policy files")
    if not re.fullmatch(r"[0-9a-f]{64}", str(reference.get("sha256", ""))):
        raise ValueError("checkpoint reference needs sha256")
    return path


def file_hash(path: Path) -> str:
    if not path.is_file() or path.stat().st_size > 256 * 1024 * 1024:
        raise ValueError("checkpoint file missing or exceeds 256 MiB")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_required(state: dict[str, Any]) -> bool:
    return (state.get("workflowProfile") == "efficient-v1"
            and state.get("permissionMode") in {"full_build", "export_allowed", "delete_allowed"}
            and not state.get("productionRequired"))


def initial_checkpoint(state: dict[str, Any], session: Path, count: int) -> dict[str, Any]:
    """Initialize the explicit requested roster without inventing progress or acceptance."""
    if type(count) is not int or not 1 <= count <= 500:
        raise ValueError("expected-slides must be 1..500 from the actual task scope")
    if state.get("checkpoint") is not None:
        raise ValueError("Checkpoint already exists; update it instead of resetting progress")
    value = {"schema": "design-brain.checkpoint.v1", "sessionId": state["sessionId"],
        "taskSha256": hashlib.sha256(state["task"].encode()).hexdigest(), "expectedSlides": count,
        "slides": [{"id": i, "status": "todo", "artifacts": []} for i in range(1, count + 1)],
        "dependencies": {kind: [] for kind in ("source", "theme", "master", "font", "image", "render", "policy")},
        "pilot": {"status": "PENDING" if build_selection(task=state["task"]).get("outputMode") in {"native", "both"} else "NOT_APPLICABLE",
                  "slideIds": list(range(1, min(3, count) + 1)), "evidence": []},
        "activeConstraints": ["Preserve the complete requested output and all applicable owner/design policies."],
        "openRepairs": [], "unknownOperations": [],
        "nextAction": {"actor": "main", "target": "task scope and pre-build gates",
                       "action": "Load applicable full sources and record current constraints before delegation",
                       "expectedOutput": "grounded plan and current checkpoint",
                       "checks": ["actual requested slide count", "owner constraints", "no acceptance from initialization"]}}
    validate_checkpoint(value, session, state)
    draft = session / "checkpoint-input.json"
    if draft.exists():
        raise ValueError("checkpoint-input.json already exists; reconcile it instead of overwriting")
    draft.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    return value


def validate_checkpoint(value: Any, session: Path, state: dict[str, Any]) -> dict[str, Any]:
    """Validate advisory continuity, never create creative acceptance or a gate receipt."""
    def need(condition: bool, message: str) -> None:
        if not condition:
            raise ValueError("checkpoint: " + message)

    def text(item: Any) -> bool:
        return isinstance(item, str) and 0 < len(item.strip()) <= 2000

    need(isinstance(value, dict) and len(json.dumps(value)) <= 128000, "expected bounded object")
    need(value.get("schema") == "design-brain.checkpoint.v1", "unsupported schema")
    need(value.get("sessionId") == state.get("sessionId"), "session identity mismatch")
    need(value.get("taskSha256") == hashlib.sha256(state.get("task", "").encode()).hexdigest(), "task identity mismatch")
    count, slides = value.get("expectedSlides"), value.get("slides")
    need(type(count) is int and 1 <= count <= 500, "expectedSlides must be 1..500")
    need(isinstance(slides, list) and len(slides) == count, "complete slide roster required")
    need(all(isinstance(s, dict) and type(s.get("id")) is int for s in slides), "invalid slide IDs")
    need(sorted(s["id"] for s in slides) == list(range(1, count + 1)), "slide IDs must cover 1..expectedSlides once")
    references = []
    for slide in slides:
        need(slide.get("status") in {"todo", "authored", "repair", "awaiting_main", "accepted"}, "invalid slide status")
        artifacts = slide.get("artifacts")
        need(isinstance(artifacts, list) and len(artifacts) <= 20, "invalid slide artifacts")
        need(slide["status"] != "accepted" or bool(artifacts), "accepted slide needs artifact identities")
        references.extend(artifacts)
    deps = value.get("dependencies")
    kinds = {"source", "theme", "master", "font", "image", "render", "policy"}
    need(isinstance(deps, dict) and set(deps) == kinds, "declare source/theme/master/font/image/render/policy dependencies")
    for kind, entries in deps.items():
        need(isinstance(entries, list) and len(entries) <= 100, "dependency list exceeds bound")
        # Empty categories are explicit declarations, not proof of dependency completeness.
        references.extend(entries)
    pilot = value.get("pilot")
    need(isinstance(pilot, dict) and pilot.get("status") in {"PENDING", "PASS", "REVISE", "NOT_APPLICABLE"}, "invalid pilot")
    need(pilot.get("slideIds") == list(range(1, min(3, count) + 1)), "pilot must identify first three slides")
    need(isinstance(pilot.get("evidence"), list) and len(pilot["evidence"]) <= 20, "invalid pilot evidence")
    need(pilot["status"] != "PASS" or bool(pilot["evidence"]), "pilot PASS needs current evidence pointers")
    references.extend(pilot["evidence"])
    constraints = value.get("activeConstraints")
    need(isinstance(constraints, list) and len(constraints) <= 100 and all(text(x) for x in constraints), "invalid active constraints")
    for field, keys in (("openRepairs", ("target", "requestedChange", "acceptanceCheck")),
                        ("unknownOperations", ("id", "status", "reconcile"))):
        entries = value.get(field)
        need(isinstance(entries, list) and len(entries) <= 100, "invalid " + field)
        need(all(isinstance(x, dict) and all(text(x.get(k)) for k in keys) for x in entries), "incomplete " + field)
    need(all(x["status"] in {"UNKNOWN", "INTERRUPTED"} for x in value["unknownOperations"]), "unknown operation must remain unresolved")
    action = value.get("nextAction")
    need(isinstance(action, dict) and action.get("actor") in {"main", "engineer"}
         and all(text(action.get(k)) for k in ("target", "action", "expectedOutput")), "specific next action required")
    need(isinstance(action.get("checks"), list) and 0 < len(action["checks"]) <= 30
         and all(text(x) for x in action["checks"]), "next action checks required")
    for reference in references:
        need(isinstance(reference, dict) and set(reference) == {"path", "sha256"}, "invalid file reference")
        checkpoint_file(session, reference)  # Reject unsafe reads even before reconciliation.
    return value


def checkpoint_issues(state: dict[str, Any], session: Path) -> list[str]:
    value = state.get("checkpoint")
    if value is None:
        return (["checkpoint: required for efficient-v1 host production; initialize the explicit slide roster"]
                if checkpoint_required(state) else [])
    try:
        validate_checkpoint(value, session, state)
    except (ValueError, OSError, TypeError) as error:
        return ["checkpoint: " + str(error).removeprefix("checkpoint: ")]
    issues = [f"slide {s['id']}: {s['status']}" for s in value["slides"] if s["status"] != "accepted"]
    issues += [f"unknown operation {op['id']}: {op['status']}; {op['reconcile']}" for op in value["unknownOperations"]]
    issues += [f"open repair {r['target']}: {r['requestedChange']}" for r in value["openRepairs"]]
    if value["pilot"]["status"] not in {"PASS", "NOT_APPLICABLE"}:
        issues.append("pilot review remains " + value["pilot"]["status"])
    refs = [r for s in value["slides"] for r in s["artifacts"]]
    refs += [r for entries in value["dependencies"].values() for r in entries] + value["pilot"]["evidence"]
    for name, expected in sorted({(r["path"], r["sha256"]) for r in refs}):
        try:
            if file_hash(checkpoint_file(session, {"path": name, "sha256": expected})) != expected:
                issues.append("sha256 changed; reopen affected review: " + name)
        except (ValueError, OSError) as error:
            issues.append(f"unverified file {name}: {error}")
    return issues


def reconciliation_issues(issues: list[str]) -> list[str]:
    return [item for item in issues if item.startswith(("checkpoint:", "unknown operation", "sha256 changed", "unverified file"))]


def save_state(session: Path, state: dict[str, Any]) -> None:
    session.mkdir(parents=True, exist_ok=True)
    state.setdefault("requiredStages", REQUIRED_STAGES[:])
    completed = state["completedStages"] = verified_stages(state)
    state["missingStages"] = [stage for stage in REQUIRED_STAGES if stage not in completed]
    refresh_tickets(session, state)
    state["checkpointIssues"] = checkpoint_issues(state, session)
    state["finalReadiness"] = final_readiness(state)
    if state.get("workflowProfile") == "efficient-v1":
        state["compactContextPath"] = str(session / "compact-context.md")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=session,
                                         prefix=".session-state-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(state, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, state_path(session))
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    (STATE_ROOT / "current-session.json").write_text(json.dumps({"session": str(session)}, indent=2) + "\n", encoding="utf-8")
    if state.get("workflowProfile") == "efficient-v1":
        from design_brain_context_compact import compact_session
        compact_session(session, mirror_root=STATE_ROOT)


def file_reference(path: Path) -> dict[str, str]:
    path = Path(path).resolve()
    return {"path": str(path), "sha256": file_hash(path)}


def references_current(refs: Any, roots: list[Path]) -> bool:
    if not isinstance(refs, list) or not refs or len(refs) > 128:
        return False
    roots = [r.resolve() for r in roots]
    try:
        for item in refs:
            if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
                return False
            path = Path(item["path"])
            if not path.is_absolute() or not any(path.resolve().is_relative_to(r) for r in roots):
                return False
            if any(part.lower() in {".git", ".aws", ".codex", "local-memory"} for part in path.parts) or path.name.lower() == ".env":
                return False
            if file_reference(path) != item:
                return False
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False


def verified_stages(state: dict[str, Any]) -> list[str]:
    """Only current direct tool outcomes satisfy a stage, never a completion label."""
    roots = [ROOT, Path(state.get("projectRoot") or ROOT)]
    completed = []
    for stage, result in state.get("toolResults", {}).items():
        if not isinstance(result, dict) or result.get("status") != "PASS" or result.get("executionState") != "verified":
            continue
        source = result.get("executionSource")
        if source == "native_router":
            if result.get("taskSha256") == hashlib.sha256(state.get("task", "").encode()).hexdigest() and references_current(result.get("evidence"), roots):
                completed.append(stage)
        elif source == "validated_post_build_receipt":
            if references_current(result.get("evidence"), roots) and references_current(result.get("inputs"), roots):
                receipt = result.get("visualReceipt", "")
                artifact = result.get("visualArtifact", "")
                if receipt and artifact and validate_post_build_receipt(receipt, artifact)["status"] == "PASS":
                    completed.append(stage)
        elif source == "native_completion_binding":
            if references_current(result.get("evidence"), roots) and references_current(result.get("inputs"), roots):
                from design_brain_post_build_audit import validate_final_completion
                receipt = result.get("completionReceipt", "")
                audit = result.get("auditReceipt", "")
                artifact = result.get("finalArtifact", "")
                if receipt and audit and artifact and validate_final_completion(Path(receipt), Path(audit), Path(artifact)):
                    completed.append(stage)
    return completed


def refresh_tickets(session: Path, state: dict[str, Any]) -> None:
    path = ticket_file(session)
    if not path.exists():
        state.setdefault("openRepairTickets", [])
        state["pendingGateReruns"] = []
        state.pop("ticketRecoveryRequired", None)
        return
    try:
        tickets = load_tickets(path)
        state["openRepairTickets"] = [ticket for ticket in tickets if ticket.get("status") != "closed"]
        state["pendingGateReruns"] = [ticket["ticketId"] for ticket in tickets if ticket.get("status") == "closed" and ticket.get("rerunGateRequired", True)]
        state.pop("ticketRecoveryRequired", None)
    except (ValueError, OSError) as error:
        state["ticketRecoveryRequired"] = str(error)


def append_history(session: Path, event: dict[str, Any]) -> None:
    event = {"timestamp": now(), **event}
    with history_path(session).open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event) + "\n")
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    with (STATE_ROOT / "session-history.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"session": str(session), **event}) + "\n")


def final_readiness(state: dict[str, Any], *, required_stages: list[str] | None = None) -> dict[str, Any]:
    verified = verified_stages(state)
    required = REQUIRED_STAGES if required_stages is None else required_stages
    missing = [stage for stage in required if stage not in verified]
    tickets = [t for t in state.get("openRepairTickets", []) if t.get("status") != "closed"]
    allowed = not missing and not tickets
    reason = "READY" if allowed else "; ".join(
        [f"missing or unverified stages: {', '.join(missing)}" if missing else "", f"open repair tickets: {len(tickets)}" if tickets else ""]
    ).strip("; ")
    if state.get("ticketRecoveryRequired") or state.get("pendingGateReruns"):
        allowed = False
        reason = (reason + "; " + (state.get("ticketRecoveryRequired") or "closed issue still requires current source-gate rerun")).strip("; ")
    if state.get("permissionMode") == "diagnostic_only":
        allowed = False
        reason = "diagnostic_only cannot claim final READY"
    if state.get("checkpointIssues"):
        allowed = False
        reason += "; continuity blockers: " + "; ".join(state["checkpointIssues"])
    if checkpoint_required(state) and state.get("checkpoint") is None:
        allowed = False
        reason += "; checkpoint required before finalization"
    if state.get("repairProgress", {}).get("mainDecisionRequired"):
        allowed = False
        reason += "; repeated repair without progress requires a recorded Main decision"
    if "post_build_audit" in verified:
        visual_path = state.get("toolResults", {}).get("post_build_audit", {}).get("visualReceipt", "")
        visual_artifact = state.get("toolResults", {}).get("post_build_audit", {}).get("visualArtifact", "")
        visual_result = validate_post_build_receipt(visual_path, visual_artifact) if visual_path and visual_artifact else {"status": "BLOCKED", "issues": ["current post-build visual receipt or target artifact missing"]}
        if visual_result["status"] != "PASS":
            allowed = False
            reason = (reason + "; " + "; ".join(visual_result["issues"])).strip("; ")
    if state.get("productionRequired"):
        from design_production.hook import load_job, valid_artifacts
        try:
            jobs = state.get("productionJobs", [])
            if not jobs:
                raise ValueError("Authorized production has not returned a reviewable result")
            # Only the latest revision of each logical stage can satisfy production readiness.
            latest = {}
            for identifier in jobs:
                job = load_job(identifier)
                key = (job["task"]["parent_request_id"], job["task"]["stage"], job["task"]["artifact_type"], tuple(u["id"] for u in job["task"]["units"]))
                if key not in latest or job["task"]["revision"] > latest[key]["task"]["revision"]:
                    latest[key] = job
            for job in latest.values():
                if job["status"] != "APPROVED":
                    raise ValueError("Design production requires Main approval")
                valid_artifacts(job)
        except (ValueError, OSError, KeyError) as error:
            allowed = False
            reason = (reason + "; " + str(error)).strip("; ")
    return {"finalAllowed": allowed, "status": "READY" if allowed else "BLOCKED", "reason": "READY" if allowed else reason}



def progress_projection(state: dict, session: Path) -> dict:
    """One current, non-approving progress/next-action projection for all status consumers."""
    current = dict(state)
    refresh_tickets(session, current)
    missing = [stage for stage in REQUIRED_STAGES if stage not in verified_stages(current)]
    ticket_path = session / "repair-tickets.json"
    tickets = [ticket for ticket in current.get("openRepairTickets", []) if ticket.get("status") != "closed"]
    issues = checkpoint_issues(current, session)
    if tickets and not ticket_path.is_file():
        issues.append("unverified file repair-tickets.json: stored open tickets require reconciliation")
    current.update(missingStages=missing, openRepairTickets=tickets, checkpointIssues=issues)
    readiness = final_readiness(current)
    checkpoint = current.get("checkpoint")
    valid = isinstance(checkpoint, dict) and not any(item.startswith("checkpoint:") for item in issues)
    checkpoint = checkpoint if valid else None
    failed = [stage for stage, result in current.get("toolResults", {}).items() if result.get("status") in {"FAIL","BLOCKED","ERROR"}]
    requested = [stage for stage, result in current.get("toolResults", {}).items() if result.get("status") in {"REQUESTED","RECORDED"}]
    reconcile = reconciliation_issues(issues)
    counts = {status: sum(slide["status"] == status for slide in checkpoint["slides"]) if checkpoint else 0
              for status in ("todo", "authored", "repair", "awaiting_main", "accepted")}

    def action(actor, target, description, output, checks, command="/design-status"):
        return {"actor": actor, "target": target, "action": description, "expectedOutput": output,
                "checks": checks, "command": command}

    if checkpoint_required(current) and current.get("checkpoint") is None:
        next_action = action("main", "requested slide roster", "Initialize checkpoint with the actual requested slide count",
            "checkpoint-input.json with todo slides; no invented acceptance",
            ["checkpoint --initialize --expected-slides N", "preserve full task and active constraints"])
    elif reconcile:
        next_action = action("main", "current source/dependencies and unknown operations", "Reconcile continuity blockers before continuing",
            "current identities and resolved operation state, without blind replay", reconcile)
    elif current.get("repairProgress", {}).get("mainDecisionRequired"):
        next_action = action("main", "repeated repair batch", "Decide a concrete repair strategy before another Engineer round",
            "checkpoint with --main-decision; open repairs remain open",
            ["inspect the unresolved defects", "batch all confirmed corrections", "preserve current quality criteria"])
    elif tickets or (checkpoint and checkpoint["openRepairs"]) or failed:
        repair = tickets[0] if tickets else checkpoint["openRepairs"][0] if checkpoint and checkpoint["openRepairs"] else {}
        next_action = action("engineer", repair.get("target", repair.get("ticketId", failed[0] if failed else "repair")),
            repair.get("requestedChange", repair.get("requiredRepair", "Repair failed gate using current evidence")),
            "repaired source and rerun evidence for Main review",
            [repair.get("acceptanceCheck", repair.get("sourceGate", ", ".join(failed) or "assigned acceptance checks"))])
    elif requested:
        next_action = action("engineer", requested[0], "Run the actual requested stage and attach current observed execution evidence",
            "Bound source-gate result or explicit unresolved status, never automatic PASS",
            ["perform the real routed operation", "inspect fresh input hashes and actual outcome"])
    elif checkpoint and checkpoint["pilot"]["status"] in {"PENDING", "REVISE"}:
        pilot_slides = [slide for slide in checkpoint["slides"] if slide["id"] in checkpoint["pilot"]["slideIds"]]
        needs_authoring = any(slide["status"] in {"todo", "repair"} for slide in pilot_slides)
        next_action = action("engineer" if needs_authoring else "main", "pilot slides " + ", ".join(str(slide["id"]) for slide in pilot_slides),
            "Author/repair only pilot slides and provide current renders" if needs_authoring else "Inspect current pilot and record PASS or REVISE",
            "pilot source/render evidence" if needs_authoring else "Main review bound to current pilot identities",
            ["first-three-slide policy", "current render/originality/image/balance evidence", "no slide 4+ authoring before Main PASS"])
    elif checkpoint and any(counts[status] for status in ("todo", "authored", "repair", "awaiting_main")) and not (missing and missing[0] in REQUIRED_STAGES[:8]):
        todo = [slide["id"] for slide in checkpoint["slides"] if slide["status"] in {"todo", "repair"}]
        pending = todo or [slide["id"] for slide in checkpoint["slides"] if slide["status"] != "accepted"]
        next_action = action("engineer" if todo else "main", "slides " + ", ".join(map(str, pending)),
            "Author remaining requested slides" if todo else "Inspect current authored slides and record review",
            "current source/render evidence for Main" if todo else "Main review bound to current artifact identities",
            ["complete original roster and active constraints", "current applicable design gates", "no inherited visual PASS"])
    elif current.get("permissionMode") == "diagnostic_only":
        next_action = action("main", "permission boundary", "diagnostic_only cannot finalize any deck",
            "Explicitly authorized non-diagnostic build session and current gate observations",
            ["Do not infer execution from recorded stages", "Do not claim READY in diagnostic mode"])
    elif missing:
        command = next((name for name, stage in COMMAND_TO_STAGE.items() if stage == missing[0]), "/design-run-next")
        next_action = action("main", missing[0], "Run required gate: " + missing[0], "current gate evidence",
                             ["actual execution and applicable acceptance criteria"], command)
    elif readiness["finalAllowed"]:
        next_action = action("main", "current complete artifact", "Finalize through closing gates and current Main inspection",
                             "truthful final readiness/delivery", ["all requested output", "current every-slide visual review"], "/design-finalize")
    else:
        next_action = action("main", "final readiness", "Reconcile current final-readiness blockers", "current verified evidence",
                             [readiness["reason"]])
    return {"schema": "design-brain.progress-projection.v1", "session": str(session.resolve()),
            "sessionId": current.get("sessionId"), "taskSha256": hashlib.sha256(current.get("task", "").encode()).hexdigest(),
            "workflowProfile": current.get("workflowProfile", "legacy"), "completedStages": current.get("completedStages", []),
            "missingStages": missing, "currentStage": missing[0] if missing else "complete", "failedGates": failed,
            "expectedSlides": checkpoint["expectedSlides"] if checkpoint else None, "slideCounts": counts,
            "openRepairTickets": tickets, "checkpointIssues": issues, "reconciliationRequired": reconcile,
            "blockers": issues + ([readiness["reason"]] if not readiness["finalAllowed"] else []),
            "evidence": {"sessionState": str(state_path(session)), "checkpoint": "session-state.json#checkpoint",
                         "repairTickets": str(ticket_path), "visualReceipt": current.get("toolResults", {}).get("post_build_audit", {}).get("visualReceipt")},
            "nextAction": next_action, "declaredNextAction": checkpoint.get("nextAction") if checkpoint else None,
            "repairProgress": current.get("repairProgress", {}),
            "finalReadiness": readiness, "finalMainVisualReviewRequired": True}

def runtime_result(command: str, tool: str, status: str, blocking: bool, next_action: str, repairs: list[str] | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "command": command,
        "tool": tool,
        "blocking": blocking,
        "requiredRepairs": repairs or [],
        "recommendedImprovements": [],
        "evidence": {},
        "nextAction": next_action,
        "finalAllowed": False,
    }


def workflow_commands(session: Path, state: dict, role: str, phase: str, epoch: str) -> dict:
    """Describe existing commands only; never run tools, dispatch workers or grant approval."""
    if role not in {"main", "engineer"} or phase not in {"plan", "build", "repair", "final"}:
        raise ValueError("Invalid workflow role/phase")
    if not epoch.strip() or len(epoch) > 200:
        raise ValueError("An explicit bounded context epoch is required")
    session = session.resolve()
    python = [sys.executable, "-B"]
    runtime = [*python, str(ROOT / "scripts/design_brain_runtime.py")]
    memory = [*python, str(ROOT / "scripts/design_brain_memory_adapter.py")]
    task = state.get("task", "")
    selection = build_selection(task=task)
    conversion = selection.get("outputMode") in {"web", "both"} and bool(re.search(
        r"\.(?:pptx|key|fig|pdf)\b|convert|conversion|deck to web|ppt(?:x)? (?:to|ke) (?:html|web)|ubah ppt|existing deck|my deck", task, re.I))
    return {"schema": "design-brain.workflow-commands.v1", "session": str(session),
            "sessionId": state.get("sessionId"), "workflowProfile": state.get("workflowProfile", "legacy"),
            "role": role, "phase": phase, "contextEpoch": epoch,
            "pluginIdentity": {"root": str(ROOT), "version": json.loads((ROOT / "package.json").read_text(encoding="utf-8")).get("version", "unknown") if (ROOT / "package.json").is_file() else "unknown",
                               "runtimeSha256": file_hash(Path(__file__))},
            "checkpointRequired": checkpoint_required(state),
            "checkpointInitializePrefix": [*runtime, "checkpoint", "--session", str(session), "--initialize", "--expected-slides"],
            "checkpointCommand": [*runtime, "checkpoint", "--session", str(session), "--file", str(session / "checkpoint-input.json"), "--json"],
            "compactCommand": [*runtime, "compact", "--session", str(session), "--json"],
            "continuity": "Save the current roster, constraints, source hashes and batched repairs before handoff/resume. Use --repair-round once per completed repair batch; two rounds with no resolved targets require --main-decision. This does not meter arbitrary host calls or grant PASS.",
            "contextCommand": [*python, str(ROOT / "scripts/design_brain_runtime.py"), "prepare-context",
                "--session", str(session), "--role", role, "--phase", phase, "--context-epoch", epoch, "--json"],
            "nativePrefix": [*python, str(ROOT / "skills/presentation-deck/runtime/presentation.py"), "--session", str(session)],
            "sourceExtractionPrefix": ["node", str(ROOT / "skills/presentation-deck/runtime/web/design_brain_deck_source_extract.mjs"),
                "--summary", "--out", str(session / "analysis/deck-source")] if conversion else None,
            "memoryDiscovery": {"search": [*memory, "search", task, "--projection", "summary"],
                "list": [*memory, "list", "--kind", "layout_case", "--projection", "summary"],
                "historyPrefix": [*memory, "history"], "historySuffix": ["--projection", "summary"],
                "fullReadPrefix": [*memory, "read"], "revisionSuffix": ["--revision", "<N>"], "originSuffix": ["--origin", "<origin>"],
                "operationSuffix": ["--operation-id", "<operation-id>"]},
            "fullReadRequired": "Page BOTH remote/local next_offset values to required coverage. Read full applicable records with each discovery full_read pointer (read ID --origin ORIGIN --revision N and --operation-id OPERATION_ID when supplied), compare all origins, and preserve corrections/negative/conflicting evidence. Each role reads its own sources; manifests never attest knowledge.",
            "navigation": {"mode": "auto for efficient-v1; off for legacy unless explicit", "authority": "supplemental only; no automatic network/model call"},
            "execution": "DESCRIBED_ONLY: original action/argv still requires applicable host approval; no automatic dispatch."}


def command_prepare_context(args: argparse.Namespace) -> dict[str, Any]:
    from design_brain_context_packet import write_packet
    session = Path(args.session).resolve()
    state = load_state(session)
    commands = workflow_commands(session, state, args.role, args.phase, args.context_epoch)
    if checkpoint_required(state) and (args.role == "engineer" or args.phase != "plan" or state.get("contextManifests", {}).get(args.role)):
        issues = reconciliation_issues(state["checkpointIssues"])
        if issues or (args.role == "engineer" and state.get("repairProgress", {}).get("mainDecisionRequired")):
            return {"status": "BLOCKED", "finalAllowed": False, "checkpointIssues": issues,
                    "progress": progress_projection(state, session), "workflowCommands": commands}
    epoch_id = hashlib.sha256(args.context_epoch.encode()).hexdigest()[:16]
    directory = session / "context" / args.role
    if not directory.resolve().is_relative_to(session):
        raise ValueError("Context output escapes project session")
    stem = f"{args.phase}-{epoch_id}"
    previous = state.get("contextManifests", {}).get(args.role, "")
    # Stored paths are untrusted session data; never read a prior manifest outside this session.
    if previous and not Path(previous).resolve().is_relative_to(session):
        raise ValueError("Previous loading manifest escapes session")
    navigation_mode = getattr(args, "navigation", "auto")
    navigation_enabled = navigation_mode == "on" or (navigation_mode == "auto" and state.get("workflowProfile", "legacy") == "efficient-v1")
    memory_discovery = getattr(args, "navigation_memory_discovery", "")
    if memory_discovery and not navigation_enabled:
        raise ValueError("Memory discovery overlay requires enabled navigation")
    packet_args = argparse.Namespace(task=state["task"], reference=False, template_type="", niche="",
        target_buyer="", visual_mood="", naming=False, review=False, output=str(directory / (stem + ".md")),
        dry_run=False, role=args.role, phase=args.phase,
        stage={"plan":"planning","build":"authoring","repair":"review","final":"delivery"}[args.phase],
        context_epoch=args.context_epoch,
        manifest_output=str(directory / (stem + ".json")), previous_manifest=previous, manifest_summary=True,
        navigation="on" if navigation_enabled else "off", navigation_session=str(session),
        navigation_cache_dir=getattr(args, "navigation_cache_dir", ""), navigation_memory_discovery=memory_discovery)
    result = write_packet(packet_args, ROOT)
    state.setdefault("contextManifests", {})[args.role] = result["manifestPath"]
    save_state(session, state)
    return {"status": "PASS", **result["summary"], "workflowCommands": commands}


def command_start(args: argparse.Namespace) -> dict[str, Any]:
    if not getattr(args, "production_request", ""):
        require_presentation(args.task)
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    sid = session_id()
    session = (Path(args.output_dir).resolve() if args.output_dir else STATE_ROOT / sid)
    if session.exists():
        raise ValueError("Session already exists; resume/status/checkpoint instead of overwriting progress")
    if getattr(args, "production_request", ""):
        from design_production.policy import within
        within(session, ROOT)
        if session.exists():
            raise ValueError("Production start requires a new session directory")
    session.mkdir(parents=True, exist_ok=True)
    state = {
        "sessionId": session.name,
        "projectRoot": str(Path(getattr(args, "project_root", "") or ROOT).resolve()),
        "task": args.task,
        "permissionMode": args.permission_mode,
        "workflowProfile": getattr(args, "workflow_profile", "efficient-v1"),
        "route": "",
        "productFamily": "",
        "expectedTemplateCount": args.expected_templates,
        "currentTemplateId": "template-1",
        "requiredStages": REQUIRED_STAGES[:],
        "completedStages": [],
        "missingStages": REQUIRED_STAGES[:],
        "activeTool": "",
        "toolResults": {},
        "openRepairTickets": [],
        "finalReadiness": {"finalAllowed": False, "status": "BLOCKED", "reason": "session just started"},
        "compactContextPath": "",
        "createdAt": now(),
        "updatedAt": now(),
    }
    count = getattr(args, "expected_slides", None)
    if count is not None:
        state["checkpoint"] = initial_checkpoint(state, session, count)
    save_state(session, state)
    append_history(session, {"event": "session_started", "task": args.task, "permissionMode": args.permission_mode})
    if getattr(args, "production_request", ""):
        args.session = str(session)
        payload = command_production(args)
        return {**payload, "session": str(session), "state": load_state(session)}
    return {"status": "PASS", "session": str(session), "state": state,
            "workflowCommands": {role: workflow_commands(session, state, role, "plan", f"{sid}-{role}")
                                 for role in ("main", "engineer")}}


def command_production(args: argparse.Namespace) -> dict[str, Any]:
    """Automatic authorized production boundary; also used for Main-requested revisions."""
    from design_production.hook import DesignProductionAutoHook
    session = Path(args.session).resolve()
    state = load_state(session)
    previously_required = state.get("productionRequired", False)
    state["productionRequired"] = True
    save_state(session, state)  # Fail closed even if request parsing or execution fails.
    def register(identifier):
        jobs = state.setdefault("productionJobs", [])
        if identifier not in jobs:
            jobs.append(identifier)
        save_state(session, state)
    try:
        payload = DesignProductionAutoHook().dispatch(args.production_request,
            state.get("permissionMode", "diagnostic_only"), getattr(args, "dry_run", False), str(session), register)
        if not payload["hook"]["eligible"]:
            state["productionRequired"] = previously_required or bool(state.get("productionJobs"))
        if payload.get("job"):
            jobs = state.setdefault("productionJobs", [])
            if payload["job"]["task_id"] not in jobs:
                jobs.append(payload["job"]["task_id"])
        state.setdefault("toolResults", {})["design_production"] = payload
    except (ValueError, OSError) as error:
        payload = {"status": "BLOCKED", "error": str(error), "finalAllowed": False}
    save_state(session, state)
    append_history(session, {"event": "design_production_auto_hook", "result": payload})
    return payload


def command_production_control(args: argparse.Namespace) -> dict[str, Any]:
    from design_production.hook import cancel, recover, main_review
    from design_production.contracts import MainReviewDecision
    from design_production.policy import input_path
    session = Path(args.session).resolve()
    state = load_state(session)
    if not can_run("/design-produce", state.get("permissionMode", "diagnostic_only")).allowed:
        raise ValueError("Production control requires full_build permission")
    identifier = (MainReviewDecision.model_validate_json(input_path(args.review).read_bytes()).task_id
                  if args.command == "review-production" else args.task_id)
    if identifier not in state.get("productionJobs", []):
        # While the synchronous start is running, its job is already durable but not yet returned.
        from design_production.hook import load_job
        record = load_job(identifier)
        if args.command != "cancel-production" or record.get("session") != str(session):
            raise ValueError("Task is not owned by this runtime session")
    if args.command == "review-production":
        job = main_review(args.review, state["permissionMode"])
    elif args.command == "cancel-production":
        job = cancel(identifier)
    else:
        job = recover(identifier)
    save_state(session, state)
    append_history(session, {"event": args.command, "job": job})
    return {"status": "PASS", "job": job, "finalAllowed": state["finalReadiness"]["finalAllowed"]}



def mark_stage(state: dict[str, Any], stage: str, result: dict[str, Any]) -> None:
    if result.get("executionState") == "verified" and result.get("status") == "PASS":
        stages = state.setdefault("completedStages", [])
        if stage not in stages:
            stages.append(stage)
    state.setdefault("toolResults", {})[stage] = result
    state["activeTool"] = result.get("tool", "")
    if stage == "route" and result.get("executionState") == "verified":
        state["route"] = result.get("route", "")
        state["productFamily"] = result.get("productFamily", "")


def command_run(args: argparse.Namespace) -> dict[str, Any]:
    if args.command_name == "/design-produce":
        if not getattr(args, "production_request", ""):
            return {"status": "BLOCKED", "error": "Supply an authorized --production-request", "finalAllowed": False}
        return command_production(args)
    session = Path(args.session).resolve()
    state = load_state(session)
    routed = route_command(args.command_name, state.get("permissionMode", "diagnostic_only"))
    if not routed.permissionAllowed:
        result = runtime_result(args.command_name, routed.tool, "BLOCKED", True, "Use a higher permission mode.", [routed.permissionReason])
        append_history(session, {"event": "permission_blocked", "result": result})
        return result
    if args.simulate_fail:
        ticket = create_ticket(session_id=state["sessionId"], source_gate=routed.stage or args.command_name,
                               issue=args.simulate_fail, required_repair=args.simulate_fail, session=session)
        refresh_tickets(session, state)
        save_state(session, state)
        result = runtime_result(args.command_name, routed.tool, "BLOCKED", True, "Repair issue and rerun gate.", [ticket["requiredRepair"]])
        append_history(session, {"event": "gate_failed", "result": result, "ticket": ticket})
        return result
    if not routed.stage:
        return runtime_result(args.command_name, routed.tool, "ERROR", True, "Use a registered command.", ["Unknown command"])
    result = runtime_result(args.command_name, routed.tool, "REQUESTED", False, "Execute the routed stage and supply observed evidence.")
    result.update(stage=routed.stage, executionState="requested", executionSource="not_executed")
    if routed.stage == "route":
        selection = build_selection(task=state.get("task", ""))
        paths = [ROOT/name for name in ("scripts/design_brain_modules.py", "scripts/design_brain_presentation_route.py",
                  "scripts/design_brain_website_types.py", ".design-brain/registry/modules.json", ".design-brain/direction-packs/directions.json")]
        evidence = [file_reference(path) for path in paths if path.is_file()]
        result.update(status="PASS", executionState="verified", executionSource="native_router",
                      route=selection["moduleId"], productFamily=selection.get("kind", "presentation_template"),
                      taskSha256=hashlib.sha256(state.get("task", "").encode()).hexdigest(),
                      evidence=evidence, verificationScope="Actual native routing only; no downstream gate execution")
    elif routed.stage == "post_build_audit":
        receipt_path, artifact = getattr(args, "visual_receipt", ""), getattr(args, "build_artifact", "")
        visual = (validate_post_build_receipt(receipt_path, artifact) if receipt_path and artifact else
                  {"status": "BLOCKED", "issues": ["Current post-build visual inspection receipt and artifact required"]})
        if visual["status"] != "PASS":
            result.update(status="BLOCKED", blocking=True, executionState="not_verified",
                          requiredRepairs=visual["issues"], nextAction="Run actual audit and visual QA; inspect result")
        else:
            from design_brain_post_build_audit import audit_inputs_current
            import json as _json
            audit = _json.loads(Path(receipt_path).read_text(encoding="utf-8"))
            if audit.get("auditPhase") != "evidence" or not audit_inputs_current(audit):
                result.update(status="BLOCKED", blocking=True, executionState="not_verified",
                              requiredRepairs=["Audited dependencies are not current or were not fully declared"])
            else:
                result.update(status="PASS", executionState="verified", executionSource="validated_post_build_receipt",
                              visualReceipt=str(Path(receipt_path).resolve()), visualArtifact=str(Path(artifact).resolve()),
                              evidence=[file_reference(Path(receipt_path))], inputs=[file_reference(Path(artifact))],
                              verificationScope="Current audit+visual record, not independent proof of pixels seen")
    elif routed.stage in {"completion_receipt", "verify_final"}:
        result["nextAction"] = "Use /design-finalize to bind the current audited inputs after prior gates."
    elif getattr(args, "stage_result", ""):
        path = Path(args.stage_result).resolve()
        try:
            if not path.is_file() or path.stat().st_size > 1024*1024:
                raise ValueError("External stage receipt missing or exceeds 1 MiB")
            receipt = json.loads(path.read_text(encoding="utf-8"))
            roots = [ROOT, Path(state.get("projectRoot") or ROOT)]
            if (receipt.get("stage") != routed.stage or receipt.get("status") != "PASS"
                    or receipt.get("executionState") != "executed"
                    or not any(path.is_relative_to(r.resolve()) for r in roots)
                    or not references_current(receipt.get("inputs"), roots)
                    or not references_current(receipt.get("evidence"), roots)):
                raise ValueError("Receipt identity, scope or declared evidence is invalid/stale")
            result.update(status="RECORDED", executionState="recorded", executionSource="external_attestation",
                          inputs=receipt["inputs"], evidence=[file_reference(path), *receipt["evidence"]],
                          verificationScope="External declaration with current file hashes; NOT direct observation")
        except (OSError, ValueError, KeyError, TypeError) as error:
            result.update(status="BLOCKED", blocking=True, executionState="not_verified",
                          requiredRepairs=[str(error)], nextAction="Reconcile external claim and inspect source-gate evidence")
    mark_stage(state, routed.stage, result)
    state["updatedAt"] = now()
    save_state(session, state)
    result["finalAllowed"] = state["finalReadiness"]["finalAllowed"]
    append_history(session, {"event": "stage_" + result["executionState"], "stage": routed.stage, "result": result})
    return result


def command_run_next(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    missing = [stage for stage in REQUIRED_STAGES if stage not in verified_stages(state)]
    if not missing:
        return {"status": "PASS", "message": "All stages complete.", "finalAllowed": final_readiness(state)["finalAllowed"]}
    stage = missing[0]
    command = next((cmd for cmd, mapped in COMMAND_TO_STAGE.items() if mapped == stage), "/design-status")
    args.command_name = command
    args.simulate_fail = ""
    return command_run(args)


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    projection = progress_projection(state, session)
    state.update(openRepairTickets=projection["openRepairTickets"], checkpointIssues=projection["checkpointIssues"],
                 missingStages=projection["missingStages"], finalReadiness=projection["finalReadiness"])
    refresh_tickets(session, state)
    return {"status": "PASS", "session": str(session), "state": state, "progress": projection}


def repair_targets(state: dict[str, Any], checkpoint: Any, session: Path | None = None) -> set[str]:
    """Keep checkpoint defects, canonical tickets and failed gates in one repair baseline."""
    repairs = checkpoint.get("openRepairs", []) if isinstance(checkpoint, dict) else []
    repairs = repairs if isinstance(repairs, list) else []
    targets = {"checkpoint:" + item["target"] for item in repairs
               if isinstance(item, dict) and isinstance(item.get("target"), str)}
    tickets = state.get("openRepairTickets", [])
    targets.update("ticket:" + item["ticketId"] for item in tickets
                   if isinstance(item, dict) and item.get("status") != "closed" and isinstance(item.get("ticketId"), str))
    targets.update("gate:" + name for name, result in state.get("toolResults", {}).items()
                   if isinstance(result, dict) and result.get("status") in {"FAIL","BLOCKED","ERROR"})
    return targets


def command_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    if getattr(args, "initialize", False):
        value = initial_checkpoint(state, session, getattr(args, "expected_slides", None))
    else:
        source = Path(args.file).resolve()
        if not source.is_relative_to(session) or source.stat().st_size > 128000:
            raise ValueError("Checkpoint input must be inside the session and at most 128 KB")
        value = validate_checkpoint(json.loads(source.read_text(encoding="utf-8")), session, state)
    previous = state.get("checkpoint")
    if isinstance(previous, dict) and value["expectedSlides"] != previous.get("expectedSlides", value["expectedSlides"]):
        raise ValueError("Checkpoint cannot silently change requested slide count; reconcile the task scope first")
    decision = getattr(args, "main_decision", "")
    if decision and (not decision.strip() or len(decision) > 2000):
        raise ValueError("Main decision must describe a bounded concrete repair strategy")
    progress = state.setdefault("repairProgress", {})
    before = set(progress.get("openTargets", repair_targets(state, previous)))
    after = repair_targets(state, value, session)
    if getattr(args, "repair_round", False):
        stagnant = progress.get("stagnantRounds", 0) + 1 if after and not (before - after) else 0
        progress.update(rounds=progress.get("rounds", 0) + 1, stagnantRounds=stagnant,
                        openTargetCount=len(after), mainDecisionRequired=stagnant >= 2)
    progress.update(openTargets=sorted(after), openTargetCount=len(after))
    if not after:
        progress.update(stagnantRounds=0, mainDecisionRequired=False)
    if decision:
        state.setdefault("repairProgress", {}).update(stagnantRounds=0, mainDecisionRequired=False, mainDecision=decision)
    state["checkpoint"] = value
    state["updatedAt"] = now()
    save_state(session, state)
    append_history(session, {"event": "checkpoint", "checkpointIssues": state["checkpointIssues"],
                             "repairProgress": state.get("repairProgress", {})})
    reconciliation = reconciliation_issues(state["checkpointIssues"])
    return {"status": "BLOCKED" if reconciliation or state.get("repairProgress", {}).get("mainDecisionRequired") else "PASS", "checkpointIssues": state["checkpointIssues"],
            "completionPending": bool(state["checkpointIssues"]), "reconciliationRequired": reconciliation,
            "slideCounts": {status: sum(s["status"] == status for s in value["slides"])
                           for status in ("todo", "authored", "repair", "awaiting_main", "accepted")},
            "statePath": str(state_path(session)), "finalAllowed": False,
            "nextAction": progress_projection(state, session)["nextAction"], "repairProgress": state.get("repairProgress", {}),
            "scope": "Continuity only; all closing gates and final Main visual inspection remain required."}



def command_finalize(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    preflight = final_readiness(state, required_stages=[stage for stage in REQUIRED_STAGES if stage not in {"completion_receipt", "verify_final"}])
    if preflight["finalAllowed"]:
        from design_brain_post_build_audit import finalize_completion
        post = state.get("toolResults", {}).get("post_build_audit", {})
        audit_path, artifact = Path(post.get("visualReceipt", "")), Path(post.get("visualArtifact", ""))
        try:
            audited = json.loads(audit_path.read_text(encoding="utf-8"))
            build_dir = Path(audited.get("buildDir") or audit_path.parent).resolve()
            allowed_roots = [ROOT.resolve(), Path(state.get("projectRoot") or ROOT).resolve()]
            if not any(build_dir.is_relative_to(root) for root in allowed_roots):
                raise ValueError("audited build directory escapes explicit project/plugin roots")
            completion = finalize_completion(build_dir, audit_path, artifact)
            if completion.get("finalAllowed") is True:
                receipt_path = build_dir / "completion-receipt.json"
                evidence = {"status": "PASS", "executionState": "verified",
                    "executionSource": "native_completion_binding", "tool": "completion_receipt_tool",
                    "completionReceipt": str(receipt_path.resolve()), "auditReceipt": str(audit_path.resolve()),
                    "finalArtifact": str(artifact.resolve()),
                    "evidence": [file_reference(receipt_path), file_reference(audit_path)],
                    "inputs": [file_reference(artifact)],
                    "verificationScope": "Revalidated audited bytes and final technical evidence only"}
                mark_stage(state, "completion_receipt", evidence)
                mark_stage(state, "verify_final", evidence)
        except (OSError, KeyError, ValueError, TypeError) as error:
            preflight = {"finalAllowed": False, "reason": f"Final binding unavailable: {error}"}
    readiness = final_readiness(state)
    if not preflight["finalAllowed"]:
        readiness = {"finalAllowed": False, "status": "BLOCKED", "reason": preflight["reason"]}
    state["finalReadiness"] = readiness
    save_state(session, state)
    append_history(session, {"event": "finalize", "finalAllowed": readiness["finalAllowed"]})
    return {"status": "PASS" if readiness["finalAllowed"] else "BLOCKED", "command": "/design-finalize",
        "tool": "completion_receipt_tool", "finalAllowed": readiness["finalAllowed"],
        "blocking": not readiness["finalAllowed"], "requiredRepairs": [] if readiness["finalAllowed"] else [readiness["reason"]],
        "nextAction": "Delivery allowed." if readiness["finalAllowed"] else "Complete actual gates and re-audit changed inputs"}


def command_compact(args: argparse.Namespace) -> dict[str, Any]:
    from design_brain_context_compact import compact_session

    session = Path(args.session).resolve()
    state = load_state(session)
    state["compactContextPath"] = str(session / "compact-context.md")
    save_state(session, state)
    payload = compact_session(session, full=getattr(args, "full", False), mirror_root=STATE_ROOT)
    append_history(session, {"event": "compact", "contextPath": payload["contextPath"]})
    return {"status": "BLOCKED" if reconciliation_issues(state["checkpointIssues"]) else "PASS", **payload}


def command_resume(args: argparse.Namespace) -> dict[str, Any]:
    """Read 2.9.0 canonical slide/checkpoint state without rewriting session bytes."""
    session = Path(args.session).resolve()
    state = load_state(session)
    issues = checkpoint_issues(state, session)
    checkpoint = state.get("checkpoint")
    if not isinstance(checkpoint, dict) or any(x.startswith("checkpoint:") for x in issues):
        currency = "UNKNOWN"
    elif any(x.startswith(("sha256 changed", "unverified file")) for x in issues):
        currency = "STALE"
    else:
        currency = "CURRENT"
    # This is a read-only projection of the validated canonical v2.9.0 roster;
    # per-slide currency is never persisted or mistaken for acceptance.
    def reference_currency(ref):
        try:
            return "current" if file_hash(checkpoint_file(session, ref)) == ref["sha256"] else "stale"
        except (OSError, ValueError, KeyError, TypeError):
            return "unknown"
    projected_checkpoint = json.loads(json.dumps(checkpoint)) if isinstance(checkpoint, dict) else {
        "status": "UNKNOWN", "slides": [], "nextSlide": None}
    affected = []
    remaining = []
    if isinstance(checkpoint, dict) and currency != "UNKNOWN":
        shared = [ref for entries in checkpoint["dependencies"].values() for ref in entries]
        shared_state = [reference_currency(ref) for ref in shared]
        for slide in projected_checkpoint["slides"]:
            originals = next(row for row in checkpoint["slides"] if row["id"] == slide["id"])
            local_state = [reference_currency(ref) for ref in originals["artifacts"]]
            status = "stale" if "stale" in [*shared_state, *local_state] else (
                "unknown" if "unknown" in [*shared_state, *local_state] else "current")
            slide["currency"] = status
            if status != "current":
                affected.append(slide["id"])
            if originals["status"] != "accepted" or status != "current":
                remaining.append(slide["id"])
        projected_checkpoint["status"] = currency
        projected_checkpoint["nextSlide"] = remaining[0] if remaining else None
    projected = progress_projection(state, session)
    return {"status": "PASS" if currency == "CURRENT" else "BLOCKED", "currency": currency,
        "checkpoint": projected_checkpoint, "remainingSlides": remaining,
        "affectedSlideIds": affected,
        "pilot": checkpoint.get("pilot") if isinstance(checkpoint, dict) else None,
        "openRepairTickets": projected["openRepairTickets"], "ticketRecoveryRequired": state.get("ticketRecoveryRequired", ""),
        "progress": projected, "finalAllowed": projected["finalReadiness"]["finalAllowed"],
        "scope": "Read-only session recovery; hashes prove byte currency, never creative acceptance"}



def command_doctor(_: argparse.Namespace) -> dict[str, Any]:
    from design_brain_doctor import run_doctor

    return run_doctor()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain Design Design Agent Runtime.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--task", required=True)
    start.add_argument("--workflow-profile", choices=("efficient-v1", "legacy"), default="efficient-v1")
    start.add_argument("--permission-mode", default="diagnostic_only")
    start.add_argument("--expected-templates", type=int, default=1)
    start.add_argument("--expected-slides", type=int, help="Actual requested slide count; initializes todo continuity without approval")
    start.add_argument("--output-dir", default="")
    start.add_argument("--project-root", default="", help="Explicit project identity for context/evidence")
    start.add_argument("--json", action="store_true")
    start.add_argument("--production-request", default="", help="Main-authored DesignTask JSON; invokes the automatic production hook")
    start.add_argument("--dry-run", action="store_true", help="Use the offline SDK model with real authorized adapters")

    run = sub.add_parser("run")
    run.add_argument("--session", required=True)
    run.add_argument("--command", dest="command_name", required=True)
    run.add_argument("--visual-receipt", default="", help="Actual post-build receipt with current inspected visual evidence")
    run.add_argument("--build-artifact", default="")
    run.add_argument("--simulate-fail", default="")
    run.add_argument("--stage-result", default="", help="Record an external attestation; not direct execution proof")
    run.add_argument("--json", action="store_true")
    run.add_argument("--production-request", default="")
    run.add_argument("--dry-run", action="store_true")

    nxt = sub.add_parser("run-next")
    nxt.add_argument("--session", required=True)
    nxt.add_argument("--visual-receipt", default="")
    nxt.add_argument("--build-artifact", default="")
    nxt.add_argument("--stage-result", default="")
    nxt.add_argument("--json", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("--session", required=True)
    status.add_argument("--json", action="store_true")

    compact = sub.add_parser("compact")
    compact.add_argument("--session", required=True)
    compact.add_argument("--json", action="store_true")
    compact.add_argument("--full", action="store_true", help="Print full canonical continuity instead of the bounded efficient-v1 projection")

    prepare = sub.add_parser("prepare-context", help="Write role/phase/epoch loading packet and manifest; does not read on behalf of a role")
    prepare.add_argument("--session", required=True)
    prepare.add_argument("--role", choices=("main", "engineer"), required=True)
    prepare.add_argument("--phase", choices=("plan", "build", "repair", "final"), required=True)
    prepare.add_argument("--context-epoch", required=True)
    prepare.add_argument("--json", action="store_true")
    prepare.add_argument("--navigation", choices=("auto", "on", "off"), default="auto")
    prepare.add_argument("--navigation-cache-dir", default="", help="Explicit writable cache for a read-only installation")
    prepare.add_argument("--navigation-memory-discovery", default="", help="Explicit project-confined existing-adapter discovery JSON; never fetched automatically")

    checkpoint = sub.add_parser("checkpoint", help="Save validated advisory per-slide continuity; never grants gate PASS")
    checkpoint.add_argument("--session", required=True)
    checkpoint_input = checkpoint.add_mutually_exclusive_group(required=True)
    checkpoint_input.add_argument("--file")
    checkpoint_input.add_argument("--initialize", action="store_true")
    checkpoint.add_argument("--expected-slides", type=int)
    checkpoint.add_argument("--repair-round", action="store_true", help="Record one completed batched repair/review round")
    checkpoint.add_argument("--main-decision", default="", help="Main's concrete strategy after repair stagnation; never closes defects")
    checkpoint.add_argument("--json", action="store_true")

    resume = sub.add_parser("resume", help="Read canonical explicit-session checkpoint without mutation")
    resume.add_argument("--session", required=True)
    resume.add_argument("--json", action="store_true")

    final = sub.add_parser("finalize")
    final.add_argument("--session", required=True)
    final.add_argument("--json", action="store_true")

    doctor = sub.add_parser("doctor")
    doctor.add_argument("--json", action="store_true")
    for action in ("review-production", "cancel-production", "recover-production"):
        control = sub.add_parser(action)
        control.add_argument("--session", required=True)
        if action == "review-production":
            control.add_argument("--review", required=True, help="MainReviewDecision JSON; never a Specialist tool")
        else:
            control.add_argument("--task-id", required=True)
        control.add_argument("--json", action="store_true")
    capabilities = sub.add_parser("production-capabilities")
    capabilities.add_argument("--json", action="store_true")
    plan = sub.add_parser("plan-production", help="Read-only capability plan; never executes or grants final readiness")
    plan.add_argument("--production-request", required=True)
    plan.add_argument("--preferred-route", choices=("auto", "main", "host_agents", "sdk"), default="auto")
    plan.add_argument("--dry-run", action="store_true", help="Plan SDK offline tests rather than paid execution")
    plan.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "start":
        payload = command_start(args)
    elif args.command == "run":
        payload = command_run(args)
    elif args.command == "run-next":
        payload = command_run_next(args)
    elif args.command == "status":
        payload = command_status(args)
    elif args.command == "compact":
        payload = command_compact(args)
    elif args.command == "prepare-context":
        payload = command_prepare_context(args)
    elif args.command == "checkpoint":
        payload = command_checkpoint(args)
    elif args.command == "resume":
        payload = command_resume(args)
    elif args.command == "finalize":
        payload = command_finalize(args)
    elif args.command == "doctor":
        payload = command_doctor(args)
    elif args.command in {"review-production", "cancel-production", "recover-production"}:
        payload = command_production_control(args)
    elif args.command == "production-capabilities":
        from design_production.profiles import PROFILES
        payload = {"status": "PASS", "main": "external Codex/ChatGPT; preferred gpt-6-astra", "specialist": "gpt-6.1-sol",
                   "maximumSpecialists": 1, "maximumSpecialistsScope": "sdk-runtime-only",
                   "executionRoutes": ["main", "host_agents", "sdk"],
                   "routePolicy": ".design-brain/runtime/PRODUCTION_EXECUTION_POLICY.md", "profiles": PROFILES}
    elif args.command == "plan-production":
        from design_production.routing import plan
        payload = plan(args.production_request, args.preferred_route, args.dry_run)
    else:
        payload = {"status": "ERROR", "error": "unknown command"}
    print(json.dumps(payload, indent=2) if getattr(args, "json", False) else payload)
    return 0 if payload.get("status") in {"PASS", "REQUESTED", "RECORDED"} else 2


if __name__ == "__main__":
    # Plugin-owned in-process runtime selection, not a daemon or independently exposed service.
    local_python = ROOT / (".venv-design-production/Scripts/python.exe" if os.name == "nt" else ".venv-design-production/bin/python")
    if local_python.is_file() and Path(sys.executable).resolve() != local_python.resolve():
        command = [str(local_python), "-B", str(Path(__file__).resolve()), *sys.argv[1:]]
        if os.name == "nt":
            # Windows execv loses argument quoting and detaches the replacement
            # from the captured parent status. Wait and propagate its real result.
            import subprocess
            raise SystemExit(subprocess.call(command))
        os.execv(str(local_python), command)
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error), "finalAllowed": False}))
        raise SystemExit(2)
