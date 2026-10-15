#!/usr/bin/env python
"""Repair ticket system for Brain Design runtime."""

from __future__ import annotations

import argparse
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
    except json.JSONDecodeError:
        return []
    return data if isinstance(data, list) else []


def save_tickets(path: Path, tickets: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(tickets, indent=2) + "\n", encoding="utf-8", newline="\n")


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
) -> dict[str, Any]:
    path = ticket_file(session)
    tickets = load_tickets(path)
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
    }
    tickets.append(payload)
    save_tickets(path, tickets)
    return payload


def open_tickets(session: Path | None = None) -> list[dict[str, Any]]:
    return [t for t in load_tickets(ticket_file(session)) if t.get("status") != "closed"]


def close_ticket(ticket_id_value: str, session: Path | None = None) -> dict[str, Any] | None:
    path = ticket_file(session)
    tickets = load_tickets(path)
    found = None
    for ticket in tickets:
        if ticket.get("ticketId") == ticket_id_value:
            ticket["status"] = "closed"
            ticket["closedAt"] = now()
            ticket["updatedAt"] = now()
            ticket["rerunGateRequired"] = False
            found = ticket
            break
    save_tickets(path, tickets)
    return found


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
    create.add_argument("--json", action="store_true")

    list_cmd = sub.add_parser("list")
    list_cmd.add_argument("--session-dir", default="")
    list_cmd.add_argument("--json", action="store_true")

    close = sub.add_parser("close")
    close.add_argument("--session-dir", default="")
    close.add_argument("--ticket-id", required=True)
    close.add_argument("--json", action="store_true")

    sub.add_parser("export-summary")

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
        )
        print(json.dumps(payload, indent=2) if args.json else f"created {payload['ticketId']}")
        return 0
    if args.command == "list":
        tickets = open_tickets(session)
        print(json.dumps(tickets, indent=2) if args.json else f"open tickets: {len(tickets)}")
        return 0
    if args.command == "close":
        payload = close_ticket(args.ticket_id, session)
        if not payload:
            print(f"ticket not found: {args.ticket_id}")
            return 2
        print(json.dumps(payload, indent=2) if args.json else f"closed {args.ticket_id}")
        return 0
    print(json.dumps({"openTickets": open_tickets(session)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
