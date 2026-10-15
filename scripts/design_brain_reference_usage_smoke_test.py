#!/usr/bin/env python
"""Smoke tests for the Brain Design brand/reference usage memory gate."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_process_utils import python_command, resolve_python_invocation, run_command


ROOT = Path(__file__).resolve().parents[1]
PYTHON = resolve_python_invocation()
CHECKS = 0


def assert_true(condition: bool, message: str, details: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(f"{message}. {details}")


def run_gate_raw(registry: Path, args: list[str], *, add_json: bool = True) -> tuple[int, str, str]:
    final_args = ["scripts/design_brain_reference_usage_gate.py", *args, "--registry", str(registry)]
    if add_json:
        final_args.append("--json")
    completed = run_command(
        python_command(final_args, PYTHON),
        cwd=ROOT,
        timeout=30,
        label="reference-usage-smoke",
    )
    return completed.returncode or 0, completed.stdout or "", completed.stderr or ""


def run_gate(registry: Path, args: list[str]) -> tuple[int, dict[str, Any], str]:
    code, stdout, stderr = run_gate_raw(registry, args)
    text = stdout.strip()
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON from gate: {stdout}\n{stderr}") from exc
    return code, payload, text


def run_receipt_checker(receipt: Path, command: str, status: str) -> tuple[int, dict[str, Any]]:
    completed = run_command(
        python_command(
            [
                "scripts/design_brain_reference_usage_receipt_check.py",
                "--receipt",
                str(receipt),
                "--expect-command",
                command,
                "--expect-status",
                status,
                "--json",
            ],
            PYTHON,
        ),
        cwd=ROOT,
        timeout=30,
        label="reference-usage-receipt-smoke",
    )
    try:
        payload = json.loads((completed.stdout or "").strip())
    except json.JSONDecodeError as exc:
        raise AssertionError(f"Invalid JSON from receipt checker: {completed.stdout}\n{completed.stderr}") from exc
    return completed.returncode or 0, payload


def read_registry(registry: Path) -> dict[str, Any]:
    return json.loads(registry.read_text(encoding="utf-8")) if registry.exists() else {}


def init_reference_canonical(registry: Path, ref_id: str, brand: str) -> None:
    code, payload, _ = run_gate(
        registry,
        [
            "init-reference",
            "--reference-id",
            ref_id,
            "--reference-brand-name",
            brand,
            "--reference-path",
            f"references/{ref_id}.fig",
            "--template-type",
            "Figma Website Template",
            "--product-family",
            "website-template",
            "--niche",
            "smoke",
        ],
    )
    assert_true(code == 0 and payload["status"] == "PASS", f"init reference {ref_id} canonical", json.dumps(payload))


def init_reference_alias(registry: Path, ref_id: str, brand: str) -> None:
    code, payload, _ = run_gate(
        registry,
        [
            "init-reference",
            "--reference-id",
            ref_id,
            "--reference-brand",
            brand,
            "--source",
            f"references/{ref_id}.fig",
            "--source-type",
            "figma",
            "--do-not-copy",
            "Do not copy exact layout, palette, motif, or brand name.",
            "--product-family",
            "website-template",
            "--niche",
            "smoke",
        ],
    )
    assert_true(code == 0 and payload["status"] == "PASS", f"init reference {ref_id} alias", json.dumps(payload))


def check_canonical(registry: Path, name: str, refs: str, mode: str = "", require_order: bool = False) -> tuple[int, dict[str, Any]]:
    args = [
        "check",
        "--candidate-brand-name",
        name,
        "--template-id",
        f"check-{name.lower().replace(' ', '-')}",
        "--template-type",
        "Figma Website Template",
        "--product-family",
        "website-template",
        "--niche",
        "smoke",
        "--reference-ids",
        refs,
    ]
    if mode:
        args.extend(["--reference-mode", mode])
    if require_order:
        args.append("--require-exhaustion-order")
    code, payload, _ = run_gate(registry, args)
    return code, payload


def check_alias(registry: Path, name: str, refs: str, mode: str = "", require_order: bool = False) -> tuple[int, dict[str, Any]]:
    args = [
        "check",
        "--candidate-name",
        name,
        "--template-id",
        f"check-{name.lower().replace(' ', '-')}",
        "--template-type",
        "Figma Website Template",
        "--product-family",
        "website-template",
        "--niche",
        "smoke",
        "--references",
        refs,
        "--reference-brands",
        "Alpha Studio, Beta Works",
    ]
    if mode:
        args.extend(["--mode", mode])
    if require_order:
        args.append("--require-order")
    code, payload, _ = run_gate(registry, args)
    return code, payload


def record_alias(registry: Path, template_id: str, name: str, refs: str, mode: str = "", require_order: bool = False) -> tuple[int, dict[str, Any]]:
    args = [
        "record",
        "--template-id",
        template_id,
        "--brand-name",
        name,
        "--references",
        refs,
        "--template-type",
        "Figma Website Template",
        "--product-family",
        "website-template",
        "--niche",
        "smoke",
        "--target-buyer",
        "template buyer",
        "--receipt-path",
        f"receipts/{template_id}.json",
        "--fingerprint-path",
        f"fingerprints/{template_id}.json",
        "--do-not-copy",
        "abstract spacing and proof rhythm only",
        "--style-dna-summary",
        "abstract spacing and proof rhythm only",
        "--reinterpretation-plan",
        "new hierarchy and color roles",
        "--structural-reconfiguration-plan",
        "fresh hero grammar and section order",
    ]
    if mode:
        args.extend(["--mode", mode])
    if require_order:
        args.append("--require-order")
    code, payload, _ = run_gate(registry, args)
    return code, payload


def record_canonical(registry: Path, template_id: str, name: str, refs: str, mode: str = "", require_order: bool = False) -> tuple[int, dict[str, Any]]:
    args = [
        "record",
        "--template-id",
        template_id,
        "--candidate-brand-name",
        name,
        "--reference-ids",
        refs,
        "--template-type",
        "Figma Website Template",
        "--product-family",
        "website-template",
        "--niche",
        "smoke",
        "--target-buyer",
        "template buyer",
        "--completion-receipt-path",
        f"receipts/{template_id}.json",
        "--fingerprint-lock-path",
        f"fingerprints/{template_id}.json",
        "--do-not-copy-boundary",
        "do not copy exact layout or palette",
    ]
    if mode:
        args.extend(["--reference-mode", mode])
    if require_order:
        args.append("--require-exhaustion-order")
    code, payload, _ = run_gate(registry, args)
    return code, payload


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="brain-reference-usage-") as tmp_str:
        tmp = Path(tmp_str)
        registry = tmp / "registry.json"

        init_reference_canonical(registry, "A", "Alpha Studio")
        init_reference_canonical(registry, "B", "Beta Works")
        init_reference_canonical(registry, "C", "Cedar House")
        assert_true(len(read_registry(registry).get("references", [])) == 3, "1. Init references A, B, C using canonical args")

        init_reference_alias(registry, "D", "Delta House")
        assert_true(len(read_registry(registry).get("references", [])) == 4, "2. Init reference D using alias args")

        code, payload = check_canonical(registry, "Northline", "A", "single")
        assert_true(code == 0 and payload["status"] == "PASS", "3. Check A as single canonical PASS", json.dumps(payload))

        code, payload = record_alias(registry, "template-a", "Northline", "A", "single")
        assert_true(code == 0 and payload["status"] == "PASS", "4. Record A as single alias PASS", json.dumps(payload))

        code, payload = check_alias(registry, "Freshmark", "A", "single")
        assert_true(code != 0 and payload["status"] == "BLOCKED", "5. Check A as single again alias BLOCKED", json.dumps(payload))

        code, payload = check_canonical(registry, "Alpha Studio", "B", "single")
        assert_true(code != 0 and payload["status"] == "BLOCKED", "6. Candidate brand same as reference brand BLOCKED", json.dumps(payload))

        code, payload = check_canonical(registry, "Northline", "B", "single")
        assert_true(code != 0 and payload["status"] == "BLOCKED", "7. Duplicate output brand BLOCKED", json.dumps(payload))

        code, payload = check_canonical(registry, "North Line", "B", "single")
        assert_true(code != 0 and payload["status"] in {"BLOCKED", "REVISE_REQUIRED"}, "8. Compact normalized duplicate BLOCKED or REVISE_REQUIRED", json.dumps(payload))

        code, payload = check_canonical(registry, "Pairmark", "A,B", "pair", require_order=True)
        assert_true(code != 0 and payload["status"] == "BLOCKED", "9. Pair A+B blocked while singles remain", json.dumps(payload))

        for template_id, name, ref in [
            ("template-b", "Eastfold", "B"),
            ("template-c", "Civora", "C"),
            ("template-d", "Deltora", "D"),
        ]:
            code, payload = record_canonical(registry, template_id, name, ref, "single")
            assert_true(code == 0 and payload["status"] == "PASS", f"10. Record {ref} as single PASS", json.dumps(payload))

        code, payload = check_alias(registry, "Pairmark", "A,B", "pair", require_order=True)
        assert_true(code == 0 and payload["status"] == "PASS", "11. Check pair A+B alias PASS", json.dumps(payload))

        code, payload = record_canonical(registry, "template-ab", "Pairmark", "A,B", "pair", require_order=True)
        assert_true(code == 0 and payload["status"] == "PASS", "12. Record pair A+B PASS", json.dumps(payload))

        code, payload = check_alias(registry, "Pairmark Two", "A+B", "pair", require_order=True)
        assert_true(code != 0 and payload["status"] == "BLOCKED", "13. Check pair A+B again BLOCKED", json.dumps(payload))

        code, payload = check_canonical(registry, "Triadmark", "A,B,C", "triple", require_order=True)
        assert_true(code != 0 and payload["status"] == "BLOCKED", "14. Triple A+B+C blocked while unused pairs remain", json.dumps(payload))

        for template_id, name, refs in [
            ("template-ac", "Harborac", "A,C"),
            ("template-ad", "Driftad", "A,D"),
            ("template-bc", "Bridgebc", "B,C"),
            ("template-bd", "Vectorbd", "B,D"),
            ("template-cd", "Castorcd", "C,D"),
        ]:
            code, payload = record_alias(registry, template_id, name, refs, "pair", require_order=True)
            assert_true(code == 0 and payload["status"] == "PASS", f"15. Mark pair {refs} used through record flow", json.dumps(payload))

        code, payload = check_canonical(registry, "Triadmark", "A,B,C", "triple", require_order=True)
        assert_true(code == 0 and payload["status"] == "PASS", "16. Check triple A+B+C PASS", json.dumps(payload))

        code, payload = check_canonical(registry, "Quadmark", "A,B,C,D", "triple", require_order=True)
        assert_true(code != 0 and payload["status"] == "BLOCKED", "17. Check group size 4 BLOCKED", json.dumps(payload))

        before = read_registry(registry)
        code, payload, _ = run_gate(
            registry,
            [
                "init-reference",
                "--reference-id",
                "E",
                "--brand-name",
                "Echo Studio",
                "--source",
                "references/E.fig",
                "--product-family",
                "website-template",
                "--niche",
                "smoke",
                "--dry-run",
            ],
        )
        after = read_registry(registry)
        assert_true(code == 0 and payload["status"] == "PASS" and before == after, "18. Dry-run does not change registry", json.dumps(payload))

        receipt = tmp / "reference-check-receipt.json"
        code, payload, _ = run_gate(
            registry,
            [
                "check",
                "--candidate-name",
                "Receiptmark",
                "--references",
                "A,B,C",
                "--mode",
                "triple",
                "--require-order",
                "--write-receipt",
                "--receipt-output",
                str(receipt),
            ],
        )
        assert_true(code == 0 and receipt.is_file(), "19. Write-receipt creates a receipt file", json.dumps(payload))
        loaded_receipt = json.loads(receipt.read_text(encoding="utf-8"))
        assert_true(loaded_receipt["command"] == "check" and loaded_receipt["status"] == "PASS", "19b. Receipt file is valid JSON", json.dumps(loaded_receipt))

        checker_code, checker_payload = run_receipt_checker(receipt, "check", "PASS")
        assert_true(checker_code == 0 and checker_payload["status"] == "PASS", "19c. Receipt checker validates receipt", json.dumps(checker_payload))

        code, stdout, stderr = run_gate_raw(registry, ["status"], add_json=True)
        parsed = json.loads(stdout.strip())
        assert_true(
            code == 0 and stdout.strip().startswith("{") and stdout.strip().endswith("}") and parsed["status"] == "PASS" and not stderr.strip(),
            "20. JSON output is parseable with no extra text",
            stdout + stderr,
        )

    print(f"PASS: Reference usage smoke tests ({CHECKS} checks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
