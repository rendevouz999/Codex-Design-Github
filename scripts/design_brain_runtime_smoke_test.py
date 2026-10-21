#!/usr/bin/env python
"""Smoke tests for Brain Design Design Agent Runtime."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]

from design_brain_process_utils import python_command, resolve_python_invocation, run_command
from design_brain_tool_registry import find_design_craft_root


PYTHON_INVOCATION = resolve_python_invocation()


class Smoke:
    def __init__(self) -> None:
        self.checks = 0

    def ok(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            raise AssertionError(message)


def run(args: list[str], cwd: Path = ROOT, check: bool = False, timeout: int = 60) -> tuple[int, dict | str]:
    completed = run_command(
        python_command(args, PYTHON_INVOCATION),
        cwd=cwd,
        timeout=timeout,
        label="runtime-smoke",
    )
    text = (completed.stdout or "").strip()
    try:
        payload: dict | str = json.loads(text)
    except json.JSONDecodeError:
        payload = text + (completed.stderr or "")
    if check and completed.returncode != 0:
        raise AssertionError(payload)
    return completed.returncode, payload


def start_session(tmp: Path, permission: str = "full_build") -> Path:
    code, payload = run([
        "scripts/design_brain_runtime.py",
        "start",
        "--task",
        "reference-led 5-slide native PPTX presentation template",
        "--permission-mode",
        permission,
        "--expected-templates",
        "1",
        "--expected-slides",
        "5",
        "--output-dir",
        str(tmp / "session"),
        "--json",
    ], check=True)
    assert code == 0
    return Path(payload["session"])  # type: ignore[index]


def main() -> int:
    smoke = Smoke()
    with tempfile.TemporaryDirectory(prefix="brain-runtime-smoke-") as tmp_str:
        tmp = Path(tmp_str)
        session = start_session(tmp)
        smoke.ok((session / "session-state.json").is_file(), "A. Runtime session starts")

        code, commands = run(["scripts/design_brain_command_router.py", "--command", "/design-route", "--permission-mode", "full_build", "--json"], check=True)
        smoke.ok(code == 0 and commands["tool"] == "route_tool", "B. Runtime command registry loads")  # type: ignore[index]

        code, tools = run(["scripts/design_brain_tool_registry.py", "validate", "--json"], check=True)
        smoke.ok(code == 0 and tools["status"] == "PASS", "C. Tool registry loads")  # type: ignore[index]

        code, denied = run(["scripts/design_brain_permission.py", "--mode", "diagnostic_only", "--command", "/design-export", "--json"], timeout=20)
        smoke.ok(code != 0 and denied["allowed"] is False, "D. Permission mode blocks export in diagnostic mode")  # type: ignore[index]

        code, final = run(["scripts/design_brain_runtime.py", "finalize", "--session", str(session), "--json"], timeout=20)
        smoke.ok(code != 0 and final["status"] == "BLOCKED" and "cognition" in final["requiredRepairs"][0], "E. Runtime cannot finalize without cognition")  # type: ignore[index]
        smoke.ok("simulation" in final["requiredRepairs"][0], "F. Runtime cannot finalize without simulation")  # type: ignore[index]
        smoke.ok("layout_audit" in final["requiredRepairs"][0], "G. Runtime cannot finalize without layout audit")  # type: ignore[index]
        smoke.ok("design_system_check" in final["requiredRepairs"][0], "H. Runtime cannot finalize without design system")  # type: ignore[index]

        code, failed = run([
            "scripts/design_brain_runtime.py",
            "run",
            "--session",
            str(session),
            "--command",
            "/design-cognition",
            "--simulate-fail",
            "missing cognition receipt",
            "--json",
        ], timeout=20)
        smoke.ok(code != 0 and failed["status"] == "BLOCKED", "J. Runtime creates repair ticket when a gate fails")  # type: ignore[index]
        code, final = run(["scripts/design_brain_runtime.py", "finalize", "--session", str(session), "--json"], timeout=20)
        smoke.ok(code != 0 and "open repair tickets" in final["requiredRepairs"][0], "I. Runtime cannot finalize with open repair tickets")  # type: ignore[index]

        code, compact = run(["scripts/design_brain_runtime.py", "compact", "--session", str(session), "--json"], check=True)
        smoke.ok(code == 0 and Path(compact["contextPath"]).is_file(), "K. Runtime can compact context")  # type: ignore[index]

        code, doctor = run(["scripts/design_brain_doctor.py", "--json"], check=True)
        smoke.ok(code == 0 and doctor["status"] == "PASS", "L. Runtime doctor PASS")  # type: ignore[index]

        code, status = run(["scripts/design_brain_status_runtime.py", "--session", str(session), "--json"], check=True)
        smoke.ok(code == 0 and status["status"] == "PASS", "M. Runtime status output valid")  # type: ignore[index]

        code, bridge = run(["scripts/design_brain_craft_adapter_bridge_smoke_test.py"], check=True)
        smoke.ok(code == 0, "N. Design Craft adapter tool is support-only")

        craft_root = find_design_craft_root()
        smoke.ok(craft_root is not None and (craft_root / "scripts" / "craft_adapter_smoke_test.py").is_file(), "O1. Bundled Design Craft smoke is available")
        code, craft = run(["scripts/craft_adapter_smoke_test.py"], cwd=craft_root, check=True)
        smoke.ok(code == 0, "O2. Design Craft override attempt is blocked")

        clean_session = start_session(tmp / "complete")
        code, routed = run(["scripts/design_brain_runtime.py", "run-next", "--session", str(clean_session), "--json"])
        smoke.ok(code == 0 and routed["status"] == "PASS" and routed["executionSource"] == "native_router", "P1. Native routing actually executes selection")
        for _ in range(2):
            code, payload = run(["scripts/design_brain_runtime.py", "run-next", "--session", str(clean_session), "--json"])
            smoke.ok(code == 0 and payload["status"] == "REQUESTED" and payload["executionState"] == "requested", "P2. Routing a gate cannot invent execution PASS")
        persisted = json.loads((clean_session / "session-state.json").read_text(encoding="utf-8"))
        smoke.ok(persisted["completedStages"] == ["route"], "P3. Repeated requests cannot advance unexecuted gates")
        code, payload = run(["scripts/design_brain_runtime.py", "run", "--session", str(clean_session), "--command", "/design-post-build", "--json"])
        smoke.ok(code != 0 and payload["status"] == "BLOCKED" and "visual" in str(payload).lower(), "P4. Actual current visual evidence remains mandatory")
        code, final = run(["scripts/design_brain_runtime.py", "finalize", "--session", str(clean_session), "--json"])
        smoke.ok(code != 0 and final["finalAllowed"] is False, "P5. Requested stages never establish final readiness")

    print(f"PASS: Brain Design runtime smoke ({smoke.checks} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
