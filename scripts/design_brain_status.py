#!/usr/bin/env python
"""Report operational status for the Codex Design Brain."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from design_brain_package_integrity import MANDATORY_FILES, result_to_dict, validate_source
from design_brain_reference_corpus_health import build_report as corpus_health_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report Codex Design Brain status.")
    parser.add_argument("--root", default="", help="Project root. Defaults to this repository root.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def status_root(value: str) -> Path:
    return Path(value).expanduser().resolve() if value else repo_root()


def typeui_status(root: Path) -> dict[str, object]:
    raw = root / ".design-brain" / "typeui-skills" / "raw"
    extracted = root / ".design-brain" / "typeui-skills" / "extracted"
    raw_files = sorted(raw.glob("*/DESIGN.md")) if raw.exists() else []
    extracted_files = sorted(extracted.glob("*.json")) if extracted.exists() else []
    return {
        "rawDirExists": raw.exists(),
        "extractedDirExists": extracted.exists(),
        "rawFileCount": len(raw_files),
        "extractedFileCount": len(extracted_files),
        "publicCoreDefault": "excluded",
        "status": "ok" if raw_files or extracted_files else "optional-missing",
    }


def release_report_context_exists(root: Path) -> bool:
    return (
        (root / "reports" / "brain-design-runtime-upgrade").is_dir()
        and (root / "reports" / "brain-design-total-integration").is_dir()
    )


def installed_integrity(root: Path) -> dict[str, object]:
    missing = [path for path in MANDATORY_FILES if not (root / path).is_file()]
    return {
        "mode": "installed",
        "target": str(root),
        "ok": not missing,
        "errors": [f"Missing installed file: {path}" for path in missing],
        "warnings": [],
        "info": [
            "Installed-target integrity check uses portable mandatory file presence.",
            "Release-source reports and generated working directories are not required in installed projects.",
        ],
        "mandatoryFilesPresent": not missing,
        "missingMandatoryFiles": missing,
    }


def collect_status(root: Path) -> dict[str, object]:
    integrity = (
        result_to_dict(validate_source(root))
        if release_report_context_exists(root)
        else installed_integrity(root)
    )
    corpus = corpus_health_report(root)
    typeui = typeui_status(root)
    version_file = root / ".design-brain" / "VERSION.md"
    version = version_file.read_text(encoding="utf-8").splitlines()[2] if version_file.exists() and len(version_file.read_text(encoding="utf-8").splitlines()) > 2 else "unknown"
    ready = "no"
    if bool(integrity.get("ok")) and (integrity.get("warnings") or corpus.get("status") == "warning" or typeui["status"] == "optional-missing"):
        ready = "yes with warnings"
    elif bool(integrity.get("ok")):
        ready = "yes"
    return {
        "root": str(root),
        "version": version,
        "ready": ready,
        "integrity": integrity,
        "referenceCorpus": corpus,
        "typeui": typeui,
    }


def print_text(status: dict[str, object]) -> None:
    integrity = status["integrity"]
    corpus = status["referenceCorpus"]
    typeui = status["typeui"]
    assert isinstance(integrity, dict)
    assert isinstance(corpus, dict)
    assert isinstance(typeui, dict)

    print("Codex Design Brain Status")
    print("=========================")
    print(f"Root: {status['root']}")
    print(f"Version: {status.get('version')}")
    print(f"READY: {status['ready']}")
    print("")

    print("Mandatory Checks")
    print(f"- Package integrity: {'PASS' if integrity['ok'] else 'FAIL'}")
    errors = integrity.get("errors", [])
    if not isinstance(errors, list):
        errors = []
    missing = integrity.get("missingMandatoryFiles", [])
    if not isinstance(missing, list):
        missing = []
    mandatory_missing_from_errors = [
        item
        for item in errors
        if "Missing mandatory source file:" in str(item) or "ZIP missing mandatory file:" in str(item)
    ]
    mandatory_present = bool(integrity.get("mandatoryFilesPresent", not missing and not mandatory_missing_from_errors))
    print(f"- Mandatory files present: {'yes' if mandatory_present else 'no'}")
    info = integrity.get("info", [])
    if isinstance(info, list):
        installer = [item for item in info if "Installer dry-run" in str(item)]
        router = [item for item in info if "Router smoke test" in str(item)]
        print(f"- Installer dry-run: {installer[0] if installer else 'not reported'}")
        print(f"- Router smoke test: {router[0] if router else 'not reported'}")
    if missing:
        for file in missing:
            print(f"  - missing: {file}")
    for item in mandatory_missing_from_errors:
        print(f"  - {item}")
    print("")

    print("Reference Integrity")
    warnings = integrity.get("warnings", [])
    if errors:
        print("- Errors:")
        for item in errors:
            print(f"  - {item}")
    else:
        print("- Errors: none")
    if warnings:
        print("- Warnings:")
        for item in warnings:
            print(f"  - {item}")
    else:
        print("- Warnings: none")
    print("")

    print("Optional Corpus")
    print(f"- Status: {corpus.get('status')}")
    print(f"- Candidate count: {corpus.get('candidateCount')}")
    print(f"- Message: {corpus.get('message')}")
    print("")

    print("Optional TypeUI")
    print(f"- Status: {typeui.get('status')}")
    print(f"- Raw files: {typeui.get('rawFileCount')}")
    print(f"- Extracted files: {typeui.get('extractedFileCount')}")
    print(f"- Public-core default: {typeui.get('publicCoreDefault')}")
    print("")

    print("Public-Core Hygiene")
    if errors:
        print("- Risk: FAIL; see errors above.")
    else:
        print("- Risk: PASS for mandatory/package/install checks.")
    if isinstance(integrity.get("info"), list):
        for item in integrity["info"]:
            if any(label in str(item) for label in ("manifest categories", "hash validation", "Router smoke test")):
                print(f"- {item}")
    if warnings:
        print("- Notes: warnings are optional assets or non-blocking references.")


def main() -> int:
    args = parse_args()
    root = status_root(args.root)
    status = collect_status(root)
    if args.json:
        print(json.dumps(status, indent=2, ensure_ascii=False))
    else:
        print_text(status)
    return 0 if status["ready"] != "no" else 1


if __name__ == "__main__":
    raise SystemExit(main())
