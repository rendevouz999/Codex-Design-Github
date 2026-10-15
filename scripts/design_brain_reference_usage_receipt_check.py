#!/usr/bin/env python
"""Validate Brain Design reference usage receipt JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


def load_receipt(path: Path) -> tuple[dict[str, Any], list[str]]:
    if not path.is_file():
        return {}, [f"RECEIPT_NOT_FOUND {path}"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return {}, [f"RECEIPT_INVALID_JSON {exc}"]


def validate_receipt(payload: dict[str, Any], *, expect_command: str = "", expect_status: str = "") -> list[str]:
    issues: list[str] = []
    command = str(payload.get("command", "") or "")
    status = str(payload.get("status", "") or "")
    if not command:
        issues.append("COMMAND_MISSING")
    if not status:
        issues.append("STATUS_MISSING")
    if expect_command and command != expect_command:
        issues.append(f"COMMAND_MISMATCH expected {expect_command}, got {command}")
    if expect_status and status != expect_status:
        issues.append(f"STATUS_MISMATCH expected {expect_status}, got {status}")
    if command in {"check", "record"}:
        if not str(payload.get("referenceGroupKey", "") or "").strip():
            issues.append("REFERENCE_GROUP_KEY_MISSING")
        if not str(payload.get("referenceMode", "") or "").strip():
            issues.append("REFERENCE_MODE_MISSING")
        if not (str(payload.get("brandName", "") or "").strip() or str(payload.get("candidateBrandName", "") or "").strip()):
            issues.append("BRAND_NAME_MISSING")
    if not isinstance(payload.get("blockingReasons"), list):
        issues.append("BLOCKING_REASONS_NOT_LIST")
    if not isinstance(payload.get("warnings"), list):
        issues.append("WARNINGS_NOT_LIST")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Brain Design reference usage receipt.")
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--expect-command", default="")
    parser.add_argument("--expect-status", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    receipt_path = Path(args.receipt).expanduser()
    if not receipt_path.is_absolute():
        receipt_path = (Path.cwd() / receipt_path).resolve()
    payload, issues = load_receipt(receipt_path)
    if not issues:
        issues.extend(validate_receipt(payload, expect_command=args.expect_command, expect_status=args.expect_status))
    result = {
        "status": "PASS" if not issues else "BLOCKED",
        "receipt": str(receipt_path),
        "command": payload.get("command", "") if payload else "",
        "receiptStatus": payload.get("status", "") if payload else "",
        "expectedCommand": args.expect_command,
        "expectedStatus": args.expect_status,
        "issues": issues,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("PASS: receipt valid" if result["status"] == "PASS" else json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
