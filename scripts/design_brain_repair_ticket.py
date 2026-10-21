#!/usr/bin/env python
"""Repair ticket system for Brain Design runtime."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_TICKETS = ROOT / ".design-brain" / "runtime" / "state" / "open-repair-tickets.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ticket_id(source_gate: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    return f"repair-{source_gate.replace('_', '-')}-{stamp}"


def ticket_file(session: Path | None = None) -> Path:
    if session:
        return session / "repair-tickets.json"
    return GLOBAL_TICKETS


def load_tickets(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"repair ticket recovery required: {path}: {error}") from error
    if not isinstance(data, list) or any(not isinstance(item, dict) or not isinstance(item.get("ticketId"), str) or not item.get("ticketId") for item in data):
        raise ValueError(f"repair ticket recovery required: invalid ticket list: {path}")
    if len({t["ticketId"] for t in data}) != len(data):
        raise ValueError(f"repair ticket recovery required: duplicate ticket IDs: {path}")
    for ticket in data:
        attempts = ticket.get("repairAttempts", [])
        if not isinstance(attempts, list) or any(not isinstance(a, dict) or not all(a.get(k) for k in ("attemptId", "beforeRevision", "afterRevision", "outcome", "evidence")) for a in attempts):
            raise ValueError(f"repair ticket recovery required: invalid repair attempts: {path}")
    return data


def save_tickets(path: Path, tickets: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(tickets, indent=2) + "\n", encoding="utf-8", newline="\n")
    temporary.replace(path)


def create_ticket(
    *,
    session_id: str,
    source_gate: str,
    issue: str,
    template_id: str = "",
    severity: str = "critical",
    required_repair: str = "",
    suggested_action: str = "",
    session: Path | None = None,
    issue_id: str = "",
    input_revision: str = "",
) -> dict[str, Any]:
    path = ticket_file(session)
    tickets = load_tickets(path)
    identity = hashlib.sha256(json.dumps([session_id, template_id, source_gate, issue_id or " ".join(issue.lower().split())]).encode()).hexdigest()
    for existing in tickets:
        legacy_identity = hashlib.sha256(json.dumps([existing.get("sessionId", ""), existing.get("templateId", ""), existing.get("sourceGate", ""), " ".join(str(existing.get("issue", "")).lower().split())]).encode()).hexdigest()
        if existing.get("issueId", legacy_identity) == identity:
            existing.update(issueId=identity, inputRevision=input_revision or existing.get("inputRevision", ""), updatedAt=now(), status="open", rerunGateRequired=True)
            existing["closedAt"] = None
            save_tickets(path, tickets)
            return existing
    payload = {
        "ticketId": ticket_id(source_gate),
        "sessionId": session_id,
        "templateId": template_id,
        "sourceGate": source_gate,
        "issue": issue,
        "severity": severity,
        "requiredRepair": required_repair or issue,
        "suggestedAction": suggested_action or "Repair issue and rerun source gate.",
        "status": "open",
        "createdAt": now(),
        "updatedAt": now(),
        "closedAt": None,
        "rerunGateRequired": True,
        "issueId": identity,
        "inputRevision": input_revision,
        "repairAttempts": [],
        "qualityStatus": "unverified",
    }
    tickets.append(payload)
    save_tickets(path, tickets)
    return payload


def open_tickets(session: Path | None = None) -> list[dict[str, Any]]:
    return [t for t in load_tickets(ticket_file(session)) if t.get("status") != "closed"]


def close_ticket(ticket_id_value: str, session: Path | None = None, *, outcome: str = "administrative", input_revision: str = "", evidence: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    path = ticket_file(session)
    tickets = load_tickets(path)
    found = None
    for ticket in tickets:
        if ticket.get("ticketId") == ticket_id_value:
            ticket["status"] = "closed"
            ticket["closedAt"] = now()
            ticket["updatedAt"] = now()
            # Administrative closure is not evidence of a source gate rerun or quality.
            ticket["rerunGateRequired"] = True
            ticket["qualityStatus"] = "unverified"
            ticket["closure"] = {"outcome": outcome, "inputRevision": input_revision, "evidence": evidence or []}
            found = ticket
            break
    save_tickets(path, tickets)
    return found


def record_repair_attempt(ticket_id_value: str, *, session: Path | None, attempt_id: str, before_revision: str, after_revision: str, outcome: str, evidence: list[dict[str, Any]]) -> dict[str, Any]:
    """Record one changed-input patch followed by a check, never one audit invocation."""
    if not attempt_id or not before_revision or not after_revision or before_revision == after_revision:
        raise ValueError("repair attempt requires a stable ID and different before/after input revisions")
    if outcome not in {"PASS", "FAIL", "BLOCKED"} or not evidence:
        raise ValueError("repair attempt requires a checked outcome and current evidence")
    for item in evidence:
        if not isinstance(item, dict) or not item.get("sha256") or hashlib.sha256(Path(item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("repair attempt evidence is missing or stale")
    path = ticket_file(session)
    tickets = load_tickets(path)
    ticket = next((item for item in tickets if item["ticketId"] == ticket_id_value), None)
    if ticket is None:
        raise ValueError(f"ticket not found: {ticket_id_value}")
    attempt = {"attemptId": attempt_id, "beforeRevision": before_revision, "afterRevision": after_revision, "outcome": outcome, "evidence": evidence}
    attempts = ticket.setdefault("repairAttempts", [])
    for previous in attempts:
        if previous["attemptId"] == attempt_id or (previous["beforeRevision"], previous["afterRevision"]) == (before_revision, after_revision):
            if {key: previous[key] for key in attempt} != attempt:
                raise ValueError("repair attempt already recorded with different data; reconcile before retrying")
            return ticket
    attempts.append({**attempt, "checkedAt": now()})
    ticket.update(inputRevision=after_revision, updatedAt=now(), rerunGateRequired=True)
    save_tickets(path, tickets)
    return ticket


def repair_accounting(session: Path | None, max_cycles: int = 3) -> dict[str, Any]:
    if max_cycles < 1:
        raise ValueError("max repair cycles must be positive")
    tickets = load_tickets(ticket_file(session))
    attempts = {(t.get("issueId") or t["ticketId"], a["attemptId"]) for t in tickets for a in t.get("repairAttempts", [])}
    layout_gates = {"layout_audit", "post_build_pass3", "post_build_layout", "visual_gate", "post_build_visual"}
    layout = {(t.get("issueId") or t["ticketId"], a["attemptId"]) for t in tickets
              if t.get("sourceGate") in layout_gates or "layout" in t.get("sourceGate", "")
              for a in t.get("repairAttempts", [])}
    exhausted = [t["ticketId"] for t in tickets if t.get("status") != "closed" and len(t.get("repairAttempts", [])) >= max_cycles]
    return {"repairCycles": len(attempts), "layoutRepairCycles": len(layout),
            "attemptsPerIssue": {t.get("issueId") or t["ticketId"]: len(t.get("repairAttempts", [])) for t in tickets}, "maxRepairCyclesPerIssue": max_cycles, "budgetExhausted": bool(exhausted), "exhaustedTickets": exhausted, "countingBasis": "explicit changed-input repair attempts followed by checks; audit calls are not attempts"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage Brain Design runtime repair tickets.")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create")
    create.add_argument("--session-dir", default="")
    create.add_argument("--session-id", required=True)
    create.add_argument("--source-gate", required=True)
    create.add_argument("--issue", required=True)
    create.add_argument("--template-id", default="")
    create.add_argument("--severity", default="critical")
    create.add_argument("--required-repair", default="")
    create.add_argument("--suggested-action", default="")
    create.add_argument("--issue-id", default="")
    create.add_argument("--input-revision", default="")
    create.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--session-dir", default="")
    list_cmd.add_argument("--json", action="store_true")

    close = sub.add_parser("close")
    close.add_argument("--session-dir", default="")
    close.add_argument("--ticket-id", required=True)
    close.add_argument("--outcome", default="administrative")
    close.add_argument("--input-revision", default="")
    close.add_argument("--evidence", default="", help="JSON array of path/SHA-256 evidence, recorded without a quality PASS")
    close.add_argument("--json", action="store_true")

    sub.add_parser("export-summary")
    attempt = sub.add_parser("record-attempt", help="One actual changed-input patch followed by a check")
    attempt.add_argument("--session-dir", required=True)
    attempt.add_argument("--ticket-id", required=True)
    attempt.add_argument("--attempt-id", required=True)
    attempt.add_argument("--before-revision", required=True)
    attempt.add_argument("--after-revision", required=True)
    attempt.add_argument("--outcome", required=True, choices=("PASS", "FAIL", "BLOCKED"))
    attempt.add_argument("--evidence", required=True)
    attempt.add_argument("--json", action="store_true")
    accounting = sub.add_parser("accounting")
    accounting.add_argument("--session-dir", required=True)
    accounting.add_argument("--max-repair-cycles", type=int, default=3)
    accounting.add_argument("--json", action="store_true")

    args = parser.parse_args()
    session = Path(args.session_dir).resolve() if getattr(args, "session_dir", "") else None

    if args.command == "create":
        payload = create_ticket(
            session_id=args.session_id,
            source_gate=args.source_gate,
            issue=args.issue,
            template_id=args.template_id,
            severity=args.severity,
            required_repair=args.required_repair,
            suggested_action=args.suggested_action,
            session=session,
            issue_id=args.issue_id,
            input_revision=args.input_revision,
        )
        print(json.dumps(payload, indent=2) if args.json else f"created {payload['ticketId']}")
        return 0
    if args.command == "list":
        tickets = open_tickets(session)
        print(json.dumps(tickets, indent=2) if args.json else f"open tickets: {len(tickets)}")
        return 0
    if args.command == "close":
        payload = close_ticket(args.ticket_id, session, outcome=args.outcome, input_revision=args.input_revision, evidence=json.loads(Path(args.evidence).read_text()) if args.evidence else [])
        if not payload:
            print(f"ticket not found: {args.ticket_id}")
            return 2
        print(json.dumps(payload, indent=2) if args.json else f"closed {args.ticket_id}")
        return 0
    if args.command == "record-attempt":
        payload = record_repair_attempt(args.ticket_id, session=session, attempt_id=args.attempt_id, before_revision=args.before_revision, after_revision=args.after_revision, outcome=args.outcome, evidence=json.loads(Path(args.evidence).read_text()))
        print(json.dumps(payload, indent=2))
        return 0
    if args.command == "accounting":
        print(json.dumps(repair_accounting(session, args.max_repair_cycles), indent=2))
        return 0
    print(json.dumps({"openTickets": open_tickets(session)}, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(json.dumps({"status": "BLOCKED", "error": str(error), "qualityStatus": "unverified"}))
        raise SystemExit(2)
