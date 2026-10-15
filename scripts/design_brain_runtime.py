#!/usr/bin/env python
"""Brain Design Design Agent Runtime.

This script wraps existing Brain Design gates as a CLI/JSON runtime loop.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_command_router import COMMAND_TO_STAGE, COMMAND_TO_TOOL, route_command
from design_brain_permission import can_run
from design_brain_visual_gate import validate_post_build_receipt
from design_brain_repair_ticket import create_ticket, open_tickets


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
    return json.loads(state_path(session).read_text(encoding="utf-8"))


def save_state(session: Path, state: dict[str, Any]) -> None:
    session.mkdir(parents=True, exist_ok=True)
    state.setdefault("requiredStages", REQUIRED_STAGES[:])
    completed = state.setdefault("completedStages", [])
    state["missingStages"] = [stage for stage in REQUIRED_STAGES if stage not in completed]
    state["openRepairTickets"] = open_tickets(session)
    state["finalReadiness"] = final_readiness(state)
    state_path(session).write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8", newline="\n")
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    (STATE_ROOT / "current-session.json").write_text(json.dumps({"session": str(session)}, indent=2) + "\n", encoding="utf-8")


def append_history(session: Path, event: dict[str, Any]) -> None:
    event = {"timestamp": now(), **event}
    with history_path(session).open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(event) + "\n")
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    with (STATE_ROOT / "session-history.jsonl").open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps({"session": str(session), **event}) + "\n")


def final_readiness(state: dict[str, Any]) -> dict[str, Any]:
    missing = [stage for stage in REQUIRED_STAGES if stage not in state.get("completedStages", [])]
    tickets = [t for t in state.get("openRepairTickets", []) if t.get("status") != "closed"]
    allowed = not missing and not tickets
    reason = "READY" if allowed else "; ".join(
        [f"missing stages: {', '.join(missing)}" if missing else "", f"open repair tickets: {len(tickets)}" if tickets else ""]
    ).strip("; ")
    if state.get("permissionMode") == "diagnostic_only":
        allowed = False
        reason = "diagnostic_only cannot claim final READY"
    if "post_build_audit" in state.get("completedStages", []):
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
    return {"finalAllowed": allowed, "status": "READY" if allowed else "BLOCKED", "reason": reason}


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


def command_start(args: argparse.Namespace) -> dict[str, Any]:
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    sid = session_id()
    session = (Path(args.output_dir).resolve() if args.output_dir else STATE_ROOT / sid)
    if getattr(args, "production_request", ""):
        from design_production.policy import within
        within(session, ROOT)
        if session.exists():
            raise ValueError("Production start requires a new session directory")
    session.mkdir(parents=True, exist_ok=True)
    state = {
        "sessionId": session.name,
        "task": args.task,
        "permissionMode": args.permission_mode,
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
    save_state(session, state)
    append_history(session, {"event": "session_started", "task": args.task, "permissionMode": args.permission_mode})
    if getattr(args, "production_request", ""):
        args.session = str(session)
        payload = command_production(args)
        return {**payload, "session": str(session), "state": load_state(session)}
    return {"status": "PASS", "session": str(session), "state": state}


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
    completed = state.setdefault("completedStages", [])
    if stage not in completed:
        completed.append(stage)
    state.setdefault("toolResults", {})[stage] = result
    state["activeTool"] = result.get("tool", "")
    if stage == "route":
        state["route"] = result.get("route", "website-template")
        state["productFamily"] = result.get("productFamily", "template_product")


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
        ticket = create_ticket(
            session_id=state["sessionId"],
            source_gate=routed.stage or args.command_name,
            issue=args.simulate_fail,
            required_repair=args.simulate_fail,
            session=session,
        )
        state["openRepairTickets"] = open_tickets(session)
        save_state(session, state)
        result = runtime_result(args.command_name, routed.tool, "BLOCKED", True, "Repair issue and rerun gate.", [ticket["requiredRepair"]])
        append_history(session, {"event": "gate_failed", "result": result, "ticket": ticket})
        return result
    if not routed.stage:
        result = runtime_result(args.command_name, routed.tool, "ERROR", True, "Use a registered command.", ["Unknown command"])
        append_history(session, {"event": "unknown_command", "result": result})
        return result
    visual_path = getattr(args, "visual_receipt", "")
    visual_artifact = getattr(args, "build_artifact", "")
    if routed.stage == "post_build_audit":
        visual_result = validate_post_build_receipt(visual_path, visual_artifact) if visual_path and visual_artifact else {"status": "BLOCKED", "issues": ["Supply --visual-receipt and --build-artifact from the actual post-build audit; stage routing alone is not execution."]}
        if visual_result["status"] != "PASS":
            result = runtime_result(args.command_name, routed.tool, "BLOCKED", True, "Inspect current evidence and rerun the real post-build gate.", visual_result["issues"])
            append_history(session, {"event": "visual_evidence_blocked", "result": result})
            return result
    result = runtime_result(args.command_name, routed.tool, "PASS", False, "Run next required stage.")
    if routed.stage == "post_build_audit":
        result["visualReceipt"] = str(Path(visual_path).resolve())
        result["visualArtifact"] = str(Path(visual_artifact).resolve())
    result.update({"stage": routed.stage, "route": "website-template", "productFamily": "template_product"})
    mark_stage(state, routed.stage, result)
    state["updatedAt"] = now()
    save_state(session, state)
    result["finalAllowed"] = state["finalReadiness"]["finalAllowed"]
    append_history(session, {"event": "stage_passed", "stage": routed.stage, "result": result})
    return result


def command_run_next(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    missing = [stage for stage in REQUIRED_STAGES if stage not in state.get("completedStages", [])]
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
    state["openRepairTickets"] = open_tickets(session)
    state["finalReadiness"] = final_readiness(state)
    save_state(session, state)
    return {"status": "PASS", "session": str(session), "state": state}


def command_finalize(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).resolve()
    state = load_state(session)
    state["openRepairTickets"] = open_tickets(session)
    readiness = final_readiness(state)
    state["finalReadiness"] = readiness
    save_state(session, state)
    result = {
        "status": "PASS" if readiness["finalAllowed"] else "BLOCKED",
        "command": "/design-finalize",
        "tool": "completion_receipt_tool",
        "blocking": not readiness["finalAllowed"],
        "requiredRepairs": [] if readiness["finalAllowed"] else [readiness["reason"]],
        "recommendedImprovements": [],
        "nextAction": "Delivery allowed." if readiness["finalAllowed"] else "Complete missing gates and close repair tickets.",
        "finalAllowed": readiness["finalAllowed"],
    }
    append_history(session, {"event": "finalize", "result": result})
    return result


def command_compact(args: argparse.Namespace) -> dict[str, Any]:
    from design_brain_context_compact import compact_session

    session = Path(args.session).resolve()
    payload = compact_session(session)
    state = load_state(session)
    state["compactContextPath"] = payload["contextPath"]
    save_state(session, state)
    append_history(session, {"event": "compact", "contextPath": payload["contextPath"]})
    return {"status": "PASS", **payload}


def command_doctor(_: argparse.Namespace) -> dict[str, Any]:
    from design_brain_doctor import run_doctor

    return run_doctor()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain Design Design Agent Runtime.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--task", required=True)
    start.add_argument("--permission-mode", default="diagnostic_only")
    start.add_argument("--expected-templates", type=int, default=1)
    start.add_argument("--output-dir", default="")
    start.add_argument("--json", action="store_true")
    start.add_argument("--production-request", default="", help="Main-authored DesignTask JSON; invokes the automatic production hook")
    start.add_argument("--dry-run", action="store_true", help="Use the offline SDK model with real authorized adapters")

    run = sub.add_parser("run")
    run.add_argument("--session", required=True)
    run.add_argument("--command", dest="command_name", required=True)
    run.add_argument("--visual-receipt", default="", help="Actual post-build receipt with current inspected visual evidence")
    run.add_argument("--build-artifact", default="")
    run.add_argument("--simulate-fail", default="")
    run.add_argument("--json", action="store_true")
    run.add_argument("--production-request", default="")
    run.add_argument("--dry-run", action="store_true")

    nxt = sub.add_parser("run-next")
    nxt.add_argument("--session", required=True)
    nxt.add_argument("--visual-receipt", default="")
    nxt.add_argument("--build-artifact", default="")
    nxt.add_argument("--json", action="store_true")

    status = sub.add_parser("status")
    status.add_argument("--session", required=True)
    status.add_argument("--json", action="store_true")

    compact = sub.add_parser("compact")
    compact.add_argument("--session", required=True)
    compact.add_argument("--json", action="store_true")

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
    return 0 if payload.get("status") == "PASS" else 2


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
