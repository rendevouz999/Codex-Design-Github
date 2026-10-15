#!/usr/bin/env python3
"""Smoke tests for Design Craft Brain Design adapter."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


class Smoke:
    def __init__(self) -> None:
        self.checks = 0

    def ok(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)


def base_request() -> dict:
    return {
        "route": "website-template",
        "productFamily": "event_venue_travel_booking",
        "mode": "website",
        "designCognition": {"status": "PASS", "colorRoleRemapping": "new palette"},
        "layoutFingerprint": {"heroGrammar": "editorial split", "sectionOrder": ["hero", "menu", "proof"]},
        "simulationVerdict": {"status": "PASS"},
        "layoutAuditStatus": "PASS",
        "designSystemRequirement": {"required": True},
        "craftScope": ["typography", "spacing", "components", "states", "accessibility"],
    }


def run_adapter(payload: dict) -> tuple[int, dict]:
    with tempfile.TemporaryDirectory(prefix="craft-adapter-") as tmp:
        request = Path(tmp) / "request.json"
        request.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "craft_adapter.py"), "--request", str(request), "--json"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
        data = json.loads(completed.stdout)
        return completed.returncode, data


def main() -> int:
    smoke = Smoke()

    code, result = run_adapter(base_request())
    smoke.ok(code == 0, "valid Brain Design request should pass")
    smoke.ok(result["status"] == "PASS", "valid request status should PASS")
    for field in ["tokens", "typography", "spacing", "components", "states", "accessibility", "sourceHandoff", "polishNotes"]:
        smoke.ok(bool(result.get(field)), f"adapter output missing {field}")

    override_route = base_request()
    override_route["overrideRoute"] = "ecommerce"
    code, result = run_adapter(override_route)
    smoke.ok(code != 0, "route override should return non-zero")
    smoke.ok(result["status"] == "BLOCKED_BY_BRAIN_DESIGN_CONTRACT", "route override should be blocked")

    override_product = base_request()
    override_product["proposedOverrides"] = {"productFamily": "portfolio"}
    code, result = run_adapter(override_product)
    smoke.ok(code != 0, "product family override should return non-zero")
    smoke.ok(result["status"] == "BLOCKED_BY_BRAIN_DESIGN_CONTRACT", "product family override should be blocked")

    generic = base_request()
    generic["craftScope"] = ["generic minimalist Hero > Features > CTA"]
    code, result = run_adapter(generic)
    smoke.ok(code != 0, "generic minimalist scaffold should be blocked")
    smoke.ok(result["status"] == "BLOCKED_BY_BRAIN_DESIGN_CONTRACT", "generic scaffold status should be blocked")

    missing = base_request()
    missing.pop("designCognition")
    code, result = run_adapter(missing)
    smoke.ok(code != 0, "missing contract fields should fail")
    smoke.ok(result["status"] == "BLOCKED_BY_BRAIN_DESIGN_CONTRACT", "missing field should be contract block")

    print(f"PASS: Design Craft adapter smoke ({smoke.checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
