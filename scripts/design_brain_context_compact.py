#!/usr/bin/env python
"""Compact Brain Design runtime context."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
STATE_ROOT = ROOT / ".design-brain" / "runtime" / "state"


def load_state(session: Path) -> dict[str, Any]:
    return json.loads((session / "session-state.json").read_text(encoding="utf-8"))


def compact_session(session: Path) -> dict[str, Any]:
    state = load_state(session)
    completed = state.get("completedStages", [])
    missing = state.get("missingStages", [])
    tickets = state.get("openRepairTickets", [])
    failed = [name for name, result in state.get("toolResults", {}).items() if result.get("status") != "PASS"]
    next_action = "Finalize delivery." if not missing and not tickets else "Run next missing gate or repair open tickets."
    blocking = state.get("finalReadiness", {}).get("reason", "")
    summary = {
        "sessionId": state.get("sessionId", session.name),
        "task": state.get("task", ""),
        "route": state.get("route", ""),
        "productFamily": state.get("productFamily", ""),
        "activeTemplate": state.get("currentTemplateId", ""),
        "currentStage": missing[0] if missing else "complete",
        "finishedGates": completed,
        "failedGates": failed,
        "compactSummary": f"{len(completed)} gates complete; {len(missing)} gates missing; {len(tickets)} open tickets.",
        "openTickets": tickets,
        "openRepairTickets": tickets,
        "nextAction": next_action,
        "finalBlockingReason": blocking,
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
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    summary_path = session / "context-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    STATE_ROOT.mkdir(parents=True, exist_ok=True)
    (STATE_ROOT / "current-context.md").write_text(md.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (STATE_ROOT / "context-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    return {"contextPath": str(md), "summaryPath": str(summary_path), "summary": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact a Brain Design runtime session.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = compact_session(Path(args.session).resolve())
    print(json.dumps(payload, indent=2) if args.json else payload["contextPath"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
