#!/usr/bin/env python
"""Bridge smoke for Brain Design -> Design Craft adapter."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

from design_brain_process_utils import python_command, resolve_python_invocation, run_command


ROOT = Path(__file__).resolve().parents[1]
PYTHON_INVOCATION = resolve_python_invocation()


def find_design_craft_root() -> Path | None:
    candidates = [
        ROOT / ".design-brain" / "adapters" / "design-craft",
        ROOT / "design-craft",
        Path.home() / ".codex" / "skills" / "design-craft",
    ]
    for candidate in candidates:
        if (candidate / "SKILL.md").is_file() and (candidate / "scripts" / "craft_adapter.py").is_file():
            return candidate
    return None


def request_payload() -> dict:
    return {
        "route": "website-template",
        "productFamily": "event_venue_travel_booking",
        "mode": "website",
        "designCognition": {"status": "PASS", "colorRoleRemapping": "new palette"},
        "layoutFingerprint": {"heroGrammar": "editorial split"},
        "simulationVerdict": {"status": "PASS"},
        "layoutAuditStatus": "PASS",
        "designSystemRequirement": {"required": True},
        "craftScope": ["tokens", "typography", "spacing", "states"],
    }


def call_adapter(payload: dict) -> tuple[int, dict]:
    craft_root = find_design_craft_root()
    if craft_root is None:
        return 1, {"status": "ERROR", "error": "Design Craft adapter not found"}
    with tempfile.TemporaryDirectory(prefix="brain-craft-bridge-") as tmp:
        request = Path(tmp) / "request.json"
        request.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        completed = run_command(
            python_command([str(craft_root / "scripts" / "craft_adapter.py"), "--request", str(request), "--json"], PYTHON_INVOCATION),
            cwd=craft_root,
            timeout=30,
            label="craft-adapter-bridge",
        )
        return completed.returncode, json.loads(completed.stdout or "{}")


def main() -> int:
    craft_root = find_design_craft_root()
    if craft_root is None:
        print("FAIL: Design Craft adapter not found")
        return 1
    code, result = call_adapter(request_payload())
    assert code == 0, result
    assert result["status"] == "PASS", result
    assert result["craftResult"]["brainDesignFinalAuthority"] is True, result
    blocked = request_payload()
    blocked["overrideRoute"] = "ecommerce"
    code, result = call_adapter(blocked)
    assert code != 0, result
    assert result["status"] == "BLOCKED_BY_BRAIN_DESIGN_CONTRACT", result
    print("PASS: Brain Design craft adapter bridge smoke")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
