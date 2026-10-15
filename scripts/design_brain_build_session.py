#!/usr/bin/env python
"""Manage Brain Design sequential build-session lifecycle ledgers."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

from design_brain_layout_similarity_audit import (
    audit_candidate_against_many,
    load_json,
    template_id as fingerprint_template_id,
)
from design_brain_design_system_check import is_web_deck_text, validate_design_system
from design_brain_visual_gate import validate_post_build_receipt


LEDGER_NAME = "build-session-ledger.json"


def utc_id(prefix: str = "session") -> str:
    return f"{prefix}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage Brain Design build-session lifecycle.")
    sub = parser.add_subparsers(dest="command", required=True)

    start = sub.add_parser("start")
    start.add_argument("--task", required=True)
    start.add_argument("--expected-templates", type=int, required=True)
    start.add_argument("--output-dir", required=True)
    start.add_argument("--product-family", default="")
    start.add_argument("--mode", default="")
    start.add_argument("--route", default="")
    start.add_argument("--json", action="store_true")

    def add_session_template(p: argparse.ArgumentParser) -> None:
        p.add_argument("--session", required=True)
        p.add_argument("--template-id", required=True)
        p.add_argument("--json", action="store_true")

    reg_ref = sub.add_parser("register-reference")
    add_session_template(reg_ref)
    reg_ref.add_argument("--reference", required=True)
    reg_ref.add_argument("--fingerprint", required=True)
    reg_ref.add_argument("--reference-id", default="")

    reg_ref_usage_check = sub.add_parser("register-reference-usage-check")
    add_session_template(reg_ref_usage_check)
    reg_ref_usage_check.add_argument("--candidate-brand-name", required=True)
    reg_ref_usage_check.add_argument("--reference-usage-mode", required=True)
    reg_ref_usage_check.add_argument("--reference-group-key", required=True)
    reg_ref_usage_check.add_argument("--receipt", required=True)

    reg_ref_usage_record = sub.add_parser("register-reference-usage-record")
    add_session_template(reg_ref_usage_record)
    reg_ref_usage_record.add_argument("--receipt", required=True)

    reg_cognition = sub.add_parser("register-cognition")
    add_session_template(reg_cognition)
    reg_cognition.add_argument("--receipt", required=True)

    reg_sim = sub.add_parser("register-simulation")
    add_session_template(reg_sim)
    reg_sim.add_argument("--verdict", required=True)

    reg_plan = sub.add_parser("register-plan")
    add_session_template(reg_plan)
    reg_plan.add_argument("--plan", required=True)
    reg_plan.add_argument("--fingerprint", required=True)

    audit = sub.add_parser("audit-layout")
    add_session_template(audit)

    reg_build = sub.add_parser("register-build")
    add_session_template(reg_build)
    reg_build.add_argument("--artifact", required=True)
    reg_build.add_argument("--fingerprint", required=True)

    reg_web_deck = sub.add_parser("register-web-deck-evidence")
    add_session_template(reg_web_deck)
    reg_web_deck.add_argument("--static-audit", required=True, choices=("PASS", "BLOCKED", "NOT_RUN"))
    reg_web_deck.add_argument("--render-review", required=True, choices=("PASS", "FAIL", "NOT_RUN"))

    reg_ds = sub.add_parser("register-design-system")
    add_session_template(reg_ds)
    reg_ds.add_argument("--receipt", required=True)

    reg_post = sub.add_parser("register-post-build")
    add_session_template(reg_post)
    reg_post.add_argument("--receipt", required=True)

    lock = sub.add_parser("lock-template")
    add_session_template(lock)

    dispose = sub.add_parser("register-scaffold-disposal")
    add_session_template(dispose)
    dispose.add_argument("--receipt", required=True)

    can = sub.add_parser("can-start-next")
    add_session_template(can)

    final = sub.add_parser("finalize")
    final.add_argument("--session", required=True)
    final.add_argument("--json", action="store_true")

    verify = sub.add_parser("verify-final")
    verify.add_argument("--session", required=True)
    verify.add_argument("--json", action="store_true")

    return parser.parse_args()


def ledger_path(session: Path) -> Path:
    return session / LEDGER_NAME


def load_ledger(session: Path) -> dict[str, Any]:
    return json.loads(ledger_path(session).read_text(encoding="utf-8"))


def save_ledger(session: Path, ledger: dict[str, Any]) -> None:
    session.mkdir(parents=True, exist_ok=True)
    ledger_path(session).write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8", newline="\n")


def rel_to_session(path: str, session: Path) -> str:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = (Path.cwd() / value).resolve()
    try:
        return value.relative_to(session.resolve()).as_posix()
    except ValueError:
        return str(value)


def absolute_input_path(path: str) -> Path:
    value = Path(path).expanduser()
    if not value.is_absolute():
        value = (Path.cwd() / value).resolve()
    return value


def empty_template(template_id: str) -> dict[str, Any]:
    return {
        "templateId": template_id,
        "referenceId": "",
        "candidateBrandName": "",
        "referenceUsageMode": "",
        "referenceGroupKey": "",
        "brandReferenceUsageCheckPath": "",
        "brandReferenceUsageRecordPath": "",
        "route": {},
        "cognitionReceiptPath": "",
        "simulationVerdictPath": "",
        "templatePlanPath": "",
        "candidateFingerprintPath": "",
        "referenceFingerprintPath": "",
        "referenceLayoutAuditPath": "",
        "buildArtifactPath": "",
        "webDeckEvidenceRequired": False,
        "webDeckStaticAuditStatus": "",
        "webDeckRenderReviewStatus": "",
        "designSystemReceiptPath": "",
        "postBuildAuditPath": "",
        "pairwiseAudits": [],
        "fingerprintPath": "",
        "scaffoldDisposalReceiptPath": "",
        "cycleNumber": 0,
        "startedAt": "",
        "lockedAt": "",
        "disposedAt": "",
        "status": "started",
        "stages": [],
    }


def template_index(ledger: dict[str, Any], template_id: str) -> int:
    for index, item in enumerate(ledger["templates"]):
        if item["templateId"] == template_id:
            return index
    return -1


def get_template(ledger: dict[str, Any], template_id: str) -> dict[str, Any]:
    index = template_index(ledger, template_id)
    if index >= 0:
        return ledger["templates"][index]
    if ledger.get("templates"):
        expected = int(ledger.get("expectedTemplateCount") or 0)
        blockers: list[str] = []
        for previous in ledger["templates"]:
            previous_id = str(previous.get("templateId") or "unknown-template")
            if previous.get("status") != "fingerprint_locked":
                blockers.append(f"{previous_id} is not fingerprint_locked")
            if expected > 1 and not previous.get("scaffoldDisposalReceiptPath"):
                blockers.append(f"{previous_id} has no scaffold disposal receipt")
        if blockers:
            raise SystemExit(
                "Cannot start or register a new template before every previous template is locked and scaffold-disposed: "
                + "; ".join(blockers)
            )
    item = empty_template(template_id)
    item["cycleNumber"] = len(ledger.get("templates", [])) + 1
    item["startedAt"] = utc_now()
    ledger["templates"].append(item)
    return item


def add_stage(item: dict[str, Any], stage: str) -> None:
    stages = item.setdefault("stages", [])
    if stage not in stages:
        stages.append(stage)


def locked_templates_before(ledger: dict[str, Any], template_id: str) -> list[dict[str, Any]]:
    index = template_index(ledger, template_id)
    if index <= 0:
        return []
    return [item for item in ledger["templates"][:index] if item.get("status") == "fingerprint_locked"]


def can_start_template(ledger: dict[str, Any], template_id: str) -> tuple[bool, str]:
    if not ledger.get("templates"):
        return True, "First template may start."
    index = template_index(ledger, template_id)
    if index == 0:
        return True, "Template is first in session."
    if index < 0:
        expected_index = len(ledger["templates"])
        previous = ledger["templates"][:expected_index]
    else:
        previous = ledger["templates"][:index]
    unlocked = [item["templateId"] for item in previous if item.get("status") != "fingerprint_locked"]
    if unlocked:
        return False, f"Previous template pair(s) must complete template + design system + post-build audit and become fingerprint_locked first: {', '.join(unlocked)}"
    expected = int(ledger.get("expectedTemplateCount") or 0)
    if expected > 1:
        not_disposed = [item["templateId"] for item in previous if not item.get("scaffoldDisposalReceiptPath")]
        if not_disposed:
            return False, f"Previous template scaffold(s) must be disposed before the next cycle starts: {', '.join(not_disposed)}"
    return True, "All previous template pairs are complete and fingerprint_locked."


def write_audit(session: Path, template_id: str, name: str, payload: dict[str, Any]) -> str:
    out_dir = session / "layout-audits"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{template_id}-{name}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path.relative_to(session).as_posix()


def command_start(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.output_dir).expanduser().resolve()
    route: dict[str, Any] = {}
    if args.route:
        try:
            route = json.loads(args.route)
        except json.JSONDecodeError:
            route = {"raw": args.route}
    ledger = {
        "sessionId": session.name if session.name else utc_id(),
        "task": args.task,
        "expectedTemplateCount": args.expected_templates,
        "productFamily": args.product_family,
        "mode": args.mode,
        "route": route,
        "templates": [],
        "references": [],
        "lifecycleStatus": "session_started",
        "globalBatchAudit": {},
        "completionReceipt": {},
        "finalStatus": "IN_PROGRESS",
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_ledger(session, ledger)
    return ledger


def command_register_reference(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    if "brand_reference_usage_checked" not in item.get("stages", []):
        raise SystemExit("Reference cannot be registered before brand/reference usage check PASS.")
    reference_id = args.reference_id or Path(args.reference).stem
    item["referenceId"] = reference_id
    item["referenceFingerprintPath"] = rel_to_session(args.fingerprint, session)
    item["referencePath"] = rel_to_session(args.reference, session)
    add_stage(item, "reference_registered")
    ledger["references"].append({"templateId": args.template_id, "referenceId": reference_id, "path": item["referencePath"], "fingerprintPath": item["referenceFingerprintPath"]})
    ledger["lifecycleStatus"] = "reference_registered"
    save_ledger(session, ledger)
    return ledger


def command_register_reference_usage_check(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    receipt_path = absolute_input_path(args.receipt)
    receipt_ok, receipt_issues = reference_usage_receipt_status(session, str(receipt_path), "check")
    if not receipt_ok:
        raise SystemExit("Brand/reference usage check receipt cannot be registered: " + "; ".join(receipt_issues))
    item["candidateBrandName"] = args.candidate_brand_name.strip()
    item["referenceUsageMode"] = args.reference_usage_mode.strip()
    item["referenceGroupKey"] = args.reference_group_key.strip()
    item["brandReferenceUsageCheckPath"] = rel_to_session(str(receipt_path), session)
    add_stage(item, "brand_reference_usage_checked")
    ledger["lifecycleStatus"] = "brand_reference_usage_checked"
    save_ledger(session, ledger)
    return ledger


def command_register_reference_usage_record(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    receipt_path = absolute_input_path(args.receipt)
    receipt_ok, receipt_issues = reference_usage_receipt_status(session, str(receipt_path), "record")
    if not receipt_ok:
        raise SystemExit("Brand/reference usage record receipt cannot be registered: " + "; ".join(receipt_issues))
    item["brandReferenceUsageRecordPath"] = rel_to_session(str(receipt_path), session)
    add_stage(item, "brand_reference_usage_recorded")
    ledger["lifecycleStatus"] = "brand_reference_usage_recorded"
    save_ledger(session, ledger)
    return ledger


def command_register_cognition(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    item["cognitionReceiptPath"] = rel_to_session(args.receipt, session)
    add_stage(item, "design_cognition_passed")
    ledger["lifecycleStatus"] = "design_cognition_passed"
    save_ledger(session, ledger)
    return ledger


def command_register_simulation(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    item["simulationVerdictPath"] = rel_to_session(args.verdict, session)
    add_stage(item, "design_simulation_passed")
    ledger["lifecycleStatus"] = "design_simulation_passed"
    save_ledger(session, ledger)
    return ledger


def command_register_plan(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    item["templatePlanPath"] = rel_to_session(args.plan, session)
    item["candidateFingerprintPath"] = rel_to_session(args.fingerprint, session)
    add_stage(item, "template_plan_created")
    ledger["lifecycleStatus"] = "template_plan_created"
    save_ledger(session, ledger)
    return ledger


def resolve_session_path(session: Path, path: str) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (session / candidate).resolve()


def command_audit_layout(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    candidate_path = resolve_session_path(session, item.get("candidateFingerprintPath") or item.get("fingerprintPath") or "")
    reference_path = resolve_session_path(session, item.get("referenceFingerprintPath") or "")
    candidate = load_json(candidate_path)
    reference = load_json(reference_path)

    ref_result = audit_candidate_against_many(candidate, [reference], "ai_vs_reference")
    item["referenceLayoutAuditPath"] = write_audit(session, args.template_id, "reference-layout-audit", ref_result)

    previous_items = locked_templates_before(ledger, args.template_id)
    previous_fingerprints = [load_json(resolve_session_path(session, prev["fingerprintPath"])) for prev in previous_items]
    if previous_fingerprints:
        pair_result = audit_candidate_against_many(candidate, previous_fingerprints, "ai_vs_ai")
        pair_path = write_audit(session, args.template_id, "ai-pairwise-layout-audit", pair_result)
        item["pairwiseAudits"] = [pair_path]
    else:
        pair_result = {"status": "N/A", "safeToProceed": True, "pairMatrix": [], "requiredRepairs": []}
        item["pairwiseAudits"] = []

    if ref_result["status"] == "PASS" and pair_result["status"] in {"PASS", "N/A"}:
        add_stage(item, "reference_layout_audit_passed")
        add_stage(item, "previous_template_similarity_audit_passed")
        item["status"] = "layout_audit_passed"
    else:
        item["status"] = "layout_audit_failed"
    ledger["lifecycleStatus"] = item["status"]
    save_ledger(session, ledger)
    return {
        "templateId": args.template_id,
        "referenceLayoutAudit": ref_result,
        "pairwiseLayoutAudit": pair_result,
        "safeToProceed": item["status"] == "layout_audit_passed",
        "ledger": ledger,
    }


def command_register_build(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    if "reference_layout_audit_passed" not in item.get("stages", []):
        raise SystemExit("Build cannot be registered before layout audit PASS.")
    artifact_path = Path(args.artifact).expanduser()
    if not artifact_path.is_absolute():
        artifact_path = (Path.cwd() / artifact_path).resolve()
    scope_issues = build_artifact_scope_issues(artifact_path, args.template_id)
    if scope_issues:
        raise SystemExit("Build artifact cannot be registered: " + "; ".join(scope_issues))
    item["buildArtifactPath"] = rel_to_session(args.artifact, session)
    item["fingerprintPath"] = rel_to_session(args.fingerprint, session)
    add_stage(item, "template_built")
    ledger["lifecycleStatus"] = "template_built"
    save_ledger(session, ledger)
    return ledger


def command_register_web_deck_evidence(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    if "template_built" not in item.get("stages", []):
        raise SystemExit("Web deck static audit and render review cannot be registered before the build.")
    item["webDeckEvidenceRequired"] = True
    item["webDeckStaticAuditStatus"] = args.static_audit
    item["webDeckRenderReviewStatus"] = args.render_review
    evidence_issues = web_deck_evidence_issues(item)
    if not evidence_issues:
        add_stage(item, "web_deck_evidence_passed")
        ledger["lifecycleStatus"] = "web_deck_evidence_passed"
    save_ledger(session, ledger)
    if evidence_issues:
        raise SystemExit("Web deck evidence is not complete: " + "; ".join(evidence_issues))
    return ledger


def command_register_design_system(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    if template_requires_web_deck_evidence(ledger, item):
        evidence_issues = web_deck_evidence_issues(item)
        if evidence_issues:
            raise SystemExit("Design system cannot be registered before web deck static audit and render review PASS: " + "; ".join(evidence_issues))
    receipt_path = Path(args.receipt).expanduser()
    if not receipt_path.is_absolute():
        receipt_path = (Path.cwd() / receipt_path).resolve()
    receipt = load_json(receipt_path)
    result = validate_design_system(receipt)
    if result.get("status") != "PASS":
        errors = ", ".join(str(error) for error in result.get("errors", [])) or "design system receipt did not pass"
        raise SystemExit(f"Design system cannot be registered before validation PASS: {errors}")
    item["designSystemReceiptPath"] = rel_to_session(str(receipt_path), session)
    item["designSystemValidation"] = result
    add_stage(item, "design_system_built")
    ledger["lifecycleStatus"] = "design_system_built"
    save_ledger(session, ledger)
    return ledger


def command_register_post_build(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    receipt = Path(args.receipt).expanduser().resolve()
    artifact = Path(item.get("buildArtifactPath") or "")
    if not item.get("buildArtifactPath"):
        raise SystemExit("Register build artifact before post-build inspection.")
    if not artifact.is_absolute():
        artifact = session / artifact
    validation = validate_post_build_receipt(receipt, artifact)
    if validation["status"] != "PASS":
        raise SystemExit("Cannot register post-build visual PASS: " + "; ".join(validation["issues"]))
    item["postBuildAuditPath"] = rel_to_session(str(receipt), session)
    add_stage(item, "post_build_audit_passed")
    ledger["lifecycleStatus"] = "post_build_audit_passed"
    save_ledger(session, ledger)
    return ledger


def command_lock_template(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    item = get_template(ledger, args.template_id)
    required = ["reference_layout_audit_passed", "template_built", "design_system_built", "post_build_audit_passed"]
    missing = [stage for stage in required if stage not in item.get("stages", [])]
    if missing:
        raise SystemExit(f"Cannot lock fingerprint; missing stages: {', '.join(missing)}")
    if not item.get("fingerprintPath"):
        raise SystemExit("Cannot lock fingerprint; fingerprintPath missing.")
    item["status"] = "fingerprint_locked"
    item["lockedAt"] = utc_now()
    add_stage(item, "fingerprint_locked")
    ledger["lifecycleStatus"] = "fingerprint_locked"
    save_ledger(session, ledger)
    return ledger


def command_register_scaffold_disposal(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    index = template_index(ledger, args.template_id)
    if index < 0:
        raise SystemExit("Cannot dispose scaffold for an unknown template.")
    item = ledger["templates"][index]
    if item.get("status") != "fingerprint_locked":
        raise SystemExit("Scaffold disposal cannot be registered before fingerprint lock.")
    receipt_path = Path(args.receipt).expanduser()
    if not receipt_path.is_absolute():
        receipt_path = (Path.cwd() / receipt_path).resolve()
    if not receipt_path.exists():
        raise SystemExit(f"Scaffold disposal receipt not found: {receipt_path}")
    item["scaffoldDisposalReceiptPath"] = rel_to_session(str(receipt_path), session)
    item["disposedAt"] = utc_now()
    add_stage(item, "scaffold_disposed")
    ledger["lifecycleStatus"] = "scaffold_disposed"
    save_ledger(session, ledger)
    return ledger


def command_can_start_next(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    allowed, reason = can_start_template(ledger, args.template_id)
    return {"templateId": args.template_id, "canStart": allowed, "reason": reason}


def path_field_exists(session: Path, value: str) -> bool:
    if not value:
        return False
    return resolve_session_path(session, value).exists()


def build_artifact_scope_issues(path: Path, template_id: str) -> list[str]:
    if not path.exists() or path.suffix.lower() != ".json":
        return []
    try:
        payload = load_json(path)
    except Exception:
        return []
    fields = (
        "templateIds",
        "builtTemplateIds",
        "createdTemplateIds",
        "mutatedTemplateIds",
        "sourceFrameIds",
        "designSystemFrameIds",
    )
    issues: list[str] = []
    for field in fields:
        value = payload.get(field)
        if isinstance(value, list) and len(set(str(item) for item in value)) > 1:
            issues.append(f"build artifact field {field} contains multiple templates/frames; {template_id} build must be single-template scoped")
    return issues


def template_requires_reference_usage(ledger: dict[str, Any], item: dict[str, Any]) -> bool:
    text_parts = [
        str(ledger.get("task", "")),
        str(ledger.get("productFamily", "")),
        str(ledger.get("mode", "")),
        str(item.get("referenceId", "")),
        str(item.get("referencePath", "")),
        str(item.get("referenceFingerprintPath", "")),
        str(item.get("brandReferenceUsageCheckPath", "")),
        str(item.get("brandReferenceUsageRecordPath", "")),
    ]
    route = ledger.get("route", {})
    item_route = item.get("route", {})
    if isinstance(route, dict):
        text_parts.extend(str(value) for value in route.values())
    if isinstance(item_route, dict):
        text_parts.extend(str(value) for value in item_route.values())
    stages = item.get("stages", [])
    if isinstance(stages, list):
        text_parts.extend(str(stage) for stage in stages)
    text = " ".join(text_parts).lower()
    if any(marker in text for marker in ("reference", "style dna")):
        return True
    return bool(item.get("referencePath") or item.get("referenceFingerprintPath") or item.get("brandReferenceUsageCheckPath") or item.get("brandReferenceUsageRecordPath"))


def template_requires_web_deck_evidence(ledger: dict[str, Any], item: dict[str, Any]) -> bool:
    if item.get("webDeckEvidenceRequired") is True:
        return True
    text_parts = [
        str(ledger.get("task", "")),
        str(ledger.get("productFamily", "")),
        str(ledger.get("mode", "")),
        str(item.get("templatePlanPath", "")),
        str(item.get("buildArtifactPath", "")),
    ]
    route = ledger.get("route", {})
    item_route = item.get("route", {})
    if isinstance(route, dict):
        text_parts.extend(str(value) for value in route.values())
    if isinstance(item_route, dict):
        text_parts.extend(str(value) for value in item_route.values())
    return is_web_deck_text(" ".join(text_parts))


def web_deck_evidence_issues(item: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    static_status = str(item.get("webDeckStaticAuditStatus") or "").upper() or "NOT_RUN"
    render_status = str(item.get("webDeckRenderReviewStatus") or "").upper() or "NOT_RUN"
    if static_status != "PASS":
        issues.append(f"web deck static audit is {static_status!r}, expected 'PASS'")
    if render_status != "PASS":
        issues.append(f"web deck render review is {render_status!r}, expected 'PASS'")
    return issues


def reference_usage_receipt_status(session: Path, value: str, expected_command: str) -> tuple[bool, list[str]]:
    if not value:
        return False, ["receipt path missing"]
    path = resolve_session_path(session, value)
    if not path.exists():
        return False, [f"receipt file missing: {value}"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, [f"receipt invalid JSON: {value}: {exc}"]
    issues: list[str] = []
    if payload.get("command") and payload.get("command") != expected_command:
        issues.append(f"receipt command is {payload.get('command')!r}, expected {expected_command!r}")
    if payload.get("status") != "PASS":
        issues.append(f"receipt status is {payload.get('status')!r}, expected 'PASS'")
    return not issues, issues


def verify_ledger_final(session: Path, ledger: dict[str, Any], *, require_completion_receipt: bool) -> dict[str, Any]:
    expected = int(ledger.get("expectedTemplateCount") or 0)
    templates = ledger.get("templates", [])
    locked = [item for item in templates if item.get("status") == "fingerprint_locked"]
    issues: list[str] = []

    route = ledger.get("route", {})
    if not isinstance(route, dict) or not route:
        issues.append("build-session route missing; router/product-family decision must be registered before final.")

    if expected <= 0:
        issues.append("expectedTemplateCount must be greater than 0.")
    if len(templates) < expected:
        issues.append(f"Expected {expected} templates, found {len(templates)}.")
    if len(locked) < expected:
        issues.append(f"Expected {expected} fingerprint locks, found {len(locked)}.")

    for item in templates:
        template_id = str(item.get("templateId") or "unknown-template")
        index = template_index(ledger, template_id)
        required_stage_fields = {
            "referencePath": "reference registration",
            "referenceFingerprintPath": "reference fingerprint",
            "cognitionReceiptPath": "Design Cognition Receipt",
            "simulationVerdictPath": "Design Simulation verdict",
            "templatePlanPath": "template plan",
            "candidateFingerprintPath": "candidate fingerprint",
            "referenceLayoutAuditPath": "reference layout audit",
            "buildArtifactPath": "build artifact",
            "fingerprintPath": "locked fingerprint",
            "designSystemReceiptPath": "design system receipt",
            "postBuildAuditPath": "post-build audit receipt",
        }
        for field, label in required_stage_fields.items():
            if not path_field_exists(session, str(item.get(field) or "")):
                issues.append(f"{template_id} missing {label}.")
        if item.get("postBuildAuditPath") and item.get("buildArtifactPath"):
            audit_path = Path(item["postBuildAuditPath"])
            artifact_path = Path(item["buildArtifactPath"])
            if not audit_path.is_absolute():
                audit_path = session / audit_path
            if not artifact_path.is_absolute():
                artifact_path = session / artifact_path
            validation = validate_post_build_receipt(audit_path, artifact_path)
            issues.extend(f"{template_id} {problem}" for problem in validation["issues"])
        if template_requires_reference_usage(ledger, item):
            if not str(item.get("candidateBrandName") or "").strip():
                issues.append(f"{template_id} missing candidate output brand name.")
            if not str(item.get("referenceUsageMode") or "").strip():
                issues.append(f"{template_id} missing reference usage mode.")
            if not str(item.get("referenceGroupKey") or "").strip():
                issues.append(f"{template_id} missing reference group key.")
            check_ok, check_issues = reference_usage_receipt_status(session, str(item.get("brandReferenceUsageCheckPath") or ""), "check")
            if not check_ok:
                issues.append(f"{template_id} brand/reference usage check receipt not PASS: {'; '.join(check_issues)}")
            record_path = str(item.get("brandReferenceUsageRecordPath") or "")
            if require_completion_receipt or record_path:
                record_ok, record_issues = reference_usage_receipt_status(session, record_path, "record")
                if not record_ok:
                    issues.append(f"{template_id} brand/reference usage registry record not PASS: {'; '.join(record_issues)}")
        if template_requires_web_deck_evidence(ledger, item):
            for issue in web_deck_evidence_issues(item):
                issues.append(f"{template_id} {issue}.")
        if expected > 1 and index > 0 and not item.get("pairwiseAudits"):
            issues.append(f"{template_id} missing AI pairwise layout audit.")
        for audit_path in item.get("pairwiseAudits", []) or []:
            if not path_field_exists(session, str(audit_path)):
                issues.append(f"{template_id} pairwise audit path missing: {audit_path}")
        if item.get("status") != "fingerprint_locked":
            issues.append(f"{template_id} fingerprint not locked.")
        if expected > 1:
            if not item.get("cycleNumber"):
                issues.append(f"{template_id} missing cycle number.")
            if not item.get("startedAt"):
                issues.append(f"{template_id} missing startedAt timestamp.")
            if not item.get("lockedAt"):
                issues.append(f"{template_id} missing lockedAt timestamp.")
            if index < expected - 1:
                if not path_field_exists(session, str(item.get("scaffoldDisposalReceiptPath") or "")):
                    issues.append(f"{template_id} missing scaffold disposal receipt before next template.")
                if not item.get("disposedAt"):
                    issues.append(f"{template_id} missing disposedAt timestamp before next template.")
                next_item = templates[index + 1] if index + 1 < len(templates) else {}
                if item.get("lockedAt") and next_item.get("startedAt") and str(next_item.get("startedAt")) < str(item.get("lockedAt")):
                    issues.append(f"{next_item.get('templateId', 'next template')} started before {template_id} was fingerprint_locked.")
                if item.get("disposedAt") and next_item.get("startedAt") and str(next_item.get("startedAt")) < str(item.get("disposedAt")):
                    issues.append(f"{next_item.get('templateId', 'next template')} started before {template_id} scaffold was disposed.")

    completion = ledger.get("completionReceipt", {})
    if require_completion_receipt:
        if not isinstance(completion, dict) or not completion:
            issues.append("final completion receipt missing from build-session ledger.")
        else:
            if completion.get("sequentialLayoutAudit") != "PASS":
                issues.append("completion receipt does not record sequentialLayoutAudit PASS.")
            if completion.get("templatesBuilt") != len(templates):
                issues.append("completion receipt template count does not match ledger.")
            if completion.get("fingerprintLocks") != len(locked):
                issues.append("completion receipt fingerprint lock count does not match ledger.")
        if ledger.get("finalStatus") != "READY":
            issues.append("build-session finalStatus is not READY.")

    return {
        "status": "PASS" if not issues else "BLOCKED",
        "sessionId": ledger.get("sessionId", ""),
        "expectedTemplateCount": expected,
        "templateCount": len(templates),
        "fingerprintLocks": len(locked),
        "completionReceiptPresent": bool(completion),
        "remainingIssues": issues,
        "safeToDeliver": not issues,
    }


def command_finalize(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    verification = verify_ledger_final(session, ledger, require_completion_receipt=False)
    issues = verification["remainingIssues"]
    locked = [item for item in ledger.get("templates", []) if item.get("status") == "fingerprint_locked"]
    ledger["completionReceipt"] = {
        "buildSessionId": ledger.get("sessionId"),
        "templatesBuilt": len(ledger.get("templates", [])),
        "fingerprintLocks": len(locked),
        "sequentialLayoutAudit": "PASS" if not issues else "FAIL",
        "remainingIssues": issues,
    }
    for item in ledger.get("templates", []):
        add_stage(item, "completion_receipt_created")
    ledger["finalStatus"] = "READY" if not issues else "BLOCKED"
    ledger["lifecycleStatus"] = "session_ready" if not issues else "blocked"
    save_ledger(session, ledger)
    return ledger


def command_verify_final(args: argparse.Namespace) -> dict[str, Any]:
    session = Path(args.session).expanduser().resolve()
    ledger = load_ledger(session)
    verification = verify_ledger_final(session, ledger, require_completion_receipt=True)
    return {
        "finalStatus": "READY" if verification["status"] == "PASS" else "BLOCKED",
        "lifecycleStatus": "final_verified" if verification["status"] == "PASS" else "blocked",
        "verification": verification,
        "completionReceipt": ledger.get("completionReceipt", {}),
    }


def main() -> int:
    args = parse_args()
    commands = {
        "start": command_start,
        "register-reference-usage-check": command_register_reference_usage_check,
        "register-reference-usage-record": command_register_reference_usage_record,
        "register-reference": command_register_reference,
        "register-cognition": command_register_cognition,
        "register-simulation": command_register_simulation,
        "register-plan": command_register_plan,
        "audit-layout": command_audit_layout,
        "register-build": command_register_build,
        "register-web-deck-evidence": command_register_web_deck_evidence,
        "register-design-system": command_register_design_system,
        "register-post-build": command_register_post_build,
        "lock-template": command_lock_template,
        "register-scaffold-disposal": command_register_scaffold_disposal,
        "can-start-next": command_can_start_next,
        "finalize": command_finalize,
        "verify-final": command_verify_final,
    }
    try:
        result = commands[args.command](args)
    except Exception as exc:
        result = {"status": "BLOCKED", "error": str(exc)}
        if getattr(args, "json", False):
            print(json.dumps(result, indent=2))
        else:
            print(f"BLOCKED: {exc}")
        return 1

    if getattr(args, "json", False):
        print(json.dumps(result, indent=2))
    else:
        if args.command == "can-start-next":
            print(("PASS" if result["canStart"] else "BLOCKED") + f": {result['reason']}")
        elif isinstance(result, dict) and "safeToProceed" in result:
            print(("PASS" if result["safeToProceed"] else "BLOCKED") + f": layout audit for {result['templateId']}")
        elif args.command == "verify-final":
            print(("PASS" if result["finalStatus"] == "READY" else "BLOCKED") + ": final lifecycle verification")
        else:
            print(f"PASS: {args.command}")
    if isinstance(result, dict) and result.get("finalStatus") == "BLOCKED":
        return 1
    if isinstance(result, dict) and result.get("safeToProceed") is False:
        return 1
    if isinstance(result, dict) and result.get("canStart") is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
