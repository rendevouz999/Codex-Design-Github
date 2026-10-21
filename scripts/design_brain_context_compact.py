#!/usr/bin/env python
"""Compact Brain Design runtime context."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = ROOT / ".design-brain" / "runtime" / "state"


def load_state(session: Path) -> dict[str, Any]:
    return json.loads((session / "session-state.json").read_text(encoding="utf-8"))


def bounded_summary(summary: dict[str, Any], summary_path: Path) -> dict[str, Any]:
    """Project transport only; the complete checkpoint and evidence remain on disk."""
    progress = summary["progress"]
    action = progress["nextAction"]
    limit = 600
    brief_action = {key: str(action[key])[:limit] for key in ("actor", "target", "action", "expectedOutput")}
    brief_action["checks"] = [str(item)[:limit] for item in action["checks"][:5]]
    brief_action["checksTotal"] = len(action["checks"])
    brief_action["detailsTruncated"] = (len(action["checks"]) > 5 or any(len(str(action[key])) > limit
        for key in ("actor", "target", "action", "expectedOutput")) or any(len(str(x)) > limit for x in action["checks"]))
    issues = progress["checkpointIssues"]
    return {"schema": "design-brain.compact-summary.v1", "session": summary["session"],
        "sessionId": summary["sessionId"], "taskSha256": summary["taskSha256"], "stateSha256": summary["stateSha256"],
        "currentStage": progress["currentStage"], "expectedSlides": progress["expectedSlides"],
        "slideCounts": progress["slideCounts"], "finishedGates": progress["completedStages"],
        "missingGates": progress["missingStages"], "openTicketCount": len(progress["openRepairTickets"]),
        "checkpointIssueCount": len(issues), "checkpointIssues": [str(item)[:limit] for item in issues[:5]],
        "checkpointIssuesTruncated": len(issues) > 5 or any(len(str(item)) > limit for item in issues),
        "nextAction": brief_action, "finalAllowed": progress["finalReadiness"]["finalAllowed"],
        "finalStatus": progress["finalReadiness"]["status"], "finalMainVisualReviewRequired": True,
        "fullRead": {"path": str(summary_path), "requiredBeforeResume": ["checkpoint", "progress", "contextRecovery"]},
        "scope": "Bounded transport only; read full current constraints, repairs and evidence before acting."}


def compact_session(session: Path, *, full: bool = False, mirror_root: Path | None = None) -> dict[str, Any]:
    from design_brain_runtime import progress_projection

    # Bind content and identity to one byte snapshot, including under concurrent replacement.
    state_bytes = (session / "session-state.json").read_bytes()
    state = json.loads(state_bytes.decode("utf-8"))
    projection = progress_projection(state, session)
    completed = projection["completedStages"]
    missing = projection["missingStages"]
    tickets = projection["openRepairTickets"]
    failed = projection["failedGates"]
    checkpoint = state.get("checkpoint")
    action = projection["nextAction"]
    next_action = (f"{action['actor']}: {action['action']}; target: {action['target']}; "
                   f"expected: {action['expectedOutput']}; checks: {', '.join(action['checks'])}")
    blocking = projection["finalReadiness"]["reason"]
    summary = {
        "session": str(session.resolve()),
        "sessionId": state.get("sessionId", session.name),
        "taskSha256": projection["taskSha256"],
        "stateSha256": hashlib.sha256(state_bytes).hexdigest(),
        "task": state.get("task", ""),
        "route": state.get("route", ""),
        "productFamily": state.get("productFamily", ""),
        "activeTemplate": state.get("currentTemplateId", ""),
        "currentStage": missing[0] if missing else "complete",
        "finishedGates": completed,
        "failedGates": failed,
        "compactSummary": f"{len(completed)} gates complete; {len(missing)} gates missing; {len(tickets)} open tickets.",
        "openRepairTickets": tickets,
        "checkpoint": checkpoint,
        "ticketRecoveryRequired": state.get("ticketRecoveryRequired", ""),
        "stateSha256": hashlib.sha256((session / "session-state.json").read_bytes()).hexdigest(),
        "nextAction": next_action,
        "finalBlockingReason": blocking,
        "checkpoint": checkpoint,
        "checkpointIssues": projection["checkpointIssues"],
        "progress": projection, "nextActionDetail": action, "finalReadiness": projection["finalReadiness"],
        "finalMainVisualReviewRequired": True,
        "contextRecovery": "Use a new context epoch after host compact/resume; prior file hashes do not prove model knowledge.",
    }
    session.mkdir(parents=True, exist_ok=True)
    md = session / "compact-context.md"
    md.write_text(
        "\n".join(
            [
                "# Brain Design Runtime Compact Context",
                "",
                f"- Task: {summary['task']}",
                f"- Route: {summary['route']}",
                f"- Product family: {summary['productFamily']}",
                f"- Active template: {summary['activeTemplate']}",
                f"- Current stage: {summary['currentStage']}",
                f"- Finished gates: {', '.join(completed) if completed else 'none'}",
                f"- Failed gates: {', '.join(failed) if failed else 'none'}",
                f"- Open tickets: {len(tickets)}",
                f"- Next action: {next_action}",
                f"- Final blocking reason: {blocking or 'none'}",
                "- Checkpoint details, accepted hashes, constraints and unresolved operations: context-summary.json (read before resume)",
                "- Final Main inspection of every actual final slide remains required; no visual PASS reuse.",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    summary_path = session / "context-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    mirror = mirror_root if mirror_root is not None else STATE_ROOT
    mirror.mkdir(parents=True, exist_ok=True)
    (mirror / "current-context.md").write_text(md.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (mirror / "context-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    (mirror / "current-session.json").write_text(json.dumps({"session": str(session.resolve())}, indent=2) + "\n", encoding="utf-8", newline="\n")
    projected = state.get("workflowProfile") == "efficient-v1" and not full
    return {"contextPath": str(md), "summaryPath": str(summary_path),
            "summary": bounded_summary(summary, summary_path) if projected else summary,
            "fullDetailsInFile": projected}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact a Brain Design runtime session.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--full", action="store_true")
    args = parser.parse_args()
    payload = compact_session(Path(args.session).resolve(), full=args.full)
    print(json.dumps(payload, indent=2) if args.json else payload["contextPath"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
