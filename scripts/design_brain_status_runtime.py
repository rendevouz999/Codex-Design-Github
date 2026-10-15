#!/usr/bin/env python
"""Report Brain Design runtime session status."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True


def load_state(session: Path) -> dict:
    return json.loads((session / "session-state.json").read_text(encoding="utf-8"))


def status_payload(session: Path) -> dict:
    state = load_state(session)
    missing = state.get("missingStages", [])
    tickets = state.get("openRepairTickets", [])
    return {
        "status": "PASS",
        "version": "2.6.0",
        "session": str(session),
        "activeRuntimeSession": state.get("sessionId", ""),
        "permissionMode": state.get("permissionMode", ""),
        "currentStage": missing[0] if missing else "complete",
        "missingStages": missing,
        "openTickets": tickets,
        "lastGateResult": next(reversed(state.get("toolResults", {}).values()), {}),
        "finalReadiness": state.get("finalReadiness", {}),
        "nextRecommendedCommand": "/design-finalize" if not missing and not tickets else "/design-run-next",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Brain Design runtime status.")
    parser.add_argument("--session", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = status_payload(Path(args.session).resolve())
    print(json.dumps(payload, indent=2) if args.json else payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
