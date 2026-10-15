#!/usr/bin/env python
"""Slash-like command router for Brain Design runtime."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

sys.dont_write_bytecode = True

from design_brain_permission import can_run


COMMAND_TO_STAGE = {
    "/design-produce": "design_production",
    "/design-route": "route",
    "/design-reference-usage": "reference_usage",
    "/design-cognition": "cognition",
    "/design-section-layout": "section_layout",
    "/design-subagents": "subagent_orchestration",
    "/design-subagent-validate": "subagent_orchestration",
    "/design-simulate": "simulation",
    "/design-layout-audit": "layout_audit",
    "/design-build-session": "build_session_verify",
    "/design-craft": "craft_support",
    "/design-design-system": "design_system_check",
    "/design-web-deck": "web_deck",
    "/design-post-build": "post_build_audit",
    "/design-completion-receipt": "completion_receipt",
    "/design-finalize": "verify_final",
    "/design-compact": "compact_context",
    "/design-doctor": "doctor",
    "/design-status": "status",
    "/design-repair": "repair",
}

COMMAND_TO_TOOL = {
    "/design-produce": "design_production_tool",
    "/design-route": "route_tool",
    "/design-reference-usage": "reference_usage_tool",
    "/design-cognition": "cognition_check_tool",
    "/design-section-layout": "section_layout_tool",
    "/design-subagents": "subagent_orchestration_tool",
    "/design-subagent-validate": "subagent_semantic_validator_tool",
    "/design-simulate": "simulation_tool",
    "/design-layout-audit": "layout_similarity_tool",
    "/design-build-session": "build_session_tool",
    "/design-craft": "design_craft_adapter_tool",
    "/design-design-system": "design_system_check_tool",
    "/design-web-deck": "web_deck_tool",
    "/design-post-build": "post_build_audit_tool",
    "/design-completion-receipt": "completion_receipt_tool",
    "/design-finalize": "completion_receipt_tool",
    "/design-compact": "compact_context_tool",
    "/design-doctor": "doctor_tool",
    "/design-status": "status_tool",
    "/design-repair": "repair_ticket_tool",
}


@dataclass(frozen=True)
class RoutedCommand:
    command: str
    stage: str
    tool: str
    permissionAllowed: bool
    permissionReason: str

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "stage": self.stage,
            "tool": self.tool,
            "permissionAllowed": self.permissionAllowed,
            "permissionReason": self.permissionReason,
        }


def route_command(command: str, permission_mode: str) -> RoutedCommand:
    decision = can_run(command, permission_mode)
    return RoutedCommand(
        command=command,
        stage=COMMAND_TO_STAGE.get(command, ""),
        tool=COMMAND_TO_TOOL.get(command, ""),
        permissionAllowed=decision.allowed,
        permissionReason=decision.reason,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Route Brain Design runtime commands.")
    parser.add_argument("--command", required=True)
    parser.add_argument("--permission-mode", default="diagnostic_only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    routed = route_command(args.command, args.permission_mode)
    print(json.dumps(routed.to_dict(), indent=2) if args.json else routed)
    return 0 if routed.permissionAllowed and routed.stage else 2


if __name__ == "__main__":
    raise SystemExit(main())
