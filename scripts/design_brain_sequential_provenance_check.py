#!/usr/bin/env python
"""Validate serial provenance for multi-template Brain Design builds.

This gate exists because visual screenshots and fingerprints can still pass
when the real implementation used one shared batch scaffold. For multi-template
website/Figma/source work, READY requires proof that each template was completed,
locked, and scaffold-disposed before the next cycle started.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True


LEDGER_NAME = "build-session-ledger.json"
TEMPLATE_MARKERS = {
    "template",
    "website",
    "figma",
    "source",
    "marketplace",
    "ecommerce",
    "landing",
    "dashboard",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate sequential build provenance.")
    parser.add_argument("--build-dir", required=True)
    parser.add_argument("--session", default="")
    parser.add_argument("--expected-templates", type=int, default=1)
    parser.add_argument("--batch", action="store_true")
    parser.add_argument("--mode", default="")
    parser.add_argument("--product-family", default="")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_json(build_dir: Path, patterns: list[str]) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(build_dir.glob(pattern))
    return sorted(set(path for path in paths if path.is_file()))


def resolve_path(base: Path, value: str) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    return (base / candidate).resolve()


def load_session_ledger(build_dir: Path, session_arg: str) -> tuple[dict[str, Any] | None, Path | None, list[str]]:
    candidates: list[Path] = []
    if session_arg:
        session_path = Path(session_arg).expanduser().resolve()
        candidates.append(session_path / LEDGER_NAME if session_path.is_dir() else session_path)
    candidates.append(build_dir / LEDGER_NAME)
    candidates.extend(build_dir.glob(f"**/{LEDGER_NAME}"))

    seen: set[Path] = set()
    for path in candidates:
        if path in seen:
            continue
        seen.add(path)
        if not path.exists():
            continue
        try:
            return load_json(path), path.parent, []
        except Exception as exc:
            return None, None, [f"build-session ledger invalid JSON: {path}: {exc}"]
    return None, None, ["build-session ledger missing for multi-template serial provenance"]


def requires_serial_provenance(
    expected_templates: int,
    *,
    batch: bool,
    mode: str,
    product_family: str,
) -> bool:
    if expected_templates <= 1:
        return False
    combined = f"{mode} {product_family}".lower().replace("_", "-")
    marker_hit = any(marker in combined for marker in TEMPLATE_MARKERS)
    return batch or marker_hit


def nonblank_line_count(path: Path) -> int:
    try:
        return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    except Exception:
        return 0


def receipt_morphology_issues(build_dir: Path, expected_templates: int) -> list[str]:
    if expected_templates <= 1:
        return []
    categories = {
        "design cognition receipts": [
            "design-cognition-receipts/*.json",
            "design_cognition_receipts/*.json",
            "*cognition*receipt*.json",
        ],
        "template fingerprints": [
            "template-fingerprints/*.json",
            "fingerprints/*.json",
            "*fingerprint*.json",
        ],
        "design-system receipts": [
            "design-system-receipts/*.json",
            "design_system_receipts/*.json",
            "design-system*.json",
            "design_system*.json",
        ],
    }
    issues: list[str] = []
    identical_categories = 0
    for label, patterns in categories.items():
        paths = discover_json(build_dir, patterns)
        if len(paths) < expected_templates:
            continue
        counts = {path.name: nonblank_line_count(path) for path in paths[:expected_templates]}
        nonzero = [count for count in counts.values() if count > 0]
        if len(nonzero) >= expected_templates and len(set(nonzero)) == 1:
            identical_categories += 1
            issues.append(
                f"{label} have identical nonblank line counts ({nonzero[0]}); this is all-at-once scaffold evidence unless rebuilt as separate cycle artifacts"
            )
    if identical_categories >= 2:
        issues.append("multiple receipt categories share identical morphology across the batch; provenance must BLOCK rather than PASS")
    return issues


def build_artifact_scope_issues(session_dir: Path, item: dict[str, Any]) -> list[str]:
    template_id = str(item.get("templateId") or "unknown-template")
    value = str(item.get("buildArtifactPath") or "")
    if not value:
        return [f"{template_id} missing build artifact path"]
    path = resolve_path(session_dir, value)
    if not path.exists():
        return [f"{template_id} build artifact missing: {value}"]
    if path.suffix.lower() != ".json":
        return []
    try:
        payload = load_json(path)
    except Exception:
        return []
    issues: list[str] = []
    scope_fields = (
        "templateIds",
        "builtTemplateIds",
        "createdTemplateIds",
        "mutatedTemplateIds",
        "sourceFrameIds",
        "designSystemFrameIds",
    )
    for field in scope_fields:
        raw = payload.get(field)
        if isinstance(raw, list) and len(set(str(item) for item in raw)) > 1:
            issues.append(f"{template_id} build artifact field {field} contains multiple templates/frames")
    return issues


def validate_ledger(ledger: dict[str, Any], session_dir: Path, expected_templates: int) -> list[str]:
    issues: list[str] = []
    templates = ledger.get("templates", [])
    if not isinstance(templates, list):
        return ["build-session templates field must be a list"]

    ledger_expected = int(ledger.get("expectedTemplateCount") or 0)
    if ledger_expected and ledger_expected != expected_templates:
        issues.append(f"build-session expectedTemplateCount is {ledger_expected}, expected {expected_templates}")
    if len(templates) < expected_templates:
        issues.append(f"build-session has {len(templates)} templates, expected {expected_templates}")

    for index, item in enumerate(templates[:expected_templates]):
        template_id = str(item.get("templateId") or f"template-{index + 1}")
        if int(item.get("cycleNumber") or 0) != index + 1:
            issues.append(f"{template_id} cycleNumber must be {index + 1}")
        if not item.get("startedAt"):
            issues.append(f"{template_id} missing startedAt timestamp")
        if item.get("status") != "fingerprint_locked":
            issues.append(f"{template_id} is not fingerprint_locked")
        if "fingerprint_locked" not in item.get("stages", []):
            issues.append(f"{template_id} missing fingerprint_locked stage")
        if not item.get("lockedAt"):
            issues.append(f"{template_id} missing lockedAt timestamp")
        issues.extend(build_artifact_scope_issues(session_dir, item))

        if index < expected_templates - 1:
            if not item.get("scaffoldDisposalReceiptPath"):
                issues.append(f"{template_id} missing scaffold disposal receipt before next template")
            else:
                disposal_path = resolve_path(session_dir, str(item["scaffoldDisposalReceiptPath"]))
                if not disposal_path.exists():
                    issues.append(f"{template_id} scaffold disposal receipt missing on disk")
            if "scaffold_disposed" not in item.get("stages", []):
                issues.append(f"{template_id} missing scaffold_disposed stage before next template")
            if not item.get("disposedAt"):
                issues.append(f"{template_id} missing disposedAt timestamp before next template")

            if index + 1 < len(templates):
                next_item = templates[index + 1]
                next_id = str(next_item.get("templateId") or f"template-{index + 2}")
                next_started = str(next_item.get("startedAt") or "")
                if item.get("lockedAt") and next_started and next_started < str(item["lockedAt"]):
                    issues.append(f"{next_id} started before {template_id} was fingerprint_locked")
                if item.get("disposedAt") and next_started and next_started < str(item["disposedAt"]):
                    issues.append(f"{next_id} started before {template_id} scaffold was disposed")

    return issues


def validate_sequential_provenance(
    *,
    build_dir: Path,
    session_arg: str = "",
    expected_templates: int = 1,
    batch: bool = False,
    mode: str = "",
    product_family: str = "",
) -> dict[str, Any]:
    required = requires_serial_provenance(
        expected_templates,
        batch=batch,
        mode=mode,
        product_family=product_family,
    )
    issues: list[str] = []
    warnings: list[str] = []
    if not required:
        return {
            "status": "PASS",
            "required": False,
            "issues": [],
            "warnings": [],
            "sessionId": "",
        }

    ledger, session_dir, ledger_issues = load_session_ledger(build_dir, session_arg)
    issues.extend(ledger_issues)
    if ledger and session_dir:
        issues.extend(validate_ledger(ledger, session_dir, expected_templates))
    morphology = receipt_morphology_issues(build_dir, expected_templates)
    if morphology:
        issues.extend(morphology)

    return {
        "status": "PASS" if not issues else "BLOCKED",
        "required": True,
        "issues": issues,
        "warnings": warnings,
        "sessionId": str(ledger.get("sessionId", "")) if ledger else "",
    }


def main() -> int:
    args = parse_args()
    result = validate_sequential_provenance(
        build_dir=Path(args.build_dir).expanduser().resolve(),
        session_arg=args.session,
        expected_templates=args.expected_templates,
        batch=args.batch,
        mode=args.mode,
        product_family=args.product_family,
    )
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['status']}: sequential provenance")
        for issue in result.get("issues", []):
            print(f"- {issue}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
