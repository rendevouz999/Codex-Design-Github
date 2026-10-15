#!/usr/bin/env python
"""Brain Design runtime permission modes."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

sys.dont_write_bytecode = True


PERMISSION_ORDER = {
    "diagnostic_only": 0,
    "plan_only": 1,
    "safe_patch": 2,
    "archive_only": 2,
    "full_build": 3,
    "export_allowed": 4,
    "delete_allowed": 5,
}

COMMAND_REQUIREMENTS = {
    "/design-produce": "full_build",
    "/design-start": "diagnostic_only",
    "/design-route": "diagnostic_only",
    "/design-reference-usage": "plan_only",
    "/design-status": "diagnostic_only",
    "/design-doctor": "diagnostic_only",
    "/design-resume": "diagnostic_only",
    "/design-compact": "diagnostic_only",
    "/design-cognition": "plan_only",
    "/design-section-layout": "plan_only",
    "/design-subagents": "plan_only",
    "/design-subagent-validate": "plan_only",
    "/design-simulate": "plan_only",
    "/design-layout-audit": "plan_only",
    "/design-craft": "plan_only",
    "/design-web-deck": "plan_only",
    "/design-repair": "safe_patch",
    "/design-rewind": "safe_patch",
    "/design-build-session": "full_build",
    "/design-design-system": "full_build",
    "/design-post-build": "full_build",
    "/design-completion-receipt": "full_build",
    "/design-finalize": "full_build",
    "/design-export": "export_allowed",
    "/design-delete": "delete_allowed",
}


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    mode: str
    required: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "mode": self.mode,
            "required": self.required,
            "reason": self.reason,
        }


def validate_mode(mode: str) -> str:
    if mode not in PERMISSION_ORDER:
        raise ValueError(f"Unknown permission mode: {mode}")
    return mode


def required_mode_for_command(command: str) -> str:
    return COMMAND_REQUIREMENTS.get(command, "diagnostic_only")


def can_run(command: str, mode: str) -> PermissionDecision:
    validate_mode(mode)
    required = required_mode_for_command(command)
    allowed = PERMISSION_ORDER[mode] >= PERMISSION_ORDER[required]
    if allowed:
        reason = f"{command} allowed in {mode}."
    else:
        reason = f"{command} requires {required}; current mode is {mode}."
    if mode == "diagnostic_only" and command == "/design-finalize":
        allowed = False
        reason = "diagnostic_only cannot finalize or claim READY."
    return PermissionDecision(allowed, mode, required, reason)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Brain Design runtime permissions.")
    parser.add_argument("--mode", required=True)
    parser.add_argument("--command", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        decision = can_run(args.command, args.mode)
    except ValueError as exc:
        decision = PermissionDecision(False, args.mode, "unknown", str(exc))

    if args.json:
        print(json.dumps(decision.to_dict(), indent=2))
    else:
        print("PASS" if decision.allowed else "BLOCKED")
        print(decision.reason)
    return 0 if decision.allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
