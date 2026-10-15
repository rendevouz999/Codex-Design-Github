#!/usr/bin/env python
"""Smoke tests for Brain Design subagent semantic receipt validation."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_validator(evidence_dir: Path, expect_code: int) -> dict:
    completed = subprocess.run(
        [
            PYTHON,
            "scripts/design_brain_subagent_receipt_validate.py",
            "--evidence-dir",
            str(evidence_dir),
            "--mode",
            "full",
            "--final",
            "--marketplace",
            "--has-reference",
            "--figma-source",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if completed.returncode != expect_code:
        raise AssertionError(f"Expected code {expect_code}, got {completed.returncode}: {completed.stderr or completed.stdout}")
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON output: {completed.stdout}\n{completed.stderr}") from exc


def write_bad_evidence(root: Path) -> None:
    agents = json.loads((ROOT / ".design-brain" / "design-subagents" / "agents.json").read_text(encoding="utf-8"))["agents"]
    for agent in agents:
        agent_dir = root / agent["id"]
        agent_dir.mkdir(parents=True, exist_ok=True)
        for output in agent["requiredOutputs"]:
            (agent_dir / output).write_text("smoke evidence\n", encoding="utf-8", newline="\n")


def write_good_evidence(root: Path) -> None:
    from design_brain_subagent_smoke_test import valid_json, valid_text

    agents = json.loads((ROOT / ".design-brain" / "design-subagents" / "agents.json").read_text(encoding="utf-8"))["agents"]
    for agent in agents:
        agent_dir = root / agent["id"]
        agent_dir.mkdir(parents=True, exist_ok=True)
        for output in agent["requiredOutputs"]:
            path = agent_dir / output
            if output.endswith(".json"):
                path.write_text(json.dumps(valid_json(agent["id"], output), indent=2) + "\n", encoding="utf-8", newline="\n")
            else:
                path.write_text(valid_text(agent["id"], output), encoding="utf-8", newline="\n")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="brain-design-subagent-semantic-") as tmp:
        bad = Path(tmp) / "bad"
        good = Path(tmp) / "good"
        write_bad_evidence(bad)
        bad_result = run_validator(bad, expect_code=2)
        if bad_result["status"] != "BLOCK":
            raise AssertionError("Placeholder evidence must BLOCK semantic validation.")
        if not bad_result["blockingReasons"]:
            raise AssertionError("Bad evidence should explain blocking reasons.")

        write_good_evidence(good)
        good_result = run_validator(good, expect_code=0)
        if good_result["status"] != "PASS":
            raise AssertionError("Structured evidence should PASS semantic validation.")

    print("PASS: Subagent semantic validation smoke tests (2 checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
